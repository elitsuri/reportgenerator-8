from fastapi import APIRouter

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.items import router as items_router
from src.api.v1.endpoints.health import router as health_router
from src.api.v1.endpoints.analytics import router as analytics_router
from src.api.v1.endpoints.notifications import router as notifications_router
from src.api.v1.endpoints.settings import router as settings_router
from src.api.v1.endpoints.admin import router as admin_router
from src.api.v1.endpoints.search import router as search_router
from src.api.v1.endpoints.upload import router as upload_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(items_router, prefix="/items", tags=["Items"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])