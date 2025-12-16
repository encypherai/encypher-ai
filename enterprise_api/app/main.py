"""
Encypher Enterprise API - Main Application

FastAPI application for C2PA-compliant content signing and verification.
"""
import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text

from app.api.v1.api import api_router as api_v1_router
from app.config import settings
from app.database import engine
from app.observability.metrics import render_prometheus
from app.routers import (
    audit,
    batch,
    chat,
    coalition,
    licensing,
    lookup,
    onboarding,
    signing,
    status,
    streaming,
    team,
    tools,
    usage,
    verification,
)
from app.services.session_service import session_service
from app.services.metrics_service import init_metrics_service, shutdown_metrics_service, get_metrics_service
from app.utils.db_startup import ensure_database_ready

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_startup_config():
    """Validate critical configuration before app starts. Logs clear errors."""
    errors = []
    warnings = []
    
    # Check database URLs
    if not settings.core_database_url_resolved:
        errors.append("DATABASE_URL or CORE_DATABASE_URL is not set")
    
    # Check encryption keys (required for key storage)
    if not settings.key_encryption_key:
        errors.append("KEY_ENCRYPTION_KEY is not set (required for private key encryption)")
    elif len(settings.key_encryption_key) != 64:
        errors.append(f"KEY_ENCRYPTION_KEY must be 64 hex chars, got {len(settings.key_encryption_key)}")
    
    if not settings.encryption_nonce:
        errors.append("ENCRYPTION_NONCE is not set (required for private key encryption)")
    elif len(settings.encryption_nonce) != 24:
        errors.append(f"ENCRYPTION_NONCE must be 24 hex chars, got {len(settings.encryption_nonce)}")
    
    # Check CORS origins for production
    if settings.is_production and "localhost" in settings.allowed_origins:
        warnings.append("ALLOWED_ORIGINS contains localhost in production mode")
    
    # Log results
    if errors:
        logger.error("=" * 60)
        logger.error("STARTUP CONFIGURATION ERRORS:")
        for err in errors:
            logger.error(f"  ✗ {err}")
        logger.error("=" * 60)
        raise RuntimeError(f"Startup failed: {len(errors)} configuration error(s). Check logs above.")
    
    if warnings:
        logger.warning("Startup configuration warnings:")
        for warn in warnings:
            logger.warning(f"  ⚠ {warn}")
    
    logger.info("✓ Startup configuration validated")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler replacing deprecated on_event startup/shutdown."""
    logger.info("Encypher Enterprise API starting up...")
    logger.info(f"Environment: {settings.environment}")
    
    # Validate configuration before proceeding
    validate_startup_config()
    # Log database connection info (safely handle None)
    db_url = settings.core_database_url_resolved or settings.database_url or ""
    logger.info(f"Database: {db_url.split('@')[1] if '@' in db_url else 'Not configured'}")
    if settings.ssl_com_api_key:
        logger.info(f"SSL.com API: {settings.ssl_com_api_url}")
    else:
        logger.info("SSL.com API: Not configured (optional for staging)")
    
    # Ensure database is ready and run migrations
    ensure_database_ready(
        database_url=db_url,
        service_name="enterprise-api",
        run_migrations=True,
        exit_on_failure=True
    )
    
    # Initialize Redis connection for session management
    try:
        await session_service.connect()
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Running without session persistence.")
    
    # Initialize metrics service for analytics
    try:
        await init_metrics_service()
        logger.info("Metrics service initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize metrics service: {e}. Running without metrics.")
    
    try:
        yield
    finally:
        logger.info("Encypher Enterprise API shutting down...")
        # Cleanup metrics service
        try:
            await shutdown_metrics_service()
        except Exception as e:
            logger.error(f"Error shutting down metrics service: {e}")
        # Cleanup Redis connection
        try:
            await session_service.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")

# Create FastAPI app
app = FastAPI(
    title="Encypher Enterprise API",
    description="C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises",
    version="1.0.0-preview",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS middleware - parse ALLOWED_ORIGINS env var
def get_cors_origins():
    """Get CORS origins from ALLOWED_ORIGINS env var."""
    origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
    logger.info(f"CORS allowed origins: {origins}")
    return origins

cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware for analytics
from app.middleware.metrics_middleware import MetricsMiddleware
app.add_middleware(MetricsMiddleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and add processing time header."""
    start_time = time.time()

    # Log request
    logger.info(f"{request.method} {request.url.path} - Client: {request.client.host}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log response
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )

    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Status and environment information
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0-preview"
    }


@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Lightweight readiness probe."""

    db_status = "ok"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        logger.warning("Readiness DB probe failed: %s", exc)
        db_status = "error"
    redis_status = "ok" if session_service.redis_client else "degraded"
    status_text = "ready" if db_status == "ok" else "degraded"
    return {
        "status": status_text,
        "database": db_status,
        "redis": redis_status,
        "version": "1.0.0-preview",
    }


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus-compatible metrics endpoint."""

    return PlainTextResponse(render_prometheus(), media_type="text/plain; version=0.0.4")


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """
    API root endpoint with basic information.

    Returns:
        dict: API information
    """
    return {
        "name": "Encypher Enterprise API",
        "version": "1.0.0-preview",
        "description": "C2PA-compliant content signing and verification",
        "docs": f"{settings.api_base_url}/docs" if not settings.is_production else None,
        "status": "preview"  # Will change to "production" after C2PA spec publication
    }


# Include routers
app.include_router(signing.router, prefix="/api/v1", tags=["Signing"])
app.include_router(verification.router, prefix="/api/v1", tags=["Verification"])
app.include_router(lookup.router, prefix="/api/v1", tags=["Lookup"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(streaming.router, prefix="/api/v1", tags=["Streaming"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(licensing.router, prefix="/api/v1", tags=["Licensing"])
app.include_router(usage.router, prefix="/api/v1", tags=["Usage"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
app.include_router(team.router, prefix="/api/v1", tags=["Team Management"])
app.include_router(coalition.router, prefix="/api/v1", tags=["Coalition"])
app.include_router(status.router, prefix="/api/v1", tags=["Status & Revocation"])
app.include_router(batch.router)
app.include_router(tools.router, prefix="/api/v1", tags=["Public Tools"])

# Include v1 API router (Merkle tree endpoints)
app.include_router(api_v1_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    correlation_id = request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "E_INTERNAL",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.is_development else None
            },
            "correlation_id": correlation_id,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return standardized error payloads for HTTP exceptions."""

    correlation_id = request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    detail = exc.detail
    if isinstance(detail, dict):
        # Preserve full detail dictionary
        error_payload = detail
        if "code" not in error_payload:
            error_payload["code"] = "E_HTTP"
        if "message" not in error_payload:
            error_payload["message"] = "Request failed"
    else:
        error_payload = {
            "code": "E_HTTP",
            "message": str(detail)
        }

    payload = {
        "success": False,
        "error": error_payload,
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=exc.headers,
    )


 
