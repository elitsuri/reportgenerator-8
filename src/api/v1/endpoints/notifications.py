from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, CurrentUser
from src.services.notification import NotificationService
from src.schemas.notification import NotificationCreate, NotificationRead, NotificationList

router = APIRouter()

@router.get("/", response_model=NotificationList)
async def list_notifications(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> NotificationList:
    """List all notifications for the current user."""
    svc = NotificationService(db)
    items = await svc.get_for_user(current_user.id)
    unread = await svc.get_unread_count(current_user.id)
    return NotificationList(items=items, unread_count=unread)

@router.post("/", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> NotificationRead:
    """Create a new notification for the current user."""
    svc = NotificationService(db)
    return await svc.create(user_id=current_user.id, payload=payload)

@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: int = Path(..., ge=1),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Mark a single notification as read."""
    svc = NotificationService(db)
    await svc.mark_read(notification_id=notification_id, user_id=current_user.id)

@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Mark all notifications as read for the current user."""
    svc = NotificationService(db)
    await svc.mark_all_read(user_id=current_user.id)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int = Path(..., ge=1),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a notification."""
    svc = NotificationService(db)
    await svc.delete(notification_id=notification_id, user_id=current_user.id)