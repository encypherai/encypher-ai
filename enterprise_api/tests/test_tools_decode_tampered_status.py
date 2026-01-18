from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tools_decode_is_deprecated(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/tools/decode",
        json={"encoded_text": "payload"},
    )

    assert response.status_code == 410
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["message"] == "Deprecated endpoint. Use /api/v1/verify instead."


@pytest.mark.asyncio
async def test_tools_encode_is_deprecated(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/tools/encode",
        json={"original_text": "payload"},
    )

    assert response.status_code == 410
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["message"] == "Deprecated endpoint. Use /api/v1/sign/advanced (authenticated) instead."
