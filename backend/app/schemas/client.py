from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ClientCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    industry: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    address: str = ""
    notes: str = ""


class ClientUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ClientResponse(BaseModel):
    id: str = Field(alias="_id")
    organization_id: str
    name: str
    industry: str
    contact_name: str
    contact_email: str
    contact_phone: str
    address: str
    notes: str
    created_by: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True, "from_attributes": True}
