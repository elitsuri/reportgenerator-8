from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
import shutil
import time
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

@dataclass
class ComponentHealth:
    status: str  # 'ok' | 'degraded' | 'error'
    latency_ms: float = 0.0
    detail: Optional[str] = None

@dataclass
class HealthStatus:
    status: str
    components: Dict[str, ComponentHealth] = field(default_factory=dict)
    version: str = "1.0.0"

    def dict(self) -> dict:
        return {
            "status": self.status,
            "version": self.version,
            "components": {
                k: {"status": v.status, "latency_ms": v.latency_ms, "detail": v.detail}
                for k, v in self.components.items()
            },
        }

async def check_db(db: AsyncSession) -> ComponentHealth:
    """Ping the database."""
    t0 = time.monotonic()
    try:
        await db.execute(text("SELECT 1"))
        return ComponentHealth(status="ok", latency_ms=round((time.monotonic() - t0) * 1000, 2))
    except Exception as exc:
        return ComponentHealth(status="error", detail=str(exc))

async def check_cache(redis) -> ComponentHealth:
    """Ping Redis cache."""
    if redis is None:
        return ComponentHealth(status="degraded", detail="Redis not configured")
    t0 = time.monotonic()
    try:
        await redis.ping()
        return ComponentHealth(status="ok", latency_ms=round((time.monotonic() - t0) * 1000, 2))
    except Exception as exc:
        return ComponentHealth(status="error", detail=str(exc))

def check_disk() -> ComponentHealth:
    """Check available disk space (warn if < 10%)."""
    usage = shutil.disk_usage("/")
    free_pct = (usage.free / usage.total) * 100
    if free_pct < 5:
        return ComponentHealth(status="error", detail=f"{free_pct:.1f}% free")
    if free_pct < 10:
        return ComponentHealth(status="degraded", detail=f"{free_pct:.1f}% free")
    return ComponentHealth(status="ok", detail=f"{free_pct:.1f}% free")

async def get_health_status(db: AsyncSession, redis=None) -> HealthStatus:
    """Aggregate all health checks into a HealthStatus."""
    db_health = await check_db(db)
    cache_health = await check_cache(redis)
    disk_health = check_disk()
    components = {"database": db_health, "cache": cache_health, "disk": disk_health}
    overall = "ok"
    for c in components.values():
        if c.status == "error":
            overall = "error"
            break
        if c.status == "degraded":
            overall = "degraded"
    return HealthStatus(status=overall, components=components)