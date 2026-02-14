"""Regression tests for demo key gating."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

import app.dependencies as dependencies
from app.config import settings
from app.dependencies import get_current_organization
from app.middleware.api_key_auth import authenticate_api_key


@pytest.mark.asyncio
async def test_demo_key_blocked_in_production_without_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "demo_api_key", "demo-key-123")
    monkeypatch.setattr(settings, "demo_key_allowlist", "")

    db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await authenticate_api_key(api_key="demo-key-123", db=db)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_demo_key_allowed_in_production_with_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "demo_api_key", "demo-key-123")
    monkeypatch.setattr(settings, "demo_key_allowlist", "demo-key-123")

    db = AsyncMock()

    result = await authenticate_api_key(api_key="demo-key-123", db=db)

    assert result["is_demo"] is True
    assert result["organization_id"] == settings.demo_organization_id


@pytest.mark.asyncio
async def test_get_current_organization_blocks_demo_key_in_production_without_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "demo_key_allowlist", "")

    credentials = MagicMock()
    credentials.credentials = "demo-api-key-for-testing"
    request = MagicMock()
    request.state = MagicMock()
    background_tasks = MagicMock()

    with patch.object(dependencies, "key_service_client") as mock_service_client:
        mock_service_client.validate_key = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await get_current_organization(
                request=request,
                background_tasks=background_tasks,
                credentials=credentials,
            )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_organization_allows_allowlisted_demo_key_in_production(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "demo_key_allowlist", "demo-api-key-for-testing")

    credentials = MagicMock()
    credentials.credentials = "demo-api-key-for-testing"
    request = MagicMock()
    request.state = MagicMock()
    background_tasks = MagicMock()

    with patch.object(dependencies, "key_service_client") as mock_service_client:
        mock_service_client.validate_key = AsyncMock(return_value=None)
        result = await get_current_organization(
            request=request,
            background_tasks=background_tasks,
            credentials=credentials,
        )

    assert result["organization_id"] == "org_demo"
    assert result["is_demo"] is True


@pytest.mark.asyncio
async def test_get_current_organization_accepts_jwt_with_default_org():
    credentials = MagicMock()
    credentials.credentials = "jwt-access-token"
    request = MagicMock()
    request.state = MagicMock()
    background_tasks = MagicMock()

    mock_verify_response = MagicMock()
    mock_verify_response.status_code = 200
    mock_verify_response.json.return_value = {
        "success": True,
        "data": {
            "id": "user_123",
            "email": "member@example.com",
            "default_organization_id": "org_jwt_123",
        },
    }

    mock_http_client = AsyncMock()
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None
    mock_http_client.post.return_value = mock_verify_response

    with (
        patch.object(dependencies, "key_service_client") as mock_key_service,
        patch("app.dependencies.httpx.AsyncClient", return_value=mock_http_client),
        patch.object(dependencies.auth_service_client, "get_organization_context", new_callable=AsyncMock) as mock_get_org,
    ):
        mock_key_service.validate_key = AsyncMock(return_value=None)
        mock_key_service.validate_key_minimal = AsyncMock(return_value=None)
        mock_get_org.return_value = {
            "name": "JWT Org",
            "tier": "free",
            "features": {},
            "monthly_api_limit": 10000,
            "monthly_api_usage": 25,
            "coalition_member": True,
            "coalition_rev_share": 65,
        }

        result = await get_current_organization(
            request=request,
            background_tasks=background_tasks,
            credentials=credentials,
        )

    assert result["organization_id"] == "org_jwt_123"
    assert result["user_id"] == "user_123"
    assert result["can_sign"] is True


@pytest.mark.asyncio
async def test_get_current_organization_rejects_jwt_without_default_org():
    credentials = MagicMock()
    credentials.credentials = "jwt-access-token"
    request = MagicMock()
    request.state = MagicMock()
    background_tasks = MagicMock()

    mock_verify_response = MagicMock()
    mock_verify_response.status_code = 200
    mock_verify_response.json.return_value = {
        "success": True,
        "data": {
            "id": "user_123",
            "email": "member@example.com",
            "default_organization_id": None,
        },
    }

    mock_http_client = AsyncMock()
    mock_http_client.__aenter__.return_value = mock_http_client
    mock_http_client.__aexit__.return_value = None
    mock_http_client.post.return_value = mock_verify_response

    with (
        patch.object(dependencies, "key_service_client") as mock_key_service,
        patch("app.dependencies.httpx.AsyncClient", return_value=mock_http_client),
    ):
        mock_key_service.validate_key = AsyncMock(return_value=None)
        mock_key_service.validate_key_minimal = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_organization(
                request=request,
                background_tasks=background_tasks,
                credentials=credentials,
            )

    assert exc_info.value.status_code == 401
