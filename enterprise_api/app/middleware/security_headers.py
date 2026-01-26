"""Security headers middleware for Enterprise API."""

from typing import Awaitable, Callable, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.config import settings

DEFAULT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


def build_security_headers() -> Dict[str, str]:
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy": DEFAULT_CSP,
    }

    if settings.is_production:
        headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

    return headers


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach standard security headers to all responses."""

    def __init__(self, app: ASGIApp, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(app)
        self._headers = headers or build_security_headers()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        for header, value in self._headers.items():
            response.headers[header] = value
        return response
