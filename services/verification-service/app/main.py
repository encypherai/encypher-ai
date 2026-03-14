"""Verification Service - Main Application"""

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from .core.config import settings
from .core.logging_config import setup_logging
from .api.v1 import endpoints as v1_endpoints
from .monitoring.metrics import setup_metrics
from .middleware.logging import RequestLoggingMiddleware
from encypher_commercial_shared.metrics import MetricsClient, MetricsMiddleware, set_metrics_client
from .db.session import get_db

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

logger = setup_logging(settings.LOG_LEVEL).bind(service=settings.SERVICE_NAME)
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

    yield
    await metrics_client.disconnect()
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Encypher Verification Service",
    description="Document verification microservice",
    version="1.0.2",
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

# Add metrics middleware for analytics
app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)

# Set up Prometheus metrics
setup_metrics(app)

app.include_router(v1_endpoints.router, prefix="/api/v1/verify", tags=["verification"])


# ---------------------------------------------------------------------------
# Task 8.2: Custom 422 handler with usage example
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return structured 422 with a usage example to guide callers."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "detail": exc.errors(),
            "hint": (
                "Ensure your request body matches the VerifyRequest schema. "
                "Example: POST /api/v1/verify with body: "
                '{"text": "<your signed text here>"}'
            ),
        },
    )


# ---------------------------------------------------------------------------
# Root and health
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.2",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
    }


# ---------------------------------------------------------------------------
# Task 3.0: Consolidated portal route
# /{document_id} and /demo/{document_id} both call the same handler.
# ---------------------------------------------------------------------------


@app.get("/{document_id}", include_in_schema=False)
async def verify_portal_document_id(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return await v1_endpoints.verify_by_document_id(document_id=document_id, db=db, request=request)


@app.get("/demo/{document_id}", include_in_schema=False)
async def verify_portal_demo_document_id(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return await v1_endpoints.verify_by_document_id(document_id=document_id, db=db, request=request)


# ---------------------------------------------------------------------------
# Task 4.3: Merged status list proxy routes
# Both UUID-based and legacy org/list_index paths are handled here.
# ---------------------------------------------------------------------------


async def _proxy_status_list(url: str) -> JSONResponse:
    """Shared proxy logic for status list endpoints."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
        return JSONResponse(
            content=resp.json(),
            status_code=resp.status_code,
            headers={
                "Cache-Control": "public, max-age=300",
                "Content-Type": "application/json",
            },
        )
    except Exception as exc:
        logger.error("Failed to proxy status list request", error=str(exc))
        return JSONResponse(
            content={
                "error": "Failed to fetch status list",
                "error_detail": str(exc),
            },
            status_code=502,
        )


@app.get("/status/v1/lists/{list_id}", include_in_schema=False)
async def status_list_proxy(list_id: str):
    """Proxy UUID-based status list requests to enterprise-api."""
    url = f"{settings.ENTERPRISE_API_URL}/api/v1/status/lists/{list_id}"
    return await _proxy_status_list(url)


@app.get("/status/v1/{organization_id}/list/{list_index}", include_in_schema=False)
async def status_list_proxy_legacy(organization_id: str, list_index: int):
    """Legacy proxy -- kept for backward compatibility with old URLs."""
    url = f"{settings.ENTERPRISE_API_URL}/api/v1/status/list/{organization_id}/{list_index}"
    return await _proxy_status_list(url)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
