import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_sign_advanced_requires_professional_tier(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    with patch("app.dependencies.key_service_client.validate_key", new=AsyncMock(return_value=None)):
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_001",
                "text": "Hello world. Advanced signing.",
            },
            headers=starter_auth_headers,
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sign_advanced_success_professional(
    async_client: AsyncClient,
    professional_auth_headers: dict,
) -> None:
    mocked = {
        "success": True,
        "document_id": "doc_adv_001",
        "merkle_tree": None,
        "embeddings": [],
        "embedded_content": "signed",
        "statistics": {"duration_ms": 1},
        "metadata": None,
    }

    with (
        patch("app.dependencies.key_service_client.validate_key", new=AsyncMock(return_value=None)),
        patch("app.routers.signing.encode_document_with_embeddings", new=AsyncMock(return_value=mocked)),
    ):
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_001",
                "text": "Hello world. Advanced signing.",
            },
            headers=professional_auth_headers,
        )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["document_id"] == "doc_adv_001"
