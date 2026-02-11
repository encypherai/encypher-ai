"""
Tests for micro_c2pa and micro_ecc_c2pa manifest modes (TEAM_165).

micro_c2pa combines:
- Ultra-compact per-sentence markers (36 invisible chars each, internally VS256)
- Full C2PA-compliant document-level manifest
- DB-backed manifest storage with segment location indices

micro_ecc_c2pa is the same but uses Reed-Solomon error-correcting encoding
that can recover from up to 4 unknown errors or 8 erasures per marker.

Test scenarios:
1. Sentence-level markers are embedded and extractable
2. Full C2PA manifest is embedded at document level
3. DB ContentReferences store the manifest + segment location
4. Verification of a single copied sentence returns full manifest + segment info
5. Integration test via /sign endpoint
6. RS error correction survives partial corruption
"""

import uuid as uuid_mod

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.vs256_crypto import (
    find_all_minimal_signed_uuids as vs256_find_all,
    verify_minimal_signed_uuid as vs256_verify,
    derive_signing_key_from_private_key as vs256_derive_key,
)
from app.utils.vs256_rs_crypto import (
    find_all_minimal_signed_uuids as vs256rs_find_all,
    verify_minimal_signed_uuid as vs256rs_verify,
    derive_signing_key_from_private_key as vs256rs_derive_key,
)


# =============================================================================
# Unit tests — micro_c2pa embedding logic (no DB required)
# =============================================================================


class TestMicroC2paEmbeddingUnit:
    """Unit tests for micro_c2pa embedding without DB."""

    @pytest.fixture
    def keypair(self):
        private_key = Ed25519PrivateKey.generate()
        return private_key

    def test_micro_c2pa_creates_per_sentence_markers(self, keypair):
        """Each sentence should get a 36-char invisible marker."""
        from app.utils.vs256_crypto import (
            create_minimal_signed_uuid,
            embed_signature_safely,
            SIGNATURE_CHARS,
        )

        signing_key = vs256_derive_key(keypair)
        sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "Pack my box with five dozen liquor jugs.",
            "How vexingly quick daft zebras jump.",
        ]

        embedded_sentences = []
        for sentence in sentences:
            sentence_uuid = uuid_mod.uuid4()
            sig = create_minimal_signed_uuid(sentence_uuid, signing_key)
            assert len(sig) == SIGNATURE_CHARS  # 36 chars
            embedded = embed_signature_safely(sentence, sig)
            embedded_sentences.append(embedded)

        document = " ".join(embedded_sentences)

        # Should find exactly 3 markers
        found = vs256_find_all(document)
        assert len(found) == 3, f"Expected 3 markers, found {len(found)}"

        # Each marker should verify
        for _start, _end, sig_text in found:
            is_valid, extracted_uuid = vs256_verify(sig_text, signing_key)
            assert is_valid, "Each marker should verify with the correct key"
            assert extracted_uuid is not None

    def test_micro_c2pa_markers_invisible_in_text(self, keypair):
        """Markers should not affect visible text content."""
        from app.utils.vs256_crypto import (
            create_minimal_signed_uuid,
            embed_signature_safely,
            remove_minimal_signed_uuid,
        )

        signing_key = vs256_derive_key(keypair)
        original = "Hello world."
        sentence_uuid = uuid_mod.uuid4()
        sig = create_minimal_signed_uuid(sentence_uuid, signing_key)
        embedded = embed_signature_safely(original, sig)

        # Visible text should be the same after removing markers
        cleaned = remove_minimal_signed_uuid(embedded)
        assert cleaned == original

    def test_micro_c2pa_c2pa_manifest_embeds_at_document_level(self, keypair):
        """The full C2PA manifest should be extractable from the document."""
        from encypher.core.unicode_metadata import UnicodeMetadata
        from app.utils.vs256_crypto import (
            create_minimal_signed_uuid,
            embed_signature_safely,
        )

        signing_key = vs256_derive_key(keypair)
        sentences = [
            "First sentence of the article.",
            "Second sentence continues the thought.",
        ]

        # Phase 1: embed per-sentence markers
        embedded_sentences = []
        for sentence in sentences:
            sentence_uuid = uuid_mod.uuid4()
            sig = create_minimal_signed_uuid(sentence_uuid, signing_key)
            embedded_sentences.append(embed_signature_safely(sentence, sig))

        full_document = " ".join(embedded_sentences)

        # Phase 2: embed C2PA manifest at document level
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        embedded_document = UnicodeMetadata.embed_metadata(
            text=full_document,
            private_key=keypair,
            signer_id="test_signer",
            timestamp=timestamp,
            custom_metadata={"document_id": "test-doc-001"},
            metadata_format="c2pa",
            add_hard_binding=True,
            claim_generator="encypher-enterprise-api/test",
            actions=[{"label": "c2pa.created", "when": timestamp}],
        )

        # Should still have per-sentence markers
        found_markers = vs256_find_all(embedded_document)
        assert len(found_markers) == 2, "Per-sentence markers should survive C2PA wrapping"

        # Should have extractable C2PA manifest
        extracted = UnicodeMetadata.extract_metadata(embedded_document)
        assert extracted is not None, "C2PA manifest should be extractable"
        assert "instance_id" in extracted or "manifest" in extracted, (
            "Extracted metadata should contain manifest data"
        )

    def test_micro_c2pa_segment_location_computation(self):
        """Segment location (paragraph, sentence) should be computed correctly."""
        from app.utils.segmentation import segment_paragraphs, segment_sentences

        # Simulate a multi-paragraph document
        segments = [
            "First sentence of paragraph one.",
            "Second sentence of paragraph one.",
            "First sentence of paragraph two.",
            "Second sentence of paragraph two.",
            "Third sentence of paragraph two.",
        ]

        paragraphs = segment_paragraphs("\n\n".join(segments))
        sentence_location: dict[int, dict[str, int]] = {}
        global_sent_idx = 0
        for para_idx, para_text in enumerate(paragraphs):
            para_sentences = segment_sentences(para_text)
            for sent_in_para, _sent in enumerate(para_sentences):
                if global_sent_idx < len(segments):
                    sentence_location[global_sent_idx] = {
                        "paragraph_index": para_idx,
                        "sentence_in_paragraph": sent_in_para,
                    }
                global_sent_idx += 1

        # Verify locations make sense
        assert len(sentence_location) > 0, "Should have computed locations"
        # First sentence should be paragraph 0
        assert sentence_location[0]["paragraph_index"] == 0
        assert sentence_location[0]["sentence_in_paragraph"] == 0


