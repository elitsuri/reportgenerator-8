from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, AdminUser
from src.models.user import User
from src.models.item import Item
from src.schemas.admin import AdminUserView, AdminStats, UpdateRole

router = APIRouter()

@router.get("/users", response_model=List[AdminUserView])
async def admin_list_users(
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> List[AdminUserView]:
    """List all users (admin only)."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [AdminUserView.model_validate(u) for u in users]

@router.put("/users/{user_id}/role", response_model=AdminUserView)
async def admin_update_role(
    payload: UpdateRole,
    user_id: int = Path(..., ge=1),
    admin: AdminUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> AdminUserView:
    """Change a user's role."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = payload.role
    await db.commit()
    await db.refresh(user)
    return AdminUserView.model_validate(user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: int = Path(..., ge=1),
    admin: AdminUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()

@router.get("/stats", response_model=AdminStats)
async def admin_stats(
    admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> AdminStats:
    """Return aggregate platform stats."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    active_users = (await db.execute(select(func.count(User.id)).where(User.is_active == True))).scalar_one()
    total_items = (await db.execute(select(func.count(Item.id)))).scalar_one()
    return AdminStats(total_users=total_users, active_users=active_users, total_items=total_items)