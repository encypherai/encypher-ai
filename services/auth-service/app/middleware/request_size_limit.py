"""Request size limiting middleware for auth endpoints."""

from typing import Optional, Set

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with bodies larger than the configured limit."""

    DEFAULT_EXCLUDE_PATHS: Set[str] = {
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/api/v1/auth/saml/acs",
    }

    def __init__(self, app, max_body_size: int, exclude_paths: Optional[Set[str]] = None) -> None:
        super().__init__(app)
        self.max_body_size = max_body_size
        self.exclude_paths = exclude_paths or self.DEFAULT_EXCLUDE_PATHS

    async def dispatch(self, request: Request, call_next):
        if self._should_exclude(request.url.path) or request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)

        if self.max_body_size > 0:
            content_length = request.headers.get("content-length")
            parsed_length = None
            if content_length:
                try:
                    parsed_length = int(content_length)
                except ValueError:
                    parsed_length = None
            if parsed_length is not None:
                if parsed_length > self.max_body_size:
                    return self._too_large_response()
            else:
                body = await self._read_body_with_limit(request)
                if body is None:
                    return self._too_large_response()

        return await call_next(request)

    def _should_exclude(self, path: str) -> bool:
        if path in self.exclude_paths:
            return True
        return any(path.startswith(exclude_path) for exclude_path in self.exclude_paths)

    async def _read_body_with_limit(self, request: Request) -> Optional[bytes]:
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > self.max_body_size:
                return None
        request._body = bytes(body)
        return request._body

    @staticmethod
    def _too_large_response() -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request body too large"},
        )
