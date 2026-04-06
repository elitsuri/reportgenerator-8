from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, CurrentUser
from src.models.settings import UserSettings
from src.schemas.settings import UserSettingsRead, UserSettingsUpdate
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=UserSettingsRead)
async def get_settings(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserSettingsRead:
    """Retrieve the current user's preferences."""
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == current_user.id))
    settings_obj = result.scalar_one_or_none()
    if settings_obj is None:
        settings_obj = UserSettings(user_id=current_user.id)
        db.add(settings_obj)
        await db.commit()
        await db.refresh(settings_obj)
    return UserSettingsRead.model_validate(settings_obj)

@router.put("/", response_model=UserSettingsRead)
async def update_settings(
    payload: UserSettingsUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserSettingsRead:
    """Update the current user's preferences."""
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == current_user.id))
    settings_obj = result.scalar_one_or_none()
    if settings_obj is None:
        settings_obj = UserSettings(user_id=current_user.id)
        db.add(settings_obj)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings_obj, key, value)
    await db.commit()
    await db.refresh(settings_obj)
    return UserSettingsRead.model_validate(settings_obj)