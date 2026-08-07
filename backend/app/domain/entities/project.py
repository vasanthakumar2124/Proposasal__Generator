from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.config.constants import IndustryType


class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v) if v is not None else v
    organization_id: str
    workspace_id: Optional[str] = None
    client_id: Optional[str] = None
    name: str
    description: str = ""
    industry: IndustryType = IndustryType.CUSTOM
    project_type: str = "custom"
    status: str = "draft"
    proposal_ids: list[str] = Field(default_factory=list)
    goal: str = ""
    budget: Optional[float] = None
    currency: str = "USD"
    timeline: Optional[str] = None
    key_features: list[str] = Field(default_factory=list)
    notes: str = ""
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}
