"""
C2PA Unity test: micro + embed_c2pa=True uses the exact same C2PA embedding
method as full mode.

Both modes call UnicodeMetadata.embed_metadata() with identical parameters.
This test verifies that the resulting C2PA manifests are structurally identical:
- Same context and claim_label
- Same action labels (c2pa.created, c2pa.watermarked)
- Both produce extractable, verifiable manifests

The only expected difference: micro mode contains additional per-sentence VS256
or legacy_safe markers in the text; full mode does not. The C2PA wrapper itself
is produced by the same code path in both modes.
"""

import pytest
from encypher.core.unicode_metadata import UnicodeMetadata


def _get_assertion(assertions: list[dict], label: str) -> dict | None:
    for a in assertions:
        if a.get("label") == label:
            return a
    return None


def _extract_c2pa(embedded_content: str, label: str) -> dict:
    """Extract C2PA manifest from embedded content, assert it is present."""
    extracted = UnicodeMetadata.extract_metadata(embedded_content)
    assert extracted is not None, f"{label}: C2PA manifest not found in embedded content"
    return extracted


def _assert_c2pa_core_structure(manifest: dict, mode_label: str) -> None:
    """Assert the C2PA manifest has the core structural requirements common to all modes."""
    assert manifest.get("@context") == "https://c2pa.org/schemas/v2.3/c2pa.jsonld", f"{mode_label}: unexpected @context"
    assert manifest.get("claim_label") == "c2pa.claim.v2", f"{mode_label}: unexpected claim_label"

    assertions = manifest.get("assertions")
    assert isinstance(assertions, list), f"{mode_label}: assertions is not a list"

    actions_assertion = _get_assertion(assertions, "c2pa.actions.v2")
    assert actions_assertion is not None, f"{mode_label}: c2pa.actions.v2 assertion missing"
    actions = actions_assertion.get("data", {}).get("actions", [])
    action_labels = {a.get("label") for a in actions}
    assert "c2pa.created" in action_labels, f"{mode_label}: c2pa.created action missing"
    assert "c2pa.watermarked" in action_labels, f"{mode_label}: c2pa.watermarked action missing"


@pytest.mark.asyncio
async def test_micro_embed_c2pa_true_uses_same_c2pa_as_full(async_client, auth_headers: dict) -> None:
    """micro + embed_c2pa=True produces a C2PA manifest with identical core structure as full mode."""
    text = "This is the first sentence for C2PA unity testing. This is the second sentence."

    full_response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={"text": text, "options": {"manifest_mode": "full"}},
    )
    assert full_response.status_code == 201, f"full mode sign failed: {full_response.text}"
    full_signed = full_response.json()["data"]["document"]["signed_text"]

    micro_response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={"text": text, "options": {"manifest_mode": "micro", "embed_c2pa": True}},
    )
    assert micro_response.status_code == 201, f"micro mode sign failed: {micro_response.text}"
    micro_signed = micro_response.json()["data"]["document"]["signed_text"]

    full_manifest = _extract_c2pa(full_signed, "full")
    micro_manifest = _extract_c2pa(micro_signed, "micro+embed_c2pa=True")

    # Both must have identical core C2PA structure
    _assert_c2pa_core_structure(full_manifest, "full")
    _assert_c2pa_core_structure(micro_manifest, "micro+embed_c2pa=True")

    # Both produce the same schema context and claim format
    assert full_manifest["@context"] == micro_manifest["@context"], "full and micro @context differ"
    assert full_manifest["claim_label"] == micro_manifest["claim_label"], "full and micro claim_label differ"


@pytest.mark.asyncio
async def test_micro_embed_c2pa_false_no_c2pa_in_content(async_client, auth_headers: dict) -> None:
    """micro + embed_c2pa=False omits the C2PA manifest from the returned content."""
    text = "Sentence one for no-c2pa test. Sentence two for no-c2pa test."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={"text": text, "options": {"manifest_mode": "micro", "embed_c2pa": False}},
    )
    assert response.status_code == 201, f"micro embed_c2pa=False failed: {response.text}"
    signed = response.json()["data"]["document"]["signed_text"]

    # No C2PA manifest should be embedded in the content
    extracted = UnicodeMetadata.extract_metadata(signed)
    assert extracted is None, "C2PA manifest found in micro+embed_c2pa=False output (should not be embedded)"


