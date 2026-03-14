"""Request ID Middleware.

Stamps every inbound request with a canonical X-Request-ID.
Propagates the ID via a contextvars.ContextVar so every log line
within the request context carries the ID without explicit threading.

Usage in logging setup:
    root = logging.getLogger()
    root.addFilter(RequestIDFilter())
    # then set format to include %(request_id)s

Usage from any coroutine inside a request:
    from app.middleware.request_id_middleware import request_id_ctx
    rid = request_id_ctx.get()  # returns "-" outside a request
"""

import contextvars
import logging
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Module-level ContextVar - readable from any coroutine in the same task tree.
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Stamp every request with a canonical X-Request-ID.

    - Reads X-Request-ID from the inbound request (supports caller tracing).
    - Generates req-{12-char hex} if the client did not supply one.
    - Sets request.state.request_id for downstream router access.
    - Sets request_id_ctx ContextVar so any logger with RequestIDFilter
      will include the ID in every log line automatically.
    - Injects X-Request-ID into the response header for client correlation.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or f"req-{uuid4().hex[:12]}"
        request.state.request_id = request_id
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["x-request-id"] = request_id
        return response


def get_correlation_id(request: Request) -> str:
    """Return the canonical correlation ID for *request*.

    Checks ``request.state.request_id`` first (set by the middleware on the
    inbound path), falls back to the ``x-request-id`` header, and finally
    generates a new ID.  Use this instead of copy-pasting the extraction
    logic in every router.
    """
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req-{uuid4().hex[:12]}"


class RequestIDFilter(logging.Filter):
    """Logging filter that injects the current request_id into every log record.

    Install once on the root logger (or any handler):
        logging.getLogger().addFilter(RequestIDFilter())

    Then use %(request_id)s in the log format string.
    Outside a request context the value is "-".
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()  # type: ignore[attr-defined]
        return True
