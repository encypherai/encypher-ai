"""
Coalition Service - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging_config import setup_logging
from .api.v1.endpoints import router as v1_router
from .monitoring.metrics import setup_metrics
from .middleware.logging import RequestLoggingMiddleware
from encypher_commercial_shared.metrics import MetricsClient, MetricsMiddleware

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

# Configure structured logging
logger = setup_logging(settings.LOG_LEVEL)

metrics_client = MetricsClient(redis_url=settings.REDIS_URL, service_name=settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}")

    await metrics_client.connect()

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
    title="Encypher Coalition Service",
    description="Coalition infrastructure and auto-onboarding microservice",
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

# Add metrics and request logging middleware
app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)
app.add_middleware(RequestLoggingMiddleware)

# Set up Prometheus metrics
setup_metrics(app)

# Include routers
app.include_router(v1_router, prefix="/api/v1/coalition", tags=["coalition"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": "2.0.0",
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