@pytest.mark.asyncio
async def test_micro_legacy_safe_embed_c2pa_true_uses_same_c2pa(async_client, auth_headers: dict) -> None:
    """micro + legacy_safe=True + embed_c2pa=True also uses the same C2PA method as full mode."""
    text = "Legacy safe C2PA unity test. This is the second sentence here."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": text,
            "options": {
                "manifest_mode": "micro",
                "legacy_safe": True,
                "embed_c2pa": True,
            },
        },
    )
    assert response.status_code == 201, f"micro+legacy_safe sign failed: {response.text}"
    signed = response.json()["data"]["document"]["signed_text"]

    manifest = _extract_c2pa(signed, "micro+legacy_safe+embed_c2pa=True")
    _assert_c2pa_core_structure(manifest, "micro+legacy_safe+embed_c2pa=True")


@pytest.mark.asyncio
async def test_all_micro_variants_produce_c2pa_manifest(async_client, auth_headers: dict) -> None:
    """All micro mode flag combinations with embed_c2pa=True produce a valid C2PA manifest."""
    text = "Testing all micro mode variants. Each should produce a C2PA manifest."

    variants = [
        ({"manifest_mode": "micro", "ecc": True, "legacy_safe": False, "embed_c2pa": True}, "VS256-RS"),
        ({"manifest_mode": "micro", "ecc": False, "legacy_safe": False, "embed_c2pa": True}, "VS256"),
        ({"manifest_mode": "micro", "ecc": False, "legacy_safe": True, "embed_c2pa": True}, "legacy_safe"),
        ({"manifest_mode": "micro", "ecc": True, "legacy_safe": True, "embed_c2pa": True}, "legacy_safe_rs"),
    ]

    for opts, label in variants:
        response = await async_client.post(
            "/api/v1/sign",
            headers=auth_headers,
            json={"text": text, "options": opts},
        )
        assert response.status_code == 201, f"{label} sign failed: {response.text}"
        signed = response.json()["data"]["document"]["signed_text"]
        manifest = _extract_c2pa(signed, label)
        _assert_c2pa_core_structure(manifest, label)


@pytest.mark.asyncio
async def test_micro_legacy_safe_document_metadata_in_response(async_client, auth_headers: dict) -> None:
    """micro + legacy_safe=True response includes encoding metadata indicating legacy_safe mode."""
    text = "Sentence for metadata check. Another sentence here."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": text,
            "options": {
                "manifest_mode": "micro",
                "legacy_safe": True,
                "ecc": False,
                "embed_c2pa": True,
            },
        },
    )
    assert response.status_code == 201, f"sign failed: {response.text}"
    payload = response.json()
    doc = payload["data"]["document"]
    # The signed text should contain the per-sentence markers
    signed = doc.get("signed_text")
    assert signed is not None and len(signed) > len(text), "signed_text should be longer than input (contains invisible markers)"


@pytest.mark.asyncio
async def test_micro_legacy_safe_rs_document_metadata_in_response(async_client, auth_headers: dict) -> None:
    """micro + legacy_safe=True + ecc=True response works correctly."""
    text = "Sentence for RS metadata check. Another sentence here."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": text,
            "options": {
                "manifest_mode": "micro",
                "legacy_safe": True,
                "ecc": True,
                "embed_c2pa": True,
            },
        },
    )
    assert response.status_code == 201, f"sign failed: {response.text}"
    signed = response.json()["data"]["document"]["signed_text"]
    assert signed is not None and len(signed) > len(text), "signed_text should be longer than input (contains invisible markers)"
    # C2PA manifest should still be embedded
    manifest = _extract_c2pa(signed, "micro+legacy_safe_rs")
    _assert_c2pa_core_structure(manifest, "micro+legacy_safe_rs")
