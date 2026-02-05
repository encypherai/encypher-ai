import uuid

import pytest


@pytest.mark.asyncio
async def test_sign_advanced_minimal_uuid_round_trip_and_payload(
    async_client,
    auth_headers: dict,
) -> None:
    original_text = "猫 猫. Cafe\u0301 latte."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": original_text,
            "options": {
                "manifest_mode": "minimal_uuid",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True

    # Unified response: data.document.signed_text
    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_content = document.get("signed_text")
    assert isinstance(embedded_content, str)

    # Ensure the service returns NFC-normalized text.
    assert "Cafe\u0301" not in embedded_content
    assert "Café" in embedded_content

    metadata = document.get("metadata", {})
    assert isinstance(metadata, dict)
    assert metadata.get("instance_id") is not None


@pytest.mark.asyncio
async def test_sign_advanced_minimal_uuid_disable_c2pa_returns_basic_metadata(
    async_client,
    auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Sentence one. Sentence two.",
            "options": {
                "manifest_mode": "minimal_uuid",
                "disable_c2pa": True,
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()
    data = payload.get("data", {})
    document = data.get("document", {})
    metadata = document.get("metadata", {})
    assert isinstance(metadata, dict)
    assert metadata.get("instance_id") is None
