"""
Key Service - Main Application
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.endpoints import router as v1_router
from .db.models import Base
from .db.session import engine
from .middleware.timing import TimingMiddleware
from encypher_commercial_shared.metrics import MetricsClient, MetricsMiddleware, set_metrics_client

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
metrics_client = MetricsClient(redis_url=settings.REDIS_URL, service_name=settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
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

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# Create FastAPI app
app = FastAPI(
    title="Encypher Key Service",
    description="API Key management microservice",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)
app.add_middleware(TimingMiddleware)

# Include routers
app.include_router(v1_router, prefix="/api/v1/keys", tags=["keys"])


@app.get("/")
async def root():
    """Root endpoint - returns service identity and endpoint index."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "generate_key": "POST /api/v1/keys/generate",
            "list_keys": "GET /api/v1/keys",
            "get_key": "GET /api/v1/keys/{key_id}",
            "update_key": "PUT /api/v1/keys/{key_id}",
            "revoke_key": "DELETE /api/v1/keys/{key_id}",
            "rotate_key": "POST /api/v1/keys/{key_id}/rotate",
            "verify_key": "POST /api/v1/keys/verify",
            "validate_key": "POST /api/v1/keys/validate",
            "validate_key_minimal": "POST /api/v1/keys/validate-minimal",
            "key_usage": "GET /api/v1/keys/{key_id}/usage",
            "health": "GET /health",
        },
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
