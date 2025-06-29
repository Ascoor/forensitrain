import io
import os
from typing import Dict, List, Optional

import requests
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup

from .advanced_osint_service import (
    apify_social_media_finder,
    social_searcher_mentions,
)


OCR_SPACE_API = "https://api.ocr.space/parse/image"


def extract_text_from_image(image_bytes: bytes) -> str:
    """Return visible text in an image using OCR.space or Tesseract."""
    api_key = os.getenv("OCR_SPACE_KEY")
    if api_key:
        try:
            resp = requests.post(
                OCR_SPACE_API,
                files={"filename": ("image.jpg", image_bytes)},
                data={"language": "eng", "apikey": api_key, "isOverlayRequired": False},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                text_parts = [res.get("ParsedText", "") for res in data.get("ParsedResults", [])]
                text = " ".join(text_parts).strip()
                if text:
                    return text
        except Exception:
            pass
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang="ara")
        return text.strip()
    except Exception:
        return ""


def validate_and_normalize_email(email_str: str) -> Dict[str, object]:
    """Check email syntax and existence via Anymail Finder."""
    result = {"valid": False, "email": email_str.strip().lower()}
    api_key = os.getenv("ANYMAILFINDER_KEY")
    if api_key:
        try:
            resp = requests.get(
                "https://api.anymailfinder.com/v5.0/search/verify",
                params={"email": result["email"]},
                headers={"X-Api-Key": api_key},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                result["valid"] = data.get("status") == "deliverable"
                result["email"] = data.get("email", result["email"])
                return result
        except Exception:
            pass
    try:
        from email_validator import validate_email, EmailNotValidError

        info = validate_email(email_str, check_deliverability=True)
        result["valid"] = True
        result["email"] = info.email
    except (EmailNotValidError, Exception):
        result["valid"] = False
    return result


def find_profiles_by_email(email_str: str) -> Dict[str, Optional[str]]:
    """Use Proxycurl to resolve social profiles from an email."""
    api_key = os.getenv("PROXYCURL_KEY")
    result = {"facebook": None, "linkedin": None, "twitter": None}
    if not api_key:
        return result
    try:
        resp = requests.get(
            "https://nubela.co/proxycurl/api/v2/linkedin/profile/resolve/email",
            params={"email": email_str},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            result["linkedin"] = data.get("linkedin_profile_url")
            result["facebook"] = data.get("facebook_url")
            result["twitter"] = data.get("twitter_url")
    except Exception:
        pass
    return result


def find_profiles_by_name(name_str: str) -> List[str]:
    """Search for social media profiles by name using Apify or SocialSearcher."""
    results: List[str] = []
    token = os.getenv("APIFY_TOKEN")
    if token:
        try:
            items = apify_social_media_finder(name_str, token)
            for item in items:
                for key in ("facebook", "linkedin", "twitter", "instagram"):
                    url = item.get(key) or item.get(f"{key}_url")
                    if url:
                        results.append(url)
        except Exception:
            pass
    api_key = os.getenv("SOCIAL_SEARCHER_KEY")
    if not results and api_key:
        try:
            posts = social_searcher_mentions(name_str, api_key)
            for p in posts:
                url = p.get("url")
                if url:
                    results.append(url)
        except Exception:
            pass
    return list(dict.fromkeys(results))


def _fetch_profile_picture(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=10)
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


def aggregate_results(
    image_bytes: Optional[bytes], email_list: List[str], name_str: str
) -> Dict[str, object]:
    """Run full OSINT pipeline and return combined results."""

    text = extract_text_from_image(image_bytes) if image_bytes else ""

    validated = [validate_and_normalize_email(e) for e in email_list]
    valid_emails = [r["email"] for r in validated if r["valid"]]

    profiles: Dict[str, Optional[str]] = {}
    profile_pics: List[str] = []
    for e in valid_emails:
        found = find_profiles_by_email(e)
        for key, url in found.items():
            if url and key not in profiles:
                profiles[key] = url
                pic = _fetch_profile_picture(url)
                if pic:
                    profile_pics.append(pic)

    name_urls = find_profiles_by_name(name_str)
    for url in name_urls:
        if url not in profiles.values():
            pic = _fetch_profile_picture(url)
            if pic:
                profile_pics.append(pic)
    combined_urls = list(dict.fromkeys(list(profiles.values()) + name_urls))

    return {
        "text": text,
        "emails": validated,
        "profiles": combined_urls,
        "profile_pictures": list(dict.fromkeys(profile_pics)),
    }
