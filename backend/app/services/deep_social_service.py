import asyncio
import httpx
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from .social_service import run_maigret, run_sherlock


_CACHE: Dict[str, dict] = {}


async def _fetch_html(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        resp = await client.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None


async def _extract_profile_picture(
    client: httpx.AsyncClient, url: str
) -> Optional[str]:
    html = await _fetch_html(client, url)
    if not html:
        return None
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


async def _extract_top_images(client: httpx.AsyncClient, url: str) -> List[Dict]:
    """Return a few prominent images from the profile page."""
    html = await _fetch_html(client, url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            images.append(src)
        if len(images) >= 3:
            break
    return [{"url": i} for i in images]


async def _process_account(client: httpx.AsyncClient, account: Dict) -> Dict:
    profile_url = account.get("profile")
    profile_pic = await _extract_profile_picture(client, profile_url)
    top_images = await _extract_top_images(client, profile_url)
    return {
        "platform": account.get("platform"),
        "username": account.get("username"),
        "profile_url": profile_url,
        "profile_picture": profile_pic,
        "top_images": top_images,
    }


async def deep_social_scan(identifier: str) -> Dict:
    if identifier in _CACHE:
        return _CACHE[identifier]

    maigret_accounts = run_maigret(identifier)
    sherlock_accounts = run_sherlock(identifier)
    accounts = maigret_accounts + [
        a for a in sherlock_accounts if a not in maigret_accounts
    ]

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [asyncio.create_task(_process_account(client, acc)) for acc in accounts]
        profiles = await asyncio.gather(*tasks)

    result = {"profiles": profiles}
    _CACHE[identifier] = result
    return result
