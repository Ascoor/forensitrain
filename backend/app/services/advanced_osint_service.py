"""Additional OSINT utilities leveraging free services.
"""

from __future__ import annotations

import json
import subprocess
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
import networkx as nx


def hibp_breaches(email: str, api_key: str) -> List[Dict]:
    """Check an email against the HaveIBeenPwned API.

    Parameters
    ----------
    email: str
        Email address to look up.
    api_key: str
        API key for HaveIBeenPwned.

    Returns
    -------
    List[Dict]
        List of breach records. Empty list if none are found or an error occurs.
    """
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {"hibp-api-key": api_key, "user-agent": "forensitrain"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def google_darkweb_report(session: requests.Session, query: str) -> List[str]:
    """Scrape Google's "Results about you" dark-web report.

    This requires an authenticated session. The function does not handle the
    login process and assumes the session already contains valid cookies.
    The returned list contains raw text snippets from the report.
    """

    url = "https://myaccount.google.com/results-about-you/dark-web"
    try:
        resp = session.get(url, params={"q": query}, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        results = [t.get_text(strip=True) for t in soup.select("div[data-result]")]
        return results
    except Exception:
        return []


def social_searcher_mentions(term: str, api_key: str) -> List[Dict]:
    """Fetch social mentions using the SocialSearcher API."""
    url = "https://api.social-searcher.com/v2/search"
    try:
        resp = requests.get(url, params={"q": term, "key": api_key}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("posts", [])
    except Exception:
        pass
    return []


def apify_social_media_finder(name: str, token: str) -> List[Dict]:
    """Run Apify's Social Media Finder actor and return found accounts."""
    url = (
        "https://api.apify.com/v2/acts/apify~social-media-finder/run-sync-get-dataset-items"
    )
    try:
        resp = requests.post(url, params={"token": token}, json={"queries": [name]}, timeout=20)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def detectdee_lookup(query: str) -> List[Dict]:
    """Use DetectDee CLI to search by email or phone."""
    cmd = ["detect", query, "--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if proc.stdout:
            return json.loads(proc.stdout)
    except Exception:
        pass
    return []


def dialaxy_lookup(phone: str) -> List[Dict]:
    """Map a phone number to social links using Dialaxy."""
    url = "https://dialaxy.org/api/v1/search"
    try:
        resp = requests.get(url, params={"query": phone}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("profiles", [])
    except Exception:
        pass
    return []


def reverse_image_search(image_url: str) -> List[str]:
    """Perform a simple reverse image search via TinEye."""
    url = "https://tineye.com/search"
    try:
        resp = requests.get(url, params={"url": image_url}, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [a["href"] for a in soup.select("div.results a") if a.get("href")]
            return links
    except Exception:
        pass
    return []


def dork_search(query: str) -> List[str]:
    """Use DuckDuckGo to perform a basic dork query."""
    url = "https://duckduckgo.com/html/"
    try:
        resp = requests.get(url, params={"q": query}, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [a["href"] for a in soup.select("a.result__a") if a.get("href")]
            return links
    except Exception:
        pass
    return []


def build_relation_graph(accounts: List[Dict]) -> nx.Graph:
    """Build a simple relation graph of accounts by shared username."""
    graph = nx.Graph()
    for acct in accounts:
        node = f"{acct.get('platform')}:{acct.get('username')}"
        graph.add_node(node, **acct)
    username_map: Dict[str, str] = {}
    for acct in accounts:
        node = f"{acct.get('platform')}:{acct.get('username')}"
        uname = acct.get("username")
        if not uname:
            continue
        if uname in username_map:
            graph.add_edge(node, username_map[uname], relation="same_username")
        else:
            username_map[uname] = node
    return graph

