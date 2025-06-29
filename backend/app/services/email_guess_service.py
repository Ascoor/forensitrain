from typing import List, Dict


def guess_emails(usernames: List[str]) -> List[Dict]:
    """Return possible free email addresses based on usernames."""
    emails = []
    for name in usernames:
        emails.append({
            "email": f"{name}@gmail.com",
            "source": "inferred",
            "confidence": 0.85,
        })
        emails.append({
            "email": f"{name}@hotmail.com",
            "source": "inferred",
            "confidence": 0.75,
        })
    return emails
