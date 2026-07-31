from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.config.constants import OrganizationPlan


class Branding(BaseModel):
    logo_url: str = ""
    primary_color: str = "#2563eb"
    secondary_color: str = "#7c3aed"
    font_family: str = "Inter"
    accent_color: str = "#10b981"


class Organization(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v) if v is not None else v
    name: str
    slug: str
    plan: OrganizationPlan = OrganizationPlan.FREE
    features: list[str] = Field(default_factory=list)
    branding: Branding = Field(default_factory=Branding)
    settings: dict = Field(default_factory=lambda: {"default_locale": "en", "timezone": "UTC"})
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    def has_feature(self, feature: str) -> bool:
        return feature in self.features
