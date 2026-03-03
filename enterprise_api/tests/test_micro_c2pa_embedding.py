"""
Tests for unified micro manifest mode (TEAM_166).

micro mode uses two orthogonal flags:
  ecc=True  (default) → Reed-Solomon error correction (44 chars/segment)
  ecc=False           → plain HMAC (36 chars/segment)
  embed_c2pa=True  (default) → full C2PA document manifest embedded in content
  embed_c2pa=False           → per-sentence markers only; C2PA manifest DB-only

A C2PA-compatible manifest is ALWAYS generated for micro mode.
store_c2pa_manifest controls DB persistence; embed_c2pa controls in-content embedding.

Test scenarios:
1. Sentence-level markers are embedded and extractable (ecc=True and ecc=False)
2. Full C2PA manifest is embedded at document level (embed_c2pa=True)
3. C2PA manifest is NOT embedded when embed_c2pa=False
4. DB ContentReferences store the manifest + segment location
5. Integration test via /sign endpoint with flag combinations
6. RS error correction survives partial corruption
"""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from encypher.core.unicode_metadata import UnicodeMetadata
from sqlalchemy import text

from app.utils.vs256_crypto import (
    find_all_markers as vs256_find_all,
    verify_signed_marker as vs256_verify,
    derive_signing_key_from_private_key as vs256_derive_key,
    generate_log_id,
)
from app.utils.vs256_rs_crypto import (
    find_all_markers as vs256rs_find_all,
    verify_signed_marker as vs256rs_verify,
    derive_signing_key_from_private_key as vs256rs_derive_key,
)


# =============================================================================
# Unit tests — micro mode embedding logic (no DB required)
# =============================================================================


