from datetime import datetime
from pydantic import BaseModel, Field

from app.config.constants import OrganizationPlan
from app.domain.entities.organization import Branding


class OrganizationResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    slug: str
    plan: OrganizationPlan
    features: list[str]
    branding: Branding
    settings: dict
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True, "from_attributes": True}


class OrganizationUpdateRequest(BaseModel):
    name: str = Field(None, min_length=1, max_length=200)
    branding: Branding = None
    settings: dict = None


class MemberResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str
    last_login: datetime | None = None


class AddMemberRequest(BaseModel):
    email: str
    role: str = "editor"
