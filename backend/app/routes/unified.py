from datetime import datetime
from fastapi import APIRouter, UploadFile, File

from ..models.unified import (
    PhoneAnalyzeRequest,
    TextAnalyzeRequest,
    SocialAnalyzeRequest,
    StandardResponse,
)
from ..services.unified_service import (
    analyze_phone,
    analyze_text,
    search_social,
    analyze_image,
)

router = APIRouter(prefix="/analyze")


@router.post("/phone", response_model=StandardResponse)
async def analyze_phone_route(payload: PhoneAnalyzeRequest):
    data = analyze_phone(payload.phone)
    return {
        "status": "success",
        "data": data,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/text", response_model=StandardResponse)
async def analyze_text_route(payload: TextAnalyzeRequest):
    data = analyze_text(payload.text)
    return {
        "status": "success",
        "data": data,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/social", response_model=StandardResponse)
async def analyze_social_route(payload: SocialAnalyzeRequest):
    profiles = search_social(payload.query)
    return {
        "status": "success",
        "data": {"profiles": profiles},
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/image", response_model=StandardResponse)
async def analyze_image_route(file: UploadFile = File(...)):
    data_bytes = await file.read()
    data = analyze_image(data_bytes)
    return {
        "status": "success",
        "data": data,
        "errors": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
