"""
Tests for public endpoint payload limits.

Note: /api/v1/public/extract-and-verify is deprecated (returns 410).
These tests verify that the deprecated endpoint returns 410.
"""

import pytest
from httpx import AsyncClient

MAX_VERIFY_BATCH_BYTES = 256 * 1024


@pytest.mark.asyncio
async def test_public_extract_and_verify_is_deprecated(async_client: AsyncClient) -> None:
    """Test that /public/extract-and-verify returns 410 Gone."""
    response = await async_client.post(
        "/api/v1/public/extract-and-verify",
        json={"text": "test"},
    )
    assert response.status_code == 410


@pytest.mark.asyncio
async def test_public_verify_batch_rejects_oversized_payload(async_client: AsyncClient) -> None:
    signature = "a" * MAX_VERIFY_BATCH_BYTES
    response = await async_client.post(
        "/api/v1/public/verify/batch",
        json={"references": [{"ref_id": "a3f9c2e1", "signature": signature}]},
    )
    assert response.status_code == 413
