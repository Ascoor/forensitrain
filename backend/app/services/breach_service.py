import requests
from typing import List


def scylla_lookup(query: str, qtype: str = "email") -> List[str]:
    """Query scylla.sh for breach records related to an email or phone."""
    url = f"https://scylla.sh/search?q={query}&type={qtype}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            breaches = [row.get("source") for row in data.get("data", []) if row.get("source")]
            return list(dict.fromkeys(breaches))
    except Exception:
        pass
    return []


def dehashed_lookup(query: str) -> List[str]:
    """Query the public dehashed API for breach exposures."""
    url = f"https://api.dehashed.com/search?query={query}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            breaches = [r.get("source") for r in data.get("entries", []) if r.get("source")]
            return list(dict.fromkeys(breaches))
    except Exception:
        pass
    return []
