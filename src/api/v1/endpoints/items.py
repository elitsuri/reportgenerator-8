"""Items CRUD endpoints with pagination and search."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.core.database import get_db
from src.core.security import decode_token, oauth2_scheme
from src.schemas.common import PaginatedResponse
from src.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from src.services.item_service import ItemService

router = APIRouter()

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    return int(payload["sub"])

@router.get("", response_model=PaginatedResponse[ItemResponse])
async def list_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search term"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    svc = ItemService(db)
    items, total = await svc.list(owner_id=user_id, page=page, limit=limit, search=q)
    return PaginatedResponse(data=items, total=total, page=page, limit=limit)

@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    payload: ItemCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await ItemService(db).create(payload, owner_id=user_id)

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = await ItemService(db).get(item_id, owner_id=user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int, payload: ItemUpdate,
    db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id),
):
    item = await ItemService(db).update(item_id, payload, owner_id=user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    deleted = await ItemService(db).delete(item_id, owner_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")