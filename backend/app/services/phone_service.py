import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import asyncio
import time
import httpx
from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError
import requests

import logging

from .phone_meta_service import parse_phone
from .social_service import run_maigret, run_sherlock
from .email_guess_service import guess_emails
from .breach_service import scylla_lookup, dehashed_lookup
from .relationship_service import build_relationship_map


# simple in-memory cache {phone_number: response_dict}
CACHE: Dict[str, dict] = {}

# ensure logs directory exists
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "queries.log")
# relationships log
REL_LOG_PATH = os.path.join(LOG_DIR, "relationships.log")

# basic logging setup
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s\t%(levelname)s\t%(message)s",
)

# separate logger for relationship mapping
rel_logger = logging.getLogger("relationships")
rel_handler = logging.FileHandler(REL_LOG_PATH)
rel_logger.addHandler(rel_handler)
rel_logger.setLevel(logging.INFO)


def _query_maigret(number: str) -> List[str]:
    return [a["profile"] for a in run_maigret(number)]


def _query_sherlock(number: str) -> List[str]:
    return [a["profile"] for a in run_sherlock(number)]


def _query_hibp(number: str) -> List[str]:
    breaches = scylla_lookup(number, "phone")
    if not breaches:
        breaches = dehashed_lookup(number)
    return breaches


async def _a_query_maigret(number: str) -> List[str]:
    return await asyncio.to_thread(_query_maigret, number)


async def _a_query_hibp(number: str) -> List[str]:
    return await asyncio.to_thread(_query_hibp, number)


async def _a_query_sherlock(number: str) -> List[str]:
    return await asyncio.to_thread(_query_sherlock, number)


def _scylla_email_lookup(number: str) -> List[str]:
    """Return emails from scylla.sh related to the phone number."""
    url = f"https://scylla.sh/search?q={number}&type=phone"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            emails = [
                row.get("email") for row in data.get("data", []) if row.get("email")
            ]
            return list(dict.fromkeys(emails))
    except Exception:
        pass
    return []


async def _a_scylla_email_lookup(number: str) -> List[str]:
    return await asyncio.to_thread(_scylla_email_lookup, number)


def _verify_email(email: str) -> bool:
    """Validate email syntax and MX availability."""
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False


async def _a_verify_email(email: str) -> bool:
    return await asyncio.to_thread(_verify_email, email)


def _detect_platform(url: str) -> str:
    url = url.lower()
    if "facebook.com" in url:
        return "Facebook"
    if "instagram.com" in url:
        return "Instagram"
    if "tiktok.com" in url:
        return "TikTok"
    return "Unknown"


async def _fetch_avatar(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        resp = await client.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            meta = soup.find("meta", property="og:image") or soup.find(
                "meta", attrs={"name": "twitter:image"}
            )
            if meta and meta.get("content"):
                return meta["content"]
            img = soup.find("img")
            if img and img.get("src"):
                return img["src"]
    except Exception:
        pass
    return None


async def _gather_profile_data(urls: List[str]) -> List[Dict]:
    results: List[Dict] = []
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [asyncio.create_task(_fetch_avatar(client, u)) for u in urls]
        avatars = await asyncio.gather(*tasks)
    for url, avatar in zip(urls, avatars):
        results.append(
            {
                "platform": _detect_platform(url),
                "profile_url": url,
                "profile_picture": avatar,
            }
        )
    return results


async def _collect_social_profiles(number: str) -> List[Dict]:
    maigret_accounts = await asyncio.to_thread(run_maigret, number)
    sherlock_accounts = await asyncio.to_thread(run_sherlock, number)
    accounts = maigret_accounts + [
        a for a in sherlock_accounts if a not in maigret_accounts
    ]
    urls = [a.get("profile") for a in accounts if a.get("profile")]
    details = await _gather_profile_data(urls)
    for detail in details:
        for a in accounts:
            if a.get("profile") == detail["profile_url"]:
                detail["username"] = a.get("username")
                break
    return details


async def _collect_emails(number: str) -> Tuple[List[str], List[str]]:
    dataset_emails = await _a_lookup_emails(number)
    scylla_emails = await _a_scylla_email_lookup(number)
    emails = list(dict.fromkeys(dataset_emails + scylla_emails))
    if not emails:
        return [], []
    verif_tasks = [asyncio.create_task(_a_verify_email(e)) for e in emails]
    verifs = await asyncio.gather(*verif_tasks)
    valid_emails = [e for e, ok in zip(emails, verifs) if ok]
    breach_tasks = [asyncio.create_task(_a_query_email_hibp(e)) for e in valid_emails]
    breach_results = await asyncio.gather(*breach_tasks)
    email_breaches: List[str] = []
    for br in breach_results:
        if br:
            email_breaches.extend(br)
    return valid_emails, list(dict.fromkeys(email_breaches))


def _lookup_emails(number: str) -> List[str]:
    """Return known emails for a phone number from the mock dataset."""
    data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/mock_data.json")
    )
    try:
        with open(data_path) as f:
            dataset = json.load(f)
        for entry in dataset:
            if entry.get("phone_number") == number and entry.get("email"):
                return [entry["email"]]
    except Exception:
        pass
    return []


