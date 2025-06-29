from typing import List, Optional
from pydantic import BaseModel


class DeepScanRequest(BaseModel):
    handle: str


class TopImage(BaseModel):
    year: int
    image_url: str
    likes: Optional[int] = None
    comments: Optional[int] = None


class ProfileData(BaseModel):
    platform: str
    username: str
    profile_url: str
    profile_picture: Optional[str] = None
    top_images: List[TopImage] = []


class SocialScanResult(BaseModel):
    profiles: List[ProfileData] = []


class SocialScanResponse(BaseModel):
    status: str
    data: Optional[SocialScanResult] = None
    errors: Optional[str] = None
    timestamp: str
