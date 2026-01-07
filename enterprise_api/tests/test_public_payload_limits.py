import pytest
from httpx import AsyncClient


MAX_EXTRACT_AND_VERIFY_BYTES = 2 * 1024 * 1024
MAX_VERIFY_BATCH_BYTES = 256 * 1024


@pytest.mark.asyncio
async def test_public_extract_and_verify_rejects_oversized_payload(async_client: AsyncClient) -> None:
    text = "a" * (MAX_EXTRACT_AND_VERIFY_BYTES + 1)
    response = await async_client.post(
        "/api/v1/public/extract-and-verify",
        json={"text": text},
    )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_public_verify_batch_rejects_oversized_payload(async_client: AsyncClient) -> None:
    signature = "a" * MAX_VERIFY_BATCH_BYTES
    response = await async_client.post(
        "/api/v1/public/verify/batch",
        json={"references": [{"ref_id": "a3f9c2e1", "signature": signature}]},
    )
    assert response.status_code == 413
