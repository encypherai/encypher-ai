"""Prometheus metrics setup."""

from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app):
    Instrumentator(
        excluded_handlers=["/health", "/metrics", "/readyz"],
        should_instrument_requests_inprogress=True,
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
