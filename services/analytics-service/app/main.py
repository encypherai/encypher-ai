"""Analytics Service - Main Application"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.endpoints import router as v1_router
from .monitoring.metrics import setup_metrics
from .middleware.logging import RequestLoggingMiddleware

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

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


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
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
