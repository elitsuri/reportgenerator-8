"""Item service — business logic layer."""
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.models.item import Item
from src.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self,
        owner_id: int,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[Item], int]:
        query = select(Item).where(Item.owner_id == owner_id)
        if search:
            term = f"%{search}%"
            query = query.where(or_(Item.title.ilike(term), Item.description.ilike(term)))
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        items = (await self.db.scalars(query.offset((page - 1) * limit).limit(limit))).all()
        return list(items), total or 0

    async def create(self, payload: ItemCreate, owner_id: int) -> Item:
        item = Item(**payload.model_dump(), owner_id=owner_id)
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def get(self, item_id: int, owner_id: int) -> Optional[Item]:
        return await self.db.scalar(
            select(Item).where(Item.id == item_id, Item.owner_id == owner_id)
        )

    async def update(self, item_id: int, payload: ItemUpdate, owner_id: int) -> Optional[Item]:
        item = await self.get(item_id, owner_id)
        if not item:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item_id: int, owner_id: int) -> bool:
        item = await self.get(item_id, owner_id)
        if not item:
            return False
        await self.db.delete(item)
        return True