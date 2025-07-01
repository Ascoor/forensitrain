"""Async helpers to call ForensiTrain geosocial endpoints."""
import httpx
from ..core.config import settings


async def footprint(username: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.api_base_url}/geosocial/footprint",
            json={"username": username},
        )
        resp.raise_for_status()
        return resp.json()
