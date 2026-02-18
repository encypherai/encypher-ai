"""
Unit tests for API Key Authentication.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT

from app.middleware.api_key_auth import (
    _normalize_service_base_url,
    authenticate_api_key,
    get_api_key_from_header,
    require_verification_permission,
)
from app.dependencies import require_embedding_permission


class TestGetAPIKeyFromHeader:
    """Test API key extraction from header."""

    @pytest.mark.asyncio
    async def test_bearer_format(self):
        """Test extracting API key from Bearer format."""
        api_key = await get_api_key_from_header("Bearer test_api_key_123")
        assert api_key == "test_api_key_123"

    @pytest.mark.asyncio
    async def test_raw_format(self):
        """Test extracting raw API key."""
        api_key = await get_api_key_from_header("test_api_key_123")
        assert api_key == "test_api_key_123"

    @pytest.mark.asyncio
    async def test_no_header(self):
        """Test with no authorization header."""
        api_key = await get_api_key_from_header(None)
        assert api_key is None


class TestAuthenticateAPIKey:
    """Test API key authentication."""

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Test authentication fails without API key."""
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_api_key(api_key=None, db=db)

        assert exc_info.value.status_code == 401
        assert "API key required" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.settings")
    async def test_demo_key(self, mock_settings):
        """Test authentication with demo key."""
        mock_settings.demo_api_key = "demo_key_123"
        mock_settings.demo_organization_id = "org_demo"
        mock_settings.demo_organization_name = "Demo Org"
        mock_settings.demo_private_key_bytes = b"demo_key"
        mock_settings.is_production = False
        mock_settings.is_demo_key_allowlisted.return_value = True

        db = AsyncMock()

        result = await authenticate_api_key(api_key="demo_key_123", db=db)

        assert result["organization_id"] == "org_demo"
        assert result["is_demo"] is True
        assert result["tier"] == "demo"

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.settings")
    async def test_invalid_api_key(self, mock_settings):
        """Test authentication fails with invalid API key."""
        mock_settings.demo_api_key = None

        db = AsyncMock()

        # Mock database query returning no results
        mock_result = Mock()
        mock_result.fetchone = Mock(return_value=None)
        db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_api_key(api_key="invalid_key", db=db)

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.settings")
    async def test_revoked_api_key(self, mock_settings):
        """Test authentication fails with revoked API key."""
        mock_settings.demo_api_key = None

        db = AsyncMock()

        # Mock database query returning revoked key
        mock_row = Mock()
        mock_row.revoked_at = datetime.utcnow()
        mock_row.is_active = False
        mock_row.organization_id = "org_123"

        mock_result = Mock()
        mock_result.fetchone = Mock(return_value=mock_row)
        db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_api_key(api_key="revoked_key", db=db)

        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.settings")
    async def test_expired_api_key(self, mock_settings):
        """Test authentication fails with expired API key."""
        mock_settings.demo_api_key = None

        db = AsyncMock()

        # Mock database query returning expired key
        mock_row = Mock()
        mock_row.revoked_at = None
        mock_row.is_active = True
        mock_row.expires_at = datetime.utcnow() - timedelta(days=1)
        mock_row.organization_id = "org_123"

        mock_result = Mock()
        mock_result.fetchone = Mock(return_value=mock_row)
        db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_api_key(api_key="expired_key", db=db)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.settings")
    async def test_quota_exceeded(self, mock_settings):
        """Test authentication fails when quota exceeded."""
        mock_settings.demo_api_key = None

        db = AsyncMock()

        # Mock database query returning org with exceeded quota
        mock_row = Mock()
        mock_row.revoked_at = None
        mock_row.is_active = True
        mock_row.expires_at = None
        mock_row.tier = "starter"
        mock_row.monthly_api_limit = 1000
        mock_row.monthly_api_usage = 1000
        mock_row.organization_id = "org_123"

        mock_result = Mock()
        mock_result.fetchone = Mock(return_value=mock_row)
        db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_api_key(api_key="quota_exceeded_key", db=db)

        assert exc_info.value.status_code == 429
        assert "quota exceeded" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.settings")
    async def test_valid_api_key(self, mock_settings):
        """Test successful authentication with valid API key."""
        mock_settings.demo_api_key = None

        db = AsyncMock()

        # Mock database query returning valid key
        mock_row = Mock()
        mock_row.api_key_id = "key_123"
        mock_row.organization_id = "org_123"
        mock_row.organization_name = "Test Org"
        mock_row.tier = "enterprise"
        mock_row.revoked_at = None
        mock_row.is_active = True
        mock_row.expires_at = None
        mock_row.scopes = ["sign", "verify", "lookup"]
        mock_row.monthly_api_limit = 10000
        mock_row.monthly_api_usage = 100
        mock_row.private_key_encrypted = b"encrypted_key"
        mock_row.features = {}
        mock_row.coalition_member = True
        mock_row.coalition_rev_share = DEFAULT_COALITION_PUBLISHER_PERCENT

        mock_result = Mock()
        mock_result.fetchone = Mock(return_value=mock_row)
        db.execute = AsyncMock(return_value=mock_result)

        result = await authenticate_api_key(api_key="valid_key", db=db)

        assert result["organization_id"] == "org_123"
        assert result["organization_name"] == "Test Org"
        assert result["tier"] == "enterprise"
        assert result["can_sign"] is True
        assert result["is_demo"] is False

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.get_key_service_client")
    @patch("app.middleware.api_key_auth.settings")
    async def test_key_service_valid_key(self, mock_settings, mock_get_client):
        mock_settings.demo_api_key = None

        response = Mock()
        response.status_code = 200
        response.json = Mock(
            return_value={
                "success": True,
                "data": {
                    "organization_id": "org_ks_123",
                    "organization_name": "Key Service Org",
                    "tier": "starter",
                    "permissions": ["sign", "verify", "read"],
                    "monthly_api_limit": 10_000,
                    "monthly_api_usage": 0,
                    "features": {},
                    "coalition_member": True,
                    "coalition_rev_share": DEFAULT_COALITION_PUBLISHER_PERCENT,
                },
            }
        )

        client = Mock()
        client.post = AsyncMock(return_value=response)
        mock_get_client.return_value = client

        db = AsyncMock()
        result = await authenticate_api_key(api_key="ency_test_12345678901234567890", db=db)

        assert result["organization_id"] == "org_ks_123"
        assert result["monthly_quota"] == 1000
        assert result["can_sign"] is True
        assert result["can_verify"] is True
        assert result["can_lookup"] is True

        client.post.assert_awaited_once_with("/api/v1/keys/validate", json={"key": "ency_test_12345678901234567890"})

    @pytest.mark.asyncio
    @patch("app.middleware.api_key_auth.get_key_service_client")
    @patch("app.middleware.api_key_auth.settings")
    async def test_key_service_unavailable_for_new_style_key_raises_503(self, mock_settings, mock_get_client):
        mock_settings.demo_api_key = None

        request = httpx.Request("POST", "http://key-service.local/api/v1/keys/validate")
        client = Mock()
        client.post = AsyncMock(side_effect=httpx.ConnectError("boom", request=request))
        mock_get_client.return_value = client

        db = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_api_key(api_key="ency_test_12345678901234567890", db=db)

        assert exc_info.value.status_code == 503
        assert "key service" in exc_info.value.detail.lower()


