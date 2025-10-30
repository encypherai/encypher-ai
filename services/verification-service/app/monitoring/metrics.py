"""
Prometheus metrics for Verification Service.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info('verification-service', 'Verification Service information')
service_info.info({
    'version': '1.0.0',
    'service': 'verification-service',
    'port': '8005'
})

# Business metrics
verifications_total = Counter(
    'verifications_total',
    'Total verifications',
    ['result']
)

signature_validations_total = Counter(
    'signature_validations_total',
    'Total signature validations',
    ['result']
)

tampering_detected_total = Counter(
    'tampering_detected_total',
    'Total tampering detections'
)

verification_cache_hits = Counter(
    'verification_cache_hits',
    'Verification cache hits'
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
