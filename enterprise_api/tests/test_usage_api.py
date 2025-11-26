"""Tests for usage metering API endpoints."""
import pytest
from httpx import AsyncClient


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
    async def test_reset_usage_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test resetting monthly usage counters."""
        response = await async_client.post(
            "/api/v1/usage/reset",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert "organization_id" in data
        assert "reset_at" in data

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
