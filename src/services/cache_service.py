import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-backed async cache service."""

    def __init__(self, redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        """Return deserialized value or None if missing/unavailable."""
        if self.redis is None:
            return None
        try:
            raw = await self.redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Cache GET error for key %r: %s", key, exc)
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Serialize and store value with TTL seconds."""
        if self.redis is None:
            return False
        try:
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as exc:
            logger.warning("Cache SET error for key %r: %s", key, exc)
            return False

    async def delete(self, key: str) -> bool:
        """Delete a single cache key."""
        if self.redis is None:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as exc:
            logger.warning("Cache DELETE error for key %r: %s", key, exc)
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern. Returns count of deleted keys."""
        if self.redis is None:
            return 0
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning("Cache INVALIDATE error for pattern %r: %s", pattern, exc)
            return 0