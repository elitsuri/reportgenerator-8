from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

class AdminUserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_items: int

class UpdateRole(BaseModel):
    role: Literal["admin", "user", "moderator"]

class BanUser(BaseModel):
    reason: Optional[str] = None
    permanent: bool = False