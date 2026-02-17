import json

from app.services.metrics_service import MetricEvent, MetricType


def test_metric_event_to_dict_serializes_metadata_as_json_string() -> None:
    event = MetricEvent(
        metric_type=MetricType.API_CALL,
        organization_id="org_demo",
        endpoint="/api/v1/sign",
        method="POST",
        status_code=500,
        metadata={
            "request_id": "req_123",
            "api_key_prefix": "ency_abc123",
            "error_code": "E_INTERNAL",
            "error_message": "Signing failed",
        },
    )

    payload = event.to_dict()

    assert isinstance(payload.get("metadata"), str)
    parsed = json.loads(payload["metadata"])
    assert parsed["request_id"] == "req_123"
    assert parsed["api_key_prefix"] == "ency_abc123"
    assert parsed["error_code"] == "E_INTERNAL"
    assert parsed["error_message"] == "Signing failed"
