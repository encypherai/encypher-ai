"""
Prometheus metrics for Auth Service.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info('auth_service', 'Auth Service information')
service_info.info({
    'version': '1.0.0',
    'service': 'auth-service',
    'port': '8001'
})

# Request metrics (automatically collected by instrumentator)
# - http_requests_total
# - http_request_duration_seconds
# - http_requests_inprogress

# Business metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']  # method: password, oauth, refresh; status: success, failure
)

user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['method']  # method: email, oauth
)

token_operations_total = Counter(
    'token_operations_total',
    'Total token operations',
    ['operation', 'status']  # operation: generate, refresh, revoke; status: success, failure
)

oauth_operations_total = Counter(
    'oauth_operations_total',
    'Total OAuth operations',
    ['provider', 'operation', 'status']  # provider: google, github; operation: login, callback
)

# System metrics
active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

# Performance metrics
auth_operation_duration = Histogram(
    'auth_operation_duration_seconds',
    'Duration of authentication operations',
    ['operation'],  # operation: login, signup, refresh, logout
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Duration of database queries',
    ['query_type'],  # query_type: select, insert, update, delete
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
        should_respect_env_var=False,
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


# Helper functions for recording metrics
def record_auth_attempt(method: str, success: bool):
    """Record an authentication attempt."""
    status = "success" if success else "failure"
    auth_attempts_total.labels(method=method, status=status).inc()


def record_user_registration(method: str):
    """Record a user registration."""
    user_registrations_total.labels(method=method).inc()


def record_token_operation(operation: str, success: bool):
    """Record a token operation."""
    status = "success" if success else "failure"
    token_operations_total.labels(operation=operation, status=status).inc()


def record_oauth_operation(provider: str, operation: str, success: bool):
    """Record an OAuth operation."""
    status = "success" if success else "failure"
    oauth_operations_total.labels(provider=provider, operation=operation, status=status).inc()
