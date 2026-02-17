from datetime import datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _import_from_service():
    service_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(service_root))

    for mod_name in list(sys.modules.keys()):
        if mod_name == "app" or mod_name.startswith("app."):
            sys.modules.pop(mod_name, None)

    from app.db.models import Base, UsageMetric
    from app.services.analytics_service import AnalyticsService

    return Base, UsageMetric, AnalyticsService


Base, UsageMetric, AnalyticsService = _import_from_service()


def _db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_get_activity_events_applies_metadata_filters_and_pagination() -> None:
    db = _db_session()
    now = datetime.utcnow()

    rows = [
        UsageMetric(
            id="m_1",
            user_id="org_1",
            organization_id="org_1",
            metric_type="document_verified",
            service_name="enterprise-api",
            endpoint="/api/v1/verify",
            count=1,
            response_time_ms=140,
            status_code=500,
            meta={
                "request_id": "req_keep",
                "api_key_prefix": "ency_keep",
                "error_code": "E_VERIFY",
                "event_type": "verify.failed",
                "actor_id": "user_1",
            },
            date=now.strftime("%Y-%m-%d"),
            hour=now.hour,
            created_at=now,
        ),
        UsageMetric(
            id="m_2",
            user_id="org_1",
            organization_id="org_1",
            metric_type="document_signed",
            service_name="enterprise-api",
            endpoint="/api/v1/sign",
            count=1,
            response_time_ms=90,
            status_code=201,
            meta={
                "request_id": "req_other",
                "api_key_prefix": "ency_other",
                "event_type": "sign.success",
                "actor_id": "user_2",
            },
            date=now.strftime("%Y-%m-%d"),
            hour=now.hour,
            created_at=now - timedelta(minutes=1),
        ),
    ]

    db.add_all(rows)
    db.commit()

    result = AnalyticsService.get_activity_events(
        db=db,
        user_id="org_1",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(minutes=1),
        page=1,
        limit=10,
        api_key_prefix="ency_keep",
        status="failure",
        error_code="E_VERIFY",
        request_id="req_keep",
        endpoint="/api/v1/verify",
        event_type="verify.failed",
        actor_id="user_1",
    )

    assert result["total"] == 1
    assert result["page"] == 1
    assert result["limit"] == 10
    assert len(result["items"]) == 1
    assert result["items"][0].id == "m_1"

    db.close()


def test_get_activity_events_paginates_results() -> None:
    db = _db_session()
    now = datetime.utcnow()

    for idx in range(3):
        db.add(
            UsageMetric(
                id=f"m_{idx}",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/verify",
                count=1,
                response_time_ms=80,
                status_code=200,
                meta={"api_key_prefix": "ency_same"},
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now - timedelta(minutes=idx),
            )
        )
    db.commit()

    page_1 = AnalyticsService.get_activity_events(
        db=db,
        user_id="org_1",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(minutes=1),
        page=1,
        limit=2,
    )
    page_2 = AnalyticsService.get_activity_events(
        db=db,
        user_id="org_1",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(minutes=1),
        page=2,
        limit=2,
    )

    assert page_1["total"] == 3
    assert len(page_1["items"]) == 2
    assert page_2["total"] == 3
    assert len(page_2["items"]) == 1

    db.close()


