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


def test_describe_activity_includes_error_metadata() -> None:
    metric = UsageMetric(
        id="metric_3",
        user_id="user_1",
        organization_id="org_1",
        metric_type="api_call",
        service_name="verification-service",
        endpoint="/api/v1/verify",
        count=1,
        value=None,
        response_time_ms=410,
        status_code=500,
        meta={
            "request_id": "req_123",
            "api_key_prefix": "ency_abc123",
            "error_code": "E_INTERNAL",
            "error_message": "Verification pipeline failed",
            "error_details": "Document parser timed out",
            "error_stack": "Traceback (most recent call last): ...",
        },
        date="2026-01-20",
        hour=12,
        created_at=datetime(2026, 1, 20, 12, 10, 0),
    )

    payload = AnalyticsService.describe_activity(metric)

    assert payload["type"] == "api_call"
    assert payload["metadata"]["request_id"] == "req_123"
    assert payload["metadata"]["api_key"] == "ency_abc123"
    assert payload["metadata"]["error_code"] == "E_INTERNAL"
    assert payload["metadata"]["error_message"] == "Verification pipeline failed"
    assert payload["metadata"]["error_details"] == "Document parser timed out"
    assert payload["metadata"]["error_stack"] == "Traceback (most recent call last): ..."


def test_describe_activity_exposes_unified_audit_contract_fields() -> None:
    metric = UsageMetric(
        id="metric_4",
        user_id="user_2",
        organization_id="org_2",
        metric_type="admin_action",
        service_name="auth-service",
        endpoint="/api/v1/team/members",
        count=1,
        value=None,
        response_time_ms=90,
        status_code=200,
        meta={
            "event_type": "member.invited",
            "actor_type": "user",
            "actor_id": "usr_admin_1",
            "resource_type": "member",
            "resource_id": "usr_invited_7",
            "api_key_prefix": "ency_admin_123",
        },
        date="2026-01-20",
        hour=12,
        created_at=datetime(2026, 1, 20, 12, 15, 0),
    )

    payload = AnalyticsService.describe_activity(metric)

    assert payload["metadata"]["event_type"] == "member.invited"
    assert payload["metadata"]["actor_type"] == "user"
    assert payload["metadata"]["actor_id"] == "usr_admin_1"
    assert payload["metadata"]["resource_type"] == "member"
    assert payload["metadata"]["resource_id"] == "usr_invited_7"
    assert payload["metadata"]["organization_id"] == "org_2"
    assert payload["metadata"]["severity"] == "medium"
