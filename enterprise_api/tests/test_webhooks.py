"""Tests for webhook endpoints.

Tests the /api/v1/webhooks endpoints for webhook management.
Uses async fixtures from conftest.py for proper database and auth handling.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestListWebhooks:
    """Tests for GET /api/v1/webhooks endpoint."""

    async def test_list_webhooks_requires_auth(self, client: AsyncClient):
        """Test that listing webhooks requires authentication."""
        response = await client.get("/api/v1/webhooks")
        assert response.status_code == 401

    async def test_list_webhooks_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful webhook listing."""
        response = await client.get("/api/v1/webhooks", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "webhooks" in data["data"]
        assert "total" in data["data"]


@pytest.mark.asyncio
class TestCreateWebhook:
    """Tests for POST /api/v1/webhooks endpoint."""

    async def test_create_webhook_requires_auth(self, client: AsyncClient):
        """Test that creating webhooks requires authentication."""
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["document.signed"]
            }
        )
        assert response.status_code == 401

    async def test_create_webhook_http_rejected(self, client: AsyncClient, auth_headers: dict):
        """Test that HTTP (non-HTTPS) URLs are rejected."""
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "http://example.com/webhook",
                "events": ["document.signed"]
            },
            headers=auth_headers
        )
        assert response.status_code == 400

    async def test_create_webhook_invalid_events(self, client: AsyncClient, auth_headers: dict):
        """Test that invalid events are rejected."""
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["invalid.event.type"]
            },
            headers=auth_headers
        )
        assert response.status_code == 400


@pytest.mark.asyncio
class TestUpdateWebhook:
    """Tests for PATCH /api/v1/webhooks/{id} endpoint."""

    async def test_update_webhook_requires_auth(self, client: AsyncClient):
        """Test that updating webhooks requires authentication."""
        response = await client.patch(
            "/api/v1/webhooks/wh_test",
            json={"is_active": False}
        )
        assert response.status_code == 401

    async def test_update_webhook_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent webhook."""
        response = await client.patch(
            "/api/v1/webhooks/wh_nonexistent_12345",
            json={"is_active": False},
            headers=auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteWebhook:
    """Tests for DELETE /api/v1/webhooks/{id} endpoint."""

    async def test_delete_webhook_requires_auth(self, client: AsyncClient):
        """Test that deleting webhooks requires authentication."""
        response = await client.delete("/api/v1/webhooks/wh_test")
        assert response.status_code == 401

    async def test_delete_webhook_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent webhook."""
        response = await client.delete(
            "/api/v1/webhooks/wh_nonexistent_12345",
            headers=auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestTestWebhook:
    """Tests for POST /api/v1/webhooks/{id}/test endpoint."""

    async def test_test_webhook_requires_auth(self, client: AsyncClient):
        """Test that testing webhooks requires authentication."""
        response = await client.post("/api/v1/webhooks/wh_test/test")
        assert response.status_code == 401

    async def test_test_webhook_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test testing non-existent webhook."""
        response = await client.post(
            "/api/v1/webhooks/wh_nonexistent_12345/test",
            headers=auth_headers
        )
        assert response.status_code == 404
