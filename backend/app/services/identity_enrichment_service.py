import asyncio
import hashlib
import logging
import re
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

# simple in-memory cache
_CACHE: Dict[str, dict] = {}

# concurrency limit for HTTP requests
_SEMAPHORE = asyncio.Semaphore(5)

logger = logging.getLogger(__name__)


async def _fetch(client: httpx.AsyncClient, url: str) -> Optional[httpx.Response]:
    """Fetch a URL with basic error handling."""
    try:
        async with _SEMAPHORE:
            resp = await client.get(url, timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            return resp
    except Exception as exc:  # noqa: BLE001
        logger.debug("fetch failed for %s: %s", url, exc)
    return None


def _extract_og_image(html: str) -> Optional[str]:
    """Return open graph image URL from HTML if present."""
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", property="og:image") or soup.find(
        "meta", attrs={"name": "twitter:image"}
    )
    if meta and meta.get("content"):
        return meta["content"]
    img = soup.find("img")
    if img and img.get("src"):
        return img["src"]
    return None


async def _check_social(client: httpx.AsyncClient, platform: str, url: str, username: str) -> Optional[Dict]:
    """Check if a social profile exists and return details."""
    resp = await _fetch(client, url)
    if not resp:
        return None
    img = _extract_og_image(resp.text)
    return {
        "platform": platform,
        "username": username,
        "url": str(resp.url),
        "avatar": img,
    }


async def _gravatar_url(client: httpx.AsyncClient, email: str) -> Optional[str]:
    """Return gravatar URL if available for an email."""
    email = email.strip().lower()
    h = hashlib.md5(email.encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    resp = await _fetch(client, url)
    if resp:
        return str(resp.url)
    return None


async def _gmail_exists(client: httpx.AsyncClient, email: str) -> bool:
    """Return True if a Gmail account appears to exist."""
    if not email.lower().endswith("@gmail.com"):
        return False
    url = f"https://mail.google.com/mail/gxlu?email={email}"
    try:
        async with _SEMAPHORE:
            resp = await client.get(url, timeout=10, follow_redirects=False)
        return resp.status_code == 302 and "set-cookie" in resp.headers
    except Exception as exc:  # noqa: BLE001
        logger.debug("gmail check failed: %s", exc)
        return False


async def _emailrep_lookup(client: httpx.AsyncClient, email: str) -> Optional[Dict]:
    url = f"https://emailrep.io/{email}"
    resp = await _fetch(client, url)
    if resp:
        try:
            return resp.json()
        except Exception:  # noqa: BLE001
            return None
    return None


def _generate_usernames(identifier: str) -> List[str]:
    """Create possible usernames from input."""
    if "@" in identifier:
        base = identifier.split("@", 1)[0]
        return [base, base.replace(".", ""), base.replace(".", "_")]
    if re.fullmatch(r"\+?\d+", identifier):
        digits = re.sub(r"\D", "", identifier)
        return [digits, digits[-7:]]
    parts = re.split(r"\s+", identifier.strip())
    if not parts:
        return []
    joined = "".join(parts)
    return [joined, "_".join(parts), ".".join(parts)]


async def enrich_identity(identifier: str) -> Dict:
    """Return publicly available social and email info for the identifier."""
    if identifier in _CACHE:
        return _CACHE[identifier]

    usernames = _generate_usernames(identifier)
    result: Dict[str, Optional[object]] = {
        "query": identifier,
        "gravatar": None,
        "gmail": False,
        "emailrep": None,
        "social_accounts": [],
        "profile_images": [],
    }

    async with httpx.AsyncClient() as client:
        tasks = []
        if "@" in identifier:
            tasks.append(asyncio.create_task(_gravatar_url(client, identifier)))
            tasks.append(asyncio.create_task(_gmail_exists(client, identifier)))
            tasks.append(asyncio.create_task(_emailrep_lookup(client, identifier)))
        social_tasks = []
        platforms = {
            "Facebook": "https://www.facebook.com/{username}",
            "Instagram": "https://www.instagram.com/{username}",
            "TikTok": "https://www.tiktok.com/@{username}",
            "Twitter": "https://twitter.com/{username}",
        }
        for uname in usernames:
            for platform, tmpl in platforms.items():
                url = tmpl.format(username=uname)
                social_tasks.append(
                    asyncio.create_task(_check_social(client, platform, url, uname))
                )
        social_results = await asyncio.gather(*social_tasks)
        social_accounts = [r for r in social_results if r]
        result["social_accounts"] = [
            {"platform": r["platform"], "url": r["url"], "username": r["username"]}
            for r in social_accounts
        ]
        images = [r["avatar"] for r in social_accounts if r.get("avatar")]

        if tasks:
            gravatar, gmail, emailrep = await asyncio.gather(*tasks)
            result["gravatar"] = gravatar
            result["gmail"] = bool(gmail)
            result["emailrep"] = emailrep
            if gravatar:
                images.append(gravatar)
        result["profile_images"] = images

    _CACHE[identifier] = result
    return result