class TestNormalizeServiceBaseURL:
    def test_strips_api_v1_suffix(self):
        assert _normalize_service_base_url("http://localhost:8003/api/v1") == "http://localhost:8003"

    def test_strips_trailing_slash(self):
        assert _normalize_service_base_url("http://localhost:8003/") == "http://localhost:8003"

    def test_leaves_clean_url_unchanged(self):
        assert _normalize_service_base_url("http://localhost:8003") == "http://localhost:8003"


class TestRequireEmbeddingPermission:
    """Test embedding permission check."""

    @pytest.mark.asyncio
    async def test_any_tier_allowed(self):
        """TEAM_166: All tiers now have embedding access (free/enterprise/strategic_partner)."""
        organization = {"tier": "free", "can_sign": True, "organization_id": "org_test"}

        result = await require_embedding_permission(organization)
        assert result == organization

    @pytest.mark.asyncio
    async def test_no_sign_permission(self):
        """Test embedding permission fails without sign permission."""
        organization = {"tier": "free", "can_sign": False}

        with pytest.raises(HTTPException) as exc_info:
            await require_embedding_permission(organization)

        assert exc_info.value.status_code == 403
        assert "sign content" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_permission(self):
        """Test embedding permission succeeds with valid org."""
        organization = {"tier": "free", "can_sign": True, "organization_id": "org_123"}

        result = await require_embedding_permission(organization)

        assert result == organization


class TestRequireVerificationPermission:
    """Test verification permission check."""

    @pytest.mark.asyncio
    async def test_no_verify_permission(self):
        """Test verification permission fails without verify permission."""
        organization = {"can_verify": False}

        with pytest.raises(HTTPException) as exc_info:
            await require_verification_permission(organization)

        assert exc_info.value.status_code == 403
        assert "verify content" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_permission(self):
        """Test verification permission succeeds with valid org."""
        organization = {"can_verify": True, "organization_id": "org_123"}

        result = await require_verification_permission(organization)

        assert result == organization


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
