"""
Encypher Enterprise API - Main Application

FastAPI application for C2PA-compliant content signing and verification.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from app.config import settings
from app.routers import audit, batch, chat, coalition, licensing, lookup, onboarding, signing, streaming, team, usage, verification
from app.api.v1.api import api_router as api_v1_router
from app.database import engine
from app.observability.metrics import render_prometheus
from app.services.session_service import session_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler replacing deprecated on_event startup/shutdown."""
    logger.info("Encypher Enterprise API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(
        f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'Not configured'}"
    )
    logger.info(f"SSL.com API: {settings.ssl_com_api_url}")
    
    # Initialize Redis connection for session management
    try:
        await session_service.connect()
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Running without session persistence.")
    
    # Verify database connection and schema
    # Note: Schema is now managed by unified migrations in services/migrations/
    # Run `start-dev.ps1` to initialize the database with all required tables
    try:
        async with engine.begin() as conn:
            # Quick health check - verify organizations table exists
            result = await conn.execute(text("SELECT COUNT(*) FROM organizations"))
            org_count = result.scalar()
            logger.info(f"Database connected. Organizations: {org_count}")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Make sure to run migrations first (start-dev.ps1 or services/migrations/*.sql)")
    
    try:
        yield
    finally:
        logger.info("Encypher Enterprise API shutting down...")
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

# CORS middleware (configure allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.marketing_domain}",
        f"https://{settings.infrastructure_domain}",
        f"https://api.{settings.infrastructure_domain}",
        f"https://verify.{settings.infrastructure_domain}",
        f"https://dashboard.{settings.infrastructure_domain}",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(batch.router)

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


 