def test_get_activity_export_rows_include_unified_fields() -> None:
    db = _db_session()
    now = datetime.utcnow()

    db.add(
        UsageMetric(
            id="m_export",
            user_id="org_1",
            organization_id="org_1",
            metric_type="api_call",
            service_name="enterprise-api",
            endpoint="/api/v1/verify",
            count=1,
            response_time_ms=120,
            status_code=500,
            meta={
                "request_id": "req_export",
                "api_key_prefix": "ency_export",
                "error_code": "E_VERIFY",
                "event_type": "verify.failed",
                "actor_type": "api_key",
                "actor_id": "key_123",
                "resource_type": "document",
                "resource_id": "doc_1",
            },
            date=now.strftime("%Y-%m-%d"),
            hour=now.hour,
            created_at=now,
        )
    )
    db.commit()

    rows = AnalyticsService.get_activity_export_rows(
        db=db,
        user_id="org_1",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
        status="failure",
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["request_id"] == "req_export"
    assert row["api_key"] == "ency_export"
    assert row["error_code"] == "E_VERIFY"
    assert row["event_type"] == "verify.failed"
    assert row["actor_type"] == "api_key"
    assert row["actor_id"] == "key_123"
    assert row["resource_type"] == "document"
    assert row["resource_id"] == "doc_1"
    assert row["severity"] == "critical"

    db.close()


def test_get_activity_alert_summary_aggregates_failures_and_error_codes() -> None:
    db = _db_session()
    now = datetime.utcnow()

    db.add_all(
        [
            UsageMetric(
                id="m_alert_1",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/verify",
                count=1,
                response_time_ms=120,
                status_code=500,
                meta={"error_code": "E_VERIFY"},
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now,
            ),
            UsageMetric(
                id="m_alert_2",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/sign",
                count=1,
                response_time_ms=130,
                status_code=500,
                meta={"error_code": "E_VERIFY"},
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now,
            ),
            UsageMetric(
                id="m_alert_3",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/sign",
                count=1,
                response_time_ms=110,
                status_code=401,
                meta={"error_code": "E_AUTH"},
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now,
            ),
            UsageMetric(
                id="m_alert_ok",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/sign",
                count=1,
                response_time_ms=90,
                status_code=200,
                meta={},
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now,
            ),
        ]
    )
    db.commit()

    summary = AnalyticsService.get_activity_alert_summary(
        db=db,
        user_id="org_1",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
    )

    assert summary["total_requests"] == 4
    assert summary["failure_requests"] == 3
    assert summary["critical_failures"] == 2
    assert summary["failure_rate"] == 75.0
    assert summary["top_error_codes"][0]["error_code"] == "E_VERIFY"
    assert summary["top_error_codes"][0]["count"] == 2

    db.close()


def test_get_activity_events_supports_search_multiselect_and_stack_filters() -> None:
    db = _db_session()
    now = datetime.utcnow()

    db.add_all(
        [
            UsageMetric(
                id="m_adv_1",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/verify",
                count=1,
                response_time_ms=120,
                status_code=500,
                meta={
                    "request_id": "req_critical",
                    "api_key_prefix": "ency_crit",
                    "error_code": "E_VERIFY",
                    "error_message": "traceable verification failure",
                    "error_stack": "Traceback: verify failed",
                    "event_type": "verify.failed",
                    "actor_id": "actor_1",
                },
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now,
            ),
            UsageMetric(
                id="m_adv_2",
                user_id="org_1",
                organization_id="org_1",
                metric_type="admin_action",
                service_name="dashboard",
                endpoint="/api/v1/admin/audit",
                count=1,
                response_time_ms=95,
                status_code=200,
                meta={
                    "request_id": "req_medium",
                    "event_type": "admin.action",
                    "actor_id": "actor_2",
                },
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now - timedelta(minutes=2),
            ),
            UsageMetric(
                id="m_adv_3",
                user_id="org_1",
                organization_id="org_1",
                metric_type="api_call",
                service_name="enterprise-api",
                endpoint="/api/v1/sign",
                count=1,
                response_time_ms=85,
                status_code=200,
                meta={
                    "request_id": "req_low",
                    "event_type": "sign.success",
                    "actor_id": "actor_3",
                },
                date=now.strftime("%Y-%m-%d"),
                hour=now.hour,
                created_at=now - timedelta(minutes=3),
            ),
        ]
    )
    db.commit()

    result = AnalyticsService.get_activity_events(
        db=db,
        user_id="org_1",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(minutes=1),
        page=1,
        limit=25,
        query="traceable",
        event_types=["verify.failed", "admin.action"],
        severities=["critical"],
        has_stack=True,
    )

    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0].id == "m_adv_1"

    db.close()
