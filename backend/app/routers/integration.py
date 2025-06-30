from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from ..services.integration_service import full_osint_scan

router = APIRouter()


class ScanRequest(BaseModel):
    text: str


@router.post("/integrated-scan")
async def integrated_scan(payload: ScanRequest):
    """Run a full OSINT scan on the provided text."""
    result = await full_osint_scan(payload.text)
    return {
        "status": "success",
        "data": result,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
