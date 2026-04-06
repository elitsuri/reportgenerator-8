"""Shared Pydantic schemas."""
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.limit))

    model_config = {"from_attributes": True}

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None