import pytest


@pytest.mark.asyncio
async def test_sign_advanced_lightweight_uuid_round_trip_and_byte_spans(
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
                "manifest_mode": "lightweight_uuid",
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
