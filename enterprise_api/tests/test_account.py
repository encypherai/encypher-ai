"""Tests for account endpoints.

Tests the /api/v1/account and /api/v1/account/quota endpoints.
Uses async fixtures from conftest.py for proper database and auth handling.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.dependencies import get_current_organization
from app.main import app
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

    async def test_user_level_quota_reports_persisted_api_usage(self, client: AsyncClient, db):
        """User-level quota should report DB-backed usage, not hardcoded zero values."""
        org_id = "user_quota_stats_test"
        await db.execute(
            text(
                """
                INSERT INTO organizations (
                    id, name, email, tier, monthly_api_limit, monthly_api_usage,
                    coalition_member, coalition_rev_share, created_at, updated_at
                ) VALUES (
                    :id, :name, :email, :tier, :monthly_api_limit, :monthly_api_usage,
                    :coalition_member, :coalition_rev_share, NOW(), NOW()
                )
                ON CONFLICT (id) DO UPDATE SET
                    monthly_api_limit = EXCLUDED.monthly_api_limit,
                    monthly_api_usage = EXCLUDED.monthly_api_usage,
                    updated_at = NOW()
                """
            ),
            {
                "id": org_id,
                "name": "Personal Account",
                "email": "user_quota_stats_test@personal.local",
                "tier": "free",
                "monthly_api_limit": 1000,
                "monthly_api_usage": 9,
                "coalition_member": True,
                "coalition_rev_share": 65,
            },
        )
        await db.commit()

        async def _override_current_org():
            return {
                "organization_id": org_id,
                "organization_name": "Personal Account",
                "tier": "free",
                "permissions": ["read"],
            }

        app.dependency_overrides[get_current_organization] = _override_current_org
        try:
            response = await client.get("/api/v1/account/quota")
        finally:
            app.dependency_overrides.pop(get_current_organization, None)

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["organization_id"] == org_id
        assert payload["metrics"]["api_calls"]["used"] == 9
        assert payload["metrics"]["api_calls"]["limit"] == 1000
        assert payload["metrics"]["c2pa_signatures"]["limit"] == 1000

    async def test_free_tier_quota_clamps_stale_db_api_limit_to_policy_cap(self, client: AsyncClient, db):
        """Free tier should never expose API call limits above the 1,000/month policy cap."""
        org_id = "user_quota_limit_clamp_test"
        await db.execute(
            text(
                """
                INSERT INTO organizations (
                    id, name, email, tier, monthly_api_limit, monthly_api_usage,
                    coalition_member, coalition_rev_share, created_at, updated_at
                ) VALUES (
                    :id, :name, :email, :tier, :monthly_api_limit, :monthly_api_usage,
                    :coalition_member, :coalition_rev_share, NOW(), NOW()
                )
                ON CONFLICT (id) DO UPDATE SET
                    monthly_api_limit = EXCLUDED.monthly_api_limit,
                    monthly_api_usage = EXCLUDED.monthly_api_usage,
                    updated_at = NOW()
                """
            ),
            {
                "id": org_id,
                "name": "Personal Account",
                "email": "user_quota_limit_clamp_test@personal.local",
                "tier": "free",
                "monthly_api_limit": 10000,
                "monthly_api_usage": 17,
                "coalition_member": True,
                "coalition_rev_share": 65,
            },
        )
        await db.commit()

        async def _override_current_org():
            return {
                "organization_id": org_id,
                "organization_name": "Personal Account",
                "tier": "free",
                "permissions": ["read"],
            }

        app.dependency_overrides[get_current_organization] = _override_current_org
        try:
            response = await client.get("/api/v1/account/quota")
        finally:
            app.dependency_overrides.pop(get_current_organization, None)

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["metrics"]["api_calls"]["used"] == 17
        assert payload["metrics"]["api_calls"]["limit"] == 1000
