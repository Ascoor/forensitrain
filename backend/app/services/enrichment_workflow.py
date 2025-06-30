import asyncio
import logging
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

import httpx

from .phone_meta_service import parse_phone
from .phone_service import (
    _a_lookup_emails,
    _a_scylla_email_lookup,
    _a_verify_email,
    _a_query_hibp,
    _a_query_email_hibp,
    _fetch_avatar,
    _calculate_confidence,
)
from .social_service import run_maigret, run_sherlock
from .relationship_service import build_relationship_map
from .image_service import a_analyze_image_bytes

logger = logging.getLogger(__name__)


async def _run_with_retries(coro: Callable[[], Any], retries: int = 2, delay: float = 1.0) -> Any:
    """Execute coroutine with basic retry logic."""
    for attempt in range(1, retries + 1):
        try:
            return await coro()
        except Exception as exc:  # noqa: BLE001
            logger.warning("attempt %s failed: %s", attempt, exc)
            if attempt == retries:
                raise
            await asyncio.sleep(delay)


async def _discover_emails(number: str) -> List[str]:
    """Gather possible emails for the phone number and verify."""
    dataset_emails, scylla_emails = await asyncio.gather(
        _a_lookup_emails(number), _a_scylla_email_lookup(number)
    )
    emails = list(dict.fromkeys(dataset_emails + scylla_emails))
    if not emails:
        return []
    tasks = [asyncio.create_task(_a_verify_email(e)) for e in emails]
    verifs = await asyncio.gather(*tasks)
    return [e for e, ok in zip(emails, verifs) if ok]


async def _collect_accounts(number: str, emails: List[str]) -> List[Dict]:
    """Find social media accounts using Maigret and Sherlock."""
    tasks = [
        asyncio.to_thread(run_maigret, number),
        asyncio.to_thread(run_sherlock, number),
    ]
    for em in emails:
        tasks.append(asyncio.to_thread(run_maigret, em))
        tasks.append(asyncio.to_thread(run_sherlock, em))
    results = await asyncio.gather(*tasks)
    accounts = []
    for arr in results:
        accounts.extend(arr or [])
    seen = set()
    deduped = []
    for acc in accounts:
        url = acc.get("profile")
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(acc)
    return deduped


async def _process_profile(client: httpx.AsyncClient, profile: Dict) -> Dict:
    """Attach avatar and basic image analysis to a social profile."""
    avatar_url = await _run_with_retries(lambda: _fetch_avatar(client, profile["profile"]))
    analysis = None
    if avatar_url:
        try:
            resp = await client.get(avatar_url, timeout=10)
            if resp.status_code == 200:
                analysis = await a_analyze_image_bytes(resp.content)
        except Exception as exc:  # noqa: BLE001
            logger.debug("image analysis failed for %s: %s", avatar_url, exc)
    return {
        "platform": profile.get("platform"),
        "username": profile.get("username"),
        "profile_url": profile.get("profile"),
        "profile_picture": avatar_url,
        "image_analysis": analysis,
    }


async def run_enrichment(
    phone_number: str,
    progress_cb: Optional[Callable[[str, Any], None]] = None,
) -> Dict:
    """Orchestrate full enrichment workflow for a phone number."""

    def update(stage: str, data: Any) -> None:
        if progress_cb:
            progress_cb(stage, data)
        logger.info("stage %s complete", stage)

    meta = parse_phone(phone_number)
    update("phone", meta)
    if not meta.get("valid"):
        return {"status": "error", "errors": "invalid number", "data": None}

    emails = await _run_with_retries(lambda: _discover_emails(phone_number))
    update("emails", emails)

    accounts = await _run_with_retries(lambda: _collect_accounts(phone_number, emails))
    update("accounts", accounts)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [asyncio.create_task(_process_profile(client, p)) for p in accounts]
        profiles = await asyncio.gather(*tasks)
    update("profiles", profiles)

    phone_breaches, email_breach_lists = await asyncio.gather(
        _a_query_hibp(phone_number),
        asyncio.gather(*[asyncio.create_task(_a_query_email_hibp(e)) for e in emails])
    )
    email_breaches: List[str] = []
    for br in email_breach_lists:
        email_breaches.extend(br or [])
    breaches = list(dict.fromkeys(phone_breaches + email_breaches))
    update("breaches", breaches)

    connections, graph = await asyncio.to_thread(
        build_relationship_map, phone_number, [p["profile_url"] for p in profiles], breaches, emails
    )
    update("relationships", connections)

    data = {
        "phone_number": phone_number,
        "meta": meta,
        "emails": emails,
        "profiles": profiles,
        "breaches": breaches,
        "connections": connections,
        "graph": graph,
    }
    data["confidence"] = _calculate_confidence({
        "valid": meta.get("valid"),
        "carrier": meta.get("carrier"),
        "accounts": [p["profile_url"] for p in profiles],
        "breaches": breaches,
        "connections": connections,
    })
    update("complete", data)
    return {"status": "success", "data": data, "errors": None}
