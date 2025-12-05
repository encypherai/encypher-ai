"""
Auth Service - Main Application
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging_config import setup_logging
from .api.v1.endpoints import router as v1_router
from .api.v1.organizations import router as organizations_router
from .db.models import Base
from .db.session import engine
from .monitoring.metrics import setup_metrics
from .middleware.logging import RequestLoggingMiddleware

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

# Configure structured logging
logger = setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}")
    
    # Ensure database is ready and run migrations
    ensure_database_ready(
        database_url=settings.DATABASE_URL,
        service_name=settings.SERVICE_NAME,
        alembic_config_path="alembic.ini",
        run_migrations=True,
        exit_on_failure=True
    )

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# Create FastAPI app
app = FastAPI(
    title="Encypher Auth Service",
    description="Authentication and authorization microservice",
    version="1.0.0",
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

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Set up Prometheus metrics
setup_metrics(app)

# Include routers
app.include_router(v1_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(organizations_router, prefix="/api/v1", tags=["organizations"])

# Fallback metrics endpoint (in case instrumentator isn't exposing it)
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    @app.get("/metrics")
    async def metrics_fallback():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
except ImportError:
    # prometheus_client not available - metrics endpoint handled by instrumentator
    logger.debug("prometheus_client not available, using instrumentator for metrics")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
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
