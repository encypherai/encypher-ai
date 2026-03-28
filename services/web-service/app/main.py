import logging
import time
import uuid as uuid_lib
from contextlib import asynccontextmanager

# Import database startup utilities
from encypher_commercial_shared.db import ensure_database_ready
from encypher_commercial_shared.metrics import MetricsClient, MetricsMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.api_v1 import api_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
metrics_client = MetricsClient(redis_url=settings.REDIS_URL, service_name="web-service")


class RequestMetaMiddleware(BaseHTTPMiddleware):
    """Attach X-Request-Id and X-Process-Time-Ms headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid_lib.uuid4())
        start = time.monotonic()
        response: Response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting web-service")

    await metrics_client.connect()

    # Ensure database is ready and run migrations
    db_url = str(settings.SQLALCHEMY_DATABASE_URI) if settings.SQLALCHEMY_DATABASE_URI else None
    if db_url:
        ensure_database_ready(
            database_url=db_url,
            service_name="web-service",
            alembic_config_path="alembic.ini",
            run_migrations=True,
            exit_on_failure=True,
        )

    yield

    await metrics_client.disconnect()
    logger.info("Shutting down web-service")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Attach timing / request-ID middleware
app.add_middleware(RequestMetaMiddleware)

# Set all CORS enabled origins
if settings.ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
elif settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check() -> dict:
    """Return service health status."""
    return {"status": "healthy", "service": "web-service"}


@app.get("/")
def root() -> dict:
    """Return service info and available API endpoint groups."""
    return {
        "service": settings.PROJECT_NAME,
        "version": "1",
        "docs": f"{settings.API_V1_STR}/docs",
        "endpoints": {
            "demo_requests": f"{settings.API_V1_STR}/demo-requests",
            "analytics": f"{settings.API_V1_STR}/marketing-analytics",
            "tools": f"{settings.API_V1_STR}/tools",
            "ai_demo": f"{settings.API_V1_STR}/ai-demo",
            "publisher_demo": f"{settings.API_V1_STR}/publisher-demo",
            "sales": f"{settings.API_V1_STR}/sales",
            "newsletter": f"{settings.API_V1_STR}/newsletter",
        },
    }
