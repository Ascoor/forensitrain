from typing import List, Optional
from pydantic import BaseModel


class PhoneRequest(BaseModel):
    phone_number: str


class PhoneResponse(BaseModel):
    phone_number: str
    name: str
    country: str
    email: Optional[str] = None
    accounts: List[str] = []
    connections: List[str] = []