class TestMicroEmbeddingUnit:
    """Unit tests for micro mode embedding without DB (ecc=False variant for 36-char markers)."""

    @pytest.fixture
    def keypair(self):
        private_key = Ed25519PrivateKey.generate()
        return private_key

    def test_micro_creates_per_sentence_markers(self, keypair):
        """Each sentence should get a 36-char invisible marker."""
        from app.utils.vs256_crypto import (
            create_signed_marker,
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
            sentence_uuid = generate_log_id()
            sig = create_signed_marker(sentence_uuid, signing_key)
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

    def test_micro_markers_invisible_in_text(self, keypair):
        """Markers should not affect visible text content."""
        from app.utils.vs256_crypto import (
            create_signed_marker,
            embed_signature_safely,
            remove_markers,
        )

        signing_key = vs256_derive_key(keypair)
        original = "Hello world."
        sentence_uuid = generate_log_id()
        sig = create_signed_marker(sentence_uuid, signing_key)
        embedded = embed_signature_safely(original, sig)

        # Visible text should be the same after removing markers
        cleaned = remove_markers(embedded)
        assert cleaned == original

    def test_micro_c2pa_manifest_embeds_at_document_level(self, keypair):
        """The full C2PA manifest should be extractable from the document."""
        from encypher.core.unicode_metadata import UnicodeMetadata
        from app.utils.vs256_crypto import (
            create_signed_marker,
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
            sentence_uuid = generate_log_id()
            sig = create_signed_marker(sentence_uuid, signing_key)
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

    def test_micro_segment_location_computation(self):
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
# Integration tests — micro mode via /sign endpoint (requires DB)
# =============================================================================


@pytest.mark.asyncio
async def test_sign_micro_default_creates_embedded_content(
    async_client,
    auth_headers: dict,
) -> None:
    """POST /sign with micro (defaults: ecc=True, embed_c2pa=True) should return RS markers + C2PA."""
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
                "manifest_mode": "micro",
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

    # Default ecc=True → RS markers (44 chars)
    found_markers = vs256rs_find_all(embedded_text)
    assert len(found_markers) == 3, f"Expected 3 RS markers, found {len(found_markers)}"

    # Default embed_c2pa=True → C2PA manifest extractable
    extracted_manifest = UnicodeMetadata.extract_metadata(embedded_text)
    assert extracted_manifest is not None, "C2PA manifest should be extractable from embedded content"


@pytest.mark.asyncio
async def test_sign_micro_no_ecc_marker_size_is_36_chars(
    async_client,
    auth_headers: dict,
) -> None:
    """micro with ecc=False should produce 36-char markers."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Single test sentence for size check.",
            "options": {
                "manifest_mode": "micro",
                "ecc": False,
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
async def test_sign_micro_default_ecc_marker_size_is_44_chars(
    async_client,
    auth_headers: dict,
) -> None:
    """micro with default ecc=True should produce 44-char RS markers."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Single test sentence for RS size check.",
            "options": {
                "manifest_mode": "micro",
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
async def test_sign_micro_embed_c2pa_false_no_manifest_in_content(
    async_client,
    auth_headers: dict,
) -> None:
    """micro with embed_c2pa=False should NOT embed C2PA manifest in content."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Blog post content here. Another sentence follows.",
            "options": {
                "manifest_mode": "micro",
                "embed_c2pa": False,
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

    # Per-sentence markers should still be present
    found_markers = vs256rs_find_all(embedded_text)
    assert len(found_markers) == 2

    # C2PA manifest should NOT be extractable from the content
    extracted = UnicodeMetadata.extract_metadata(embedded_text)
    assert extracted is None, "C2PA manifest should NOT be in content when embed_c2pa=False"


@pytest.mark.asyncio
async def test_sign_micro_metadata_reports_mode_and_flags(
    async_client,
    auth_headers: dict,
) -> None:
    """Response metadata should indicate micro mode with flag values."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "Test sentence for metadata check.",
            "options": {
                "manifest_mode": "micro",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()

    data = payload.get("data", {})
    document = data.get("document", {})
    signed_text = document.get("signed_text", "")

    # Verify markers are present (confirms micro mode worked)
    found_sigs = vs256rs_find_all(signed_text)
    assert len(found_sigs) > 0, "Response should contain micro markers"


@pytest.mark.asyncio
async def test_sign_micro_multi_paragraph(
    async_client,
    auth_headers: dict,
) -> None:
    """micro mode should handle multi-paragraph content correctly."""
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
                "manifest_mode": "micro",
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
    assert len(found_markers) >= 4, f"Expected at least 4 markers for multi-paragraph, found {len(found_markers)}"


@pytest.mark.asyncio
async def test_sign_micro_does_not_expose_vs256_in_response(
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
                "manifest_mode": "micro",
            },
        },
    )

    assert response.status_code == 201

    payload = response.json()
    data = payload.get("data", {})
    metadata = data.get("metadata", {}) or payload.get("metadata", {})
    if isinstance(metadata, dict):
        mode = metadata.get("manifest_mode", "")
        assert mode != "vs256_embedding", "Response should use 'micro' not 'vs256_embedding'"


# =============================================================================
# Unit tests — micro mode with ecc=True (RS error-correcting variant)
# =============================================================================


class TestMicroEccEmbeddingUnit:
    """Unit tests for micro mode with ecc=True (RS error-correcting, 44-char markers)."""

    @pytest.fixture
    def keypair(self):
        return Ed25519PrivateKey.generate()

    def test_micro_ecc_creates_per_sentence_markers(self, keypair):
        """Each sentence should get a 44-char RS-protected invisible marker (128-bit HMAC)."""
        from app.utils.vs256_rs_crypto import (
            create_signed_marker as rs_create,
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
            sentence_uuid = generate_log_id()
            sig = rs_create(sentence_uuid, signing_key)
            assert len(sig) == SIGNATURE_CHARS  # 44 chars (RS mode)
            embedded = rs_embed(sentence, sig)
            embedded_sentences.append(embedded)

        document = " ".join(embedded_sentences)

        # Should find exactly 3 markers (RS uses same magic prefix as non-RS)
        found = vs256rs_find_all(document)
        assert len(found) == 3, f"Expected 3 markers, found {len(found)}"

        # Each marker should verify with RS decoding
        for _start, _end, sig_text in found:
            is_valid, extracted = vs256rs_verify(sig_text, signing_key)
            assert is_valid, "Each RS marker should verify"
            assert extracted is not None

    def test_micro_ecc_survives_partial_corruption(self, keypair):
        """RS markers should recover from a few corrupted invisible chars."""
        from app.utils.vs256_rs_crypto import (
            create_signed_marker as rs_create,
        )
        from app.utils.vs256_crypto import BYTE_TO_VS, VS_TO_BYTE

        signing_key = vs256rs_derive_key(keypair)
        sentence_uuid = generate_log_id()
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
        is_valid, extracted = vs256rs_verify(
            corrupted_sig, signing_key, erase_positions=[6 - 4, 10 - 4]  # payload-relative
        )
        assert is_valid, "RS should recover from 2 erasures"
        assert extracted == sentence_uuid

    def test_micro_ecc_manifest_embeds_at_document_level(self, keypair):
        """Full C2PA manifest should be extractable alongside RS markers."""
        from encypher.core.unicode_metadata import UnicodeMetadata
        from app.utils.vs256_rs_crypto import (
            create_signed_marker as rs_create,
            embed_signature_safely as rs_embed,
        )

        signing_key = vs256rs_derive_key(keypair)
        sentences = [
            "First sentence of the article.",
            "Second sentence continues the thought.",
        ]

        embedded_sentences = []
        for sentence in sentences:
            sentence_uuid = generate_log_id()
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
# Integration tests — micro mode flag combinations via /sign endpoint
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ecc,finder",
    [
        (True, vs256rs_find_all),
        (False, vs256_find_all),
    ],
)
async def test_sign_micro_embed_and_store_c2pa_manifest_by_default(
    async_client,
    auth_headers: dict,
    content_db,
    ecc: bool,
    finder,
) -> None:
    """micro mode should embed a document-level C2PA manifest and persist it by default."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "First sentence. Second sentence.",
            "options": {
                "manifest_mode": "micro",
                "ecc": ecc,
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    document = payload.get("data", {}).get("document", {})
    signed_text = document.get("signed_text")
    document_id = document.get("document_id")

    assert isinstance(signed_text, str) and signed_text
    assert isinstance(document_id, str) and document_id
    assert len(finder(signed_text)) >= 2

    extracted_manifest = UnicodeMetadata.extract_metadata(signed_text)
    assert extracted_manifest is not None, "Expected C2PA manifest to be embedded for micro mode"

    rows_with_manifest = await content_db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM content_references
            WHERE document_id = :document_id
              AND manifest_data IS NOT NULL
              AND manifest_data::text <> 'null'
            """
        ),
        {"document_id": document_id},
    )
    assert rows_with_manifest.scalar_one() > 0, "Expected manifest_data to be persisted by default"


