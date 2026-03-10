"""
Tests for /sign endpoint with advanced options.

Note: /sign/advanced is deprecated (returns 410). Use /sign with options instead.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sign_with_advanced_options_allowed_for_free_tier(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    """TEAM_166: Free tier can use advanced options like manifest_mode."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "Hello world. Advanced signing.",
            "options": {
                "manifest_mode": "micro",
            },
        },
        headers=starter_auth_headers,
    )

    # TEAM_166: Free tier now has access to manifest_mode
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_sign_with_advanced_options_success_free_tier(
    async_client: AsyncClient,
    professional_auth_headers: dict,
) -> None:
    """TEAM_166: Free tier (legacy professional key) can use advanced options."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "Hello world. Advanced signing.",
            "options": {
                "manifest_mode": "micro",
            },
        },
        headers=professional_auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data.get("data", {}).get("document", {}).get("document_id") is not None
