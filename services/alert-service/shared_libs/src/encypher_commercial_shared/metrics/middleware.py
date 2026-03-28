"""
FastAPI Middleware for automatic metrics collection.

This middleware automatically records API call metrics for all requests,
extracting organization and user information from the request context.

Usage:
    from fastapi import FastAPI
    from encypher_commercial_shared.metrics import MetricsMiddleware, MetricsClient

    app = FastAPI()
    metrics_client = MetricsClient(redis_url="redis://localhost:6379/0")

    app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)
"""

import logging
import time
from typing import Callable, Optional, Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .client import MetricsClient, MetricType

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic API metrics collection.

    Records timing, status codes, and request metadata for all API calls.
    Extracts organization/user info from request state or headers.
    """

    # Paths to exclude from metrics (health checks, static files, etc.)
    DEFAULT_EXCLUDE_PATHS: Set[str] = {
        "/health",
        "/readyz",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    }

    def __init__(
        self,
        app,
        metrics_client: MetricsClient,
        exclude_paths: Optional[Set[str]] = None,
        include_request_size: bool = True,
        include_response_size: bool = False,  # Can be expensive
    ):
        """
        Initialize metrics middleware.

        Args:
            app: FastAPI application
            metrics_client: Metrics client instance
            exclude_paths: Paths to exclude from metrics
            include_request_size: Whether to measure request body size
            include_response_size: Whether to measure response body size
        """
        super().__init__(app)
        self.metrics_client = metrics_client
        self.exclude_paths = exclude_paths or self.DEFAULT_EXCLUDE_PATHS
        self.include_request_size = include_request_size
        self.include_response_size = include_response_size

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and record metrics."""
        path = request.url.path

        # Skip excluded paths
        if self._should_exclude(path):
            return await call_next(request)

        # Record start time
        start_time = time.perf_counter()

        # Get request size if enabled
        request_size = None
        if self.include_request_size:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    request_size = int(content_length)
                except ValueError:
                    pass

        # Process request
        response = await call_next(request)

        # Calculate response time
        response_time_ms = (time.perf_counter() - start_time) * 1000

        # Get response size if enabled
        response_size = None
        if self.include_response_size:
            content_length = response.headers.get("content-length")
            if content_length:
                try:
                    response_size = int(content_length)
                except ValueError:
                    pass

        # Extract organization and user info from request state
        # These are typically set by auth middleware
        organization_id = getattr(request.state, "organization_id", None)
        user_id = getattr(request.state, "user_id", None)
        api_key_id = getattr(request.state, "api_key_id", None)

        # Fallback: try to get from request headers or path
        if not organization_id:
            organization_id = self._extract_org_from_request(request)

        # Only record metrics if we have an organization
        if organization_id:
            # Determine metric type based on endpoint
            metric_type = self._get_metric_type(path, request.method)

            # Emit metric (non-blocking)
            await self.metrics_client.emit(
                metric_type=metric_type,
                organization_id=organization_id,
                user_id=user_id,
                api_key_id=api_key_id,
                endpoint=path,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                request_size_bytes=request_size,
                response_size_bytes=response_size,
            )

        return response

    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded from metrics."""
        # Exact match
        if path in self.exclude_paths:
            return True

        # Prefix match for paths like /docs/*
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True

        return False

    def _extract_org_from_request(self, request: Request) -> Optional[str]:
        """Try to extract organization ID from request."""
        # Check for organization in path (e.g., /api/v1/org/{org_id}/...)
        # This is a fallback - prefer setting request.state.organization_id

        # Check authorization header for API key format
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # If it looks like an API key (starts with ek_), we'll get org from auth
            if token.startswith("ek_"):
                # The auth middleware should have set this
                return None

        return None

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
        else:
            return MetricType.API_CALL