async def _a_lookup_emails(number: str) -> List[str]:
    return await asyncio.to_thread(_lookup_emails, number)


def _query_email_hibp(email: str) -> List[str]:
    return scylla_lookup(email, "email") or dehashed_lookup(email)


async def _a_query_email_hibp(email: str) -> List[str]:
    return await asyncio.to_thread(_query_email_hibp, email)


def _log_query(phone: str, status: str, error: Optional[str] = None) -> None:
    if error:
        logging.error("%s\t%s", phone, error)
    else:
        logging.info("%s\t%s", phone, status)


def _log_source_time(phone: str, source: str, duration: float) -> None:
    """Log time taken for a specific source lookup."""
    logging.info("%s\t%s_time\t%.2f", phone, source, duration)


async def _a_build_relationship_map(
    number: str,
    accounts: List[str],
    breaches: List[str],
    emails: Optional[List[str]] = None,
) -> (List[Dict], Dict):
    return await asyncio.to_thread(
        build_relationship_map, number, accounts, breaches, emails
    )


def analyze_phone(phone_number: str) -> dict:
    """Return OSINT intelligence for the given phone number."""
    if phone_number in CACHE:
        return CACHE[phone_number]

    result: Dict = {
        "phone_number": phone_number,
        "valid": False,
        "country": "Unknown",
        "carrier": None,
        "name": None,
        "accounts": [],
        "profiles": [],
        "breaches": [],
        "emails": [],
        "email_breaches": [],
        "connections": [],
        "graph": {},
    }

    meta = parse_phone(phone_number)
    result["valid"] = meta.get("valid")
    result["country"] = meta.get("country")
    result["carrier"] = meta.get("carrier")
    result["line_type"] = meta.get("line_type")
    if not result["valid"]:
        resp = {
            "status": "error",
            "data": None,
            "errors": "Invalid phone number",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        _log_query(phone_number, resp["status"], resp["errors"])
        return resp

    try:
        result["accounts"] = _query_maigret(phone_number)
        result["breaches"] = _query_hibp(phone_number)
        result["emails"] = _lookup_emails(phone_number)
        email_breaches = []
        for em in result["emails"]:
            email_breaches.extend(_breach_lookup(em))
        result["email_breaches"] = list(dict.fromkeys(email_breaches))
        result["connections"], result["graph"] = build_relationship_map(
            phone_number,
            result["accounts"],
            result["breaches"],
            result["emails"],
        )
    except Exception as exc:
        resp = {
            "status": "error",
            "data": None,
            "errors": "Lookup failed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        _log_query(phone_number, resp["status"], str(exc))
        return resp

    resp = {
        "status": "success",
        "data": result,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    CACHE[phone_number] = resp
    _log_query(phone_number, resp["status"])
    return resp


async def multi_source_lookup(phone_number: str) -> dict:
    """Run multiple OSINT lookups concurrently for a phone number."""
    if phone_number in CACHE:
        return CACHE[phone_number]

    result: Dict = {
        "phone_number": phone_number,
        "valid": False,
        "country": "Unknown",
        "carrier": None,
        "name": None,
        "accounts": [],
        "breaches": [],
        "emails": [],
        "email_breaches": [],
        "connections": [],
        "graph": {},
        "sources_used": [],
    }

    errors: Dict[str, Optional[str]] = {}
    timings: Dict[str, float] = {}

    # parse phone number first
    meta = parse_phone(phone_number)
    result["valid"] = meta.get("valid")
    result["country"] = meta.get("country")
    result["carrier"] = meta.get("carrier")
    result["line_type"] = meta.get("line_type")
    result["sources_used"].append("phonenumbers")
    if not result["valid"]:
        resp = {
            "status": "error",
            "data": None,
            "errors": {"phonenumbers": "invalid"},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        _log_query(phone_number, resp["status"], "Invalid phone number")
        return resp

    async def run_source(name: str, coro):
        start = time.perf_counter()
        try:
            res = await coro
            timings[name] = time.perf_counter() - start
            _log_source_time(phone_number, name, timings[name])
            return res
        except Exception as exc:
            timings[name] = time.perf_counter() - start
            _log_source_time(phone_number, name, timings[name])
            errors[name] = str(exc)
            return None

    tasks = {
        "social": asyncio.create_task(
            run_source("social", _collect_social_profiles(phone_number))
        ),
        "hibp": asyncio.create_task(run_source("hibp", _a_query_hibp(phone_number))),
        "emails": asyncio.create_task(
            run_source("emails", _collect_emails(phone_number))
        ),
    }

    results = await asyncio.gather(*tasks.values())
    profiles, breaches, email_data = results
    valid_emails, email_breaches = email_data or ([], [])

    if profiles is not None:
        result["profiles"] = profiles
        result["accounts"] = [p.get("profile_url") for p in profiles]
        if profiles:
            result["sources_used"].append("maigret")
            result["sources_used"].append("sherlock")
            result["sources_used"].append("avatar_scrape")

    if breaches is not None:
        result["breaches"] = breaches
        if breaches:
            result["sources_used"].append("hibp")

    if valid_emails is not None:
        result["emails"] = valid_emails
        if valid_emails:
            result["sources_used"].append("mock dataset")

    if email_breaches:
        result["email_breaches"] = email_breaches
        result["sources_used"].append("hibp_email")

    connections, graph = await _a_build_relationship_map(
        phone_number, result["accounts"], result["breaches"], result["emails"]
    )
    result["connections"] = connections
    result["graph"] = graph

    resp = {
        "status": "success",
        "data": result,
        "errors": errors or None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    CACHE[phone_number] = resp
    _log_query(phone_number, resp["status"])
    return resp


def _calculate_confidence(data: Dict) -> float:
    """Simple heuristic to assign a confidence score."""
    score = 0.0
    if data.get("valid"):
        score += 0.2
    if data.get("carrier"):
        score += 0.2
    if data.get("accounts"):
        score += 0.2
    if data.get("breaches"):
        score += 0.2
    if data.get("connections"):
        score += 0.2
    return round(min(score, 1.0), 2)


def enrich_phone_data(phone_number: str) -> dict:
    """Run lookups and return a unified enrichment structure."""
    result = asyncio.run(multi_source_lookup(phone_number))
    if result.get("status") != "success" or not result.get("data"):
        return result

    data = result["data"]
    unified = {
        "phone": data.get("phone_number"),
        "valid": data.get("valid"),
        "country": data.get("country"),
        "carrier": data.get("carrier"),
        "line_type": data.get("line_type"),
        "name": data.get("name"),
        "social_profiles": data.get("accounts", []),
        "profile_details": data.get("profiles", []),
        "emails": data.get("emails", []),
        "email_breaches": data.get("email_breaches", []),
        "breaches": data.get("breaches", []),
        "connections": data.get("connections", []),
        "confidence_score": _calculate_confidence(data),
        "sources": data.get("sources_used", []),
    }

    return {
        "status": result["status"],
        "data": unified,
        "errors": result.get("errors"),
        "timestamp": result.get("timestamp"),
    }


async def a_enrich_phone_data(phone_number: str) -> dict:
    """Async wrapper around :func:`enrich_phone_data`."""
    result = await multi_source_lookup(phone_number)
    if result.get("status") != "success" or not result.get("data"):
        return result

    data = result["data"]
    unified = {
        "phone": data.get("phone_number"),
        "valid": data.get("valid"),
        "country": data.get("country"),
        "carrier": data.get("carrier"),
        "line_type": data.get("line_type"),
        "name": data.get("name"),
        "social_profiles": data.get("accounts", []),
        "profile_details": data.get("profiles", []),
        "emails": data.get("emails", []),
        "email_breaches": data.get("email_breaches", []),
        "breaches": data.get("breaches", []),
        "connections": data.get("connections", []),
        "confidence_score": _calculate_confidence(data),
        "sources": data.get("sources_used", []),
    }

    return {
        "status": result["status"],
        "data": unified,
        "errors": result.get("errors"),
        "timestamp": result.get("timestamp"),
    }
