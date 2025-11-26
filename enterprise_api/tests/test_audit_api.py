"""Tests for audit logging API endpoints."""
import pytest
from httpx import AsyncClient


class TestAuditLogEndpoints:
    """Test suite for /api/v1/audit-logs endpoints.
    
    Note: Audit logs are tier-gated (Business+ only).
    Uses business-api-key-for-testing which has Business tier.
    """

    @pytest.mark.asyncio
    async def test_get_audit_logs_success(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test successful retrieval of audit logs (Business+ tier)."""
        response = await async_client.get(
            "/api/v1/audit-logs",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "organization_id" in data
        assert "logs" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "has_more" in data
        
        assert isinstance(data["logs"], list)

    @pytest.mark.asyncio
    async def test_get_audit_logs_pagination(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test audit logs pagination."""
        response = await async_client.get(
            "/api/v1/audit-logs?page=1&page_size=10",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert len(data["logs"]) <= 10

    @pytest.mark.asyncio
    async def test_get_audit_logs_filter_by_action(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test filtering audit logs by action type."""
        response = await async_client.get(
            "/api/v1/audit-logs?action=document.signed",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned logs should match the filter
        for log in data["logs"]:
            assert log["action"] == "document.signed"

    @pytest.mark.asyncio
    async def test_get_audit_logs_filter_by_date_range(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test filtering audit logs by date range."""
        response = await async_client.get(
            "/api/v1/audit-logs?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["logs"], list)

    @pytest.mark.asyncio
    async def test_get_audit_logs_unauthorized(self, async_client: AsyncClient):
        """Test audit logs requires authentication."""
        response = await async_client.get("/api/v1/audit-logs")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_audit_logs_tier_gated(self, async_client: AsyncClient, starter_auth_headers: dict):
        """Test audit logs is tier-gated (requires Business+)."""
        response = await async_client.get(
            "/api/v1/audit-logs",
            headers=starter_auth_headers,
        )
        
        # Should return 403 for Starter/Demo tier
        assert response.status_code == 403
        data = response.json()
        # Check in error object (our API format)
        assert data.get("error", {}).get("code") == "FEATURE_NOT_AVAILABLE"

    @pytest.mark.asyncio
    async def test_export_audit_logs_json(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test exporting audit logs as JSON."""
        response = await async_client.get(
            "/api/v1/audit-logs/export?format=json",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "organization_id" in data
        assert "export_date" in data
        assert "logs" in data
        assert "total_records" in data

    @pytest.mark.asyncio
    async def test_export_audit_logs_csv(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test exporting audit logs as CSV."""
        response = await async_client.get(
            "/api/v1/audit-logs/export?format=csv",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_audit_log_entry_structure(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test audit log entry has correct structure."""
        response = await async_client.get(
            "/api/v1/audit-logs?page_size=1",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["logs"]:
            log = data["logs"][0]
            assert "id" in log
            assert "timestamp" in log
            assert "action" in log
            assert "actor_id" in log
            assert "actor_type" in log
            assert "resource_type" in log
            # Optional fields
            assert "resource_id" in log or log.get("resource_id") is None
            assert "details" in log or log.get("details") is None