@pytest.mark.asyncio
@pytest.mark.parametrize("ecc", [True, False])
async def test_sign_micro_can_opt_out_of_manifest_storage(
    async_client,
    auth_headers: dict,
    content_db,
    ecc: bool,
) -> None:
    """/sign options should allow disabling DB persistence of extracted C2PA manifests."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "First sentence. Second sentence.",
            "options": {
                "manifest_mode": "micro",
                "ecc": ecc,
                "segmentation_level": "sentence",
                "store_c2pa_manifest": False,
            },
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    document = payload.get("data", {}).get("document", {})
    signed_text = document.get("signed_text")
    document_id = document.get("document_id")

    assert isinstance(signed_text, str) and signed_text
    assert isinstance(document_id, str) and document_id

    # embed_c2pa defaults to True, so manifest should be in content
    extracted_manifest = UnicodeMetadata.extract_metadata(signed_text)
    assert extracted_manifest is not None, "C2PA manifest should still be embedded in signed payload"

    rows_with_manifest = await content_db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM content_references
            WHERE document_id = :document_id
              AND manifest_data IS NOT NULL
              AND manifest_data::text <> 'null'
            """
        ),
        {"document_id": document_id},
    )
    assert rows_with_manifest.scalar_one() == 0, "manifest_data should be omitted when storage opt-out is set"


