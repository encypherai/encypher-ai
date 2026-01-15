"""Verification Service - Main Application"""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from .core.config import settings
from .core.logging_config import setup_logging
from .api.v1 import endpoints as v1_endpoints
from .monitoring.metrics import setup_metrics
from .middleware.logging import RequestLoggingMiddleware
from .db.session import get_db

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready

logger = setup_logging(settings.LOG_LEVEL).bind(service=settings.SERVICE_NAME)


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


app = FastAPI(
    title="Encypher Verification Service",
    description="Document verification microservice",
    version="1.0.1",
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

app.include_router(v1_endpoints.router, prefix="/api/v1/verify", tags=["verification"])


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.1",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
    }


@app.get("/{document_id}", include_in_schema=False)
async def verify_portal_document_id(
    document_id: str,
    db: Session = Depends(get_db),
):
    return await v1_endpoints.verify_by_document_id(document_id=document_id, db=db)


@app.get("/demo/{document_id}", include_in_schema=False)
async def verify_portal_demo_document_id(
    document_id: str,
    db: Session = Depends(get_db),
):
    return await v1_endpoints.verify_by_document_id(document_id=document_id, db=db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
