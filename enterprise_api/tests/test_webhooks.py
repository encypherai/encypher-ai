"""
Tests for webhook endpoints.

Tests the /api/v1/webhooks endpoints for webhook management.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_org_context():
    """Mock organization context."""
    return {
        "organization_id": "org_test123",
        "organization_name": "Test Organization",
        "tier": "professional",
        "features": {},
        "permissions": ["sign", "verify"],
    }


class TestListWebhooks:
    """Tests for GET /api/v1/webhooks endpoint."""

    def test_list_webhooks_requires_auth(self, client):
        """Test that listing webhooks requires authentication."""
        response = client.get("/api/v1/webhooks")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_list_webhooks_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful webhook listing."""
        mock_auth.return_value = mock_org_context

        mock_webhook = MagicMock()
        mock_webhook.id = "wh_001"
        mock_webhook.url = "https://example.com/webhook"
        mock_webhook.events = ["document.signed", "document.revoked"]
        mock_webhook.is_active = True
        mock_webhook.is_verified = True
        mock_webhook.created_at = datetime(2024, 12, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_webhook.last_triggered_at = datetime(2024, 12, 23, 15, 0, 0, tzinfo=timezone.utc)
        mock_webhook.success_count = 150
        mock_webhook.failure_count = 2

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [mock_webhook]

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/webhooks",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert data["data"]["webhooks"][0]["id"] == "wh_001"
        assert data["data"]["webhooks"][0]["is_verified"] is True


class TestCreateWebhook:
    """Tests for POST /api/v1/webhooks endpoint."""

    def test_create_webhook_requires_auth(self, client):
        """Test that creating webhooks requires authentication."""
        response = client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["document.signed"]}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_create_webhook_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful webhook creation."""
        mock_auth.return_value = mock_org_context

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_count_result
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["document.signed", "document.revoked"],
                "secret": "my_shared_secret_123"
            },
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["data"]["url"] == "https://example.com/webhook"
        assert "document.signed" in data["data"]["events"]

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_create_webhook_http_rejected(self, mock_db, mock_auth, client, mock_org_context):
        """Test that HTTP (non-HTTPS) URLs are rejected."""
        mock_auth.return_value = mock_org_context

        response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "http://example.com/webhook",  # HTTP, not HTTPS
                "events": ["document.signed"]
            },
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "HTTPS" in response.json()["detail"]["message"]

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_create_webhook_invalid_events(self, mock_db, mock_auth, client, mock_org_context):
        """Test that invalid events are rejected."""
        mock_auth.return_value = mock_org_context

        response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["invalid.event"]
            },
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "INVALID_EVENTS" in response.json()["detail"]["code"]

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_create_webhook_limit_reached(self, mock_db, mock_auth, client, mock_org_context):
        """Test webhook creation when limit is reached."""
        mock_auth.return_value = mock_org_context

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 10  # Max limit

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_count_result
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["document.signed"]
            },
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateWebhook:
    """Tests for PATCH /api/v1/webhooks/{id} endpoint."""

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_update_webhook_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful webhook update."""
        mock_auth.return_value = mock_org_context

        mock_webhook = MagicMock()
        mock_webhook.id = "wh_001"

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_webhook

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.patch(
            "/api/v1/webhooks/wh_001",
            json={"events": ["document.signed", "quota.warning"]},
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["updated"] is True

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_update_webhook_not_found(self, mock_db, mock_auth, client, mock_org_context):
        """Test updating non-existent webhook."""
        mock_auth.return_value = mock_org_context

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.patch(
            "/api/v1/webhooks/nonexistent",
            json={"is_active": False},
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteWebhook:
    """Tests for DELETE /api/v1/webhooks/{id} endpoint."""

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_delete_webhook_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful webhook deletion."""
        mock_auth.return_value = mock_org_context

        mock_webhook = MagicMock()
        mock_webhook.id = "wh_001"

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_webhook

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.delete(
            "/api/v1/webhooks/wh_001",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["deleted"] is True

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_delete_webhook_not_found(self, mock_db, mock_auth, client, mock_org_context):
        """Test deleting non-existent webhook."""
        mock_auth.return_value = mock_org_context

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.delete(
            "/api/v1/webhooks/nonexistent",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTestWebhook:
    """Tests for POST /api/v1/webhooks/{id}/test endpoint."""

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    @patch("app.routers.webhooks.httpx.AsyncClient")
    def test_test_webhook_success(self, mock_httpx, mock_db, mock_auth, client, mock_org_context):
        """Test successful webhook test."""
        mock_auth.return_value = mock_org_context

        mock_webhook = MagicMock()
        mock_webhook.id = "wh_001"
        mock_webhook.url = "https://example.com/webhook"
        mock_webhook.secret_hash = None

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_webhook

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.15

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_httpx.return_value = mock_client_instance

        response = client.post(
            "/api/v1/webhooks/wh_001/test",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["success"] is True


class TestWebhookDeliveries:
    """Tests for GET /api/v1/webhooks/{id}/deliveries endpoint."""

    @patch("app.routers.webhooks.get_current_organization")
    @patch("app.routers.webhooks.get_db")
    def test_get_deliveries_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful delivery history retrieval."""
        mock_auth.return_value = mock_org_context

        # Mock webhook exists check
        mock_webhook = MagicMock()
        mock_webhook.id = "wh_001"

        mock_webhook_result = MagicMock()
        mock_webhook_result.fetchone.return_value = mock_webhook

        # Mock count
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 5

        # Mock deliveries
        mock_delivery = MagicMock()
        mock_delivery.id = "del_001"
        mock_delivery.event_type = "document.signed"
        mock_delivery.status = "success"
        mock_delivery.attempts = 1
        mock_delivery.response_status_code = 200
        mock_delivery.response_time_ms = 150
        mock_delivery.error_message = None
        mock_delivery.created_at = datetime(2024, 12, 23, 15, 0, 0, tzinfo=timezone.utc)
        mock_delivery.delivered_at = datetime(2024, 12, 23, 15, 0, 0, tzinfo=timezone.utc)

        mock_deliveries_result = MagicMock()
        mock_deliveries_result.fetchall.return_value = [mock_delivery]

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [
            mock_webhook_result,
            mock_count_result,
            mock_deliveries_result
        ]
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/webhooks/wh_001/deliveries",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 5
        assert len(data["data"]["deliveries"]) == 1
