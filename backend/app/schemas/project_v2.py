from typing import Optional

from pydantic import BaseModel, Field


class ProjectHubUpdateRequest(BaseModel):
    goal: Optional[str] = Field(None, max_length=2000)
    budget: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    timeline: Optional[str] = Field(None, max_length=200)
    key_features: Optional[list[str]] = None
    notes: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, max_length=50)


class ProjectHubGenerateRequest(BaseModel):
    client_input: str = Field(..., min_length=1)
    domain: Optional[str] = None
    project_type: Optional[str] = None
