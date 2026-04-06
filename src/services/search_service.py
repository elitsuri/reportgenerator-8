from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from src.models.user import User

class SearchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search_items(self, q: str, limit: int = 20) -> List[dict]:
        term = f"%{q}%"
        result = await self.db.execute(
            select(Item)
            .where(Item.title.ilike(term) | Item.description.ilike(term))
            .limit(limit)
        )
        rows = result.scalars().all()
        return [{"id": r.id, "title": r.title, "type": "item"} for r in rows]

    async def search_users(self, q: str, limit: int = 20) -> List[dict]:
        term = f"%{q}%"
        result = await self.db.execute(
            select(User)
            .where(User.email.ilike(term) | User.full_name.ilike(term))
            .limit(limit)
        )
        rows = result.scalars().all()
        return [{"id": r.id, "email": r.email, "full_name": r.full_name, "type": "user"} for r in rows]

    async def combined_search(self, q: str, limit: int = 20) -> dict:
        half = limit // 2
        items = await self.search_items(q=q, limit=half)
        users = await self.search_users(q=q, limit=half)
        return {"items": items, "users": users, "total": len(items) + len(users)}