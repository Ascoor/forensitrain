import io
import os
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from extractor_phone_email import extract_emails, extract_phone_numbers

from .phone_meta_service import parse_phone
from .social_service import run_sherlock
from .image_service import analyze_image_bytes
from .misc_profile_service import find_profiles_by_email


def analyze_phone(number: str) -> Dict[str, object]:
    """Parse phone metadata using phonenumbers."""
    return parse_phone(number)


def analyze_text(text: str) -> Dict[str, List[str]]:
    """Extract phones and emails from raw text or HTML."""
    phones = extract_phone_numbers(text)
    emails = extract_emails(text)
    try:
        soup = BeautifulSoup(text, "html.parser")
        plain = soup.get_text()
        phones.extend(extract_phone_numbers(plain))
        emails.extend(extract_emails(plain))
    except Exception:
        pass
    return {"phones": list(dict.fromkeys(phones)), "emails": list(dict.fromkeys(emails))}


def search_social(query: str) -> List[str]:
    """Lookup social profiles via snscrape, sherlock and Proxycurl."""
    results: List[str] = []
    try:
        import snscrape.modules.twitter as tw

        for item in tw.TwitterSearchScraper(query).get_items():
            results.append(f"https://twitter.com/{item.user.username}")
            if len(results) >= 10:
                break
    except Exception:
        pass
    try:
        accounts = run_sherlock(query)
        for a in accounts:
            url = a.get("profile")
            if url:
                results.append(url)
    except Exception:
        pass
    if "@" in query:
        profiles = find_profiles_by_email(query)
        for url in profiles.values():
            if url:
                results.append(url)
    return list(dict.fromkeys(results))


def analyze_image(data: bytes) -> Dict[str, object]:
    """Run OCR and face/object detection on the given image bytes."""
    return analyze_image_bytes(data)
