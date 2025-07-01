import json
import os
import subprocess
from typing import List, Dict
import logging

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger(__name__)


def run_maigret(target: str) -> List[Dict]:
    """Run Maigret CLI and return found accounts."""
    results: List[Dict] = []
    out_file = os.path.join(LOG_DIR, f"maigret_{target}.json")
    cmd = ["maigret", target, "--json", "--top-sites", "-o", out_file]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if os.path.exists(out_file):
            with open(out_file) as f:
                data = json.load(f)
            for site in data.get("sites", []):
                url = site.get("url") or site.get("url_user")
                if not url:
                    continue
                results.append(
                    {
                        "platform": site.get("name"),
                        "username": site.get("id"),
                        "profile": url,
                        "status": site.get("status") or "unknown",
                    }
                )
            os.remove(out_file)
    except FileNotFoundError:
        logger.error("Maigret CLI not found. Please install maigret")
    except Exception as exc:  # noqa: BLE001
        logger.error("Maigret error: %s", exc)
    return results


def run_sherlock(username: str) -> List[Dict]:
    """Run Sherlock CLI and return found accounts."""
    results: List[Dict] = []
    out_file = os.path.join(LOG_DIR, f"sherlock_{username}.json")
    cmd = ["sherlock", username, "--json", out_file]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if os.path.exists(out_file):
            with open(out_file) as f:
                data = json.load(f)
            for site, entry in data.items():
                url = entry.get("url")
                if not url:
                    continue
                results.append(
                    {
                        "platform": site,
                        "username": username,
                        "profile": url,
                        "status": entry.get("status", "unknown"),
                    }
                )
            os.remove(out_file)
    except FileNotFoundError:
        logger.error("Sherlock CLI not found. Please install sherlock")
    except Exception as exc:  # noqa: BLE001
        logger.error("Sherlock error: %s", exc)
    return results
