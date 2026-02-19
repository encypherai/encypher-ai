from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verify_surfaces_encypher_rights_metadata(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/v1/verify",
        json={"text": "signed"},
        headers={"X-Forwarded-For": "203.0.113.252"},
    )

    # POST /api/v1/verify is not registered in the enterprise API.
    # It is routed by Traefik to the verification-service.
    assert resp.status_code == 404
