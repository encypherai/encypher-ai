from datetime import datetime
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import endpoints
from app.api.v1.endpoints import router, get_current_user
from app.db.session import get_db
from encypher_commercial_shared.metrics import MetricsMiddleware


class DummyMetricsClient:
    def __init__(self) -> None:
        self.events = []

    async def emit(self, metric_type, organization_id, **kwargs):
        self.events.append({
            "metric_type": metric_type,
            "organization_id": organization_id,
            **kwargs,
        })
        return True


def _build_app(metrics_client: DummyMetricsClient) -> TestClient:
    app = FastAPI()
    app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)
    app.include_router(router, prefix="/api/v1/keys")
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "user_123",
        "is_super_admin": True,
    }
    return TestClient(app)


def test_generate_key_emits_metrics(monkeypatch):
    metrics_client = DummyMetricsClient()
    client = _build_app(metrics_client)

    def fake_create_key(_db, user_id, key_data, organization_id=None, authorization=None):
        db_key = SimpleNamespace(
            id="key_123",
            name=key_data.name,
            fingerprint="fp_123",
            permissions=key_data.permissions,
            created_at=datetime.utcnow(),
            organization_id=organization_id,
            user_id=user_id,
            created_by=user_id,
        )
        return db_key, "ency_test"

    monkeypatch.setattr(endpoints.KeyService, "create_key", fake_create_key)

    response = client.post(
        "/api/v1/keys/generate",
        json={"name": "Org Key", "organization_id": "org_123"},
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 201
    assert metrics_client.events
    event = metrics_client.events[0]
    assert event["organization_id"] == "org_123"
    assert event["api_key_id"] == "key_123"


def test_validate_key_emits_metrics(monkeypatch):
    metrics_client = DummyMetricsClient()
    client = _build_app(metrics_client)

    def fake_verify_key_with_org(_db, _api_key):
        return {
            "key_id": "key_456",
            "organization_id": "org_456",
            "user_id": "user_456",
            "permissions": ["verify"],
            "features": {},
            "tier": "starter",
            "monthly_api_limit": 1000,
            "monthly_api_usage": 0,
            "organization_name": "Org",
            "coalition_member": False,
            "coalition_rev_share": 0,
            "certificate_pem": None,
        }

    monkeypatch.setattr(endpoints.KeyService, "verify_key_with_org", fake_verify_key_with_org)

    response = client.post(
        "/api/v1/keys/validate",
        json={"key": "ency_test"},
    )

    assert response.status_code == 200
    assert metrics_client.events
    event = metrics_client.events[0]
    assert event["organization_id"] == "org_456"
    assert event["api_key_id"] == "key_456"
