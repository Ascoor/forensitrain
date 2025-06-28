from typing import List, Optional
from pydantic import BaseModel


class PhoneRequest(BaseModel):
    phone_number: str


class PhoneResponse(BaseModel):
    phone_number: str
    valid: bool
    country: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    name: Optional[str] = None
    accounts: List[str] = []
    breaches: List[str] = []
