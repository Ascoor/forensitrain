from fastapi import APIRouter
from ..models.phone import PhoneRequest, PhoneResponse
from ..services.phone_service import analyze_phone

router = APIRouter()


@router.post('/analyze', response_model=PhoneResponse)
def analyze(request: PhoneRequest):
    result = analyze_phone(request.phone_number)
    return result
