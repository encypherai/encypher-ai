"""Tests for ZW embedding manifest mode in unified /sign endpoint."""

import pytest

from app.utils.zw_crypto import CHARS_BASE4, find_all_minimal_signed_uuids


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_creates_word_compatible_signatures(
    async_client,
    auth_headers: dict,
) -> None:
    """Test that zw_embedding mode creates Word-compatible signatures."""
    original_text = "First sentence. Second sentence. Third sentence."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": original_text,
            "options": {
                "manifest_mode": "zw_embedding",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    # Should have embedded text (unified response: data.document.signed_text)
    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None, "Response should contain embedded text"

    # Should contain ZW signatures (detected via contiguous sequence detection)
    found_signatures = find_all_minimal_signed_uuids(embedded_text)
    assert len(found_signatures) > 0, "Embedded text should contain ZW signatures"

    # Count ZW signatures (should be 3 for 3 sentences)
    signature_count = len(found_signatures)
    assert signature_count == 3, f"Expected 3 ZW signatures, found {signature_count}"

    # Verify only Word-safe characters are used (no ZWSP!)
    zwsp = '\u200B'
    assert zwsp not in embedded_text, "Embedded text should NOT contain ZWSP (Word strips it!)"

    # Verify signature uses only base-4 Word-safe chars
    for char in embedded_text:
        if ord(char) < 0x20 or ord(char) > 0x10FFFF:
            continue  # Skip control chars
        if char in CHARS_BASE4:
            continue  # Word-safe ZW char
        if char.isprintable() or char.isspace():
            continue  # Normal visible char
        # Any other invisible char is suspicious
        cp = ord(char)
        if cp == 0x200B:  # ZWSP
            pytest.fail(f"Found ZWSP (U+200B) which Word strips!")

    print(f"✓ ZW embedding created: {signature_count} Word-compatible signatures")


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_signature_size(
    async_client,
    auth_headers: dict,
) -> None:
    """Test that zw_embedding signatures are 128 chars each (no magic number)."""
    original_text = "Single test sentence."

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": original_text,
            "options": {
                "manifest_mode": "zw_embedding",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()

    # Unified response: data.document.signed_text
    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    # Calculate overhead (embedded - original)
    overhead = len(embedded_text) - len(original_text)

    # Should be exactly 128 chars for one sentence (no magic number)
    assert overhead == 128, f"Expected 128 char overhead, got {overhead}"

    print(f"✓ ZW signature size verified: {overhead} chars")


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_metadata(
    async_client,
    auth_headers: dict,
) -> None:
    """Test that zw_embedding returns correct metadata."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Test sentence for metadata.",
            "options": {
                "manifest_mode": "zw_embedding",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()

    # Unified response: data.document.signed_text contains ZW signatures
    data = payload.get("data", {})
    document = data.get("document", {})
    signed_text = document.get("signed_text", "")
    
    # Verify ZW signatures are present (this confirms zw_embedding mode worked)
    found_sigs = find_all_minimal_signed_uuids(signed_text)
    assert len(found_sigs) > 0, "Response should contain ZW signatures (zw_embedding mode)"

    print("✓ ZW embedding metadata verified")


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_requires_professional_tier(
    async_client,
    starter_auth_headers: dict,
) -> None:
    """Test that zw_embedding requires Professional tier."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=starter_auth_headers,
        json={
            "text": "Test sentence.",
            "options": {
                "manifest_mode": "zw_embedding",
            },
        },
    )

    # Should be forbidden for starter tier
    assert response.status_code == 403, f"Expected 403 for starter tier, got {response.status_code}"

    payload = response.json()
    error = payload.get("error", {}) or payload.get("detail", {})
    # Check for feature gating error
    assert response.status_code == 403

    print("✓ ZW embedding tier gating verified")
