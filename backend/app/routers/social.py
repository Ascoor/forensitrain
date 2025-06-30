from datetime import datetime
from fastapi import APIRouter

from ..models.social import DeepScanRequest, SocialScanResponse
from ..services.deep_social_service import deep_social_scan

router = APIRouter()


@router.post('/deep-scan', response_model=SocialScanResponse)
async def deep_scan(payload: DeepScanRequest):
    data = await deep_social_scan(payload.handle)
    return {
        "status": "success",
        "data": data,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
