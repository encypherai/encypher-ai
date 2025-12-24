"""
Tests for account endpoints.

Tests the /api/v1/account and /api/v1/account/quota endpoints.
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
    """Mock organization context for authenticated requests."""
    return {
        "organization_id": "org_test123",
        "organization_name": "Test Organization",
        "tier": "professional",
        "features": {
            "merkle_enabled": False,
            "byok_enabled": False,
            "sentence_tracking": True,
        },
        "permissions": ["sign", "verify"],
    }


@pytest.fixture
def mock_user_context():
    """Mock user-level key context."""
    return {
        "organization_id": "user_123",
        "organization_name": "Personal Account",
        "tier": "starter",
        "features": {},
        "permissions": ["sign", "verify"],
    }


class TestGetAccountInfo:
    """Tests for GET /api/v1/account endpoint."""

    def test_get_account_requires_auth(self, client):
        """Test that account endpoint requires authentication."""
        response = client.get("/api/v1/account")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.account.get_current_organization")
    @patch("app.routers.account.get_db")
    def test_get_account_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful account info retrieval."""
        mock_auth.return_value = mock_org_context

        # Mock database response
        mock_row = MagicMock()
        mock_row.id = "org_test123"
        mock_row.name = "Test Organization"
        mock_row.email = "test@example.com"
        mock_row.tier = "professional"
        mock_row.subscription_status = "active"
        mock_row.created_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        mock_row.features = {"sentence_tracking": True}

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        # Make request with auth header
        response = client.get(
            "/api/v1/account",
            headers={"Authorization": "Bearer test_key"}
        )

        # Verify response structure
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["organization_id"] == "org_test123"
        assert data["data"]["tier"] == "professional"

    @patch("app.routers.account.get_current_organization")
    def test_get_account_user_level_key(self, mock_auth, client, mock_user_context):
        """Test account info for user-level keys."""
        mock_auth.return_value = mock_user_context

        response = client.get(
            "/api/v1/account",
            headers={"Authorization": "Bearer user_key"}
        )

        # User-level keys should return starter tier
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["tier"] == "starter"
        assert data["data"]["name"] == "Personal Account"


class TestGetAccountQuota:
    """Tests for GET /api/v1/account/quota endpoint."""

    def test_get_quota_requires_auth(self, client):
        """Test that quota endpoint requires authentication."""
        response = client.get("/api/v1/account/quota")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.account.get_current_organization")
    @patch("app.routers.account.get_db")
    @patch("app.routers.account.get_content_db")
    def test_get_quota_success(self, mock_content_db, mock_db, mock_auth, client, mock_org_context):
        """Test successful quota retrieval."""
        mock_auth.return_value = mock_org_context

        # Mock organization query
        mock_org_row = MagicMock()
        mock_org_row.tier = "professional"
        mock_org_row.monthly_api_usage = 5000
        mock_org_row.monthly_api_limit = 100000

        mock_org_result = MagicMock()
        mock_org_result.fetchone.return_value = mock_org_row

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_org_result
        mock_db.return_value = mock_session

        # Mock content database queries
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 150

        mock_content_session = AsyncMock()
        mock_content_session.execute.return_value = mock_count_result
        mock_content_db.return_value = mock_content_session

        response = client.get(
            "/api/v1/account/quota",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data["data"]
        assert data["data"]["tier"] == "professional"

    @patch("app.routers.account.get_current_organization")
    def test_get_quota_user_level_key(self, mock_auth, client, mock_user_context):
        """Test quota for user-level keys."""
        mock_auth.return_value = mock_user_context

        response = client.get(
            "/api/v1/account/quota",
            headers={"Authorization": "Bearer user_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["tier"] == "starter"


class TestTierFeatures:
    """Tests for tier-based feature flags."""

    @patch("app.routers.account.get_current_organization")
    @patch("app.routers.account.get_db")
    def test_starter_tier_features(self, mock_db, mock_auth, client):
        """Test starter tier has limited features."""
        mock_auth.return_value = {
            "organization_id": "org_starter",
            "tier": "starter",
            "features": {},
        }

        mock_row = MagicMock()
        mock_row.id = "org_starter"
        mock_row.name = "Starter Org"
        mock_row.email = "starter@example.com"
        mock_row.tier = "starter"
        mock_row.subscription_status = "active"
        mock_row.created_at = datetime.now(timezone.utc)
        mock_row.features = {}

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/account",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        features = response.json()["data"]["features"]
        assert features["merkle_enabled"] is False
        assert features["byok_enabled"] is False
        assert features["bulk_operations"] is False

    @patch("app.routers.account.get_current_organization")
    @patch("app.routers.account.get_db")
    def test_enterprise_tier_features(self, mock_db, mock_auth, client):
        """Test enterprise tier has all features."""
        mock_auth.return_value = {
            "organization_id": "org_enterprise",
            "tier": "enterprise",
            "features": {},
        }

        mock_row = MagicMock()
        mock_row.id = "org_enterprise"
        mock_row.name = "Enterprise Org"
        mock_row.email = "enterprise@example.com"
        mock_row.tier = "enterprise"
        mock_row.subscription_status = "active"
        mock_row.created_at = datetime.now(timezone.utc)
        mock_row.features = {}

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/account",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        features = response.json()["data"]["features"]
        assert features["merkle_enabled"] is True
        assert features["byok_enabled"] is True
        assert features["bulk_operations"] is True
        assert features["sso"] is True
