"""
Tests for minimal UUID signing and verification round-trip.

Note: /api/v1/public/extract-and-verify is deprecated (returns 410).
Use /api/v1/verify/advanced instead.
"""

import pytest


@pytest.mark.asyncio
async def test_minimal_uuid_sign_and_verify_round_trip(
    async_client,
    auth_headers: dict,
) -> None:
    """Test that minimal_uuid signed content can be verified."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Sentence one. Sentence two.",
            "options": {
                "manifest_mode": "minimal_uuid",
            },
        },
    )

    assert response.status_code == 201
    sign_payload = response.json()
    # Unified response: data.document.signed_text
    data = sign_payload.get("data", {})
    document = data.get("document", {})
    embedded_content = document.get("signed_text")
    assert embedded_content is not None, "signed_text should be present"

    # Verify using /verify/advanced endpoint
    verify_response = await async_client.post(
        "/api/v1/verify/advanced",
        headers=auth_headers,
        json={"text": embedded_content},
    )

    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    verdict = verify_payload.get("data", {})
    assert verdict.get("valid") is True or verdict.get("embeddings_found") is True
