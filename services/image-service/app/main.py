import logging
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers.health import router as health_router
from app.routers.watermark import router as watermark_router
from app.services.trustmark_service import TrustMarkService

logger = logging.getLogger(__name__)


class ProcessingTimeMiddleware(BaseHTTPMiddleware):
    """Attach X-Processing-Time-Ms header to every response."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        response.headers["X-Processing-Time-Ms"] = str(elapsed_ms)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Loads the TrustMark model at startup so it is warm before any
    requests arrive. If trustmark/torch are not installed the service
    still starts and returns 503 for watermark endpoints.
    """
    logger.info("Loading TrustMark model...")
    svc = TrustMarkService()
    try:
        svc.load_model()
        if svc.is_available:
            logger.info("TrustMark model loaded")
        else:
            logger.warning("TrustMark model not available. Install trustmark + torch to enable watermarking endpoints.")
    except Exception as e:
        logger.warning("TrustMark model not available: %s. Service will return errors.", e)
    app.state.trustmark_service = svc
    yield
    logger.info("image-service shutting down")


app = FastAPI(title="Encypher Image Service", version="0.1.0", lifespan=lifespan)

app.add_middleware(ProcessingTimeMiddleware)
app.include_router(health_router)
app.include_router(watermark_router, prefix="/api/v1")
