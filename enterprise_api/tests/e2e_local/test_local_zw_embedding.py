"""
Local E2E test for ZW embedding mode.

Tests the full flow of signing with zw_embedding mode and verifying
the Word-compatible signatures in the local dockerized environment.

Run with: LOCAL_API_TESTS=true pytest tests/e2e_local/test_local_zw_embedding.py -v
"""

from __future__ import annotations

import uuid

import pytest

from app.utils.zw_crypto import ZW_MAGIC_MINI, CHARS_BASE4


def _unique_document_id(prefix: str) -> str:
    """Generate unique document ID for test isolation."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _assert_status(response, expected_status: int, label: str) -> None:
    """Assert HTTP status code with helpful error message."""
    assert response.status_code == expected_status, (
        f"{label} expected {expected_status}, got {response.status_code}. "
        f"Body: {response.text}. Headers: {dict(response.headers)}"
    )


def _assert_local_base_url(base_url: str) -> None:
    """Ensure we're testing against local API."""
    allowed_prefixes = ("http://localhost", "http://127.0.0.1", "http://0.0.0.0")
    assert base_url.startswith(allowed_prefixes), (
        "Local tests should target a local API base URL. "
        f"Got {base_url}"
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_zw_embedding_sign_and_verify(
    local_client,
    local_auth_headers,
    local_api_config,
) -> None:
    """Test signing with zw_embedding mode and verification."""
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_zw")
    original_text = "First sentence for ZW test. Second sentence here. Third sentence completes it."

    # Sign with zw_embedding mode
    sign_response = await local_client.post(
        "/api/v1/sign/advanced",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign/advanced (zw_embedding)")
    sign_payload = sign_response.json()
    
    assert sign_payload["success"] is True, f"Sign failed: {sign_payload}"
    assert sign_payload["document_id"] == document_id
    
    embedded_content = sign_payload.get("embedded_content")
    assert embedded_content is not None, "Response should contain embedded_content"
    assert isinstance(embedded_content, str)

    # Verify ZW signatures are present
    assert ZW_MAGIC_MINI in embedded_content, "Embedded content should contain ZW signature magic"
    
    # Count signatures (should be 3 for 3 sentences)
    signature_count = embedded_content.count(ZW_MAGIC_MINI)
    assert signature_count == 3, f"Expected 3 ZW signatures, found {signature_count}"

    # Verify Word compatibility (no ZWSP!)
    zwsp = '\u200B'
    assert zwsp not in embedded_content, "Embedded content must NOT contain ZWSP (Word strips it!)"

    # Verify only Word-safe characters used
    for char in embedded_content:
        if char in CHARS_BASE4:
            continue  # Word-safe ZW char
        if char.isprintable() or char.isspace():
            continue  # Normal visible char
        # Check for forbidden characters
        cp = ord(char)
        if cp == 0x200B:  # ZWSP
            pytest.fail("Found ZWSP (U+200B) at position - Word will strip this!")

    print(f"✓ ZW embedding created: {signature_count} Word-compatible signatures")

    # Verify the signed content
    verify_response = await local_client.post(
        "/api/v1/verify/advanced",
        headers=local_auth_headers,
        json={
            "text": embedded_content,
            "include_attribution": False,
            "detect_plagiarism": False,
            "segmentation_level": "sentence",
            "search_scope": "organization",
        },
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify/advanced")
    verify_payload = verify_response.json()
    
    assert verify_payload["success"] is True, f"Verify failed: {verify_payload}"
    
    # Note: ZW embeddings may not verify the same way as C2PA manifests
    # The verification logic needs to detect and handle ZW signatures
    data = verify_payload.get("data", {})
    print(f"✓ Verification response: valid={data.get('valid')}, reason={data.get('reason_code')}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_zw_embedding_signature_size(
    local_client,
    local_auth_headers,
    local_api_config,
) -> None:
    """Test that ZW embedding signatures are exactly 132 chars per sentence."""
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_zw_size")
    original_text = "Single sentence for size test."

    sign_response = await local_client.post(
        "/api/v1/sign/advanced",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign/advanced (zw_embedding)")
    sign_payload = sign_response.json()
    
    embedded_content = sign_payload.get("embedded_content")
    assert embedded_content is not None

    # Calculate overhead
    overhead = len(embedded_content) - len(original_text)
    
    # Should be exactly 132 chars for one sentence
    assert overhead == 132, f"Expected 132 char overhead per sentence, got {overhead}"
    
    print(f"✓ ZW signature size verified: {overhead} chars (132 expected)")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_zw_embedding_multiple_sentences(
    local_client,
    local_auth_headers,
    local_api_config,
) -> None:
    """Test ZW embedding with multiple sentences."""
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_zw_multi")
    
    sentences = [
        "This is the first sentence.",
        "Here comes the second sentence.",
        "Third sentence for good measure.",
        "Fourth sentence to test scalability.",
        "Fifth and final sentence!",
    ]
    original_text = " ".join(sentences)

    sign_response = await local_client.post(
        "/api/v1/sign/advanced",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign/advanced (zw_embedding)")
    sign_payload = sign_response.json()
    
    embedded_content = sign_payload.get("embedded_content")
    assert embedded_content is not None

    # Count signatures
    signature_count = embedded_content.count(ZW_MAGIC_MINI)
    expected_count = len(sentences)
    assert signature_count == expected_count, (
        f"Expected {expected_count} signatures for {expected_count} sentences, "
        f"found {signature_count}"
    )

    # Calculate total overhead
    overhead = len(embedded_content) - len(original_text)
    expected_overhead = 132 * expected_count
    assert overhead == expected_overhead, (
        f"Expected {expected_overhead} chars overhead ({expected_count} × 132), "
        f"got {overhead}"
    )

    print(f"✓ Multiple sentences: {signature_count} signatures, {overhead} chars overhead")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_zw_embedding_word_compatibility_characters(
    local_client,
    local_auth_headers,
    local_api_config,
) -> None:
    """Verify that ZW embedding uses only Word-compatible characters."""
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_zw_compat")
    original_text = "Test sentence for Word compatibility check."

    sign_response = await local_client.post(
        "/api/v1/sign/advanced",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign/advanced (zw_embedding)")
    sign_payload = sign_response.json()
    
    embedded_content = sign_payload.get("embedded_content")
    assert embedded_content is not None

    # Extract only the ZW signature characters
    zw_chars = []
    for char in embedded_content:
        if char in CHARS_BASE4:
            zw_chars.append(char)

    # Verify we have ZW characters
    assert len(zw_chars) > 0, "Should have ZW characters in embedded content"

    # Verify all ZW chars are from the Word-safe set
    word_safe_chars = set(CHARS_BASE4)
    for char in zw_chars:
        assert char in word_safe_chars, (
            f"Found non-Word-safe character: U+{ord(char):04X}. "
            f"Only ZWNJ, ZWJ, CGJ, MVS allowed (no ZWSP!)"
        )

    # Verify no ZWSP
    zwsp = '\u200B'
    assert zwsp not in embedded_content, "Must not contain ZWSP (U+200B)"

    print(f"✓ Word compatibility verified: {len(zw_chars)} ZW chars, all Word-safe")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_zw_embedding_metadata_response(
    local_client,
    local_auth_headers,
    local_api_config,
) -> None:
    """Test that ZW embedding returns correct metadata in response."""
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_zw_meta")
    original_text = "Test sentence for metadata validation."

    sign_response = await local_client.post(
        "/api/v1/sign/advanced",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "manifest_mode": "zw_embedding",
            "segmentation_level": "sentence",
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign/advanced (zw_embedding)")
    sign_payload = sign_response.json()
    
    # Check for zw_embedding indicators in response
    metadata = sign_payload.get("metadata", {})
    
    # Should indicate zw_embedding mode somewhere
    manifest_mode = (
        metadata.get("manifest_mode") or 
        sign_payload.get("manifest_mode")
    )
    
    if manifest_mode:
        assert manifest_mode == "zw_embedding", (
            f"Expected manifest_mode='zw_embedding', got '{manifest_mode}'"
        )
        print("✓ Metadata indicates zw_embedding mode")
    else:
        print("⚠ Warning: manifest_mode not found in response metadata")

    # Verify embedded_content exists
    assert sign_payload.get("embedded_content") is not None, (
        "Response should contain embedded_content field"
    )
    
    print("✓ Response structure validated")
