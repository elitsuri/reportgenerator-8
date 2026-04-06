import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

class AuditMiddleware(BaseHTTPMiddleware):
    """Log every mutating request to the audit_logs table."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        if request.method not in MUTATING_METHODS:
            return response
        try:
            from src.core.database import AsyncSessionLocal
            from src.models.audit_log import AuditLog
            user_id: int | None = None
            if hasattr(request.state, "user") and request.state.user:
                user_id = request.state.user.id
            path_parts = request.url.path.strip("/").split("/")
            resource_type = path_parts[-2] if len(path_parts) >= 2 else path_parts[0]
            resource_id = path_parts[-1] if len(path_parts) >= 2 else None
            ip = request.client.host if request.client else None
            ua = request.headers.get("User-Agent")
            async with AsyncSessionLocal() as session:
                log = AuditLog(
                    user_id=user_id,
                    action=request.method,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    ip_address=ip,
                    user_agent=ua,
                )
                session.add(log)
                await session.commit()
        except Exception as exc:
            logger.warning("AuditMiddleware failed to log: %s", exc)
        return response