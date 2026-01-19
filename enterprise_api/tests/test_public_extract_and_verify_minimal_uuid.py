import pytest


@pytest.mark.asyncio
async def test_public_extract_and_verify_minimal_uuid_basic(
    async_client,
    auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=auth_headers,
        json={
            "document_id": "doc_adv_minimal_uuid_verify_001",
            "text": "Sentence one. Sentence two.",
            "manifest_mode": "minimal_uuid",
        },
    )

    assert response.status_code == 201
    sign_payload = response.json()
    embedded_content = sign_payload["embedded_content"]

    verify_response = await async_client.post(
        "/api/v1/public/extract-and-verify",
        json={"text": embedded_content},
    )

    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["valid"] is True
    assert verify_payload["metadata"]["format"] == "c2pa"
    assert verify_payload["metadata"]["custom_metadata"]["manifest_mode"] == "minimal_uuid"
    assert verify_payload["document"]["document_id"] == "doc_adv_minimal_uuid_verify_001"
