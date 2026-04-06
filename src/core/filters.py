from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import InstrumentedAttribute

@dataclass
class DateRangeFilter:
    """Filter records by a date range on a given column."""
    start: Optional[date] = None
    end: Optional[date] = None

    def apply(self, query, column: InstrumentedAttribute):
        if self.start:
            query = query.where(column >= self.start)
        if self.end:
            query = query.where(column <= self.end)
        return query

@dataclass
class SearchFilter:
    """Full-text ILIKE search across one or more columns."""
    q: Optional[str] = None

    def apply(self, query, *columns: InstrumentedAttribute):
        if not self.q or not self.q.strip():
            return query
        term = f"%{self.q.strip()}%"
        conditions = [col.ilike(term) for col in columns]
        return query.where(or_(*conditions))

@dataclass
class SortFilter:
    """Dynamic column sorting."""
    sort_by: Optional[str] = None
    sort_dir: str = "asc"

    def apply(self, query, allowed_columns: dict):
        if not self.sort_by or self.sort_by not in allowed_columns:
            return query
        column = allowed_columns[self.sort_by]
        if self.sort_dir.lower() == "desc":
            return query.order_by(desc(column))
        return query.order_by(asc(column))

@dataclass
class CompositeFilter:
    """Compose date, search, and sort filters."""
    date_range: Optional[DateRangeFilter] = None
    search: Optional[SearchFilter] = None
    sort: Optional[SortFilter] = None

    def apply(self, query, date_column=None, search_columns=None, sort_columns=None):
        if self.date_range and date_column is not None:
            query = self.date_range.apply(query, date_column)
        if self.search and search_columns:
            query = self.search.apply(query, *search_columns)
        if self.sort and sort_columns:
            query = self.sort.apply(query, sort_columns)
        return query