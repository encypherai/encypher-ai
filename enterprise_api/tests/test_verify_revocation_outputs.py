from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verify_doc_revoked_is_not_tampered(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/v1/verify",
        json={"text": "signed"},
        headers={"X-Forwarded-For": "203.0.113.250"},
    )

    assert resp.status_code == 410
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "ENDPOINT_DEPRECATED"


@pytest.mark.asyncio
async def test_verify_cert_revoked_is_not_tampered(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/v1/verify",
        json={"text": "signed"},
        headers={"X-Forwarded-For": "203.0.113.251"},
    )

    assert resp.status_code == 410
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "ENDPOINT_DEPRECATED"


@pytest.mark.asyncio
async def test_verify_revocation_unknown_is_exposed(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/v1/verify",
        json={"text": "signed"},
        headers={"X-Forwarded-For": "203.0.113.252"},
    )

    assert resp.status_code == 410
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "ENDPOINT_DEPRECATED"
