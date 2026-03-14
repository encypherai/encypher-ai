"""
Request timing middleware.

Adds an X-Processing-Time-Ms header to every response with the wall-clock
milliseconds elapsed between receiving the request and sending the response.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """Attach X-Processing-Time-Ms to every HTTP response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response: Response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        response.headers["X-Processing-Time-Ms"] = str(elapsed_ms)
        return response
