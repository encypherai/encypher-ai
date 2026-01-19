"""
Metrics module for Encypher Commercial services.

Provides async, non-blocking metrics collection using Redis Streams.
"""

from .client import MetricsClient, MetricEvent, MetricType
from .middleware import MetricsMiddleware

__all__ = [
    "MetricsClient",
    "MetricEvent",
    "MetricType",
    "MetricsMiddleware",
]
