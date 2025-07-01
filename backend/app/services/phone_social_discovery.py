"""Asynchronous phone number to social account discovery."""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from typing import Dict, List, Optional

import httpx

from .social_service import run_maigret, run_sherlock

logger = logging.getLogger(__name__)


async def _run_with_backoff(coro, retries: int = 3, delay: float = 1.0):
    """Execute a coroutine with exponential backoff."""
    for attempt in range(1, retries + 1):
        try:
            return await coro()
        except Exception as exc:  # noqa: BLE001
            logger.warning("attempt %s failed: %s", attempt, exc)
            if attempt == retries:
                raise
            await asyncio.sleep(delay * attempt)


def _run_cli(cmd: List[str]) -> str:
    """Return stdout from running a CLI command."""
    return subprocess.check_output(cmd, text=True)


async def detectdee_usernames(number: str) -> List[str]:
    """Extract usernames from DetectDee CLI output."""
    cmd = ["detectdee", "--phone", number, "--json"]
    try:
        output = await _run_with_backoff(lambda: asyncio.to_thread(_run_cli, cmd))
        data = json.loads(output)
        return [r.get("username") for r in data.get("results", []) if r.get("username")]
    except Exception as exc:  # noqa: BLE001
        logger.debug("detectdee failed: %s", exc)
        return []


async def ignorant_usernames(number: str) -> List[str]:
    """Extract usernames from Ignorant CLI output."""
    cmd = ["ignorant", "--phone", number, "--json"]
    try:
        output = await _run_with_backoff(lambda: asyncio.to_thread(_run_cli, cmd))
        data = json.loads(output)
        return [r.get("username") for r in data.get("results", []) if r.get("username")]
    except Exception as exc:  # noqa: BLE001
        logger.debug("ignorant failed: %s", exc)
        return []


async def _fetch_scylla_usernames(number: str) -> List[str]:
    """Query scylla.sh for leaked usernames associated with the number."""
    url = f"https://scylla.sh/search?q={number}&type=phone"
    try:
        async with httpx.AsyncClient() as client:
            resp = await _run_with_backoff(lambda: client.get(url, timeout=10))
            if resp.status_code == 200:
                data = resp.json()
                return [row.get("username") for row in data.get("data", []) if row.get("username")]
    except Exception as exc:  # noqa: BLE001
        logger.debug("scylla lookup failed: %s", exc)
    return []


async def _collect_usernames(number: str) -> List[str]:
    """Return a deduplicated list of usernames for the phone number."""
    tasks = [
        asyncio.create_task(detectdee_usernames(number)),
        asyncio.create_task(ignorant_usernames(number)),
        asyncio.create_task(_fetch_scylla_usernames(number)),
    ]
    results = await asyncio.gather(*tasks)
    usernames: List[str] = []
    for lst in results:
        usernames.extend(lst)
    sanitized = number.lstrip("+").replace(" ", "").replace("-", "")
    usernames.append(sanitized)
    return list(dict.fromkeys([u for u in usernames if u]))


async def _run_profile_queries(username: str) -> List[Dict[str, str]]:
    """Run Maigret and Sherlock for a single username."""
    maigret_future = asyncio.to_thread(run_maigret, username)
    sherlock_future = asyncio.to_thread(run_sherlock, username)
    results = await asyncio.gather(maigret_future, sherlock_future)
    accounts: List[Dict[str, str]] = []
    for arr in results:
        accounts.extend(arr or [])
    return accounts


async def discover_social_accounts(number: str) -> Dict[str, Dict[str, Optional[str]]]:
    """Discover social media profiles associated with ``number``."""
    usernames = await _collect_usernames(number)
    if not usernames:
        return {}

    tasks = [asyncio.create_task(_run_profile_queries(u)) for u in usernames]
    results = await asyncio.gather(*tasks)
    accounts: List[Dict[str, str]] = []
    for arr in results:
        accounts.extend(arr)

    aggregated: Dict[str, Dict[str, Optional[str]]] = {}
    for acc in accounts:
        platform = acc.get("platform")
        if not platform:
            continue
        key = platform.lower()
        if key in aggregated:
            continue
        aggregated[key] = {
            "platform": platform,
            "username": acc.get("username"),
            "profile": acc.get("profile"),
            "status": acc.get("status", "unknown"),
        }
    return aggregated


__all__ = ["discover_social_accounts"]


if __name__ == "__main__":
    import json as _json

    result = asyncio.run(discover_social_accounts("+12024561111"))
    print(_json.dumps(result, indent=2))
