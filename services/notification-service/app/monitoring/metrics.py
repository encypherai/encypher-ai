"""
Prometheus metrics for Notification Service.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""

from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info("notification-service", "Notification Service information")
service_info.info({"version": "1.0.0", "service": "notification-service", "port": "8008"})

# Business metrics
notifications_sent_total = Counter("notifications_sent_total", "Total notifications sent", ["channel", "status"])

emails_sent_total = Counter("emails_sent_total", "Total emails sent", ["status"])

sms_sent_total = Counter("sms_sent_total", "Total SMS sent", ["status"])

webhooks_delivered_total = Counter("webhooks_delivered_total", "Total webhooks delivered", ["status"])

notification_queue_size = Gauge("notification_queue_size", "Size of notification queue")

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
