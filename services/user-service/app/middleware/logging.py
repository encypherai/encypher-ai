"""
Request logging middleware with structured logging and request IDs.
"""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request IDs and structured logging to all requests.

    Features:
    - Generates unique request ID for each request
    - Adds request ID to response headers
    - Logs request start and completion
    - Tracks request duration
    - Binds request context to structlog
    """

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get logger
        logger = structlog.get_logger()

        # Bind request context to structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        # Log request start
        start_time = time.time()
        logger.info("request_started", query_params=dict(request.query_params) if request.query_params else None)

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log request completion
            logger.info("request_completed", status_code=response.status_code, duration_ms=round(duration * 1000, 2))

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error("request_failed", error=str(e), error_type=type(e).__name__, duration_ms=round(duration * 1000, 2))

            # Re-raise exception
            raise
