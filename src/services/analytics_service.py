from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from src.models.user import User
from src.models.notification import Notification
from src.schemas.analytics import OverviewStats, TimeseriesData, TimeseriesPoint, TopItem

class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_overview(self, user_id: int) -> OverviewStats:
        total_items = (await self.db.execute(select(func.count(Item.id)))).scalar_one()
        total_users = (await self.db.execute(select(func.count(User.id)))).scalar_one()
        total_notifs = (await self.db.execute(select(func.count(Notification.id)).where(Notification.user_id == user_id))).scalar_one()
        week_ago = datetime.utcnow() - timedelta(days=7)
        items_week = (await self.db.execute(select(func.count(Item.id)).where(Item.created_at >= week_ago))).scalar_one()
        today = datetime.utcnow().date()
        active_today = (await self.db.execute(select(func.count(User.id)).where(func.date(User.last_login) == today))).scalar_one()
        return OverviewStats(
            total_items=total_items,
            total_users=total_users,
            total_notifications=total_notifs,
            items_this_week=items_week,
            active_users_today=active_today,
        )

    async def get_timeseries(self, user_id: int, days: int = 30) -> TimeseriesData:
        since = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.date(Item.created_at).label("day"), func.count(Item.id).label("cnt"))
            .where(Item.created_at >= since)
            .group_by(func.date(Item.created_at))
            .order_by(func.date(Item.created_at))
        )
        rows = result.all()
        points = [TimeseriesPoint(date=r.day, count=r.cnt) for r in rows]
        return TimeseriesData(points=points, total=sum(p.count for p in points))

    async def get_top_items(self, user_id: int, limit: int = 10) -> List[TopItem]:
        result = await self.db.execute(
            select(Item).order_by(Item.view_count.desc()).limit(limit)
        )
        rows = result.scalars().all()
        return [
            TopItem(id=r.id, title=r.title, view_count=getattr(r, "view_count", 0), created_at=r.created_at.date())
            for r in rows
        ]