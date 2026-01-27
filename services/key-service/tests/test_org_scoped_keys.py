from datetime import datetime
from types import SimpleNamespace

import pytest


@pytest.fixture
def user_override(client):
    from app.api.v1 import endpoints

    client.app.dependency_overrides[endpoints.get_current_user] = lambda: {
        "id": "user_123",
        "is_super_admin": False,
    }
    yield
    client.app.dependency_overrides.pop(endpoints.get_current_user, None)


def _mock_key(organization_id: str):
    return SimpleNamespace(
        id="key_123",
        name="Org Key",
        key_prefix="ency_abc...",
        fingerprint="fp_123",
        permissions=["sign", "verify"],
        is_active=True,
        is_revoked=False,
        last_used_at=None,
        usage_count=0,
        created_at=datetime.utcnow(),
        expires_at=None,
        description=None,
        organization_id=organization_id,
    )


def test_list_keys_requires_org_role(client, monkeypatch, user_override):
    from app.api.v1 import endpoints

    async def fake_fetch_org_role(authorization: str, org_id: str, user_id: str):
        return "member"

    monkeypatch.setattr(endpoints, "_fetch_org_role", fake_fetch_org_role)

    response = client.get(
        "/api/v1/keys",
        params={"organization_id": "org_123"},
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 403


def test_list_keys_returns_org_keys(client, monkeypatch, user_override):
    from app.api.v1 import endpoints

    async def fake_fetch_org_role(authorization: str, org_id: str, user_id: str):
        return "admin"

    def fake_get_org_keys(db, organization_id: str, include_revoked: bool = False):
        return [_mock_key(organization_id)]

    monkeypatch.setattr(endpoints, "_fetch_org_role", fake_fetch_org_role)
    monkeypatch.setattr(endpoints.KeyService, "get_org_keys", fake_get_org_keys)

    response = client.get(
        "/api/v1/keys",
        params={"organization_id": "org_123"},
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["organization_id"] == "org_123"


def test_generate_key_with_org_enforces_permission(client, monkeypatch, user_override):
    from app.api.v1 import endpoints

    async def fake_fetch_org_role(authorization: str, org_id: str, user_id: str):
        return "viewer"

    monkeypatch.setattr(endpoints, "_fetch_org_role", fake_fetch_org_role)

    response = client.post(
        "/api/v1/keys/generate",
        json={"name": "Org Key", "organization_id": "org_123"},
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 403


def test_generate_key_with_org_calls_service(client, monkeypatch, user_override):
    from app.api.v1 import endpoints

    async def fake_fetch_org_role(authorization: str, org_id: str, user_id: str):
        return "owner"

    captured = {}

    def fake_create_key(db, user_id: str, key_data, organization_id: str = None, authorization: str = None):
        captured["organization_id"] = organization_id
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

    monkeypatch.setattr(endpoints, "_fetch_org_role", fake_fetch_org_role)
    monkeypatch.setattr(endpoints.KeyService, "create_key", fake_create_key)

    response = client.post(
        "/api/v1/keys/generate",
        json={"name": "Org Key", "organization_id": "org_123"},
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert captured["organization_id"] == "org_123"
    assert payload["organization_id"] == "org_123"


def test_revoke_keys_by_user_calls_service(client, monkeypatch, user_override):
    from app.api.v1 import endpoints

    async def fake_fetch_org_role(authorization: str, org_id: str, user_id: str):
        return "manager"

    captured = {}

    def fake_revoke_keys_by_user(db, organization_id: str, target_user_id: str, actor_user_id: str):
        captured["organization_id"] = organization_id
        captured["target_user_id"] = target_user_id
        captured["actor_user_id"] = actor_user_id
        return 3

    monkeypatch.setattr(endpoints, "_fetch_org_role", fake_fetch_org_role)
    monkeypatch.setattr(endpoints.KeyService, "revoke_keys_by_user", fake_revoke_keys_by_user)

    response = client.post(
        "/api/v1/keys/revoke-by-user",
        json={"organization_id": "org_123", "user_id": "user_999"},
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["revoked_count"] == 3
    assert captured["organization_id"] == "org_123"
    assert captured["target_user_id"] == "user_999"
    assert captured["actor_user_id"] == "user_123"
