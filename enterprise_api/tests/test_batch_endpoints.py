from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


def _batch_request(*, items: int) -> dict:
    return {
        "mode": "c2pa",
        "segmentation_level": "sentence",
        "idempotency_key": "idem-key-1234",
        "items": [
            {
                "document_id": f"doc-{idx}",
                "text": f"payload-{idx}",
                "title": f"title-{idx}",
            }
            for idx in range(items)
        ],
    }


async def _fake_batch_response(*, correlation_id: str, **_kwargs) -> dict:
    return {
        "success": True,
        "batch_id": "batch_test",
        "data": None,
        "error": None,
        "correlation_id": correlation_id,
    }


# TEAM_166: Batch operations require Enterprise tier (free tier gets 403)

@pytest.mark.asyncio
async def test_batch_sign_rejected_for_free_tier(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    """Free tier (starter key) should be rejected for batch sign."""
    with patch("app.routers.batch.batch_service.sign_batch", new=AsyncMock(side_effect=_fake_batch_response)):
        response = await async_client.post(
            "/api/v1/batch/sign",
            json=_batch_request(items=2),
            headers=starter_auth_headers,
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_batch_sign_rejects_single_item_for_enterprise(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    """Enterprise tier should still reject single-item batch."""
    with patch("app.routers.batch.batch_service.sign_batch", new=AsyncMock(side_effect=_fake_batch_response)):
        response = await async_client.post(
            "/api/v1/batch/sign",
            json=_batch_request(items=1),
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_verify_rejected_for_free_tier(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    """Free tier should be rejected for batch verify."""
    with patch("app.routers.batch.batch_service.verify_batch", new=AsyncMock(side_effect=_fake_batch_response)):
        response = await async_client.post(
            "/api/v1/batch/verify",
            json=_batch_request(items=2),
            headers=starter_auth_headers,
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_batch_verify_rejects_single_item_for_enterprise(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    """Enterprise tier should still reject single-item batch."""
    with patch("app.routers.batch.batch_service.verify_batch", new=AsyncMock(side_effect=_fake_batch_response)):
        response = await async_client.post(
            "/api/v1/batch/verify",
            json=_batch_request(items=1),
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_verify_allows_enterprise_multi_document(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    """Enterprise tier should allow multi-document batch verify."""
    with patch("app.routers.batch.batch_service.verify_batch", new=AsyncMock(side_effect=_fake_batch_response)):
        response = await async_client.post(
            "/api/v1/batch/verify",
            json=_batch_request(items=2),
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["batch_id"] == "batch_test"
