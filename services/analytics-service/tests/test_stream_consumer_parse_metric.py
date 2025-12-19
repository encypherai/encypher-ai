import sys
from pathlib import Path


def _import_stream_consumer():
    service_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(service_root))

    # The monorepo contains multiple top-level "app" packages across services.
    # Ensure we import analytics-service's "app" package by clearing any
    # previously-imported "app" modules.
    for mod_name in list(sys.modules.keys()):
        if mod_name == "app" or mod_name.startswith("app."):
            sys.modules.pop(mod_name, None)

    from app.services.stream_consumer import StreamConsumer as _StreamConsumer

    return _StreamConsumer


StreamConsumer = _import_stream_consumer()


def test_parse_metric_accepts_float_string_response_time_ms() -> None:
    consumer = StreamConsumer(redis_url="redis://example")

    metric = consumer._parse_metric(
        {
            "metric_type": "api_call",
            "organization_id": "org_demo",
            "response_time_ms": "345.9395617246628",
            "status_code": "200",
            "timestamp": "2025-12-19T17:05:35.947Z",
        }
    )

    assert metric is not None
    assert metric.response_time_ms == 346
    assert metric.status_code == 200


def test_parse_metric_accepts_float_response_time_ms() -> None:
    consumer = StreamConsumer(redis_url="redis://example")

    metric = consumer._parse_metric(
        {
            "metric_type": "api_call",
            "organization_id": "org_demo",
            "response_time_ms": 3.9123892784118652,
            "status_code": 201,
        }
    )

    assert metric is not None
    assert metric.response_time_ms == 4
    assert metric.status_code == 201


def test_parse_metric_invalid_response_time_is_none_not_error() -> None:
    consumer = StreamConsumer(redis_url="redis://example")

    metric = consumer._parse_metric(
        {
            "metric_type": "api_call",
            "organization_id": "org_demo",
            "response_time_ms": "not-a-number",
            "status_code": "200",
        }
    )

    assert metric is not None
    assert metric.response_time_ms is None
    assert metric.status_code == 200
