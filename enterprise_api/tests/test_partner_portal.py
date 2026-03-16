"""Tests for the Partner Portal router (TEAM_256)."""

import pytest
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from app.dependencies import get_current_organization_dep
from app.main import app


def _make_org_context(tier: str, org_id: str = "org_partner_test") -> dict:
    return {
        "organization_id": org_id,
        "organization_name": "Test Partner Org",
        "tier": tier,
        "permissions": ["sign", "verify", "lookup"],
    }


@pytest.mark.asyncio
async def test_list_publishers_requires_strategic_partner():
    """Free-tier org should get 403 on partner portal endpoints."""

    async def override_dep():
        return _make_org_context("free")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/partner/portal/publishers")

    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_publishers_requires_strategic_partner_enterprise():
    """Enterprise-tier org should also get 403 on partner portal endpoints."""

    async def override_dep():
        return _make_org_context("enterprise")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/partner/portal/publishers")

    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_aggregate_requires_strategic_partner():
    """Free-tier org should get 403 on aggregate endpoint."""

    async def override_dep():
        return _make_org_context("free")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/partner/portal/aggregate")

    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_publisher_detail_requires_strategic_partner():
    """Free-tier org should get 403 on publisher detail endpoint."""

    async def override_dep():
        return _make_org_context("free")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/partner/portal/publishers/some_org_id")

    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_publishers_strategic_partner_allowed(client, db):
    """Strategic partner tier should be allowed to access portal endpoints."""

    async def override_dep():
        return _make_org_context("strategic_partner", "org_sp_test")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    response = await client.get("/api/v1/partner/portal/publishers")

    assert response.status_code == 200
    body = response.json()
    assert "publishers" in body
    assert "total" in body
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_aggregate_strategic_partner_allowed(client, db):
    """Strategic partner tier should get aggregate stats."""

    async def override_dep():
        return _make_org_context("strategic_partner", "org_sp_test")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    response = await client.get("/api/v1/partner/portal/aggregate")

    assert response.status_code == 200
    body = response.json()
    assert body["total_publishers"] == 0
    assert "total_documents_signed" in body


@pytest.mark.asyncio
async def test_demo_tier_allowed(client, db):
    """Demo tier should also be allowed (for dev/testing)."""

    async def override_dep():
        return _make_org_context("demo", "org_demo")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    response = await client.get("/api/v1/partner/portal/publishers")

    assert response.status_code == 200
    body = response.json()
    assert "publishers" in body


@pytest.mark.asyncio
async def test_publisher_detail_not_found(client, db):
    """Publisher detail should return 404 for non-existent child org."""

    async def override_dep():
        return _make_org_context("strategic_partner", "org_sp_test")

    app.dependency_overrides[get_current_organization_dep] = override_dep

    response = await client.get("/api/v1/partner/portal/publishers/nonexistent_org")

    assert response.status_code == 404
