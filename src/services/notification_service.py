from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification
from src.schemas.notification import NotificationCreate, NotificationRead

class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_for_user(self, user_id: int) -> List[NotificationRead]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        rows = result.scalars().all()
        return [NotificationRead.model_validate(r) for r in rows]

    async def get_unread_count(self, user_id: int) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id, Notification.read == False)
        )
        return result.scalar_one()

    async def create(self, user_id: int, payload: NotificationCreate) -> NotificationRead:
        notif = Notification(user_id=user_id, **payload.model_dump())
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return NotificationRead.model_validate(notif)

    async def mark_read(self, notification_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        notif = result.scalar_one_or_none()
        if notif is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif.read = True
        await self.db.commit()

    async def mark_all_read(self, user_id: int) -> None:
        await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read == False)
            .values(read=True)
        )
        await self.db.commit()

    async def delete(self, notification_id: int, user_id: int) -> None:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        notif = result.scalar_one_or_none()
        if notif is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        await self.db.delete(notif)
        await self.db.commit()