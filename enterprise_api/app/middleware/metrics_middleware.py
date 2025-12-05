"""
Metrics Middleware for Enterprise API.

Automatically records API call metrics for all requests.
Non-blocking - metrics are buffered and flushed asynchronously.
"""
import logging
import time
from typing import Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.services.metrics_service import get_metrics_service, MetricType

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
            return await call_next(request)
        
        # Record start time
        start_time = time.perf_counter()
        
        # Process request
        response = await call_next(request)
        
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
                )
            except Exception as e:
                # Never let metrics collection break the request
                logger.debug(f"Failed to emit metric: {e}")
        
        return response
    
    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded from metrics."""
        if path in self.EXCLUDE_PATHS:
            return True
        for exclude_path in self.EXCLUDE_PATHS:
            if path.startswith(exclude_path + "/"):
                return True
        return False
    
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
