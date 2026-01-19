"""
Prometheus metrics for User Service.

This module provides comprehensive metrics collection for monitoring
service health, performance, and business operations.
"""

from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator

# Service information
service_info = Info("user_service", "User Service information")
service_info.info({"version": "1.0.0", "service": "user-service", "port": "8002"})

# Business metrics
user_operations_total = Counter(
    "user_operations_total",
    "Total user operations",
    ["operation", "status"],  # operation: create, update, delete, get; status: success, failure
)

profile_updates_total = Counter(
    "profile_updates_total",
    "Total profile updates",
    ["field"],  # field: name, email, avatar, preferences
)

team_operations_total = Counter(
    "team_operations_total",
    "Total team operations",
    ["operation", "status"],  # operation: create, add_member, remove_member, delete
)

organization_operations_total = Counter(
    "organization_operations_total",
    "Total organization operations",
    ["operation", "status"],  # operation: create, update, delete, add_member
)

# System metrics
active_users = Gauge("active_users", "Number of active users")

total_teams = Gauge("total_teams", "Total number of teams")

total_organizations = Gauge("total_organizations", "Total number of organizations")

database_connections = Gauge("database_connections_active", "Number of active database connections")

# Performance metrics
user_operation_duration = Histogram(
    "user_operation_duration_seconds",
    "Duration of user operations",
    ["operation"],  # operation: create_user, update_profile, get_user
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
)

database_query_duration = Histogram(
    "database_query_duration_seconds",
    "Duration of database queries",
    ["query_type"],  # query_type: select, insert, update, delete
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
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


# Helper functions for recording metrics
def record_user_operation(operation: str, success: bool):
    """Record a user operation."""
    status = "success" if success else "failure"
    user_operations_total.labels(operation=operation, status=status).inc()


def record_profile_update(field: str):
    """Record a profile update."""
    profile_updates_total.labels(field=field).inc()


def record_team_operation(operation: str, success: bool):
    """Record a team operation."""
    status = "success" if success else "failure"
    team_operations_total.labels(operation=operation, status=status).inc()


def record_organization_operation(operation: str, success: bool):
    """Record an organization operation."""
    status = "success" if success else "failure"
    organization_operations_total.labels(operation=operation, status=status).inc()
