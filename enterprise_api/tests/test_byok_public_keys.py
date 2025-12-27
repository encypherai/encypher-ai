from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


SAMPLE_ED25519_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGb9F2CMCwPz5K8VdBkPbVkPJPvPZMhLGpIRvXe5Rnvs=
-----END PUBLIC KEY-----"""


@pytest.mark.asyncio
async def test_byok_public_keys_requires_business_tier(
    async_client: AsyncClient,
    starter_auth_headers: dict,
    professional_auth_headers: dict,
) -> None:
    response = await async_client.get("/api/v1/byok/public-keys", headers=starter_auth_headers)
    assert response.status_code == 403

    response = await async_client.get("/api/v1/byok/public-keys", headers=professional_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_byok_public_keys_list_business_success(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    with patch(
        "app.services.admin_service.PublicKeyService.list_public_keys",
        new=AsyncMock(return_value={"success": True, "data": {"keys": [], "total": 0}}),
    ):
        response = await async_client.get("/api/v1/byok/public-keys", headers=business_auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["keys"] == []


@pytest.mark.asyncio
async def test_byok_public_keys_register_business_success(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    mock_result = {
        "success": True,
        "data": {
            "id": "pk_123",
            "organization_id": "org_business",
            "key_name": "Test Key",
            "key_algorithm": "Ed25519",
            "key_fingerprint": "SHA256:abc123",
            "public_key_pem": SAMPLE_ED25519_PUBLIC_KEY,
            "is_active": True,
            "created_at": "2025-01-01T00:00:00Z",
        },
    }

    with patch(
        "app.services.admin_service.PublicKeyService.register_public_key",
        new=AsyncMock(return_value=mock_result),
    ):
        response = await async_client.post(
            "/api/v1/byok/public-keys",
            json={"public_key_pem": SAMPLE_ED25519_PUBLIC_KEY, "key_name": "Test Key"},
            headers=business_auth_headers,
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["id"] == "pk_123"


@pytest.mark.asyncio
async def test_byok_public_keys_revoke_business_success(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    with patch(
        "app.services.admin_service.PublicKeyService.revoke_public_key",
        new=AsyncMock(return_value={"success": True, "data": {"key_id": "pk_123", "revoked_at": "2025-01-01T00:00:00Z"}}),
    ):
        response = await async_client.delete(
            "/api/v1/byok/public-keys/pk_123?reason=Key%20compromised",
            headers=business_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["key_id"] == "pk_123"
