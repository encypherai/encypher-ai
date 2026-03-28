"""Tests for WebSocket JWT session token authentication fallback."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocketException

from app.middleware.websocket_auth import _authenticate_websocket_jwt, authenticate_websocket


@pytest.mark.asyncio
async def test_authenticate_websocket_jwt_returns_org_context():
    """JWT token that resolves to a valid org should return a well-formed dict."""
    fake_org_context = {
        "organization_id": "org_abc",
        "organization_name": "Test Org",
        "tier": "enterprise",
        "features": {"streaming": True},
        "permissions": ["sign", "verify", "lookup", "read"],
        "monthly_api_limit": 10000,
        "monthly_api_usage": 42,
    }

    mock_row = MagicMock()
    mock_row.private_key_encrypted = b"encrypted_key_bytes"

    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__.return_value = mock_db
    mock_session_ctx.__aexit__.return_value = False

    with (
        patch(
            "app.middleware.websocket_auth._get_org_context_from_jwt_access_token",
            new_callable=AsyncMock,
            return_value=fake_org_context,
        ),
        patch(
            "app.middleware.websocket_auth.async_session_factory",
            return_value=mock_session_ctx,
        ),
    ):
        result = await _authenticate_websocket_jwt("jwt-token-here")

    assert result is not None
    assert result["organization_id"] == "org_abc"
    assert result["organization_name"] == "Test Org"
    assert result["tier"] == "enterprise"
    assert result["can_sign"] is True
    assert result["can_verify"] is True
    assert result["is_demo"] is False
    assert result["private_key_encrypted"] == b"encrypted_key_bytes"


@pytest.mark.asyncio
async def test_authenticate_websocket_jwt_returns_none_on_invalid_token():
    """Invalid JWT should return None so the caller can raise."""
    with patch(
        "app.middleware.websocket_auth._get_org_context_from_jwt_access_token",
        new_callable=AsyncMock,
        return_value=None,
    ):
        result = await _authenticate_websocket_jwt("bad-token")

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_websocket_falls_back_to_jwt():
    """When API key lookup finds no row, should try JWT before rejecting."""
    fake_ws = MagicMock()

    # DB returns no row for API key lookup
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__.return_value = mock_db
    mock_session_ctx.__aexit__.return_value = False

    jwt_org = {
        "api_key": None,
        "organization_id": "org_jwt",
        "organization_name": "JWT Org",
        "tier": "professional",
        "can_sign": True,
        "can_verify": True,
        "can_lookup": True,
        "monthly_quota": 5000,
        "api_calls_this_month": 10,
        "is_demo": False,
        "private_key_encrypted": None,
        "features": {},
    }

    with (
        patch(
            "app.middleware.websocket_auth.async_session_factory",
            return_value=mock_session_ctx,
        ),
        patch(
            "app.middleware.websocket_auth._authenticate_websocket_jwt",
            new_callable=AsyncMock,
            return_value=jwt_org,
        ),
        patch("app.middleware.websocket_auth.settings") as mock_settings,
    ):
        mock_settings.demo_api_key = None
        result = await authenticate_websocket(fake_ws, api_key="jwt-session-token")  # pragma: allowlist secret

    assert result["organization_id"] == "org_jwt"


@pytest.mark.asyncio
async def test_authenticate_websocket_raises_when_both_api_key_and_jwt_fail():
    """When both API key lookup and JWT fail, should raise WebSocketException."""
    fake_ws = MagicMock()

    mock_result = MagicMock()
    mock_result.fetchone.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__.return_value = mock_db
    mock_session_ctx.__aexit__.return_value = False

    with (
        patch(
            "app.middleware.websocket_auth.async_session_factory",
            return_value=mock_session_ctx,
        ),
        patch(
            "app.middleware.websocket_auth._authenticate_websocket_jwt",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch("app.middleware.websocket_auth.settings") as mock_settings,
    ):
        mock_settings.demo_api_key = None
        with pytest.raises(WebSocketException):
            await authenticate_websocket(fake_ws, api_key="invalid-everything")  # pragma: allowlist secret
