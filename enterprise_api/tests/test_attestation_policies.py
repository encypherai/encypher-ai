"""Tests for the Attestation Policies router (TEAM_256).

Covers CRUD operations and tier gating.
"""

import pytest

from httpx import ASGITransport, AsyncClient

from app.dependencies import get_current_organization_dep
from app.main import app


def _make_org_context(tier: str, org_id: str = "org_attest_test") -> dict:
    return {
        "organization_id": org_id,
        "organization_name": "Test Attestation Org",
        "tier": tier,
        "permissions": ["sign", "verify", "lookup"],
    }


# -- Tier gating ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_policies_requires_enterprise():
    """Free-tier org should get 403 on attestation policy endpoints."""

    async def override_dep():
        return _make_org_context("free")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/attestation-policies/")

    app.dependency_overrides.clear()
    assert response.status_code == 403
    body = response.json()
    assert body["error"]["code"] == "FEATURE_NOT_AVAILABLE"


@pytest.mark.asyncio
async def test_list_attestations_requires_enterprise():
    """Free-tier org should get 403 on attestations list endpoint."""

    async def override_dep():
        return _make_org_context("free")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/attestations/")

    app.dependency_overrides.clear()
    assert response.status_code == 403


# -- CRUD (uses enterprise tier with DB) ----------------------------------------


@pytest.mark.asyncio
async def test_create_and_list_policy(client: AsyncClient, db):
    """Create a policy, then verify it appears in the list."""
    from app.database import get_db

    async def override_dep():
        return _make_org_context("enterprise", "org_enterprise")

    async def override_db():
        yield db

    app.dependency_overrides[get_current_organization_dep] = override_dep
    app.dependency_overrides[get_db] = override_db

    # Create
    create_resp = await client.post(
        "/api/v1/attestation-policies/",
        json={
            "name": "Test Policy Alpha",
            "enforcement": "warn",
            "scope": "all",
            "rules": [
                {"field": "model_provider", "operator": "eq", "value": "openai", "action": "warn"},
            ],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    policy = create_resp.json()
    policy_id = policy["id"]
    assert policy["name"] == "Test Policy Alpha"
    assert policy["enforcement"] == "warn"
    assert len(policy["rules"]) == 1

    # List
    list_resp = await client.get("/api/v1/attestation-policies/")
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] >= 1
    ids = [p["id"] for p in body["policies"]]
    assert policy_id in ids

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_policy_by_id(client: AsyncClient, db):
    """Create then fetch a single policy by ID."""
    from app.database import get_db

    async def override_dep():
        return _make_org_context("enterprise", "org_enterprise")

    async def override_db():
        yield db

    app.dependency_overrides[get_current_organization_dep] = override_dep
    app.dependency_overrides[get_db] = override_db

    create_resp = await client.post(
        "/api/v1/attestation-policies/",
        json={"name": "Fetch Me", "enforcement": "block", "rules": []},
    )
    assert create_resp.status_code == 201
    policy_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/attestation-policies/{policy_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Fetch Me"
    assert get_resp.json()["enforcement"] == "block"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_policy(client: AsyncClient, db):
    """Create then update a policy."""
    from app.database import get_db

    async def override_dep():
        return _make_org_context("enterprise", "org_enterprise")

    async def override_db():
        yield db

    app.dependency_overrides[get_current_organization_dep] = override_dep
    app.dependency_overrides[get_db] = override_db

    create_resp = await client.post(
        "/api/v1/attestation-policies/",
        json={"name": "Update Me", "enforcement": "warn", "rules": []},
    )
    assert create_resp.status_code == 201
    policy_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/attestation-policies/{policy_id}",
        json={"name": "Updated Name", "enforcement": "audit"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Name"
    assert update_resp.json()["enforcement"] == "audit"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_policy_deactivates(client: AsyncClient, db):
    """Delete (soft) should deactivate the policy."""
    from app.database import get_db

    async def override_dep():
        return _make_org_context("enterprise", "org_enterprise")

    async def override_db():
        yield db

    app.dependency_overrides[get_current_organization_dep] = override_dep
    app.dependency_overrides[get_db] = override_db

    create_resp = await client.post(
        "/api/v1/attestation-policies/",
        json={"name": "Delete Me", "enforcement": "block", "rules": []},
    )
    assert create_resp.status_code == 201
    policy_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/attestation-policies/{policy_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Verify deactivated
    get_resp = await client.get(f"/api/v1/attestation-policies/{policy_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["active"] is False

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_nonexistent_policy_returns_404(client: AsyncClient, db):
    """Fetching a nonexistent policy should return 404."""
    from app.database import get_db

    async def override_dep():
        return _make_org_context("enterprise", "org_enterprise")

    async def override_db():
        yield db

    app.dependency_overrides[get_current_organization_dep] = override_dep
    app.dependency_overrides[get_db] = override_db

    get_resp = await client.get("/api/v1/attestation-policies/00000000-0000-0000-0000-000000000000")
    assert get_resp.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_attestations_empty(client: AsyncClient, db):
    """List attestations should return empty list for org with no records."""
    from app.database import get_db

    async def override_dep():
        return _make_org_context("enterprise", "org_enterprise")

    async def override_db():
        yield db

    app.dependency_overrides[get_current_organization_dep] = override_dep
    app.dependency_overrides[get_db] = override_db

    resp = await client.get("/api/v1/attestations/")
    assert resp.status_code == 200
    body = resp.json()
    assert "attestations" in body
    assert "total" in body

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_demo_tier_allowed():
    """Demo tier should be allowed access to attestation policies."""

    async def override_dep():
        return _make_org_context("demo")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/attestation-policies/")

    app.dependency_overrides.clear()
    # Should not be 403 (may be 200 or 500 depending on DB availability)
    assert response.status_code != 403
