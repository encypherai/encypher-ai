"""Response Envelope Middleware.

Ensures every JSON response from the API includes a consistent metadata
footer with processing time, status indicator, API version, and correlation ID.

This middleware enforces Unix Agent Design criterion 4 (metadata footer) and
criterion 8 (two-layer separation) by centralizing presentation logic that
was previously duplicated across individual route handlers.

The middleware only touches responses that already have an ``ApiResponse``-shaped
body (i.e. contain a ``success`` key).  Responses that don't match (health
checks, static files, non-JSON) pass through untouched.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Inject metadata footer into every ApiResponse-shaped JSON response.

    Adds or updates the ``meta`` object with:
    - ``processing_time_ms``: wall-clock time for the request
    - ``status``: ``"ok"`` or ``"error"`` derived from ``success`` field
    - ``api_version``: always ``"v1"``
    - ``correlation_id``: from request state (set by RequestIDMiddleware)

    Responses that are not JSON, not ApiResponse-shaped, or on excluded paths
    are passed through without modification.
    """

    EXCLUDE_PATHS = frozenset(
        {
            "/health",
            "/readyz",
            "/metrics",
            "/favicon.ico",
        }
    )

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        response: Response = await call_next(request)

        # Skip non-API paths
        if request.url.path in self.EXCLUDE_PATHS:
            return response

        # Only process JSON responses
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        # Use request.state directly (no fallback generation needed here --
        # RequestIDMiddleware has already set it on the inbound path).
        correlation_id: str | None = getattr(request.state, "request_id", None)

        body = await self._read_body(response)
        if body is None:
            return response

        payload = self._parse_json(body)
        if payload is None:
            # Body was consumed but isn't valid JSON -- rebuild response
            return self._rebuild(response, body)

        # Only touch ApiResponse-shaped payloads (must have "success" key)
        if "success" not in payload:
            return self._rebuild(response, body)

        self._inject_meta(payload, elapsed_ms, correlation_id)

        new_body = json.dumps(payload, default=str).encode("utf-8")
        return self._rebuild(response, new_body)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _rebuild(response: Response, body: bytes) -> Response:
        """Reconstruct a Response from consumed body bytes.

        Strips ``content-length`` from the copied headers so that Starlette
        recalculates it from the (possibly resized) *body*.
        """
        headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
            background=response.background,
        )

    @staticmethod
    async def _read_body(response: Response) -> Optional[bytes]:
        """Read the response body, handling both regular and streaming responses."""
        body = getattr(response, "body", None)
        if body:
            return body

        body_iterator = getattr(response, "body_iterator", None)
        if body_iterator is None:
            return None

        chunks: list[bytes] = []
        async for chunk in body_iterator:
            if isinstance(chunk, bytes):
                chunks.append(chunk)
            elif isinstance(chunk, (bytearray, memoryview)):
                chunks.append(bytes(chunk))
            else:
                chunks.append(str(chunk).encode("utf-8"))

        return b"".join(chunks) if chunks else None

    @staticmethod
    def _parse_json(body: bytes) -> Optional[Dict[str, Any]]:
        """Attempt to parse bytes as JSON dict. Returns None on failure."""
        try:
            payload = json.loads(body)
        except (TypeError, ValueError, UnicodeDecodeError):
            return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _inject_meta(
        payload: Dict[str, Any],
        elapsed_ms: int,
        correlation_id: Optional[str],
    ) -> None:
        """Mutate *payload* in place, ensuring ``meta`` has required fields."""
        meta = payload.get("meta")
        if not isinstance(meta, dict):
            meta = {}
            payload["meta"] = meta

        meta.setdefault("api_version", "v1")
        meta["processing_time_ms"] = elapsed_ms
        meta["status"] = "ok" if payload.get("success") else "error"

        if correlation_id:
            meta["correlation_id"] = correlation_id
            # Also ensure top-level correlation_id is set
            payload.setdefault("correlation_id", correlation_id)
