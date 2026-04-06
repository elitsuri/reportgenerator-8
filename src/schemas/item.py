"""Item Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from src.models.item import ItemStatus

class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    status: ItemStatus = ItemStatus.ACTIVE

class ItemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    status: ItemStatus | None = None

class ItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: ItemStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}