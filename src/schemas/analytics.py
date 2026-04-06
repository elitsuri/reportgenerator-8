from datetime import date
from typing import List

from pydantic import BaseModel

class OverviewStats(BaseModel):
    total_items: int
    total_users: int
    total_notifications: int
    items_this_week: int
    active_users_today: int

class TimeseriesPoint(BaseModel):
    date: date
    count: int

class TimeseriesData(BaseModel):
    points: List[TimeseriesPoint]
    label: str = "Items created"
    total: int

class TopItem(BaseModel):
    id: int
    title: str
    view_count: int
    created_at: date