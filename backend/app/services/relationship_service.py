import json
import os
from typing import List, Dict, Optional
import logging

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(LOG_DIR, exist_ok=True)
REL_LOG_PATH = os.path.join(LOG_DIR, "relationships.log")
rel_logger = logging.getLogger("relationships")
rel_handler = logging.FileHandler(REL_LOG_PATH)
rel_logger.addHandler(rel_handler)
rel_logger.setLevel(logging.INFO)


def build_relationship_map(
    number: str,
    accounts: List[str],
    breaches: List[str],
    emails: Optional[List[str]] = None,
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
    email_map = {e.get("phone_number"): e.get("email") for e in dataset if e.get("email")}

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

    if number in entry_map:
        entry = entry_map[number]
        email = entry.get("email")
        if email:
            if not any(n.get("id") == email for n in nodes):
                nodes.append({"id": email, "label": email})
            edges.append({"from": number, "to": email, "label": "email"})
            relationships.append(
                {
                    "email": email,
                    "relationship": "associated email",
                    "source": "mock dataset",
                }
            )
            rel_logger.info("%s\t%s\t%s\t%s", number, email, "email", "mock dataset")
            for pn, em in email_map.items():
                if em == email and pn != number:
                    add_relation(pn, entry_map.get(pn, {}).get("name"), "shared email", "mock dataset")
                    edges.append({"from": email, "to": pn, "label": "shared email"})
        for conn in entry.get("connections", []):
            target = entry_map.get(conn)
            add_relation(
                conn,
                target.get("name") if target else None,
                "known connection",
                "mock dataset",
            )

    for pn, entry in entry_map.items():
        if pn == number:
            continue
        if number in entry.get("connections", []):
            add_relation(pn, entry.get("name"), "linked connection", "mock dataset")
        if set(accounts) & set(entry.get("accounts", [])):
            add_relation(pn, entry.get("name"), "shared social account", "mock dataset")

    graph = {"nodes": nodes, "edges": edges}
    return relationships, graph
