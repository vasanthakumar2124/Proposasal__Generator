from pydantic import BaseModel, Field
from typing import Optional


class SearchQuery(BaseModel):
    query: str
    collection_name: str = "industry_knowledge"
    top_k: int = Field(default=5, ge=1, le=50)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    content: str
    score: float
    metadata: dict = Field(default_factory=dict)
    collection_name: str = ""


class IngestDocument(BaseModel):
    content: str
    metadata: dict = Field(default_factory=dict)
    collection_name: str = "industry_knowledge"


class CollectionInfo(BaseModel):
    name: str
    vectors_count: int = 0
    dimensions: int = 0
