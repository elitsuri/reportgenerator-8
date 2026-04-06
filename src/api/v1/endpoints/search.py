from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, CurrentUser
from src.services.search import SearchService

router = APIRouter()

@router.get("/")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    type: Optional[Literal["items", "users", "all"]] = Query("all"),
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Full-text search across items and/or users."""
    svc = SearchService(db)
    if type == "items":
        items = await svc.search_items(q=q, limit=limit)
        return {"items": items, "users": []}
    elif type == "users":
        users = await svc.search_users(q=q, limit=limit)
        return {"items": [], "users": users}
    else:
        return await svc.combined_search(q=q, limit=limit)