from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, CurrentUser
from src.services.analytics import AnalyticsService
from src.schemas.analytics import OverviewStats, TimeseriesData, TopItem

router = APIRouter()

@router.get("/overview", response_model=OverviewStats)
async def get_analytics_overview(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> OverviewStats:
    """Return aggregated platform overview statistics."""
    svc = AnalyticsService(db)
    return await svc.get_overview(user_id=current_user.id)

@router.get("/timeseries", response_model=TimeseriesData)
async def get_analytics_timeseries(
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
) -> TimeseriesData:
    """Return timeseries counts for items created per day."""
    svc = AnalyticsService(db)
    return await svc.get_timeseries(user_id=current_user.id, days=days)

@router.get("/top-items", response_model=List[TopItem])
async def get_top_items(
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[TopItem]:
    """Return top items by view/interaction count."""
    svc = AnalyticsService(db)
    return await svc.get_top_items(user_id=current_user.id, limit=limit)