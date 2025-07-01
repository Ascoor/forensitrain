from typing import List, Optional
from pydantic import BaseModel

class FootprintRequest(BaseModel):
    """Payload with Twitter handle."""

    username: str


class TweetLocation(BaseModel):
    lat: float
    lon: float
    text: Optional[str] = None
    created_at: Optional[str] = None


class FootprintResult(BaseModel):
    count: int
    locations: List[TweetLocation] = []


class FootprintResponse(BaseModel):
    status: str
    data: Optional[FootprintResult] = None
    errors: Optional[str] = None
    timestamp: str
