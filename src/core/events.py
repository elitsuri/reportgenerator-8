from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.database import engine, Base
from src.core.config import settings

logger = logging.getLogger(__name__)

async def _create_db_pool(app: FastAPI) -> None:
    """Create database connection pool on startup."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database pool created successfully")
    except Exception as exc:
        logger.error("Failed to create database pool: %s", exc)
        raise

async def _init_cache(app: FastAPI) -> None:
    """Initialize Redis cache connection."""
    try:
        import aioredis
        app.state.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await app.state.redis.ping()
        logger.info("Redis cache initialized")
    except Exception as exc:
        logger.warning("Redis unavailable, running without cache: %s", exc)
        app.state.redis = None

async def _close_db_pool(app: FastAPI) -> None:
    """Dispose database connection pool on shutdown."""
    await engine.dispose()
    logger.info("Database pool closed")

async def _close_cache(app: FastAPI) -> None:
    """Close Redis cache connection."""
    if getattr(app.state, 'redis', None):
        await app.state.redis.close()
        logger.info("Redis cache closed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown events."""
    logger.info("Starting up %s", settings.PROJECT_NAME)
    await _create_db_pool(app)
    await _init_cache(app)
    logger.info("Startup complete")
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)
    await _close_cache(app)
    await _close_db_pool(app)
    logger.info("Shutdown complete")