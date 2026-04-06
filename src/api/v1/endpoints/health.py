"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()
_start_time = datetime.now(timezone.utc)

@router.get("")
async def health():
    return {
        "status": "healthy",
        "service": "reportgenerator",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": (datetime.now(timezone.utc) - _start_time).seconds,
    }

@router.get("/ready")
async def ready():
    return {"status": "ready"}