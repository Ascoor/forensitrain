import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

import logging

from dotenv import load_dotenv

import phonenumbers
from phonenumbers import carrier, geocoder
import requests

load_dotenv()


HIBP_API_KEY = os.getenv("HIBP_API_KEY")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY")

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


def _query_numverify(number: str) -> Dict:
    """Query numverify API for enriched phone metadata."""
    if not NUMVERIFY_API_KEY:
        return {}
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


def _query_maigret(number: str) -> List[str]:
    """Run Maigret CLI to find social profiles for the phone number."""
    profiles: List[str] = []
    output_path = os.path.join(LOG_DIR, f"maigret_{number}.json")
    cmd = ["maigret", number, "--json", "--top-sites", "-o", output_path]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if os.path.exists(output_path):
            with open(output_path) as f:
                data = json.load(f)
            for site in data.get("sites", []):
                url = site.get("url")
                if url:
                    profiles.append(url)
            os.remove(output_path)
    except Exception:
        pass
    return profiles


def _query_hibp(number: str) -> List[str]:
    """Check HaveIBeenPwned for breach exposure."""
    if not HIBP_API_KEY:
        return []
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{number}"
    headers = {"hibp-api-key": HIBP_API_KEY, "user-agent": "ForensiTrain"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return [b.get("Name") for b in resp.json()]
    except Exception:
        pass
    return []


def _log_query(phone: str, status: str, error: Optional[str] = None) -> None:
    if error:
        logging.error("%s\t%s", phone, error)
    else:
        logging.info("%s\t%s", phone, status)


def build_relationship_map(
    number: str, accounts: List[str], breaches: List[str]
) -> (List[Dict], Dict):
    """Create relationship mapping for a phone number based on mock data."""
    relationships: List[Dict] = []
    nodes: List[Dict] = [{"id": number, "label": number}]
    edges: List[Dict] = []

    data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/mock_data.json")
    )
    try:
        with open(data_path) as f:
            dataset = json.load(f)
    except Exception:
        dataset = []

    entry_map = {e.get("phone_number"): e for e in dataset}

    def add_relation(target: str, name: Optional[str], rel: str, source: str) -> None:
        data = {
            "phone_number": target,
            "name": name,
            "relationship": rel,
            "source": source,
        }
        if data not in relationships:
            relationships.append(data)
            nodes.append({"id": target, "label": name or target})
            edges.append({"from": number, "to": target, "label": rel})
            rel_logger.info("%s\t%s\t%s\t%s", number, target, rel, source)

    # direct connections from dataset
    if number in entry_map:
        entry = entry_map[number]
        for conn in entry.get("connections", []):
            target = entry_map.get(conn)
            add_relation(
                conn,
                target.get("name") if target else None,
                "known connection",
                "mock dataset",
            )

    # connections pointing back to this number or shared data
    for pn, entry in entry_map.items():
        if pn == number:
            continue
        if number in entry.get("connections", []):
            add_relation(pn, entry.get("name"), "linked connection", "mock dataset")
        if set(accounts) & set(entry.get("accounts", [])):
            add_relation(pn, entry.get("name"), "shared social account", "mock dataset")

    graph = {"nodes": nodes, "edges": edges}
    return relationships, graph


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
        "breaches": [],
        "connections": [],
        "graph": {},
    }

    try:
        parsed = phonenumbers.parse(phone_number, None)
        result["valid"] = phonenumbers.is_valid_number(parsed)
        result["country"] = geocoder.description_for_number(parsed, "en")
        result["carrier"] = carrier.name_for_number(parsed, "en")
    except phonenumbers.NumberParseException:
        resp = {
            "status": "error",
            "data": None,
            "errors": "Invalid phone number",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        _log_query(phone_number, resp["status"], resp["errors"])
        return resp

    try:
        meta = _query_numverify(phone_number)
        if meta:
            result["carrier"] = meta.get("carrier") or result["carrier"]
            result["line_type"] = meta.get("line_type")
            result["name"] = meta.get("location")

        result["accounts"] = _query_maigret(phone_number)
        result["breaches"] = _query_hibp(phone_number)
        result["connections"], result["graph"] = build_relationship_map(
            phone_number, result["accounts"], result["breaches"]
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
