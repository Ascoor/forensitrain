from typing import List, Optional
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
    breaches: List[str] = []
    connections: List[dict] = []
    graph: Optional[dict] = None


class StandardResponse(BaseModel):
    status: str
    data: Optional[PhoneData] = None
    errors: Optional[str] = None
    timestamp: str
