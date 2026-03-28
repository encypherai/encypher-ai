"""
Request logging middleware
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import structlog

logger = structlog.get_logger()


def _resolve_client_ip(request: Request) -> str:
    """Extract real client IP from X-Forwarded-For (rightmost entry).

    Behind a reverse proxy, the proxy appends the real client IP as the last
    entry in X-Forwarded-For. Earlier entries may be spoofed by the client.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ips = [ip.strip() for ip in forwarded_for.split(",") if ip.strip()]
        if ips:
            return ips[-1]
    return request.client.host if request.client else "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and responses
    """

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=_resolve_client_ip(request),
        )

        # Process request
        try:
            response = await call_next(request)

            # Log response
            duration = time.time() - start_time
            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=f"{duration:.3f}s",
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration=f"{duration:.3f}s",
            )
            raise
