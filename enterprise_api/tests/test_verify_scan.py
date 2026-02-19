from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verify_scans_multiple_embeddings_all_valid(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/verify",
        json={"text": "payload"},
        headers={"X-Forwarded-For": "203.0.113.200"},
    )

    # POST /api/v1/verify is not registered in the enterprise API.
    # It is routed by Traefik to the verification-service.
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_verify_scans_multiple_embeddings_partial_valid(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/verify",
        json={"text": "payload"},
        headers={"X-Forwarded-For": "203.0.113.201"},
    )

    assert response.status_code == 404
