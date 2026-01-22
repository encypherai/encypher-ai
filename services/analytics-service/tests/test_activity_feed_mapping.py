from datetime import datetime
import sys
from pathlib import Path


def _import_from_service():
    service_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(service_root))

    for mod_name in list(sys.modules.keys()):
        if mod_name == "app" or mod_name.startswith("app."):
            sys.modules.pop(mod_name, None)

    from app.db.models import UsageMetric
    from app.services.analytics_service import AnalyticsService

    return UsageMetric, AnalyticsService


UsageMetric, AnalyticsService = _import_from_service()


def test_describe_activity_maps_signing_metric() -> None:
    metric = UsageMetric(
        id="metric_1",
        user_id="user_1",
        organization_id="org_1",
        metric_type="document_signed",
        service_name="verification-service",
        endpoint="/api/v1/sign",
        count=1,
        value=None,
        response_time_ms=123,
        status_code=201,
        meta={"api_key_prefix": "key_123"},
        date="2026-01-20",
        hour=12,
        created_at=datetime(2026, 1, 20, 12, 0, 0),
    )

    payload = AnalyticsService.describe_activity(metric)

    assert payload["type"] == "sign"
    assert payload["description"] == "Signing request completed"
    assert payload["metadata"]["status"] == 201
    assert payload["metadata"]["api_key"] == "key_123"


def test_describe_activity_maps_failed_status() -> None:
    metric = UsageMetric(
        id="metric_2",
        user_id="user_1",
        organization_id="org_1",
        metric_type="api_call",
        service_name="verification-service",
        endpoint="/api/v1/verify",
        count=1,
        value=None,
        response_time_ms=221,
        status_code=500,
        meta={},
        date="2026-01-20",
        hour=12,
        created_at=datetime(2026, 1, 20, 12, 5, 0),
    )

    payload = AnalyticsService.describe_activity(metric)

    assert payload["type"] == "api_call"
    assert payload["description"] == "Request failed with status 500"
