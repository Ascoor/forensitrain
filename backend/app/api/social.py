"""Async helpers to call ForensiTrain social endpoints."""
import httpx
from ..core.config import settings


async def deep_scan(handle: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.api_base_url}/social/deep-scan",
            json={"handle": handle},
        )
        resp.raise_for_status()
        return resp.json()
