import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

import phonenumbers
from phonenumbers import carrier, geocoder
import requests
from dotenv import load_dotenv

from .phone_service import build_relationship_map

load_dotenv()

HIBP_API_KEY = os.getenv("HIBP_API_KEY")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY")

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(LOG_DIR, exist_ok=True)


def _numverify_lookup(number: str) -> Dict:
    if not NUMVERIFY_API_KEY:
        return {}
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def _run_maigret(target: str) -> List[Dict]:
    """Run Maigret CLI and parse results."""
    results: List[Dict] = []
    out_file = os.path.join(LOG_DIR, f"maigret_{target}.json")
    cmd = ["maigret", target, "--json", "--top-sites", "-o", out_file]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if os.path.exists(out_file):
            with open(out_file) as f:
                data = json.load(f)
            for site in data.get("sites", []):
                url = site.get("url") or site.get("url_user")
                if not url:
                    continue
                results.append({
                    "platform": site.get("name"),
                    "username": site.get("id"),
                    "profile": url,
                    "status": site.get("status") or "unknown",
                })
            os.remove(out_file)
    except Exception:
        pass
    return results


def _run_sherlock(username: str) -> List[Dict]:
    """Run Sherlock CLI for a username."""
    results: List[Dict] = []
    out_file = os.path.join(LOG_DIR, f"sherlock_{username}.json")
    cmd = ["sherlock", username, "--json", out_file]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if os.path.exists(out_file):
            with open(out_file) as f:
                data = json.load(f)
            for site, entry in data.items():
                url = entry.get("url")
                if not url:
                    continue
                results.append({
                    "platform": site,
                    "username": username,
                    "profile": url,
                    "status": entry.get("status", "unknown"),
                })
            os.remove(out_file)
    except Exception:
        pass
    return results


def _infer_emails(usernames: List[str]) -> List[Dict]:
    """Generate possible gmail addresses from usernames."""
    emails = []
    for name in usernames:
        addr = f"{name}@gmail.com"
        emails.append({"email": addr, "source": "inferred", "confidence": 0.85})
    return emails


def _hibp_breaches(email: str) -> List[str]:
    if not HIBP_API_KEY:
        return []
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=true"
    headers = {"hibp-api-key": HIBP_API_KEY, "user-agent": "ForensiTrain"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return [b.get("Name") for b in r.json()]
    except Exception:
        pass
    return []


def _parse_phone(number: str) -> Dict:
    data = {"phone": number, "country": "Unknown", "carrier": None, "valid": False}
    try:
        parsed = phonenumbers.parse(number, None)
        data["valid"] = phonenumbers.is_valid_number(parsed)
        data["country"] = geocoder.description_for_number(parsed, "en")
        data["carrier"] = carrier.name_for_number(parsed, "en")
    except phonenumbers.NumberParseException:
        pass
    return data


def _derive_usernames(number: str) -> List[str]:
    """Attempt to derive usernames from mock dataset or digits."""
    usernames = []
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/mock_data.json"))
    try:
        with open(dataset_path) as f:
            dataset = json.load(f)
        for entry in dataset:
            if entry.get("phone_number") == number:
                for acct in entry.get("accounts", []):
                    if ":" in acct:
                        usernames.append(acct.split(":", 1)[1])
    except Exception:
        pass
    if not usernames:
        digits = ''.join(filter(str.isdigit, number))
        if len(digits) >= 6:
            usernames.append(digits[-6:])
    return usernames



def extract_osint_footprint(phone_number: str) -> dict:
    """Return enriched OSINT footprint for a phone number.

    The function only uses openly available data sources and does not perform
    any intrusive probing. Results may be incomplete if external tools are not
    installed or API keys are missing.
    """

    meta = _parse_phone(phone_number)
    sources_used = ["phonenumbers"]

    if meta.get("valid"):
        nv = _numverify_lookup(phone_number)
        if nv:
            meta["carrier"] = nv.get("carrier") or meta.get("carrier")
            sources_used.append("numverify")

    usernames = _derive_usernames(phone_number)
    accounts: List[Dict] = []

    for uname in usernames:
        accounts.extend(_run_sherlock(uname))
        accounts.extend(_run_maigret(uname))
    accounts.extend(_run_maigret(phone_number))
    if accounts:
        sources_used.append("maigret")
        sources_used.append("sherlock")

    emails = _infer_emails(usernames)
    if emails:
        sources_used.append("inference")

    breaches = []
    for e in emails:
        exposures = _hibp_breaches(e["email"])
        if exposures:
            breaches.extend(exposures)
            sources_used.append("hibp")

    relationships, graph = build_relationship_map(phone_number, [a["profile"] for a in accounts], breaches)

    result = {
        "accounts": accounts,
        "emails": emails,
        "relationships": relationships,
        "metadata": {
            "phone": meta.get("phone"),
            "country": meta.get("country"),
            "carrier": meta.get("carrier"),
            "sources_used": list(dict.fromkeys(sources_used)),
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    return result
