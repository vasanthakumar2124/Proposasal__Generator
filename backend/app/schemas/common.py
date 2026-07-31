from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    has_more: bool = False


class MessageResponse(BaseModel):
    message: str
    status: str = "success"


class ErrorResponse(BaseModel):
    detail: str
    error_code: str = ""
    status: int = 400
