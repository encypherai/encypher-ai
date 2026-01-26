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
