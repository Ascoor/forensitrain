import asyncio
import json
import subprocess
from typing import Dict
import logging

_CACHE: Dict[str, dict] = {}
logger = logging.getLogger(__name__)


async def extract_footprint(username: str) -> Dict:
    """Run GeoSocial Footprint CLI and return parsed JSON."""
    if username in _CACHE:
        return _CACHE[username]

    cmd = ["geosocial-footprint", "--user", username, "--json"]
    try:
        output = await asyncio.to_thread(subprocess.check_output, cmd, text=True)
        data = json.loads(output)
    except FileNotFoundError:
        logger.error("GeoSocial Footprint CLI not found. Install geosocial-footprint")
        raise RuntimeError("GeoSocial Footprint CLI missing")
    except Exception as exc:  # noqa: BLE001
        logger.error("GeoSocial Footprint error: %s", exc)
        raise RuntimeError(str(exc))

    _CACHE[username] = data
    return data
