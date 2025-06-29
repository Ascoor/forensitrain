from fastapi import APIRouter, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime

from ..models.phone import (
    PhoneRequest,
    StandardResponse,
    EnrichedResponse,
)
from ..services.phone_service import multi_source_lookup, a_enrich_phone_data
from ..services.export_service import generate_export

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "errors": "Rate limit exceeded",
            "data": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )



@router.post('/analyze', response_model=StandardResponse)
@limiter.limit("30/minute")
async def analyze(request: Request, payload: PhoneRequest):
    result = await multi_source_lookup(payload.phone_number)
    return result


@router.post('/enrich', response_model=EnrichedResponse)
@limiter.limit("30/minute")
async def enrich(request: Request, payload: PhoneRequest):
    """Return unified enrichment info for a phone number."""
    result = await a_enrich_phone_data(payload.phone_number)
    return result


@router.post('/export')
@limiter.limit("30/minute")
async def export(request: Request, payload: PhoneRequest, fmt: str = Query("json", regex="^(json|pdf)$")):
    """Export report for a phone number in JSON or PDF format."""
    resp = await generate_export(payload.phone_number, fmt)
    if isinstance(resp, StreamingResponse):
        resp.headers["Content-Disposition"] = f"attachment; filename=report.{fmt}"
    return resp
