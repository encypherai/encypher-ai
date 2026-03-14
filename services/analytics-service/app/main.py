"""Analytics Service - Main Application"""

import logging
from contextlib import asynccontextmanager

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1.endpoints import router as v1_router
from .core.config import settings
from .middleware.logging import RequestLoggingMiddleware
from .monitoring.metrics import setup_metrics

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.SERVICE_NAME}")

    # Ensure database is ready and run migrations
    ensure_database_ready(
        database_url=settings.DATABASE_URL,
        service_name=settings.SERVICE_NAME,
        alembic_config_path="alembic.ini",
        run_migrations=True,
        exit_on_failure=True,
    )

    # Start Redis Stream consumer for processing metrics
    stream_consumer = None
    if settings.REDIS_URL:
        try:
            from .services.stream_consumer import start_stream_consumer, stop_stream_consumer

            stream_consumer = await start_stream_consumer(redis_url=settings.REDIS_URL)
            logger.info("Redis Stream consumer started")
        except Exception as e:
            logger.warning(f"Failed to start Redis Stream consumer: {e}")
            logger.warning("Analytics will only process direct API calls")

    yield

    # Stop stream consumer
    if stream_consumer:
        try:
            from .services.stream_consumer import stop_stream_consumer

            await stop_stream_consumer()
            logger.info("Redis Stream consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping stream consumer: {e}")

    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Encypher Analytics Service",
    description="Analytics and metrics microservice",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Set up Prometheus metrics
setup_metrics(app)

app.include_router(v1_router, prefix="/api/v1/analytics", tags=["analytics"])

# ---- Capability index used by root and health endpoints ----
_CAPABILITIES = [
    {"route": "POST /api/v1/analytics/metrics", "summary": "Record a usage metric (auth required)"},
    {"route": "GET  /api/v1/analytics/usage", "summary": "Usage statistics for the authenticated user/org"},
    {"route": "GET  /api/v1/analytics/services", "summary": "Per-service metric breakdown"},
    {"route": "GET  /api/v1/analytics/timeseries", "summary": "Time-series data for a metric type"},
    {"route": "GET  /api/v1/analytics/activity", "summary": "Recent activity feed"},
    {"route": "GET  /api/v1/analytics/activity/audit-events", "summary": "Paginated audit event log"},
    {"route": "GET  /api/v1/analytics/activity/audit-events/export", "summary": "Export audit events as CSV or JSON (max 10000 rows)"},
    {"route": "GET  /api/v1/analytics/activity/audit-events/alerts", "summary": "Alert summary for incident triage"},
    {"route": "GET  /api/v1/analytics/report", "summary": "Comprehensive analytics report"},
    {"route": "POST /api/v1/analytics/pageview", "summary": "Record anonymous pageview (public, rate-limited)"},
    {"route": "GET  /api/v1/analytics/trace/{request_id}", "summary": "Reconstruct full trace for a request ID"},
    {"route": "POST /api/v1/analytics/discovery", "summary": "Record discovery events from Chrome extension (public, rate-limited)"},
    {"route": "GET  /api/v1/analytics/discovery/stats", "summary": "Discovery statistics for the authenticated org"},
    {"route": "GET  /api/v1/analytics/discovery/domains", "summary": "Domain summaries for content discovery"},
    {"route": "GET  /api/v1/analytics/discovery/alerts", "summary": "Unacknowledged external-domain alerts"},
    {"route": "POST /api/v1/analytics/discovery/alerts/{id}/ack", "summary": "Acknowledge a domain alert"},
    {"route": "GET  /api/v1/analytics/discovery/events", "summary": "Paginated content discovery events"},
    {"route": "GET  /api/v1/analytics/discovery/owned-domains", "summary": "List owned domain patterns"},
    {"route": "POST /api/v1/analytics/discovery/owned-domains", "summary": "Add an owned domain pattern"},
    {"route": "PATCH /api/v1/analytics/discovery/owned-domains/{id}", "summary": "Update an owned domain entry"},
    {"route": "DELETE /api/v1/analytics/discovery/owned-domains/{id}", "summary": "Remove an owned domain pattern"},
    {"route": "POST /api/v1/analytics/admin/usage-counts", "summary": "Bulk usage counts for multiple users (admin only)"},
    {"route": "GET  /api/v1/analytics/user/{user_id}/activity", "summary": "Activity log for a specific user (admin or self)"},
    {"route": "GET  /api/v1/analytics/health", "summary": "Router-level health check"},
]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom 422 handler with field-level hints and example usage."""
    errors = exc.errors()
    hints = []
    for err in errors:
        loc = " -> ".join(str(part) for part in err.get("loc", []))
        msg = err.get("msg", "")
        hints.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "detail": "Request validation failed",
                "fields": hints,
                "help": (
                    "Check that all required fields are present and correctly typed. "
                    "Most authenticated endpoints require: Authorization: Bearer <jwt_token>. "
                    "See GET / for a list of available routes."
                ),
            },
            "data": None,
        },
    )


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "capabilities": _CAPABILITIES,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "capabilities_count": len(_CAPABILITIES),
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
