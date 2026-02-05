"""
Tests for NMA (News Media Alliance) member flag functionality.

NMA members on starter tier have special features enabled (sentence_tracking, merkle_enabled)
but the unified /sign endpoint enforces tier-based feature gating.

Note: /sign/advanced is deprecated (returns 410). Use /sign with options instead.
Advanced options like segmentation_level and index_for_attribution require Professional tier.
"""

import pytest
from httpx import AsyncClient

from app.dependencies import DEMO_KEYS


def test_nma_demo_key_exists():
    """Verify NMA demo key is configured."""
    assert "nma-starter-api-key-for-testing" in DEMO_KEYS
    nma_key = DEMO_KEYS["nma-starter-api-key-for-testing"]
    assert nma_key["tier"] == "starter"
    assert nma_key["nma_member"] is True
    assert nma_key["features"]["sentence_tracking"] is True
    assert nma_key["features"]["merkle_enabled"] is True


def test_regular_starter_key_not_nma():
    """Verify regular starter key is not NMA member."""
    assert "starter-api-key-for-testing" in DEMO_KEYS
    starter_key = DEMO_KEYS["starter-api-key-for-testing"]
    assert starter_key["tier"] == "starter"
    assert starter_key.get("nma_member", False) is False


@pytest.mark.asyncio
async def test_nma_member_can_use_basic_sign(async_client: AsyncClient):
    """NMA members on starter tier can use basic signing."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "This is a test document from an NMA member. The News Media Alliance partnership.",
        },
        headers={"Authorization": "Bearer nma-starter-api-key-for-testing"},
    )
    assert response.status_code == 201, f"NMA member should use basic /sign: {response.text}"
    data = response.json()
    document = data.get("data", {}).get("document", {})
    assert document.get("document_id") is not None
    assert document.get("signed_text") is not None


@pytest.mark.asyncio
async def test_regular_starter_cannot_access_advanced_options(async_client: AsyncClient):
    """Regular starter tier users cannot use advanced signing options."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "This is a test document from a regular starter user.",
            "options": {
                "segmentation_level": "sentence",
                "manifest_mode": "minimal_uuid",
            },
        },
        headers={"Authorization": "Bearer starter-api-key-for-testing"},
    )
    assert response.status_code == 403, f"Regular starter should be denied advanced options: {response.text}"


@pytest.mark.asyncio
async def test_nma_member_denied_advanced_options_without_tier(async_client: AsyncClient):
    """NMA members on starter tier are denied advanced options that require Professional tier."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "This is a test document with attribution indexing.",
            "options": {
                "segmentation_level": "sentence",
                "index_for_attribution": True,
            },
        },
        headers={"Authorization": "Bearer nma-starter-api-key-for-testing"},
    )
    # NMA members on starter tier are denied advanced options - tier gating is enforced
    assert response.status_code == 403, f"NMA member should be denied advanced options: {response.text}"


@pytest.mark.asyncio
async def test_professional_tier_can_access_advanced_options(async_client: AsyncClient):
    """Professional tier users can use advanced signing options."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "This is a test document from Professional tier.",
            "options": {
                "segmentation_level": "sentence",
                "index_for_attribution": True,
            },
        },
        headers={"Authorization": "Bearer professional-api-key-for-testing"},
    )
    assert response.status_code == 201, f"Professional should access advanced options: {response.text}"


@pytest.mark.asyncio
async def test_regular_starter_can_use_basic_sign(async_client: AsyncClient):
    """Regular starter tier users can use basic /sign endpoint without advanced options."""
    response = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "This is a basic signing test for regular starter tier.",
        },
        headers={"Authorization": "Bearer starter-api-key-for-testing"},
    )
    assert response.status_code == 201, f"Starter should use basic /sign: {response.text}"
