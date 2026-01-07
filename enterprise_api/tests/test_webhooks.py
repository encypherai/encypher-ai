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

    async def test_create_webhook_localhost_rejected(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://localhost/webhook",
                "events": ["document.signed"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    async def test_create_webhook_private_ip_rejected(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://127.0.0.1/webhook",
                "events": ["document.signed"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    async def test_create_webhook_nonstandard_port_rejected(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://93.184.216.34:8443/webhook",
                "events": ["document.signed"],
            },
            headers=auth_headers,
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

    async def test_update_webhook_rejects_private_ip_url(self, client: AsyncClient, auth_headers: dict):
        # First, clean up any existing webhooks to avoid hitting the limit
        list_response = await client.get("/api/v1/webhooks", headers=auth_headers)
        if list_response.status_code == 200:
            webhooks = list_response.json().get("data", {}).get("webhooks", [])
            for wh in webhooks:
                await client.delete(f"/api/v1/webhooks/{wh['id']}", headers=auth_headers)

        create_response = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["document.signed"]},
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Create failed: {create_response.json()}"
        webhook_id = create_response.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/webhooks/{webhook_id}",
            json={"url": "https://127.0.0.1/webhook"},
            headers=auth_headers,
        )
        assert response.status_code == 400

        # Clean up
        await client.delete(f"/api/v1/webhooks/{webhook_id}", headers=auth_headers)


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
