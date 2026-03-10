"""
Metrics Middleware for Enterprise API.

Automatically records API call metrics for all requests.
Non-blocking - metrics are buffered and flushed asynchronously.
"""

import json
import logging
import time
import traceback
from typing import Set, cast

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.services.metrics_service import MetricType, get_metrics_service

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic API metrics collection.

    Records timing, status codes, and request metadata for all API calls.
    Extracts organization/user info from request state (set by auth middleware).
    """

    # Paths to exclude from metrics
    EXCLUDE_PATHS: Set[str] = {
        "/health",
        "/readyz",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and record metrics."""
        path = request.url.path

        # Skip excluded paths
        if self._should_exclude(path):
            return cast(Response, await call_next(request))

        # Record start time
        start_time = time.perf_counter()

        # Process request
        try:
            response = cast(Response, await call_next(request))
        except Exception as exc:
            await self._emit_unhandled_exception_metric(request, path, start_time, exc)
            raise

        # Calculate response time
        response_time_ms = (time.perf_counter() - start_time) * 1000

        # Get metrics service
        metrics = get_metrics_service()
        if not metrics:
            return response

        # Extract organization and user info from request state
        # These are set by the auth middleware/dependency
        organization_id = getattr(request.state, "organization_id", None)
        user_id = getattr(request.state, "user_id", None)
        api_key_id = getattr(request.state, "api_key_id", None)
        api_key_prefix = getattr(request.state, "api_key_prefix", None)

        metadata = {
            "request_id": getattr(request.state, "request_id", None) or request.headers.get("x-request-id"),
            "method": request.method,
            "api_key_prefix": api_key_prefix,
        }
        if response.status_code >= 400:
            body_bytes, consumed_stream = await self._read_response_body(response)
            metadata.update(self._extract_error_metadata(body_bytes))
            if consumed_stream:
                response = Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                    background=response.background,
                )

        # Only record metrics if we have an organization
        if organization_id:
            # Determine metric type based on endpoint
            metric_type = self._get_metric_type(path, request.method)

            # Emit metric (non-blocking)
            try:
                await metrics.emit(
                    metric_type=metric_type,
                    organization_id=organization_id,
                    user_id=user_id,
                    api_key_id=api_key_id,
                    endpoint=path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    metadata={k: v for k, v in metadata.items() if v},
                )
            except Exception as e:
                # Never let metrics collection break the request
                logger.debug(f"Failed to emit metric: {e}")

        return response

    async def _emit_unhandled_exception_metric(self, request: Request, path: str, start_time: float, exc: Exception) -> None:
        """Emit telemetry for unhandled exceptions before they are converted to HTTP 500."""
        metrics = get_metrics_service()
        if not metrics:
            return

        organization_id = getattr(request.state, "organization_id", None)
        if not organization_id:
            return

        user_id = getattr(request.state, "user_id", None)
        api_key_id = getattr(request.state, "api_key_id", None)
        api_key_prefix = getattr(request.state, "api_key_prefix", None)

        metadata = {
            "request_id": getattr(request.state, "request_id", None) or request.headers.get("x-request-id"),
            "method": request.method,
            "api_key_prefix": api_key_prefix,
            "error_code": "E_UNHANDLED",
            "error_message": str(exc),
            "error_stack": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        }

        response_time_ms = (time.perf_counter() - start_time) * 1000
        metric_type = self._get_metric_type(path, request.method)

        try:
            await metrics.emit(
                metric_type=metric_type,
                organization_id=organization_id,
                user_id=user_id,
                api_key_id=api_key_id,
                endpoint=path,
                method=request.method,
                status_code=500,
                response_time_ms=response_time_ms,
                metadata={k: v for k, v in metadata.items() if v},
            )
        except Exception as metric_exc:
            logger.debug(f"Failed to emit unhandled exception metric: {metric_exc}")

    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded from metrics."""
        if path in self.EXCLUDE_PATHS:
            return True
        for exclude_path in self.EXCLUDE_PATHS:
            if path.startswith(exclude_path + "/"):
                return True
        return False

    async def _read_response_body(self, response: Response) -> tuple[bytes, bool]:
        """Read response body bytes, including streaming responses."""
        body = getattr(response, "body", None)
        if body:
            return body, False

        body_iterator = getattr(response, "body_iterator", None)
        if body_iterator is None:
            return b"", False

        chunks: list[bytes] = []
        async for chunk in body_iterator:
            if isinstance(chunk, bytes):
                chunks.append(chunk)
            elif isinstance(chunk, bytearray):
                chunks.append(bytes(chunk))
            elif isinstance(chunk, memoryview):
                chunks.append(chunk.tobytes())
            else:
                chunks.append(str(chunk).encode("utf-8"))
        return b"".join(chunks), True

    def _extract_error_metadata(self, body: bytes) -> dict:
        """Extract structured error fields from JSON response payloads."""
        if not body:
            return {}

        try:
            payload = json.loads(body)
        except (TypeError, ValueError):
            return {}

        if not isinstance(payload, dict):
            return {}

        error = payload.get("error")
        if not isinstance(error, dict):
            return {}

        error_details = error.get("details")
        return {
            "error_code": error.get("code"),
            "error_message": error.get("message"),
            "error_details": error_details,
            "error_stack": error.get("stack") or error.get("traceback"),
        }

    def _get_metric_type(self, path: str, method: str) -> MetricType:
        """Determine metric type based on endpoint."""
        path_lower = path.lower()

        if "/sign" in path_lower:
            return MetricType.DOCUMENT_SIGNED
        elif "/verify" in path_lower:
            return MetricType.DOCUMENT_VERIFIED
        elif "/batch" in path_lower:
            return MetricType.BATCH_OPERATION
        elif "/streaming" in path_lower or "/stream" in path_lower:
            return MetricType.STREAMING_SESSION
        elif "/merkle" in path_lower:
            return MetricType.MERKLE_ENCODE
        elif "/lookup" in path_lower:
            return MetricType.LOOKUP
        elif "/rsl" in path_lower:
            return MetricType.RSL_FETCH
        elif "/robots" in path_lower:
            return MetricType.ROBOTS_TXT_FETCH
        elif "/rights" in path_lower:
            return MetricType.RIGHTS_RESOLUTION
        elif "/notices" in path_lower:
            return MetricType.NOTICE_DELIVERED
        elif "/licensing" in path_lower:
            return MetricType.LICENSING_REQUEST
        else:
            return MetricType.API_CALL
