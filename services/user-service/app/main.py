"""User Service - Main Application"""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1.endpoints import router as v1_router
from .core.config import settings
from .core.logging_config import setup_logging
from .middleware.logging import RequestLoggingMiddleware
from .monitoring.metrics import setup_metrics

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready
from encypher_commercial_shared.metrics import MetricsClient, MetricsMiddleware, set_metrics_client

# Configure structured logging
logger = setup_logging(settings.LOG_LEVEL)

metrics_client = MetricsClient(redis_url=settings.REDIS_URL, service_name=settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.SERVICE_NAME}")

    await metrics_client.connect()
    set_metrics_client(metrics_client)

    # Ensure database is ready and run migrations
    ensure_database_ready(
        database_url=settings.DATABASE_URL,
        service_name=settings.SERVICE_NAME,
        alembic_config_path="alembic.ini",
        run_migrations=True,
        exit_on_failure=True,
    )

    # Shared HTTP client -- reuses connections across all requests
    app.state.http_client = httpx.AsyncClient()

    yield

    await app.state.http_client.aclose()
    await metrics_client.disconnect()
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(title="Encypher User Service", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Set up Prometheus metrics
setup_metrics(app)

app.include_router(v1_router, prefix="/api/v1/users", tags=["users"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return structured 422 with field errors and usage guidance."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "hint": (
                "One or more request fields failed validation. "
                "Check the 'detail' list for field names and expected types. "
                "See the interactive API docs at GET /docs for full schema examples."
            ),
        },
    )


# Capabilities summary exposed on the root and health routes so agent
# callers can discover available endpoints without reading full OpenAPI docs.
_CAPABILITIES = {
    "endpoints": [
        {
            "method": "GET",
            "path": "/api/v1/users/profile",
            "description": "Get the authenticated user's profile",
        },
        {
            "method": "PUT",
            "path": "/api/v1/users/profile",
            "description": "Update the authenticated user's profile",
        },
        {
            "method": "POST",
            "path": "/api/v1/users/teams",
            "description": "Create a new team",
        },
        {
            "method": "GET",
            "path": "/api/v1/users/teams",
            "description": "List teams (paginated; query params: page, page_size)",
        },
    ],
    "auth": "Bearer token required in Authorization header for all /api/v1/ routes",
    "docs": "/docs",
}


@app.get("/")
async def root():
    """Service identity and capabilities summary."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "2.0.0",
        "status": "running",
        "capabilities": _CAPABILITIES,
    }


@app.get("/health")
async def health():
    """Liveness probe with capabilities summary."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "capabilities": _CAPABILITIES,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.SERVICE_HOST, port=settings.SERVICE_PORT, reload=True)
