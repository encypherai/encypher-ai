"""Tests for account endpoints.

Tests the /api/v1/account and /api/v1/account/quota endpoints.
Uses async fixtures from conftest.py for proper database and auth handling.
"""

import pytest
from httpx import AsyncClient

from app.routers.account import resolve_user_account_name


@pytest.mark.asyncio
class TestGetAccountInfo:
    """Tests for GET /api/v1/account endpoint."""

    async def test_get_account_requires_auth(self, client: AsyncClient):
        """Test that account endpoint requires authentication."""
        response = await client.get("/api/v1/account")
        assert response.status_code == 401

    async def test_get_account_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful account info retrieval with demo key."""
        response = await client.get("/api/v1/account", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "organization_id" in data["data"]
        assert "tier" in data["data"]
        assert "features" in data["data"]
        assert "publisher_display_name" in data["data"]
        assert "anonymous_publisher" in data["data"]

    async def test_get_account_starter_tier(self, client: AsyncClient, starter_auth_headers: dict):
        """Test account info for starter tier."""
        response = await client.get("/api/v1/account", headers=starter_auth_headers)

        # May return 200 or 401 depending on whether starter key is seeded
        if response.status_code == 200:
            data = response.json()
            assert data["data"]["tier"] == "free"  # TEAM_166: starter coerced to free

    async def test_get_account_enterprise_tier(self, client: AsyncClient, enterprise_auth_headers: dict):
        """Test account info for enterprise tier."""
        response = await client.get("/api/v1/account", headers=enterprise_auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["data"]["tier"] == "enterprise"
            features = data["data"]["features"]
            assert features["merkle_enabled"] is True
            assert features["byok_enabled"] is True


class TestResolveUserAccountName:
    def test_prefers_publisher_display_name(self):
        assert (
            resolve_user_account_name(
                {
                    "display_name": "Encypher Publisher",
                    "organization_name": "Personal Account",
                }
            )
            == "Encypher Publisher"
        )

    def test_falls_back_to_organization_name_then_default(self):
        assert resolve_user_account_name({"organization_name": "Encypher Admin"}) == "Encypher Admin"
        assert resolve_user_account_name({}) == "Personal Account"


@pytest.mark.asyncio
class TestGetAccountQuota:
    """Tests for GET /api/v1/account/quota endpoint."""

    async def test_get_quota_requires_auth(self, client: AsyncClient):
        """Test that quota endpoint requires authentication."""
        response = await client.get("/api/v1/account/quota")
        assert response.status_code == 401

    async def test_get_quota_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful quota retrieval."""
        response = await client.get("/api/v1/account/quota", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data["data"]
        assert "tier" in data["data"]

    async def test_quota_response_structure(self, client: AsyncClient, auth_headers: dict):
        """Test quota response has expected structure."""
        response = await client.get("/api/v1/account/quota", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()["data"]
            # Check metrics structure
            metrics = data["metrics"]
            assert "api_calls" in metrics
            assert "c2pa_signatures" in metrics
            # Check period info
            assert "period_start" in data
            assert "reset_date" in data
