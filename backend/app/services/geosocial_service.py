import asyncio
import json
import subprocess
from typing import Dict

_CACHE: Dict[str, dict] = {}


async def extract_footprint(username: str) -> Dict:
    """Run GeoSocial Footprint CLI and return parsed JSON."""
    if username in _CACHE:
        return _CACHE[username]

    cmd = ["geosocial-footprint", "--user", username, "--json"]
    try:
        output = await asyncio.to_thread(subprocess.check_output, cmd, text=True)
        data = json.loads(output)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(str(exc))

    _CACHE[username] = data
    return data
