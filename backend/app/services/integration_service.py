# -*- coding: utf-8 -*-
"""High level OSINT integration utilities.

This module provides asynchronous helpers to extract contact
information from raw text and enrich it using the existing
phone, email and social modules. Results can be consumed
by dashboard widgets in real time.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Dict, List, Tuple

import httpx
from email_validator import EmailNotValidError, validate_email

from .phone_meta_service import parse_phone
from .phone_service import multi_source_lookup
from .identity_enrichment_service import enrich_identity
from .image_service import a_analyze_image_bytes

# configure module level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\+?\d[\d\s().-]{5,}\d")


def extract_contacts(text: str) -> Tuple[List[str], List[str]]:
    """Return lists of valid phone numbers and emails from text."""
    emails = []
    for match in EMAIL_REGEX.findall(text):
        try:
            validate_email(match, check_deliverability=False)
            emails.append(match)
        except EmailNotValidError:
            continue

    phones = []
    for match in PHONE_REGEX.findall(text):
        data = parse_phone(match)
        if data.get("valid"):
            phones.append(match)
    return list(dict.fromkeys(phones)), list(dict.fromkeys(emails))


async def _fetch_image_bytes(url: str) -> bytes | None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.content
    except Exception as exc:  # noqa: BLE001
        logger.debug("image fetch failed for %s: %s", url, exc)
    return None


async def _analyze_profile_image(url: str) -> Dict | None:
    data = await _fetch_image_bytes(url)
    if not data:
        return None
    return await a_analyze_image_bytes(data)


async def _enrich_phone(number: str) -> Dict:
    logger.info("enriching phone %s", number)
    return await multi_source_lookup(number)


async def _enrich_email(email: str) -> Dict:
    logger.info("enriching email %s", email)
    return await enrich_identity(email)


async def full_osint_scan(text: str) -> Dict:
    """Run a complete OSINT workflow for the given text.

    Extracts contacts, fetches related social accounts and analyses
    profile images. The function returns a dictionary suitable for
    direct consumption by dashboard widgets.
    """

    phones, emails = extract_contacts(text)

    phone_tasks = [asyncio.create_task(_enrich_phone(p)) for p in phones]
    email_tasks = [asyncio.create_task(_enrich_email(e)) for e in emails]

    phone_results = await asyncio.gather(*phone_tasks) if phone_tasks else []
    email_results = await asyncio.gather(*email_tasks) if email_tasks else []

    image_tasks = []
    for result in phone_results:
        for prof in result.get("data", {}).get("profiles", []):
            if prof.get("profile_picture"):
                image_tasks.append(
                    asyncio.create_task(_analyze_profile_image(prof["profile_picture"]))
                )
    image_results = await asyncio.gather(*image_tasks) if image_tasks else []

    return {
        "phones": dict(zip(phones, phone_results)),
        "emails": dict(zip(emails, email_results)),
        "images": image_results,
    }


# Example usage
if __name__ == "__main__":
    sample = "Contact me at +12024561111 or user@example.com"
    data = asyncio.run(full_osint_scan(sample))
    print(data)
