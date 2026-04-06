"""
Background cleanup worker.
Run with: python -m src.workers.cleanup
Or schedule as a cron job.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

AUDIT_LOG_RETENTION_DAYS = 90
UPLOAD_DIR = Path("uploads")

async def purge_old_audit_logs(db: AsyncSession) -> int:
    cutoff = datetime.utcnow() - timedelta(days=AUDIT_LOG_RETENTION_DAYS)
    result = await db.execute(delete(AuditLog).where(AuditLog.created_at < cutoff))
    await db.commit()
    count = result.rowcount
    logger.info("Purged %d audit logs older than %d days", count, AUDIT_LOG_RETENTION_DAYS)
    return count

async def purge_orphaned_files(db: AsyncSession) -> int:
    if not UPLOAD_DIR.exists():
        return 0
    removed = 0
    cutoff_ts = datetime.utcnow() - timedelta(days=30)
    for f in UPLOAD_DIR.iterdir():
        if not f.is_file():
            continue
        mtime = datetime.utcfromtimestamp(f.stat().st_mtime)
        if mtime < cutoff_ts:
            f.unlink()
            removed += 1
    logger.info("Removed %d orphaned upload files", removed)
    return removed

async def run_cleanup() -> None:
    async with AsyncSessionLocal() as db:
        await purge_old_audit_logs(db)
        await purge_orphaned_files(db)
    logger.info("Cleanup run complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_cleanup())