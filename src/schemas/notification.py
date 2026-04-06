from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict

class NotificationBase(BaseModel):
    title: str
    body: str
    type: Literal["info", "warning", "error", "success"] = "info"

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    read: bool
    created_at: datetime

class NotificationList(BaseModel):
    items: List[NotificationRead]
    unread_count: int