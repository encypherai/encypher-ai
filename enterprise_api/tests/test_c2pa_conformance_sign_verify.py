import pytest
from encypher.core.unicode_metadata import UnicodeMetadata


def _get_assertion_payload(assertions: list[dict], label: str) -> dict | None:
    for assertion in assertions:
        if assertion.get("label") == label:
            return assertion
    return None


@pytest.mark.asyncio
async def test_sign_advanced_minimal_uuid_c2pa_conformance(async_client, auth_headers: dict) -> None:
    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=auth_headers,
        json={
            "document_id": "doc_c2pa_conformance_001",
            "text": "Sentence one. Sentence two.",
            "manifest_mode": "minimal_uuid",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    embedded_content = payload["embedded_content"]

    extracted = UnicodeMetadata.extract_metadata(embedded_content)
    assert extracted is not None
    assert extracted.get("@context") == "https://c2pa.org/schemas/v2.3/c2pa.jsonld"
    assert extracted.get("claim_label") == "c2pa.claim.v2"

    assertions = extracted.get("assertions")
    assert isinstance(assertions, list)

    actions_assertion = _get_assertion_payload(assertions, "c2pa.actions.v2")
    assert actions_assertion is not None
    actions = actions_assertion.get("data", {}).get("actions", [])
    action_labels = {action.get("label") for action in actions}
    assert "c2pa.created" in action_labels
    assert "c2pa.watermarked" in action_labels

    metadata_assertion = _get_assertion_payload(assertions, "c2pa.metadata")
    assert metadata_assertion is not None
    metadata = metadata_assertion.get("data", {})
    assert metadata.get("@context") == "https://schema.org"
    assert metadata.get("identifier") == "doc_c2pa_conformance_001"
    assert metadata.get("manifest_mode") == "minimal_uuid"


@pytest.mark.asyncio
async def test_extract_and_verify_includes_c2pa_conformance_metadata(async_client, auth_headers: dict) -> None:
    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=auth_headers,
        json={
            "document_id": "doc_c2pa_conformance_002",
            "text": "Sentence one. Sentence two.",
            "manifest_mode": "minimal_uuid",
        },
    )

    assert response.status_code == 201
    embedded_content = response.json()["embedded_content"]

    verify_response = await async_client.post(
        "/api/v1/public/extract-and-verify",
        json={"text": embedded_content},
    )

    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["valid"] is True
    assert verify_payload["metadata"]["format"] == "c2pa"
    assert verify_payload["metadata"]["custom_metadata"]["manifest_mode"] == "minimal_uuid"
    assert verify_payload["document"]["document_id"] == "doc_c2pa_conformance_002"
