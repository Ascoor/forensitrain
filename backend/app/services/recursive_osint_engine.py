import json
import os
from typing import Dict, List, Set

from .phone_meta_service import parse_phone
from .social_service import run_maigret, run_sherlock
from .email_guess_service import guess_emails
from .breach_service import scylla_lookup

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/mock_data.json"))
try:
    with open(DATA_PATH) as f:
        DATASET = json.load(f)
except Exception:
    DATASET = []


def _phones_for_email(email: str) -> List[str]:
    phones = []
    for entry in DATASET:
        if entry.get("email") == email:
            phones.append(entry.get("phone_number"))
    return phones


def _phones_for_username(username: str) -> List[str]:
    phones = []
    for entry in DATASET:
        for acct in entry.get("accounts", []):
            if ":" in acct and acct.split(":", 1)[1] == username:
                phones.append(entry.get("phone_number"))
    return phones


def smart_osint_lookup(phone_number: str, depth: int = 2) -> dict:
    """Recursively gather OSINT intelligence about a phone number."""
    visited_phones: Set[str] = set()
    visited_emails: Set[str] = set()
    visited_usernames: Set[str] = set()

    entities = {"phones": [], "emails": [], "usernames": [], "accounts": []}
    relationships: List[Dict] = []
    sources: Set[str] = set()

    graph = {"nodes": [], "edges": []}

    def add_node(node_id: str, label: str, ntype: str):
        if not any(n.get("id") == node_id for n in graph["nodes"]):
            graph["nodes"].append({"id": node_id, "label": label, "type": ntype})

    def add_edge(frm: str, to: str, rel: str):
        graph["edges"].append({"from": frm, "to": to, "type": rel})

    def process_phone(pn: str, level: int):
        if pn in visited_phones or level > depth:
            return
        visited_phones.add(pn)
        entities["phones"].append(pn)
        add_node(pn, pn, "phone")

        meta = parse_phone(pn)
        sources.add("phonenumbers")
        if meta.get("carrier"):
            relationships.append({"from": pn, "to": meta.get("carrier"), "type": "carrier"})

        accounts = run_maigret(pn)
        if accounts:
            sources.add("maigret")
        for acct in accounts:
            entities["accounts"].append(acct)
            uname = acct.get("username")
            if uname and uname not in visited_usernames:
                visited_usernames.add(uname)
                entities["usernames"].append(uname)
                add_node(uname, uname, "username")
                add_edge(pn, uname, "possible_owner")

        for uname in list(visited_usernames):
            sherlock_accounts = run_sherlock(uname)
            if sherlock_accounts:
                sources.add("sherlock")
            for acct in sherlock_accounts:
                entities["accounts"].append(acct)
                add_edge(uname, acct.get("profile"), "social_presence")

        emails = guess_emails(list(visited_usernames))
        if emails:
            sources.add("inference")
        for e in emails:
            email = e.get("email")
            if email in visited_emails:
                continue
            visited_emails.add(email)
            entities["emails"].append(email)
            add_node(email, email, "email")
            add_edge(pn, email, "related_email")

            exposures = scylla_lookup(email, "email")
            if exposures:
                sources.add("scylla")
                for src in exposures:
                    relationships.append({"from": email, "to": src, "type": "breach"})

            for new_phone in _phones_for_email(email):
                add_edge(email, new_phone, "co-breached")
                process_phone(new_phone, level + 1)

        for uname in list(visited_usernames):
            for new_phone in _phones_for_username(uname):
                add_edge(uname, new_phone, "same_username")
                process_phone(new_phone, level + 1)

    process_phone(phone_number, 0)

    confidence = min(1.0, 0.25 * sum(bool(entities[key]) for key in entities))

    return {
        "entities": entities,
        "relationships": relationships,
        "graph": graph,
        "sources": list(sources),
        "confidence_scores": {"overall": round(confidence, 2)},
    }
