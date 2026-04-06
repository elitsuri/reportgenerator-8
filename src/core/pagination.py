from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

@dataclass
class PageParams:
    """Encapsulates pagination parameters."""
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

@dataclass
class Page(Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int = field(init=False)
    has_next: bool = field(init=False)
    has_prev: bool = field(init=False)

    def __post_init__(self) -> None:
        self.pages = ceil(self.total / self.page_size) if self.page_size else 0
        self.has_next = self.page < self.pages
        self.has_prev = self.page > 1

    def dict(self) -> dict:
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "pages": self.pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }

async def paginate(
    db: AsyncSession,
    query,
    params: PageParams,
    scalar_type=None,
) -> Page:
    """Execute a paginated query and return a Page instance."""
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    paginated = query.offset(params.offset).limit(params.limit)
    result = await db.execute(paginated)
    if scalar_type is not None:
        items = result.scalars().all()
    else:
        items = result.all()

    return Page(
        items=list(items),
        total=total,
        page=params.page,
        page_size=params.page_size,
    )