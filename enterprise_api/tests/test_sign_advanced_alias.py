"""
Tests for /sign endpoint with advanced options.

Note: /sign/advanced is deprecated (returns 410). Use /sign with options instead.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_sign_with_advanced_options_requires_professional_tier(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    """Test that advanced options (like manifest_mode) require professional tier."""
    with patch("app.dependencies.key_service_client.validate_key", new=AsyncMock(return_value=None)):
        response = await async_client.post(
            "/api/v1/sign",
            json={
                "text": "Hello world. Advanced signing.",
                "options": {
                    "manifest_mode": "minimal_uuid",
                },
            },
            headers=starter_auth_headers,
        )

    # Should be forbidden for starter tier when using advanced options
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sign_with_advanced_options_success_professional(
    async_client: AsyncClient,
    professional_auth_headers: dict,
) -> None:
    """Test that professional tier can use advanced options."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "Hello world. Advanced signing.",
            "options": {
                "manifest_mode": "minimal_uuid",
            },
        },
        headers=professional_auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data.get("data", {}).get("document", {}).get("document_id") is not None
