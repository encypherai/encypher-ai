"""Tests for ZW embedding manifest mode in /sign/advanced endpoint."""

import pytest

from app.utils.zw_crypto import ZW_MAGIC_MINI, CHARS_BASE4


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_creates_word_compatible_signatures(
    async_client,
    auth_headers: dict,
) -> None:
    """Test that zw_embedding mode creates Word-compatible signatures."""
    original_text = "First sentence. Second sentence. Third sentence."

    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=auth_headers,
        json={
            "document_id": "doc_zw_embedding_001",
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    # Should have embedded text
    embedded_text = payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None, "Response should contain embedded text"

    # Should contain ZW magic number (signature present)
    assert ZW_MAGIC_MINI in embedded_text, "Embedded text should contain ZW signature magic"

    # Count ZW signatures (should be 3 for 3 sentences)
    signature_count = embedded_text.count(ZW_MAGIC_MINI)
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
    """Test that zw_embedding signatures are 132 chars each."""
    original_text = "Single test sentence."

    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=auth_headers,
        json={
            "document_id": "doc_zw_embedding_size_001",
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    assert response.status_code == 201
    payload = response.json()

    embedded_text = payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    # Calculate overhead (embedded - original)
    overhead = len(embedded_text) - len(original_text)

    # Should be exactly 132 chars for one sentence
    assert overhead == 132, f"Expected 132 char overhead, got {overhead}"

    print(f"✓ ZW signature size verified: {overhead} chars")


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_metadata(
    async_client,
    auth_headers: dict,
) -> None:
    """Test that zw_embedding returns correct metadata."""
    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=auth_headers,
        json={
            "document_id": "doc_zw_embedding_meta_001",
            "text": "Test sentence for metadata.",
            "manifest_mode": "zw_embedding",
        },
    )

    assert response.status_code == 201
    payload = response.json()

    metadata = payload.get("metadata", {})

    # Should indicate zw_embedding mode
    assert metadata.get("manifest_mode") == "zw_embedding" or \
           payload.get("manifest_mode") == "zw_embedding", \
           "Response should indicate zw_embedding mode"

    print("✓ ZW embedding metadata verified")


@pytest.mark.asyncio
async def test_sign_advanced_zw_embedding_requires_professional_tier(
    async_client,
    starter_auth_headers: dict,
) -> None:
    """Test that zw_embedding requires Professional tier."""
    response = await async_client.post(
        "/api/v1/sign/advanced",
        headers=starter_auth_headers,
        json={
            "document_id": "doc_zw_embedding_tier_001",
            "text": "Test sentence.",
            "manifest_mode": "zw_embedding",
        },
    )

    # Should be forbidden for starter tier
    assert response.status_code == 403, f"Expected 403 for starter tier, got {response.status_code}"

    payload = response.json()
    detail = payload.get("detail", {})
    assert detail.get("code") == "FEATURE_NOT_AVAILABLE"
    assert "professional" in detail.get("required_tier", "").lower()

    print("✓ ZW embedding tier gating verified")
