from fastapi import APIRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from datetime import datetime

from ..models.phone import PhoneRequest, StandardResponse
from ..services.phone_service import analyze_phone

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
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
def analyze(request: PhoneRequest):
    result = analyze_phone(request.phone_number)
    return result
