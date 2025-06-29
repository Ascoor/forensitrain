from typing import List, Optional, Dict
from pydantic import BaseModel

class ImageData(BaseModel):
    dimensions: str
    format: str
    text: str = ""
    faces_detected: int = 0
    objects: List[str] = []
    exif: Optional[Dict[str, str]] = None
    inferred_platform: Optional[str] = None

class ImageResponse(BaseModel):
    status: str
    data: Optional[ImageData] = None
    errors: Optional[str] = None
    timestamp: str
