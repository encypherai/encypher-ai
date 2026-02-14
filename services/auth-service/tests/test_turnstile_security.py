"""Tests for Turnstile-backed auth hardening primitives."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.schemas import UserCreate, UserLogin
from app.services.turnstile_service import verify_turnstile_token


def test_user_create_accepts_turnstile_token_alias() -> None:
    payload = UserCreate(
        email="user@example.com",
        password="SecurePass123!",
        name="User",
        turnstileToken="cf-token",
    )

    assert payload.turnstile_token == "cf-token"


def test_user_login_accepts_turnstile_token_field() -> None:
    payload = UserLogin(
        email="user@example.com",
        password="SecurePass123!",
        turnstile_token="cf-token",
    )

    assert payload.turnstile_token == "cf-token"


@pytest.mark.asyncio
async def test_verify_turnstile_disabled_short_circuits() -> None:
    fake_settings = SimpleNamespace(TURNSTILE_ENABLED=False)

    with patch("app.services.turnstile_service.settings", fake_settings):
        assert await verify_turnstile_token("any") is True


@pytest.mark.asyncio
async def test_verify_turnstile_enabled_with_missing_secret_fails() -> None:
    fake_settings = SimpleNamespace(
        TURNSTILE_ENABLED=True,
        TURNSTILE_SECRET_KEY="",
        TURNSTILE_VERIFY_URL="https://example.com",
    )

    with patch("app.services.turnstile_service.settings", fake_settings):
        assert await verify_turnstile_token("token") is False


@pytest.mark.asyncio
async def test_verify_turnstile_success_response() -> None:
    fake_settings = SimpleNamespace(
        TURNSTILE_ENABLED=True,
        TURNSTILE_SECRET_KEY="secret",
        TURNSTILE_VERIFY_URL="https://example.com",
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with (
        patch("app.services.turnstile_service.settings", fake_settings),
        patch("app.services.turnstile_service.httpx.AsyncClient") as mock_async_client,
    ):
        mock_async_client.return_value.__aenter__.return_value = mock_client
        mock_async_client.return_value.__aexit__.return_value = None
        assert await verify_turnstile_token("token") is True


@pytest.mark.asyncio
async def test_verify_turnstile_failure_response() -> None:
    fake_settings = SimpleNamespace(
        TURNSTILE_ENABLED=True,
        TURNSTILE_SECRET_KEY="secret",
        TURNSTILE_VERIFY_URL="https://example.com",
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": False}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with (
        patch("app.services.turnstile_service.settings", fake_settings),
        patch("app.services.turnstile_service.httpx.AsyncClient") as mock_async_client,
    ):
        mock_async_client.return_value.__aenter__.return_value = mock_client
        mock_async_client.return_value.__aexit__.return_value = None
        assert await verify_turnstile_token("token") is False
