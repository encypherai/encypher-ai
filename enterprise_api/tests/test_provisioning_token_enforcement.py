import types
from datetime import datetime, timezone

import pytest

from app.config import settings


@pytest.mark.asyncio
async def test_provisioning_auto_provision_requires_token_in_production(
    async_client,
    monkeypatch,
):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "provisioning_token", "token-test-123", raising=False)

    response = await async_client.post(
        "/api/v1/provisioning/auto-provision",
        json={
            "email": "provisioning-test@example.com",
            "organization_name": "Provisioning Test",
            "source": "sdk",
            "source_metadata": {"test": True},
            "tier": "free",
            "auto_activate": True,
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_provisioning_auto_provision_accepts_valid_token_in_production(
    async_client,
    monkeypatch,
):
    from app.api.v1.endpoints import provisioning as provisioning_endpoints

    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "provisioning_token", "token-test-123", raising=False)

    async def fake_auto_provision(*, db, email, organization_name, source, source_metadata, tier, auto_activate):
        _ = db
        _ = email
        _ = source
        _ = tier
        _ = auto_activate
        _ = source_metadata
        return (
            types.SimpleNamespace(
                organization_id="org_provisioned",
                name=organization_name or "Provisioned",
                tier=tier,
                created_at=datetime.now(timezone.utc),
            ),
            "ency_live_fake_key_123",
            "user_provisioned",
        )

    monkeypatch.setattr(provisioning_endpoints.ProvisioningService, "auto_provision", fake_auto_provision)

    response = await async_client.post(
        "/api/v1/provisioning/auto-provision",
        headers={"X-Provisioning-Token": "token-test-123"},
        json={
            "email": "provisioning-test@example.com",
            "organization_name": "Provisioning Test",
            "source": "sdk",
            "source_metadata": {"test": True},
            "tier": "free",
            "auto_activate": True,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload.get("success") is True
    assert payload.get("organization_id") == "org_provisioned"
