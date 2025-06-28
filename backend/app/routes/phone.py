from fastapi import APIRouter, HTTPException
import time
from ..models.phone import PhoneRequest, PhoneResponse
from ..services.phone_service import analyze_phone

router = APIRouter()

REQUEST_LOG = []

def _check_rate_limit():
    now = time.time()
    REQUEST_LOG.append(now)
    REQUEST_LOG[:] = [t for t in REQUEST_LOG if now - t < 60]
    if len(REQUEST_LOG) > 30:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


@router.post('/analyze', response_model=PhoneResponse)
def analyze(request: PhoneRequest):
    _check_rate_limit()
    result = analyze_phone(request.phone_number)
    return result
