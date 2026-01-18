"""
Prometheus metrics for Key Service.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info("key-service", "Key Service information")
service_info.info({"version": "1.0.0", "service": "key-service", "port": "8003"})

# Business metrics
api_key_operations_total = Counter("api_key_operations_total", "Total API key operations", ["operation", "status"])

key_rotations_total = Counter("key_rotations_total", "Total key rotations", ["status"])

key_validations_total = Counter("key_validations_total", "Total key validations", ["result"])

active_api_keys = Gauge("active_api_keys", "Number of active API keys")

# System metrics
database_connections = Gauge("database_connections_active", "Number of active database connections")

# Performance metrics
operation_duration = Histogram("operation_duration_seconds", "Duration of operations", ["operation"], buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0])

database_query_duration = Histogram(
    "database_query_duration_seconds", "Duration of database queries", ["query_type"], buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)


def setup_metrics(app):
    """
    Set up Prometheus metrics for the FastAPI application.

    Args:
        app: FastAPI application instance

    Returns:
        Instrumentator instance
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # Instrument the app
    instrumentator.instrument(app)

    # Expose metrics endpoint
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)

    return instrumentator
