"""
reportgenerator
ReportGenerator: Automated report generation with PDF, Excel, and email delivery
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from src.core.config import settings
from src.core.database import create_tables
from src.api.v1.router import api_router
from src.middleware.logging import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ReportGenerator: Automated report generation with PDF, Excel, and email delivery",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# ── Global exception handlers ──────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "request_id": getattr(request.state, "request_id", "unknown")},
    )

# ── Routers ──────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")