"""Billing Service - Main Application"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.endpoints import router as v1_router
from .api.v1.stripe_webhooks import router as webhook_router
from .monitoring.metrics import setup_metrics
from .middleware.logging import RequestLoggingMiddleware
from .services.price_cache import price_cache

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

    # Validate Stripe price configuration on startup
    if settings.STRIPE_API_KEY:
        logger.info("Validating Stripe price configuration...")
        try:
            validation_results = await price_cache.validate_prices_on_startup()
            valid_count = sum(1 for v in validation_results.values() if v)
            total_count = len(validation_results)

            if valid_count == total_count:
                logger.info(f"All {total_count} Stripe prices validated successfully")
            else:
                logger.warning(f"Only {valid_count}/{total_count} Stripe prices validated")
                logger.warning("Service will continue, but some checkout flows may fail")
        except Exception as e:
            logger.error(f"Failed to validate Stripe prices: {e}")
            logger.warning("Service will continue without price validation")
    else:
        logger.warning("STRIPE_API_KEY not set - skipping price validation")

    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Encypher Billing Service",
    description="Billing and subscription microservice",
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

app.include_router(v1_router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(webhook_router, prefix="/api/v1", tags=["webhooks"])


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "health_url": "/health",
        "capabilities": [
            "GET  /api/v1/billing/subscription   - get current subscription",
            "POST /api/v1/billing/subscription   - create subscription",
            "DELETE /api/v1/billing/subscription/{id} - cancel subscription",
            "GET  /api/v1/billing/invoices        - list invoices",
            "GET  /api/v1/billing/stats           - billing statistics",
            "GET  /api/v1/billing/usage           - current period usage metrics",
            "GET  /api/v1/billing/plans           - available plans and pricing",
            "POST /api/v1/billing/checkout        - create Stripe checkout session",
            "POST /api/v1/billing/checkout/add-on - purchase add-on",
            "GET  /api/v1/billing/portal          - Stripe billing portal URL",
            "POST /api/v1/billing/upgrade         - change subscription tier",
            "GET  /api/v1/billing/coalition        - coalition earnings summary",
            "GET  /api/v1/billing/health          - service health",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
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
