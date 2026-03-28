"""Request logging middleware with structured logging and request IDs."""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def _resolve_client_ip(request: Request) -> str:
    """Extract real client IP from X-Forwarded-For (rightmost entry)."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ips = [ip.strip() for ip in forwarded_for.split(",") if ip.strip()]
        if ips:
            return ips[-1]
    return request.client.host if request.client else "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        logger = structlog.get_logger()

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=_resolve_client_ip(request),
        )

        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info("request_completed", status_code=response.status_code, duration_ms=round(duration * 1000, 2))
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error("request_failed", error=str(e), duration_ms=round(duration * 1000, 2))
            raise
