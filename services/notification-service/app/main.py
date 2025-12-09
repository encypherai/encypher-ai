"""Notification Service - Main Application"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.endpoints import router as v1_router
from .core.config import settings
from .core.logging_config import setup_logging
from .db.models import Base
from .db.session import engine
from .middleware.logging import RequestLoggingMiddleware
from .monitoring.metrics import setup_metrics

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

# Configure structured logging
logger = setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(title="Encypher Notification Service", version="1.0.0", lifespan=lifespan)

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

app.include_router(v1_router, prefix="/api/v1/notifications", tags=["notifications"])


@app.get("/")
async def root():
    return {"service": settings.SERVICE_NAME, "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.SERVICE_HOST, port=settings.SERVICE_PORT, reload=True)
