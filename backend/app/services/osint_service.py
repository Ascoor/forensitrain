import os
import json
from datetime import datetime
from typing import List, Dict

from .phone_meta_service import parse_phone
from .social_service import run_maigret, run_sherlock
from .email_guess_service import guess_emails
from .breach_service import scylla_lookup, dehashed_lookup
from .relationship_service import build_relationship_map

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(LOG_DIR, exist_ok=True)





def _infer_emails(usernames: List[str]) -> List[Dict]:
    return guess_emails(usernames)


def _breach_lookup(email: str) -> List[str]:
    breaches = scylla_lookup(email, "email")
    if not breaches:
        breaches = dehashed_lookup(email)
    return breaches




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

    meta = parse_phone(phone_number)
    sources_used = ["phonenumbers"]

    usernames = _derive_usernames(phone_number)
    accounts: List[Dict] = []

    for uname in usernames:
        accounts.extend(run_sherlock(uname))
        accounts.extend(run_maigret(uname))
    accounts.extend(run_maigret(phone_number))
    if accounts:
        sources_used.append("maigret")
        sources_used.append("sherlock")

    emails = _infer_emails(usernames)
    if emails:
        sources_used.append("inference")

    breaches = []
    for e in emails:
        exposures = _breach_lookup(e["email"])
        if exposures:
            breaches.extend(exposures)
            sources_used.append("scylla")

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
