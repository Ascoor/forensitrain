from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from ..services.recursive_osint_engine import smart_osint_lookup
from ..services.osint_service import extract_osint_footprint

router = APIRouter()


class PhoneReq(BaseModel):
    phone: str


@router.post("/smart-lookup")
async def smart_lookup(payload: PhoneReq):
    """Run the recursive smart OSINT lookup."""
    data = smart_osint_lookup(payload.phone)
    return {
        "status": "success",
        "data": data,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/footprint")
async def osint_footprint(payload: PhoneReq):
    """Return footprint information for a phone number."""
    data = extract_osint_footprint(payload.phone)
    return {
        "status": "success",
        "data": data,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
