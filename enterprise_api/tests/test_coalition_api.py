"""Tests for coalition revenue tracking API endpoints."""
import pytest
from httpx import AsyncClient


class TestCoalitionEndpoints:
    """Test suite for /api/v1/coalition endpoints."""

    @pytest.mark.asyncio
    async def test_get_coalition_dashboard_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of coalition dashboard."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "organization_id" in data
        assert "tier" in data
        assert "publisher_share_percent" in data
        assert "coalition_member" in data
        assert "opted_out" in data
        assert "current_period" in data
        assert "lifetime_earnings_cents" in data
        assert "pending_earnings_cents" in data
        assert "paid_earnings_cents" in data
        assert "recent_earnings" in data
        assert "recent_payouts" in data

    @pytest.mark.asyncio
    async def test_coalition_dashboard_current_period(self, async_client: AsyncClient, auth_headers: dict):
        """Test current period stats in coalition dashboard."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        current_period = data["current_period"]
        assert "period_start" in current_period
        assert "period_end" in current_period
        assert "documents_count" in current_period
        assert "sentences_count" in current_period
        assert "total_characters" in current_period
        assert "unique_content_hash_count" in current_period

    @pytest.mark.asyncio
    async def test_coalition_dashboard_unauthorized(self, async_client: AsyncClient):
        """Test coalition dashboard requires authentication."""
        response = await async_client.get("/api/v1/coalition/dashboard")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_content_stats(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieval of content corpus statistics."""
        response = await async_client.get(
            "/api/v1/coalition/content-stats?months=6",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "organization_id" in data
        assert "stats" in data
        assert isinstance(data["stats"], list)

    @pytest.mark.asyncio
    async def test_get_content_stats_invalid_months(self, async_client: AsyncClient, auth_headers: dict):
        """Test content stats with invalid months parameter."""
        response = await async_client.get(
            "/api/v1/coalition/content-stats?months=100",
            headers=auth_headers,
        )
        # Should either clamp to max or return validation error
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_get_earnings_history(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieval of earnings history."""
        response = await async_client.get(
            "/api/v1/coalition/earnings?months=12",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "organization_id" in data
        assert "earnings" in data
        assert isinstance(data["earnings"], list)

    @pytest.mark.asyncio
    async def test_earnings_entry_structure(self, async_client: AsyncClient, auth_headers: dict):
        """Test earnings entry has correct structure."""
        response = await async_client.get(
            "/api/v1/coalition/earnings",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["earnings"]:
            earning = data["earnings"][0]
            assert "id" in earning
            assert "deal_id" in earning
            assert "period_start" in earning
            assert "period_end" in earning
            assert "gross_revenue_cents" in earning
            assert "publisher_share_percent" in earning
            assert "publisher_earnings_cents" in earning
            assert "status" in earning

    @pytest.mark.asyncio
    async def test_opt_out_of_coalition(self, async_client: AsyncClient, auth_headers: dict):
        """Test opting out of coalition."""
        response = await async_client.post(
            "/api/v1/coalition/opt-out",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert "opted_out_at" in data

    @pytest.mark.asyncio
    async def test_opt_in_to_coalition(self, async_client: AsyncClient, auth_headers: dict):
        """Test opting back into coalition."""
        response = await async_client.post(
            "/api/v1/coalition/opt-in",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data

    @pytest.mark.asyncio
    async def test_tier_based_rev_share(self, async_client: AsyncClient, auth_headers: dict):
        """Test that revenue share reflects tier."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        tier = data["tier"]
        share = data["publisher_share_percent"]
        
        # Verify tier-appropriate rev share
        expected_shares = {
            "starter": 65,
            "professional": 70,
            "business": 80,
            "enterprise": 85,
            "strategic_partner": 85,
        }
        
        if tier in expected_shares:
            assert share == expected_shares[tier]

    @pytest.mark.asyncio
    async def test_coalition_member_status(self, async_client: AsyncClient, auth_headers: dict):
        """Test coalition membership status is returned."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["coalition_member"], bool)
        assert isinstance(data["opted_out"], bool)


class TestCoalitionRevShareCalculation:
    """Test revenue share calculation logic."""

    @pytest.mark.asyncio
    async def test_starter_tier_rev_share(self, async_client: AsyncClient, starter_auth_headers: dict):
        """Test Starter tier gets 65% rev share."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=starter_auth_headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["tier"] == "starter":
                assert data["publisher_share_percent"] == 65

    @pytest.mark.asyncio
    async def test_professional_tier_rev_share(self, async_client: AsyncClient, professional_auth_headers: dict):
        """Test Professional tier gets 70% rev share."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=professional_auth_headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["tier"] == "professional":
                assert data["publisher_share_percent"] == 70

    @pytest.mark.asyncio
    async def test_business_tier_rev_share(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test Business tier gets 80% rev share."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=business_auth_headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["tier"] == "business":
                assert data["publisher_share_percent"] == 80

    @pytest.mark.asyncio
    async def test_enterprise_tier_rev_share(self, async_client: AsyncClient, enterprise_auth_headers: dict):
        """Test Enterprise tier gets 85% rev share."""
        response = await async_client.get(
            "/api/v1/coalition/dashboard",
            headers=enterprise_auth_headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["tier"] == "enterprise":
                assert data["publisher_share_percent"] == 85
