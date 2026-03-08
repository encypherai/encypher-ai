from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app import dependencies
from app.config import settings
from app.dependencies import _normalize_org_context, get_current_organization


@pytest.mark.asyncio
async def test_get_current_organization_composes_org_context_via_auth_service(monkeypatch):
    monkeypatch.setattr(settings, "compose_org_context_via_auth_service", True)
    monkeypatch.setattr(settings, "internal_service_token", "secret-token")

    mock_credentials = MagicMock()
    mock_credentials.credentials = "ency_test_key"

    mock_request = MagicMock()
    mock_request.state = MagicMock()

    mock_background_tasks = MagicMock()

    with (
        patch.object(dependencies, "key_service_client") as mock_key_service_client,
        patch("app.services.auth_service_client.httpx.AsyncClient") as mock_async_client,
    ):
        mock_key_service_client.validate_key_minimal = AsyncMock(
            return_value={
                "key_id": "key_123",
                "organization_id": "org_123",
                "user_id": "user_123",
                "permissions": ["sign", "verify", "lookup"],
            }
        )

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "success": True,
            "data": {
                "id": "org_123",
                "name": "Acme",
                "tier": "professional",
                "features": {"byok": True},
                "monthly_api_limit": 100000,
                "monthly_api_usage": 5,
                "coalition_member": True,
                "coalition_rev_share": 70,
                "certificate_pem": None,
                "account_type": "organization",
                "display_name": "The Acme Times",
                "anonymous_publisher": False,
            },
        }

        http_client = AsyncMock()
        http_client.get = AsyncMock(return_value=response)
        mock_async_client.return_value.__aenter__.return_value = http_client
        mock_async_client.return_value.__aexit__.return_value = None

        result = await get_current_organization(
            request=mock_request,
            background_tasks=mock_background_tasks,
            credentials=mock_credentials,
        )

    assert result["organization_id"] == "org_123"
    assert result["organization_name"] == "Acme"
    assert result["tier"] == "free"  # TEAM_166: 'professional' coerced to 'free'
    assert result["byok_enabled"] is True
    assert result["can_sign"] is True
    assert result["can_verify"] is True
    assert result["can_lookup"] is True
    assert result["monthly_api_limit"] == 100000
    assert result["monthly_api_usage"] == 5
    assert result["account_type"] == "organization"
    assert result["display_name"] == "The Acme Times"
    assert result["anonymous_publisher"] is False
    assert result["publisher_identity_base"] == "The Acme Times"
    assert result["publisher_attribution"] == "The Acme Times · Powered by Encypher"
    assert mock_request.state.organization_id == "org_123"
    assert mock_request.state.user_id == "user_123"
    assert mock_request.state.api_key_id == "key_123"
    assert mock_request.state.api_key_prefix == "fixture-toke"


@pytest.mark.asyncio
async def test_get_current_organization_prefers_composed_auth_context_over_fallbacks(monkeypatch):
    monkeypatch.setattr(settings, "compose_org_context_via_auth_service", True)

    mock_credentials = MagicMock()
    mock_credentials.credentials = "fixture-token-alpha"

    mock_request = MagicMock()
    mock_request.state = MagicMock()

    mock_background_tasks = MagicMock()

    composed_context = {
        "api_key_id": "key_123",
        "organization_id": "org_123",
        "organization_name": "Acme",
        "tier": "enterprise",
        "features": {"audit_logs": True},
        "permissions": ["sign", "verify", "lookup"],
        "user_id": "user_123",
    }

    with (
        patch.object(
            dependencies,
            "_resolve_org_context_via_composed_auth_service",
            new=AsyncMock(return_value=composed_context),
        ) as mock_composed,
        patch.object(dependencies.key_service_client, "validate_key", new=AsyncMock()) as mock_validate_key,
        patch.object(dependencies, "_get_org_context_from_jwt_access_token", new=AsyncMock()) as mock_jwt,
    ):
        result = await get_current_organization(
            request=mock_request,
            background_tasks=mock_background_tasks,
            credentials=mock_credentials,
        )

    mock_composed.assert_awaited_once_with("fixture-token-alpha")
    mock_validate_key.assert_not_awaited()
    mock_jwt.assert_not_awaited()
    assert result["organization_id"] == "org_123"
    assert result["api_key_id"] == "key_123"
    assert mock_request.state.organization_id == "org_123"
    assert mock_request.state.user_id == "user_123"
    assert mock_request.state.api_key_id == "key_123"
    assert mock_request.state.api_key_prefix == "fixture-toke"


@pytest.mark.asyncio
async def test_get_current_organization_falls_back_to_key_service_before_jwt(monkeypatch):
    monkeypatch.setattr(settings, "compose_org_context_via_auth_service", True)

    mock_credentials = MagicMock()
    mock_credentials.credentials = "fallback-token-beta"

    mock_request = MagicMock()
    mock_request.state = MagicMock()

    mock_background_tasks = MagicMock()

    key_service_context = {
        "api_key_id": "key_fallback",
        "organization_id": "org_fallback",
        "organization_name": "Fallback Org",
        "tier": "enterprise",
        "features": {},
        "permissions": ["sign", "verify"],
        "user_id": "user_fallback",
    }

    with (
        patch.object(
            dependencies,
            "_resolve_org_context_via_composed_auth_service",
            new=AsyncMock(return_value=None),
        ) as mock_composed,
        patch.object(
            dependencies.key_service_client,
            "validate_key",
            new=AsyncMock(return_value=key_service_context),
        ) as mock_validate_key,
        patch.object(dependencies, "_get_org_context_from_jwt_access_token", new=AsyncMock()) as mock_jwt,
    ):
        result = await get_current_organization(
            request=mock_request,
            background_tasks=mock_background_tasks,
            credentials=mock_credentials,
        )

    mock_composed.assert_awaited_once_with("fallback-token-beta")
    mock_validate_key.assert_awaited_once_with("fallback-token-beta")
    mock_jwt.assert_not_awaited()
    assert result["organization_id"] == "org_fallback"
    assert result["can_sign"] is True
    assert result["can_verify"] is True
    assert result["can_lookup"] is False
    assert mock_request.state.organization_id == "org_fallback"
    assert mock_request.state.user_id == "user_fallback"
    assert mock_request.state.api_key_id == "key_fallback"
    assert mock_request.state.api_key_prefix == "fallback-tok"


def test_normalize_org_context_expands_read_permission_to_lookup_aliases():
    result = _normalize_org_context(
        {
            "permissions": ["read"],
            "features": {},
        }
    )

    assert result["permissions"] == ["lookup", "read"]
    assert result["can_lookup"] is True


def test_normalize_org_context_expands_admin_permission_to_lookup_aliases():
    result = _normalize_org_context(
        {
            "permissions": ["admin"],
            "features": {},
        }
    )

    assert "admin" in result["permissions"]
    assert "lookup" in result["permissions"]
    assert "read" in result["permissions"]
    assert result["can_sign"] is True
    assert result["can_verify"] is True
    assert result["can_lookup"] is True
