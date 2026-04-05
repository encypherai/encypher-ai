import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers.health import router as health_router
from app.routers.watermark import router as watermark_router

logger = logging.getLogger(__name__)


class ProcessingTimeMiddleware(BaseHTTPMiddleware):
    """Attach X-Processing-Time-Ms header to every response."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        response.headers["X-Processing-Time-Ms"] = str(elapsed_ms)
        return response


app = FastAPI(title="Encypher Video Watermark Service", version="0.1.0")
app.add_middleware(ProcessingTimeMiddleware)
app.include_router(health_router)
app.include_router(watermark_router, prefix="/api/v1")
