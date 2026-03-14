"""
Prometheus metrics for User Service.

HTTP request metrics are auto-instrumented by prometheus-fastapi-instrumentator.
Additional business metrics should be added here and wired in when needed.
"""

from prometheus_fastapi_instrumentator import Instrumentator


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

    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)

    return instrumentator
