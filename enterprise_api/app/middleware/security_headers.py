"""Security headers middleware for Enterprise API."""

from typing import Awaitable, Callable, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.config import settings

DEFAULT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"

DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://unpkg.com; "
    "style-src 'self' 'unsafe-inline' https://unpkg.com; "
    "img-src 'self' https://encypherai.com data:; "
    "font-src 'self' https://unpkg.com; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "form-action 'none'"
)


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


def _build_docs_headers() -> Dict[str, str]:
    """Security headers with a relaxed CSP for the /docs pages (Swagger UI)."""
    headers = build_security_headers()
    headers["Content-Security-Policy"] = DOCS_CSP
    return headers


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach standard security headers to all responses."""

    def __init__(self, app: ASGIApp, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(app)
        self._headers = headers or build_security_headers()
        self._docs_headers = _build_docs_headers()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        headers = self._docs_headers if request.url.path.startswith("/docs") else self._headers
        for header, value in headers.items():
            response.headers[header] = value
        return response
