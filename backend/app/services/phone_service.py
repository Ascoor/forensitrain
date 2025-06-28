import json
import os
import subprocess
from typing import List, Dict

import phonenumbers
from phonenumbers import carrier, geocoder
import requests


HIBP_API_KEY = os.getenv("HIBP_API_KEY")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY")


def _query_numverify(number: str) -> Dict:
    """Query numverify API for enriched phone metadata."""
    if not NUMVERIFY_API_KEY:
        return {}
    url = (
        f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


def _query_maigret(number: str) -> List[str]:
    """Run Maigret CLI to find social profiles for the phone number."""
    profiles = []
    cmd = ["maigret", number, "--json"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, check=False
        )
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            for site in data.get("sites", []):
                url = site.get("url")
                if url:
                    profiles.append(url)
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


def analyze_phone(phone_number: str) -> dict:
    """Return OSINT intelligence for the given phone number."""
    result: Dict = {
        "phone_number": phone_number,
        "valid": False,
        "country": "Unknown",
        "carrier": None,
        "name": None,
        "accounts": [],
        "breaches": [],
    }

    try:
        parsed = phonenumbers.parse(phone_number, None)
        result["valid"] = phonenumbers.is_valid_number(parsed)
        result["country"] = geocoder.description_for_number(parsed, "en")
        result["carrier"] = carrier.name_for_number(parsed, "en")
    except phonenumbers.NumberParseException:
        return result

    meta = _query_numverify(phone_number)
    if meta:
        result["carrier"] = meta.get("carrier") or result["carrier"]
        result["line_type"] = meta.get("line_type")
        result["name"] = meta.get("location")

    result["accounts"] = _query_maigret(phone_number)
    result["breaches"] = _query_hibp(phone_number)

    return result
