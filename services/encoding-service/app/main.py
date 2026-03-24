"""
Encoding Service - Main Application
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.endpoints import router as v1_router
from .middleware.logging import RequestLoggingMiddleware

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("Starting %s", settings.SERVICE_NAME)

    # Ensure database is ready and run migrations
    ensure_database_ready(
        database_url=settings.DATABASE_URL,
        service_name=settings.SERVICE_NAME,
        alembic_config_path="alembic.ini",
        run_migrations=True,
        exit_on_failure=True,
    )

    yield

    # Shutdown
    logger.info("Shutting down %s", settings.SERVICE_NAME)


# Create FastAPI app
app = FastAPI(
    title="Encypher Encoding Service",
    description="Document encoding and signing microservice",
    version="2.0.0",
    lifespan=lifespan,
)

# Request logging / request-ID middleware (registered first so request_id is
# available to all subsequent middleware and exception handlers)
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom 422 handler that adds a usage hint alongside the standard error detail.
    """
    request_id = str(getattr(request.state, "request_id", "") or "")
    body: dict = {
        "detail": exc.errors(),
        "hint": ("Check the request body against the API schema at /docs. All required fields must be present and match the declared types."),
    }
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=body,
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Include routers
app.include_router(v1_router, prefix="/api/v1/encode", tags=["encoding"])


# ---------------------------------------------------------------------------
# Root and health endpoints
# ---------------------------------------------------------------------------

_ENDPOINTS = [
    {"method": "POST", "path": "/api/v1/encode/sign", "description": "Sign a document"},
    {"method": "POST", "path": "/api/v1/encode/embed", "description": "Embed metadata without signing"},
    {"method": "GET", "path": "/api/v1/encode/documents", "description": "List documents (summaries)"},
    {"method": "GET", "path": "/api/v1/encode/documents/{document_id}", "description": "Get document summary"},
    {"method": "GET", "path": "/api/v1/encode/documents/{document_id}/manifest", "description": "Get document manifest"},
    {"method": "GET", "path": "/api/v1/encode/stats", "description": "Get operation statistics"},
    {"method": "GET", "path": "/api/v1/encode/health", "description": "Service health"},
    {"method": "GET", "path": "/health", "description": "Top-level health check"},
    {"method": "GET", "path": "/docs", "description": "Interactive API documentation (Swagger UI)"},
    {"method": "GET", "path": "/redoc", "description": "Interactive API documentation (ReDoc)"},
]


@app.get("/")
async def root():
    """Root endpoint -- returns service info and available endpoints."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "2.0.0",
        "status": "running",
        "endpoints": _ENDPOINTS,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
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
