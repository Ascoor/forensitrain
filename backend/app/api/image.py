"""Async helpers to call ForensiTrain image endpoints."""
import httpx
from ..core.config import settings


async def analyze_image(data: bytes) -> dict:
    async with httpx.AsyncClient() as client:
        files = {"file": ("image.jpg", data)}
        resp = await client.post(
            f"{settings.api_base_url}/analyze-image",
            files=files,
        )
        resp.raise_for_status()
        return resp.json()