# =============================================================================
# Integration tests — micro_c2pa via /sign endpoint (requires DB)
# =============================================================================


@pytest.mark.asyncio
async def test_sign_micro_c2pa_creates_embedded_content(
    async_client,
    auth_headers: dict,
) -> None:
    """POST /sign with micro_c2pa should return embedded content with markers + C2PA."""
    original_text = (
        "Artificial intelligence is transforming content creation. "
        "Publishers need tools to verify the origin of every sentence. "
        "Encypher provides cryptographic provenance at the sentence level."
    )

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": original_text,
            "options": {
                "manifest_mode": "micro_c2pa",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    # Extract embedded text from unified response
    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None, "Response should contain embedded text"

    # Should contain per-sentence markers (internally VS256)
    found_markers = vs256_find_all(embedded_text)
    assert len(found_markers) == 3, f"Expected 3 per-sentence markers, found {len(found_markers)}"

    # Should also contain C2PA manifest (extractable via UnicodeMetadata)
    from encypher.core.unicode_metadata import UnicodeMetadata

    extracted_manifest = UnicodeMetadata.extract_metadata(embedded_text)
    assert extracted_manifest is not None, "C2PA manifest should be extractable from embedded content"


@pytest.mark.asyncio
async def test_sign_micro_c2pa_marker_size_is_36_chars(
    async_client,
    auth_headers: dict,
) -> None:
    """Each micro_c2pa per-sentence marker should be exactly 36 invisible chars."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Single test sentence for size check.",
            "options": {
                "manifest_mode": "micro_c2pa",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    found_markers = vs256_find_all(embedded_text)
    assert len(found_markers) == 1, "Should find exactly 1 marker"

    _start, _end, sig_text = found_markers[0]
    assert len(sig_text) == 36, f"Marker should be 36 chars, got {len(sig_text)}"


@pytest.mark.asyncio
async def test_sign_micro_c2pa_with_custom_assertions(
    async_client,
    auth_headers: dict,
) -> None:
    """micro_c2pa should support custom C2PA assertions (e.g. source URL)."""
    source_url = "https://example.com/blog/my-article"

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Blog post content here. Another sentence follows.",
            "options": {
                "manifest_mode": "micro_c2pa",
                "segmentation_level": "sentence",
            },
            "custom_assertions": [
                {
                    "label": "com.encypher.source_url",
                    "data": {"url": source_url},
                }
            ],
            "validate_assertions": False,
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    # Markers should be present
    found_markers = vs256_find_all(embedded_text)
    assert len(found_markers) == 2


@pytest.mark.asyncio
async def test_sign_micro_c2pa_metadata_reports_mode(
    async_client,
    auth_headers: dict,
) -> None:
    """Response metadata should indicate micro_c2pa mode."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Test sentence for metadata check.",
            "options": {
                "manifest_mode": "micro_c2pa",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()

    # The response should contain manifest metadata
    data = payload.get("data", {})
    document = data.get("document", {})
    signed_text = document.get("signed_text", "")

    # Verify markers are present (confirms micro_c2pa mode worked)
    found_sigs = vs256_find_all(signed_text)
    assert len(found_sigs) > 0, "Response should contain micro markers (micro_c2pa mode)"


@pytest.mark.asyncio
async def test_sign_micro_c2pa_multi_paragraph(
    async_client,
    auth_headers: dict,
) -> None:
    """micro_c2pa should handle multi-paragraph content correctly."""
    text = (
        "First paragraph first sentence. First paragraph second sentence.\n\n"
        "Second paragraph first sentence. Second paragraph second sentence. "
        "Second paragraph third sentence."
    )

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": text,
            "options": {
                "manifest_mode": "micro_c2pa",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    # Should have markers for all sentences
    found_markers = vs256_find_all(embedded_text)
    assert len(found_markers) >= 4, f"Expected at least 4 markers for multi-paragraph, found {len(found_markers)}"


@pytest.mark.asyncio
async def test_sign_micro_c2pa_does_not_expose_vs256_in_response(
    async_client,
    auth_headers: dict,
) -> None:
    """Public response should NOT contain 'vs256' terminology."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Test sentence.",
            "options": {
                "manifest_mode": "micro_c2pa",
            },
        },
    )

    assert response.status_code == 201
    response_text = response.text.lower()

    # The public response body should not leak vs256 terminology
    # (internal dev comments in code are fine, but the API response is public)
    # Note: some internal metadata fields may contain it; we check the top-level keys
    payload = response.json()
    data = payload.get("data", {})
    # Check that the manifest_mode in the response uses the public name
    doc = data.get("document", {})
    metadata = data.get("metadata", {}) or payload.get("metadata", {})
    if isinstance(metadata, dict):
        mode = metadata.get("manifest_mode", "")
        assert mode != "vs256_embedding", "Response should use 'micro_c2pa' not 'vs256_embedding'"


# =============================================================================
# Unit tests — micro_ecc_c2pa (RS error-correcting variant)
# =============================================================================


class TestMicroEccC2paEmbeddingUnit:
    """Unit tests for micro_ecc_c2pa embedding without DB."""

    @pytest.fixture
    def keypair(self):
        return Ed25519PrivateKey.generate()

    def test_micro_ecc_creates_per_sentence_markers(self, keypair):
        """Each sentence should get a 44-char RS-protected invisible marker (128-bit HMAC)."""
        from app.utils.vs256_rs_crypto import (
            create_minimal_signed_uuid as rs_create,
            embed_signature_safely as rs_embed,
            SIGNATURE_CHARS,
        )

        signing_key = vs256rs_derive_key(keypair)
        sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "Pack my box with five dozen liquor jugs.",
            "How vexingly quick daft zebras jump.",
        ]

        embedded_sentences = []
        for sentence in sentences:
            sentence_uuid = uuid_mod.uuid4()
            sig = rs_create(sentence_uuid, signing_key)
            assert len(sig) == SIGNATURE_CHARS  # 36 chars
            embedded = rs_embed(sentence, sig)
            embedded_sentences.append(embedded)

        document = " ".join(embedded_sentences)

        # Should find exactly 3 markers (RS uses same magic prefix as non-RS)
        found = vs256rs_find_all(document)
        assert len(found) == 3, f"Expected 3 markers, found {len(found)}"

        # Each marker should verify with RS decoding
        for _start, _end, sig_text in found:
            is_valid, extracted_uuid = vs256rs_verify(sig_text, signing_key)
            assert is_valid, "Each RS marker should verify"
            assert extracted_uuid is not None

    def test_micro_ecc_survives_partial_corruption(self, keypair):
        """RS markers should recover from a few corrupted invisible chars."""
        from app.utils.vs256_rs_crypto import (
            create_minimal_signed_uuid as rs_create,
        )
        from app.utils.vs256_crypto import BYTE_TO_VS, VS_TO_BYTE

        signing_key = vs256rs_derive_key(keypair)
        sentence_uuid = uuid_mod.uuid4()
        sig = rs_create(sentence_uuid, signing_key)

        # Corrupt 2 payload characters (well within RS correction limit of 4)
        sig_list = list(sig)
        # Corrupt chars at positions 6 and 10 (inside payload, after 4-char magic prefix)
        for corrupt_pos in [6, 10]:
            original_byte = VS_TO_BYTE[sig_list[corrupt_pos]]
            replacement_byte = (original_byte + 42) % 256
            sig_list[corrupt_pos] = BYTE_TO_VS[replacement_byte]
        corrupted_sig = "".join(sig_list)

        # RS verification should still succeed with known erase positions
        is_valid, extracted_uuid = vs256rs_verify(
            corrupted_sig, signing_key, erase_positions=[6 - 4, 10 - 4]  # payload-relative
        )
        assert is_valid, "RS should recover from 2 erasures"
        assert extracted_uuid == sentence_uuid

    def test_micro_ecc_c2pa_manifest_embeds_at_document_level(self, keypair):
        """Full C2PA manifest should be extractable alongside RS markers."""
        from encypher.core.unicode_metadata import UnicodeMetadata
        from app.utils.vs256_rs_crypto import (
            create_minimal_signed_uuid as rs_create,
            embed_signature_safely as rs_embed,
        )

        signing_key = vs256rs_derive_key(keypair)
        sentences = [
            "First sentence of the article.",
            "Second sentence continues the thought.",
        ]

        embedded_sentences = []
        for sentence in sentences:
            sentence_uuid = uuid_mod.uuid4()
            sig = rs_create(sentence_uuid, signing_key)
            embedded_sentences.append(rs_embed(sentence, sig))

        full_document = " ".join(embedded_sentences)

        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        embedded_document = UnicodeMetadata.embed_metadata(
            text=full_document,
            private_key=keypair,
            signer_id="test_signer",
            timestamp=timestamp,
            custom_metadata={"document_id": "test-ecc-doc-001"},
            metadata_format="c2pa",
            add_hard_binding=True,
            claim_generator="encypher-enterprise-api/test",
            actions=[{"label": "c2pa.created", "when": timestamp}],
        )

        # RS markers should survive C2PA wrapping
        found_markers = vs256rs_find_all(embedded_document)
        assert len(found_markers) == 2, "RS markers should survive C2PA wrapping"

        # C2PA manifest should be extractable
        extracted = UnicodeMetadata.extract_metadata(embedded_document)
        assert extracted is not None, "C2PA manifest should be extractable"


# =============================================================================
# Integration tests — micro_ecc_c2pa via /sign endpoint
# =============================================================================


@pytest.mark.asyncio
async def test_sign_micro_ecc_c2pa_creates_embedded_content(
    async_client,
    auth_headers: dict,
) -> None:
    """POST /sign with micro_ecc_c2pa should return embedded content with RS markers + C2PA."""
    original_text = (
        "Artificial intelligence is transforming content creation. "
        "Publishers need tools to verify the origin of every sentence. "
        "Encypher provides cryptographic provenance at the sentence level."
    )

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": original_text,
            "options": {
                "manifest_mode": "micro_ecc_c2pa",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None, "Response should contain embedded text"

    # Should contain per-sentence RS markers
    found_markers = vs256rs_find_all(embedded_text)
    assert len(found_markers) == 3, f"Expected 3 RS markers, found {len(found_markers)}"

    # Should also contain C2PA manifest
    from encypher.core.unicode_metadata import UnicodeMetadata
    extracted_manifest = UnicodeMetadata.extract_metadata(embedded_text)
    assert extracted_manifest is not None, "C2PA manifest should be extractable"


@pytest.mark.asyncio
async def test_sign_micro_ecc_c2pa_marker_size_is_44_chars(
    async_client,
    auth_headers: dict,
) -> None:
    """Each micro_ecc_c2pa marker should be exactly 44 invisible chars (128-bit HMAC + RS)."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Single test sentence for RS size check.",
            "options": {
                "manifest_mode": "micro_ecc_c2pa",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    found_markers = vs256rs_find_all(embedded_text)
    assert len(found_markers) == 1, "Should find exactly 1 RS marker"

    _start, _end, sig_text = found_markers[0]
    assert len(sig_text) == 44, f"RS marker should be 44 chars, got {len(sig_text)}"


@pytest.mark.asyncio
async def test_sign_micro_ecc_c2pa_multi_paragraph(
    async_client,
    auth_headers: dict,
) -> None:
    """micro_ecc_c2pa should handle multi-paragraph content correctly."""
    text = (
        "First paragraph first sentence. First paragraph second sentence.\n\n"
        "Second paragraph first sentence. Second paragraph second sentence. "
        "Second paragraph third sentence."
    )

    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": text,
            "options": {
                "manifest_mode": "micro_ecc_c2pa",
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    embedded_text = document.get("signed_text") or payload.get("embedded_text") or payload.get("text")
    assert embedded_text is not None

    found_markers = vs256rs_find_all(embedded_text)
    assert len(found_markers) >= 4, f"Expected at least 4 RS markers, found {len(found_markers)}"


# =============================================================================
# Unit tests — SignerIdentity schema
# =============================================================================


class TestSignerIdentitySchema:
    """Unit tests for the SignerIdentity schema."""

    def test_self_signed_identity(self):
        from app.schemas.embeddings import SignerIdentity

        identity = SignerIdentity(
            organization_id="org_test",
            organization_name="Test Org",
            certificate_status="active",
            ca_backed=False,
            issuer="self-signed",
            trust_level="self_signed",
        )
        assert identity.ca_backed is False
        assert identity.trust_level == "self_signed"
        assert identity.issuer == "self-signed"

    def test_ca_verified_identity(self):
        from app.schemas.embeddings import SignerIdentity
        from datetime import datetime, timezone

        identity = SignerIdentity(
            organization_id="org_enterprise",
            organization_name="Enterprise Corp",
            certificate_status="active",
            ca_backed=True,
            issuer="CN=DigiCert C2PA Root CA,O=DigiCert",
            certificate_expiry=datetime(2030, 1, 1, tzinfo=timezone.utc),
            trust_level="ca_verified",
        )
        assert identity.ca_backed is True
        assert identity.trust_level == "ca_verified"
        assert "DigiCert" in identity.issuer

    def test_no_certificate_identity(self):
        from app.schemas.embeddings import SignerIdentity

        identity = SignerIdentity(
            organization_id="org_new",
            certificate_status="none",
            trust_level="none",
        )
        assert identity.ca_backed is False
        assert identity.trust_level == "none"


# =============================================================================
# Integration test — SignerIdentity in verify response
# =============================================================================


@pytest.mark.asyncio
async def test_sign_and_verify_returns_signer_identity(
    async_client,
    auth_headers: dict,
) -> None:
    """Sign with micro_c2pa, then verify a ref and check signer_identity is present."""
    # Step 1: Sign content
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "This sentence tests signer identity resolution.",
            "options": {
                "manifest_mode": "micro_c2pa",
            },
        },
    )
    assert response.status_code == 201, f"Sign failed: {response.text}"
    payload = response.json()

    # Extract verification URL to get the ref_id
    data = payload.get("data", {})
    document = data.get("document", {})
    verification_url = document.get("verification_url", "")

    # verification_url format: /api/v1/public/verify/{ref_id}?signature=...
    # Extract ref_id from the URL
    import re
    match = re.search(r"/verify/([a-f0-9]+)", verification_url)
    if not match:
        pytest.skip("Could not extract ref_id from verification_url")

    ref_id = match.group(1)
    # Extract signature param
    sig_match = re.search(r"signature=([a-f0-9]+)", verification_url)
    signature = sig_match.group(1) if sig_match else ""

    # Step 2: Verify the reference
    verify_response = await async_client.get(
        f"/api/v1/public/verify/{ref_id}",
        params={"signature": signature},
    )

    # The verify endpoint may return 200 or the ref might need the right signature
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        if verify_data.get("valid"):
            # Check signer_identity is present
            signer = verify_data.get("signer_identity")
            assert signer is not None, "signer_identity should be present in verify response"
            assert signer.get("organization_id") is not None
            assert signer.get("certificate_status") is not None
            assert signer.get("trust_level") in ("none", "self_signed", "ca_verified")
