"""
Tests for API key management endpoints.

Tests the /api/v1/keys endpoints for key creation, rotation, and revocation.
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


@pytest.fixture
def mock_user_context():
    """Mock user-level key context."""
    return {
        "organization_id": "user_123",
        "tier": "starter",
        "features": {},
    }


class TestListKeys:
    """Tests for GET /api/v1/keys endpoint."""

    def test_list_keys_requires_auth(self, client):
        """Test that listing keys requires authentication."""
        response = client.get("/api/v1/keys")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_list_keys_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful key listing."""
        mock_auth.return_value = mock_org_context

        mock_key1 = MagicMock()
        mock_key1.id = "key_001"
        mock_key1.name = "Production Key"
        mock_key1.key_prefix = "ek_live_abc1"
        mock_key1.permissions = ["sign", "verify"]
        mock_key1.created_at = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_key1.last_used_at = datetime(2024, 12, 23, 18, 0, 0, tzinfo=timezone.utc)
        mock_key1.expires_at = None
        mock_key1.is_active = True
        mock_key1.is_revoked = False
        mock_key1.usage_count = 1500

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [mock_key1]

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/keys",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert data["data"]["keys"][0]["id"] == "key_001"
        assert data["data"]["keys"][0]["prefix"] == "ek_live_abc1"

    @patch("app.routers.keys.get_current_organization")
    def test_list_keys_user_level_forbidden(self, mock_auth, client, mock_user_context):
        """Test that user-level keys cannot list org keys."""
        mock_auth.return_value = mock_user_context

        response = client.get(
            "/api/v1/keys",
            headers={"Authorization": "Bearer user_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["total"] == 0
        assert "cannot manage" in data["data"].get("message", "").lower()


class TestCreateKey:
    """Tests for POST /api/v1/keys endpoint."""

    def test_create_key_requires_auth(self, client):
        """Test that creating keys requires authentication."""
        response = client.post("/api/v1/keys", json={"name": "Test Key"})
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_create_key_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful key creation."""
        mock_auth.return_value = mock_org_context

        # Mock key count check
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_count_result
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/keys",
            json={
                "name": "CI/CD Pipeline Key",
                "permissions": ["sign", "verify"],
                "expires_in_days": 365
            },
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "key" in data["data"]  # Full key returned
        assert data["data"]["key"].startswith("ek_live_")
        assert "warning" in data

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_create_key_limit_reached(self, mock_db, mock_auth, client):
        """Test key creation when limit is reached."""
        mock_auth.return_value = {
            "organization_id": "org_starter",
            "tier": "starter",  # Starter has 2 key limit
            "features": {},
        }

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2  # Already at limit

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_count_result
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/keys",
            json={"name": "Another Key"},
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "limit" in response.json()["detail"]["message"].lower()

    @patch("app.routers.keys.get_current_organization")
    def test_create_key_user_level_forbidden(self, mock_auth, client, mock_user_context):
        """Test that user-level keys cannot create org keys."""
        mock_auth.return_value = mock_user_context

        response = client.post(
            "/api/v1/keys",
            json={"name": "Test Key"},
            headers={"Authorization": "Bearer user_key"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRevokeKey:
    """Tests for DELETE /api/v1/keys/{id} endpoint."""

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_revoke_key_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful key revocation."""
        mock_auth.return_value = mock_org_context

        mock_key = MagicMock()
        mock_key.id = "key_001"
        mock_key.is_revoked = False

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_key

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.delete(
            "/api/v1/keys/key_001",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["revoked"] is True

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_revoke_key_not_found(self, mock_db, mock_auth, client, mock_org_context):
        """Test revoking non-existent key."""
        mock_auth.return_value = mock_org_context

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.delete(
            "/api/v1/keys/nonexistent",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_revoke_already_revoked_key(self, mock_db, mock_auth, client, mock_org_context):
        """Test revoking an already revoked key."""
        mock_auth.return_value = mock_org_context

        mock_key = MagicMock()
        mock_key.id = "key_001"
        mock_key.is_revoked = True

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_key

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.delete(
            "/api/v1/keys/key_001",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRotateKey:
    """Tests for POST /api/v1/keys/{id}/rotate endpoint."""

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_rotate_key_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful key rotation."""
        mock_auth.return_value = mock_org_context

        mock_key = MagicMock()
        mock_key.id = "key_001"
        mock_key.name = "Production Key"
        mock_key.permissions = ["sign", "verify"]
        mock_key.expires_at = None
        mock_key.is_revoked = False

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_key

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/keys/key_001/rotate",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "key" in data["data"]  # New key returned
        assert data["data"]["old_key_id"] == "key_001"
        assert data["data"]["new_key_id"] != "key_001"

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_rotate_revoked_key_fails(self, mock_db, mock_auth, client, mock_org_context):
        """Test that rotating a revoked key fails."""
        mock_auth.return_value = mock_org_context

        mock_key = MagicMock()
        mock_key.id = "key_001"
        mock_key.is_revoked = True

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_key

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/keys/key_001/rotate",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUpdateKey:
    """Tests for PATCH /api/v1/keys/{id} endpoint."""

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_update_key_name(self, mock_db, mock_auth, client, mock_org_context):
        """Test updating key name."""
        mock_auth.return_value = mock_org_context

        mock_key = MagicMock()
        mock_key.id = "key_001"
        mock_key.name = "Old Name"
        mock_key.permissions = ["sign", "verify"]

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_key

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.patch(
            "/api/v1/keys/key_001",
            json={"name": "New Name"},
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["updated"] is True

    @patch("app.routers.keys.get_current_organization")
    @patch("app.routers.keys.get_db")
    def test_update_key_permissions(self, mock_db, mock_auth, client, mock_org_context):
        """Test updating key permissions."""
        mock_auth.return_value = mock_org_context

        mock_key = MagicMock()
        mock_key.id = "key_001"
        mock_key.name = "Test Key"
        mock_key.permissions = ["sign", "verify"]

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_key

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.patch(
            "/api/v1/keys/key_001",
            json={"permissions": ["verify"]},  # Remove sign permission
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
