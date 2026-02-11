from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app import dependencies
from app.dependencies import get_current_organization
from app.config import settings


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
