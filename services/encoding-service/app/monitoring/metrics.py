"""
Prometheus metrics for Encoding Service.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info('encoding-service', 'Encoding Service information')
service_info.info({
    'version': '1.0.0',
    'service': 'encoding-service',
    'port': '8004'
})

# Business metrics
documents_signed_total = Counter(
    'documents_signed_total',
    'Total documents signed',
    ['status']
)

signing_operations_total = Counter(
    'signing_operations_total',
    'Total signing operations',
    ['operation', 'status']
)

metadata_embedded_total = Counter(
    'metadata_embedded_total',
    'Total metadata embeddings',
    ['status']
)

active_signing_operations = Gauge(
    'active_signing_operations',
    'Number of active signing operations'
)

# System metrics
database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

# Performance metrics
operation_duration = Histogram(
    'operation_duration_seconds',
    'Duration of operations',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Duration of database queries',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
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
