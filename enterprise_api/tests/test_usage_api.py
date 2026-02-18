"""Tests for usage metering API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.dependencies import require_read_permission
from app.main import app


class TestUsageEndpoints:
    """Test suite for /api/v1/usage endpoints."""

    @pytest.mark.asyncio
    async def test_get_usage_stats_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of usage statistics."""
        response = await async_client.get(
            "/api/v1/usage",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "organization_id" in data
        assert "tier" in data
        assert "period_start" in data
        assert "period_end" in data
        assert "metrics" in data
        assert "reset_date" in data

        # Verify metrics structure
        metrics = data["metrics"]
        assert "c2pa_signatures" in metrics
        assert "sentences_tracked" in metrics
        assert "batch_operations" in metrics
        assert "api_calls" in metrics

        # Verify metric fields
        for metric_name, metric in metrics.items():
            assert "name" in metric
            assert "used" in metric
            assert "limit" in metric
            assert "remaining" in metric
            assert "percentage_used" in metric
            assert "available" in metric

    @pytest.mark.asyncio
    async def test_get_usage_stats_unauthorized(self, async_client: AsyncClient):
        """Test usage stats requires authentication."""
        response = await async_client.get("/api/v1/usage")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_usage_stats_invalid_api_key(self, async_client: AsyncClient):
        """Test usage stats with invalid API key."""
        response = await async_client.get(
            "/api/v1/usage",
            headers={"X-API-Key": "invalid_key_12345"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_reset_usage_requires_super_admin(self, async_client: AsyncClient, auth_headers: dict):
        """Test resetting monthly usage counters requires super admin."""
        response = await async_client.post(
            "/api/v1/usage/reset",
            headers=auth_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data.get("success") is False
        assert (data.get("error") or {}).get("message") == "Super admin access required"

    @pytest.mark.asyncio
    async def test_get_usage_history(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieval of usage history."""
        response = await async_client.get(
            "/api/v1/usage/history?months=6",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert "organization_id" in data
        assert "history" in data
        assert isinstance(data["history"], list)
        assert len(data["history"]) <= 6

    @pytest.mark.asyncio
    async def test_usage_history_invalid_months(self, async_client: AsyncClient, auth_headers: dict):
        """Test usage history with invalid months parameter."""
        response = await async_client.get(
            "/api/v1/usage/history?months=0",
            headers=auth_headers,
        )
        # Should either return 422 (validation error) or default to valid value
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_usage_metrics_tier_limits(self, async_client: AsyncClient, auth_headers: dict):
        """Test that usage metrics reflect correct tier limits."""
        response = await async_client.get(
            "/api/v1/usage",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        metrics = data["metrics"]

        # Verify tier-appropriate limits
        if tier == "starter":
            assert metrics["c2pa_signatures"]["limit"] == 10000
            assert metrics["sentences_tracked"]["limit"] == 0  # Not available
        elif tier == "professional":
            assert metrics["c2pa_signatures"]["limit"] == -1  # Unlimited
            assert metrics["sentences_tracked"]["limit"] == 50000
        elif tier == "business":
            assert metrics["c2pa_signatures"]["limit"] == -1
            assert metrics["sentences_tracked"]["limit"] == 500000
        elif tier in ["enterprise", "strategic_partner"]:
            assert metrics["c2pa_signatures"]["limit"] == -1
            assert metrics["sentences_tracked"]["limit"] == -1

    @pytest.mark.asyncio
    async def test_get_usage_stats_user_level_reports_persisted_api_usage(self, async_client: AsyncClient, db):
        """User-level contexts should report tracked DB usage, not hardcoded zero."""
        org_id = "user_usage_stats_test"
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
                "email": "user_usage_stats_test@personal.local",
                "tier": "free",
                "monthly_api_limit": 1000,
                "monthly_api_usage": 7,
                "coalition_member": True,
                "coalition_rev_share": 65,
            },
        )
        await db.commit()

        async def _override_user_read_permission():
            return {
                "organization_id": org_id,
                "organization_name": "Personal Account",
                "tier": "free",
                "permissions": ["read"],
            }

        app.dependency_overrides[require_read_permission] = _override_user_read_permission
        try:
            response = await async_client.get("/api/v1/usage")
        finally:
            app.dependency_overrides.pop(require_read_permission, None)

        assert response.status_code == 200
        data = response.json()
        assert data["organization_id"] == org_id
        assert data["metrics"]["api_calls"]["used"] == 7
        assert data["metrics"]["api_calls"]["limit"] == 1000
