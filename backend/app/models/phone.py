from typing import List, Optional, Dict
from pydantic import BaseModel


class PhoneRequest(BaseModel):
    phone_number: str


class PhoneData(BaseModel):
    phone_number: str
    valid: bool
    country: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    name: Optional[str] = None
    accounts: List[str] = []
    profiles: List[Dict[str, Optional[str]]] = []
    breaches: List[str] = []
    emails: List[str] = []
    email_breaches: List[str] = []
    connections: List[dict] = []
    graph: Optional[dict] = None
    sources_used: List[str] = []


class StandardResponse(BaseModel):
    status: str
    data: Optional[PhoneData] = None
    errors: Optional[Dict[str, Optional[str]]] = None
    timestamp: str


class EnrichedPhoneData(BaseModel):
    phone: str
    valid: bool
    country: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    name: Optional[str] = None
    social_profiles: List[str] = []
    profile_details: List[Dict[str, Optional[str]]] = []
    emails: List[str] = []
    email_breaches: List[str] = []
    breaches: List[str] = []
    connections: List[dict] = []
    confidence_score: float
    sources: List[str] = []


class EnrichedResponse(BaseModel):
    status: str
    data: Optional[EnrichedPhoneData] = None
    errors: Optional[Dict[str, Optional[str]]] = None
    timestamp: str
