"""OpenTelemetry distributed tracing setup.

Tracing is opt-in: configure OTEL_EXPORTER_OTLP_ENDPOINT (e.g.
"http://otel-collector:4318") to enable. Omitting the env var is a
safe no-op -- all spans are created but immediately discarded.

FastAPI and httpx are auto-instrumented when tracing is enabled.
The service name reported to the collector is "enterprise-api" unless
overridden via the standard OTEL_SERVICE_NAME env var.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_tracer_provider = None


def setup_tracing(app=None) -> None:
    """Configure OpenTelemetry tracing.

    Safe to call unconditionally at startup. When OTEL_EXPORTER_OTLP_ENDPOINT
    is not set, a NoOpTracerProvider is used so no overhead is incurred.

    Args:
        app: FastAPI application instance for auto-instrumentation. Pass None
             to skip FastAPI instrumentation (useful in tests).
    """
    global _tracer_provider

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    otlp_endpoint: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip() or None
    service_name = os.getenv("OTEL_SERVICE_NAME", "enterprise-api")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("OpenTelemetry tracing enabled: exporting to %s (service=%s)", otlp_endpoint, service_name)
        except Exception as exc:
            logger.warning("Failed to configure OTLP exporter: %s -- tracing disabled", exc)
    else:
        logger.info("OpenTelemetry tracing: OTEL_EXPORTER_OTLP_ENDPOINT not set, spans discarded (no-op)")

    trace.set_tracer_provider(provider)
    _tracer_provider = provider

    # Auto-instrument FastAPI
    if app is not None:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI auto-instrumented for tracing")
        except Exception as exc:
            logger.warning("FastAPI OTEL instrumentation failed: %s", exc)

    # Auto-instrument httpx (client-side spans for outbound calls)
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
        logger.info("httpx auto-instrumented for tracing")
    except Exception as exc:
        logger.warning("httpx OTEL instrumentation failed: %s", exc)


def shutdown_tracing() -> None:
    """Flush and shut down the tracer provider gracefully."""
    global _tracer_provider
    if _tracer_provider is not None:
        try:
            _tracer_provider.shutdown()
        except Exception as exc:
            logger.warning("Error shutting down tracer provider: %s", exc)
        finally:
            _tracer_provider = None
