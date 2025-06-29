from typing import List, Optional, Dict
from pydantic import BaseModel

class PhoneAnalyzeRequest(BaseModel):
    phone: str

class TextAnalyzeRequest(BaseModel):
    text: str

class SocialAnalyzeRequest(BaseModel):
    query: str

class PhoneAnalyzeData(BaseModel):
    phone: str
    valid: bool
    country: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None

class TextAnalyzeData(BaseModel):
    phones: List[str] = []
    emails: List[str] = []

class SocialAnalyzeData(BaseModel):
    profiles: List[str] = []

class ImageAnalyzeData(BaseModel):
    ocr_text: str = ""
    faces_detected: int = 0
    objects: List[str] = []

class StandardResponse(BaseModel):
    status: str
    data: Optional[Dict[str, object]] = None
    errors: Optional[str] = None
    timestamp: str
