from datetime import datetime
from fastapi import APIRouter, UploadFile, File
from ..models.image import ImageResponse
from ..services.image_service import a_analyze_image_bytes

router = APIRouter()


@router.post('/analyze-image', response_model=ImageResponse)
async def analyze_image(file: UploadFile = File(...)):
    data = await file.read()
    result = await a_analyze_image_bytes(data)
    return {
        "status": "success",
        "data": result,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
