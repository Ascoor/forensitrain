"""Async helpers to call ForensiTrain phone endpoints."""
import httpx
from ..core.config import settings


async def analyze(phone_number: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.api_base_url}/phone/analyze",
            json={"phone_number": phone_number},
        )
        resp.raise_for_status()
        return resp.json()