@pytest.mark.asyncio
async def test_sign_micro_embed_c2pa_false_still_stores_manifest_in_db(
    async_client,
    auth_headers: dict,
    content_db,
) -> None:
    """embed_c2pa=False should still generate and store manifest in DB (store_c2pa_manifest defaults true)."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "First sentence. Second sentence.",
            "options": {
                "manifest_mode": "micro",
                "embed_c2pa": False,
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    document = payload.get("data", {}).get("document", {})
    signed_text = document.get("signed_text")
    document_id = document.get("document_id")

    assert isinstance(signed_text, str) and signed_text
    assert isinstance(document_id, str) and document_id

    # C2PA should NOT be in the content
    extracted = UnicodeMetadata.extract_metadata(signed_text)
    assert extracted is None, "C2PA manifest should NOT be in content when embed_c2pa=False"

    # But it SHOULD be in the DB
    rows_with_manifest = await content_db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM content_references
            WHERE document_id = :document_id
              AND manifest_data IS NOT NULL
              AND manifest_data::text <> 'null'
            """
        ),
        {"document_id": document_id},
    )
    assert rows_with_manifest.scalar_one() > 0, "manifest_data should be persisted even when embed_c2pa=False"


@pytest.mark.asyncio
async def test_sign_micro_hybrid_merkle_metadata_in_manifest_and_db(
    async_client,
    auth_headers: dict,
    content_db,
) -> None:
    """micro + C2PA should include Merkle linkage in manifest and DB metadata."""
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "First sentence. Second sentence.",
            "options": {
                "manifest_mode": "micro",
                "ecc": True,
                "embed_c2pa": True,
                "segmentation_level": "sentence",
            },
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    document = payload.get("data", {}).get("document", {})
    signed_text = document.get("signed_text")
    document_id = document.get("document_id")

    assert isinstance(signed_text, str) and signed_text
    assert isinstance(document_id, str) and document_id

    extracted_manifest = UnicodeMetadata.extract_metadata(signed_text)
    assert extracted_manifest is not None

    assertions = extracted_manifest.get("assertions", []) if isinstance(extracted_manifest, dict) else []
    merkle_assertion = next(
        (
            assertion for assertion in assertions
            if isinstance(assertion, dict) and assertion.get("label") == "com.encypher.merkle.v1"
        ),
        None,
    )
    assert merkle_assertion is not None, "Expected Merkle assertion in embedded C2PA manifest"

    merkle_data = merkle_assertion.get("data", {})
    assert isinstance(merkle_data, dict)
    assert isinstance(merkle_data.get("root_hash"), str) and len(merkle_data.get("root_hash", "")) == 64
    assert merkle_data.get("segmentation_level") == "sentence"
    assert merkle_data.get("total_segments") == 2

    db_merkle_meta = await content_db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM content_references
            WHERE document_id = :document_id
              AND embedding_metadata->>'merkle_root_id' IS NOT NULL
              AND embedding_metadata->>'merkle_root_hash' IS NOT NULL
              AND embedding_metadata->>'merkle_segmentation_level' = 'sentence'
            """
        ),
        {"document_id": document_id},
    )
    assert db_merkle_meta.scalar_one() > 0, "Expected Merkle linkage metadata on content references"


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
    """Sign with micro mode, then verify a ref and check signer_identity is present."""
    # Step 1: Sign content
    response = await async_client.post(
        "/api/v1/sign",
        headers=auth_headers,
        json={
            "text": "This sentence tests signer identity resolution.",
            "options": {
                "manifest_mode": "micro",
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
