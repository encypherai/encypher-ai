import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.watermark import router as watermark_router
from app.services.trustmark_service import TrustMarkService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Loads the TrustMark model at startup so it is warm before any
    requests arrive. If trustmark/torch are not installed the service
    still starts and returns 503 for watermark endpoints.
    """
    global trustmark_service  # noqa: PLW0603 -- module-level reference for tests
    logger.info("Loading TrustMark model...")
    trustmark_service = TrustMarkService()
    try:
        trustmark_service.load_model()
        if trustmark_service.is_available:
            logger.info("TrustMark model loaded")
        else:
            logger.warning(
                "TrustMark model not available. "
                "Install trustmark + torch to enable watermarking endpoints."
            )
    except Exception as e:
        logger.warning("TrustMark model not available: %s. Service will return errors.", e)
    app.state.trustmark_service = trustmark_service
    yield
    logger.info("image-service shutting down")


# Module-level reference used by tests to override app.state before TestClient.
trustmark_service: TrustMarkService | None = None

app = FastAPI(title="Encypher Image Service", version="0.1.0", lifespan=lifespan)

app.include_router(health_router)
app.include_router(watermark_router, prefix="/api/v1")
