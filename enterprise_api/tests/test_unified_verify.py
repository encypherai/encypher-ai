"""Tests for unified verify endpoint and service.

TEAM_273: Tests for POST /api/v1/verify (text + media).
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.verify_schemas import (
    ContentInfo,
    SignerInfo,
    UnifiedVerifyRequest,
    UnifiedVerifyResponse,
    VerifyDocument,
    VerifyOptions,
)
from app.services.unified_verify_service import (
    classify_mime,
    verify_media,
    verify_text,
    _map_c2pa_result,
)
from app.utils.c2pa_verifier_core import C2paVerificationResult


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


class TestUnifiedVerifyRequest:
    def test_text_mode(self):
        req = UnifiedVerifyRequest(text="Hello world")
        docs = req.get_documents()
        assert len(docs) == 1
        assert docs[0].text == "Hello world"

    def test_batch_mode(self):
        req = UnifiedVerifyRequest(
            documents=[
                VerifyDocument(text="doc1"),
                VerifyDocument(text="doc2", document_id="d2"),
            ]
        )
        assert len(req.get_documents()) == 2

    def test_neither_raises(self):
        with pytest.raises(ValueError, match="exactly one"):
            UnifiedVerifyRequest()

    def test_both_raises(self):
        with pytest.raises(ValueError, match="exactly one"):
            UnifiedVerifyRequest(
                text="hello",
                documents=[VerifyDocument(text="world")],
            )

    def test_default_options(self):
        req = UnifiedVerifyRequest(text="test")
        assert req.options.include_tamper_localization is False
        assert req.options.detect_print_fingerprint is True
        assert req.options.segmentation_level == "sentence"


class TestVerifyOptions:
    def test_defaults(self):
        opts = VerifyOptions()
        assert opts.include_tamper_localization is False
        assert opts.include_attribution is False
        assert opts.detect_plagiarism is False
        assert opts.fuzzy_search is False
        assert opts.min_match_percentage == 0.0
        assert opts.search_scope == "organization"
        assert opts.detect_print_fingerprint is True
        assert opts.include_heat_map is False
        assert opts.fuzzy_similarity_threshold == 0.82
        assert opts.fuzzy_max_candidates == 20
        assert opts.fuzzy_fallback_when_no_binding is True

    def test_override(self):
        opts = VerifyOptions(
            include_tamper_localization=True,
            segmentation_level="paragraph",
        )
        assert opts.include_tamper_localization is True
        assert opts.segmentation_level == "paragraph"

    def test_invalid_segmentation_level_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            VerifyOptions(segmentation_level="word")


class TestResponseModels:
    def test_signer_info(self):
        s = SignerInfo(organization_id="org_123", trust_level="trusted")
        assert s.organization_id == "org_123"
        assert s.organization_name is None
        assert s.ca_backed is None

    def test_content_info_text(self):
        c = ContentInfo(
            manifest_mode="micro",
            embeddings_found=5,
            leaf_hash_verified=True,
        )
        assert c.manifest_mode == "micro"
        assert c.c2pa_manifest_valid is None

    def test_content_info_media(self):
        c = ContentInfo(
            hash_verified=True,
            c2pa_manifest_valid=True,
            c2pa_instance_id="abc-123",
        )
        assert c.hash_verified is True


# ---------------------------------------------------------------------------
# Service unit tests
# ---------------------------------------------------------------------------


class TestClassifyMime:
    def test_image_types(self):
        assert classify_mime("image/jpeg") == "image"
        assert classify_mime("image/png") == "image"
        assert classify_mime("image/webp") == "image"
        assert classify_mime("image/heic") == "image"

    def test_audio_types(self):
        assert classify_mime("audio/mpeg") == "audio"
        assert classify_mime("audio/wav") == "audio"
        assert classify_mime("audio/mp3") == "audio"

    def test_video_types(self):
        assert classify_mime("video/mp4") == "video"
        assert classify_mime("video/webm") == "video"
        assert classify_mime("video/quicktime") == "video"

    def test_unknown(self):
        assert classify_mime("application/pdf") == "unknown"
        assert classify_mime("text/plain") == "unknown"

    def test_case_insensitive(self):
        assert classify_mime("IMAGE/JPEG") == "image"
        assert classify_mime("Audio/MPEG") == "audio"

    def test_generic_prefix_fallback(self):
        assert classify_mime("image/x-custom-format") == "image"
        assert classify_mime("audio/x-custom") == "audio"
        assert classify_mime("video/x-custom") == "video"


class TestMapC2paResult:
    def test_valid_result(self):
        c2pa = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
            c2pa_instance_id="inst-1",
            signer="Acme Corp",
            signed_at="2026-01-01T00:00:00Z",
            manifest_data={"key": "val"},
        )
        resp = _map_c2pa_result(c2pa, "image", "corr-1")
        assert resp.valid is True
        assert resp.tampered is False
        assert resp.reason_code == "OK"
        assert resp.media_type == "image"
        assert resp.correlation_id == "corr-1"
        assert resp.signer.organization_id == "Acme Corp"
        assert resp.content.hash_verified is True
        assert resp.content.c2pa_manifest_valid is True
        assert resp.content.c2pa_instance_id == "inst-1"

    def test_invalid_result(self):
        c2pa = C2paVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
        )
        resp = _map_c2pa_result(c2pa, "audio", "corr-2")
        assert resp.valid is False
        assert resp.tampered is True
        assert resp.reason_code == "SIGNATURE_INVALID"
        assert resp.signer is None

    def test_error_result(self):
        c2pa = C2paVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
            error="c2pa-python not installed",
        )
        resp = _map_c2pa_result(c2pa, "video", "corr-3")
        assert resp.valid is False
        assert resp.tampered is False
        assert resp.reason_code == "VERIFY_EXCEPTION"
        assert resp.error == "c2pa-python not installed"


class TestVerifyMedia:
    @patch("app.services.image_verification_service.verify_image_c2pa")
    def test_routes_image(self, mock_verify):
        mock_verify.return_value = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )
        resp = verify_media(b"fake-image", "image/jpeg")
        mock_verify.assert_called_once_with(b"fake-image", "image/jpeg")
        assert resp.valid is True
        assert resp.media_type == "image"

    @patch("app.services.audio_verification_service.verify_audio_c2pa")
    def test_routes_audio(self, mock_verify):
        mock_verify.return_value = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )
        resp = verify_media(b"fake-audio", "audio/mpeg")
        mock_verify.assert_called_once_with(b"fake-audio", "audio/mpeg")
        assert resp.media_type == "audio"

    @patch("app.services.video_verification_service.verify_video_c2pa")
    def test_routes_video(self, mock_verify):
        mock_verify.return_value = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )
        resp = verify_media(b"fake-video", "video/mp4")
        mock_verify.assert_called_once_with(b"fake-video", "video/mp4")
        assert resp.media_type == "video"

    def test_unsupported_mime(self):
        resp = verify_media(b"fake", "application/pdf")
        assert resp.valid is False
        assert resp.reason_code == "UNSUPPORTED_MEDIA_TYPE"
        assert "Unsupported" in resp.error


class TestVerifyText:
    @pytest.mark.asyncio
    @patch("app.services.verification_logic.execute_verification")
    @patch("app.services.verification_logic.determine_reason_code")
    @patch("app.services.verification_logic.build_verdict")
    async def test_text_verification_valid(self, mock_build, mock_reason, mock_exec):
        from types import SimpleNamespace

        mock_exec.return_value = SimpleNamespace(
            is_valid=True,
            signer_id="org_demo",
            manifest={"manifest_mode": "micro"},
            resolved_cert=None,
            trust_status="trusted",
        )
        mock_reason.return_value = "OK"

        from app.models.response_models import VerifyVerdict

        mock_build.return_value = VerifyVerdict(
            valid=True,
            tampered=False,
            reason_code="OK",
            signer_id="org_demo",
            signer_name="Demo Org",
            timestamp=None,
            details={
                "manifest": {"manifest_mode": "micro"},
                "duration_ms": 42,
            },
        )

        resp = await verify_text(
            "Hello world",
            options=VerifyOptions(),
            core_db=AsyncMock(),
            content_db=AsyncMock(),
        )

        assert resp.valid is True
        assert resp.reason_code == "OK"
        assert resp.media_type == "text"
        assert resp.signer.organization_id == "org_demo"

    @pytest.mark.asyncio
    @patch("app.services.verification_logic.execute_verification")
    @patch("app.services.verification_logic.determine_reason_code")
    @patch("app.services.verification_logic.build_verdict")
    async def test_text_verification_tampered(self, mock_build, mock_reason, mock_exec):
        from types import SimpleNamespace

        mock_exec.return_value = SimpleNamespace(
            is_valid=False,
            signer_id="org_demo",
            manifest={},
            resolved_cert=None,
            trust_status=None,
        )
        mock_reason.return_value = "SIGNATURE_INVALID"

        from app.models.response_models import VerifyVerdict

        mock_build.return_value = VerifyVerdict(
            valid=False,
            tampered=True,
            reason_code="SIGNATURE_INVALID",
            signer_id="org_demo",
            signer_name=None,
            timestamp=None,
            details={"manifest": {}},
        )

        resp = await verify_text(
            "tampered text",
            options=VerifyOptions(),
            core_db=AsyncMock(),
        )

        assert resp.valid is False
        assert resp.tampered is True
        assert resp.reason_code == "SIGNATURE_INVALID"


# ---------------------------------------------------------------------------
# Integration tests (endpoint-level)
# ---------------------------------------------------------------------------


class TestUnifiedVerifyEndpoint:
    """Integration tests that hit the actual FastAPI endpoint."""

    @pytest.mark.asyncio
    async def test_text_verify_returns_200(self, async_client):
        """POST /api/v1/public/verify with text body returns 200."""
        resp = await async_client.post(
            "/api/v1/public/verify",
            json={"text": "This is unsigned plain text."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "valid" in data
        assert "reason_code" in data
        assert data["media_type"] == "text"
        assert "correlation_id" in data

    @pytest.mark.asyncio
    async def test_text_verify_empty_text_400(self, async_client):
        """Empty text should return 400."""
        resp = await async_client.post(
            "/api/v1/public/verify",
            json={"text": "   "},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_text_verify_neither_input_422(self, async_client):
        """No text or documents should return 422 (validation error)."""
        resp = await async_client.post(
            "/api/v1/public/verify",
            json={},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_media_verify_unsupported_mime(self, async_client):
        """Multipart with unsupported MIME returns unsupported error."""
        resp = await async_client.post(
            "/api/v1/public/verify/media",
            files={"file": ("test.pdf", b"fake-pdf-bytes", "application/pdf")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert data["reason_code"] == "UNSUPPORTED_MEDIA_TYPE"

    @pytest.mark.asyncio
    async def test_media_verify_no_file_422(self, async_client):
        """Multipart with no file should return 422."""
        resp = await async_client.post(
            "/api/v1/public/verify/media",
            data={"mime_type": "image/jpeg"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Advanced feature helper tests (TEAM_273 Phase 2)
# ---------------------------------------------------------------------------


class TestExtractManifestMetadata:
    def test_nested_custom_metadata(self):
        from app.services.unified_verify_service import _extract_manifest_metadata

        manifest = {
            "custom_metadata": {"document_id": "doc-1", "organization_id": "org-1"},
        }
        meta = _extract_manifest_metadata(manifest)
        assert meta["document_id"] == "doc-1"
        assert meta["organization_id"] == "org-1"

    def test_nested_manifest_metadata(self):
        from app.services.unified_verify_service import _extract_manifest_metadata

        manifest = {
            "manifest": {
                "custom_metadata": {"document_id": "doc-2"},
            },
        }
        meta = _extract_manifest_metadata(manifest)
        assert meta["document_id"] == "doc-2"

    def test_assertion_metadata(self):
        from app.services.unified_verify_service import _extract_manifest_metadata

        manifest = {
            "assertions": [
                {"label": "org.encypher.metadata", "data": {"organization_id": "org-3"}},
                {"label": "other", "data": {"ignored": True}},
            ],
        }
        meta = _extract_manifest_metadata(manifest)
        assert meta["organization_id"] == "org-3"
        assert "ignored" not in meta

    def test_empty_manifest(self):
        from app.services.unified_verify_service import _extract_manifest_metadata

        assert _extract_manifest_metadata({}) == {}
        assert _extract_manifest_metadata("not-a-dict") == {}


class TestBuildLocalizationEvents:
    def test_no_changes(self):
        from app.services.unified_verify_service import _build_localization_events

        result = _build_localization_events(
            stored_hashes=["a", "b", "c"],
            request_hashes=["a", "b", "c"],
            request_segments=["seg1", "seg2", "seg3"],
        )
        assert result["events"] == []
        assert result["counts"] == {"changed": 0, "inserted": 0, "deleted": 0}

    def test_changed_segment(self):
        from app.services.unified_verify_service import _build_localization_events

        result = _build_localization_events(
            stored_hashes=["a", "b", "c"],
            request_hashes=["a", "X", "c"],
            request_segments=["seg1", "MODIFIED", "seg3"],
        )
        assert len(result["events"]) == 1
        assert result["events"][0]["type"] == "changed"
        assert result["counts"]["changed"] >= 1

    def test_inserted_segment(self):
        from app.services.unified_verify_service import _build_localization_events

        result = _build_localization_events(
            stored_hashes=["a", "c"],
            request_hashes=["a", "b", "c"],
            request_segments=["seg1", "NEW", "seg3"],
        )
        assert result["counts"]["inserted"] >= 1

    def test_deleted_segment(self):
        from app.services.unified_verify_service import _build_localization_events

        result = _build_localization_events(
            stored_hashes=["a", "b", "c"],
            request_hashes=["a", "c"],
            request_segments=["seg1", "seg3"],
        )
        assert result["counts"]["deleted"] >= 1


class TestRunMerkleVerification:
    @pytest.mark.asyncio
    @patch("app.services.unified_verify_service.merkle_crud")
    async def test_root_found_match(self, mock_crud):
        from app.services.unified_verify_service import run_merkle_verification
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        # Mock a MerkleRoot
        mock_root = MagicMock()
        mock_root.id = "root-uuid-1"
        mock_root.root_hash = "fakehash"

        mock_db = AsyncMock()
        # Mock the select().where().order_by().limit() chain
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_root
        mock_db.execute.return_value = mock_result

        # Mock subhashes
        mock_crud.find_subhashes_by_root = AsyncMock(return_value=[])

        result = await run_merkle_verification(
            text="Hello world.",
            segmentation_level="sentence",
            document_id="doc-1",
            organization_id="org-1",
            content_db=mock_db,
        )
        assert result["tamper_detection"]["status"] in ("computed", "no_segments")

    @pytest.mark.asyncio
    async def test_root_not_found(self):
        from app.services.unified_verify_service import run_merkle_verification

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await run_merkle_verification(
            text="Hello world.",
            segmentation_level="sentence",
            document_id="doc-1",
            organization_id="org-1",
            content_db=mock_db,
        )
        assert result["tamper_detection"]["status"] == "root_not_found"

    @pytest.mark.asyncio
    async def test_metadata_missing(self):
        from app.services.unified_verify_service import run_merkle_verification

        result = await run_merkle_verification(
            text="Hello world.",
            segmentation_level="sentence",
            document_id=None,
            organization_id=None,
            content_db=AsyncMock(),
        )
        assert result["tamper_detection"]["status"] == "metadata_missing"


class TestRunAttribution:
    @pytest.mark.asyncio
    @patch("app.services.merkle_service.MerkleService.find_sources")
    async def test_attribution_returns_sources(self, mock_find):
        from app.services.unified_verify_service import run_attribution

        mock_sub = MagicMock()
        mock_sub.hash_value = "hash-1"
        mock_root = MagicMock()
        mock_root.document_id = "doc-src"
        mock_root.organization_id = "org-src"
        mock_root.root_hash = "root-hash"
        mock_root.segmentation_level = "sentence"
        mock_find.return_value = [(mock_sub, mock_root)]

        result = await run_attribution(
            text="Some text to attribute",
            segmentation_level="sentence",
            db=AsyncMock(),
        )
        assert result["matches_found"] == 1
        assert result["sources"][0]["document_id"] == "doc-src"

    @pytest.mark.asyncio
    @patch("app.services.merkle_service.MerkleService.find_sources")
    async def test_attribution_no_matches(self, mock_find):
        from app.services.unified_verify_service import run_attribution

        mock_find.return_value = []
        result = await run_attribution(
            text="Unique text",
            segmentation_level="sentence",
            db=AsyncMock(),
        )
        assert result["matches_found"] == 0
        assert result["sources"] == []

    @pytest.mark.asyncio
    @patch("app.services.merkle_service.MerkleService.find_sources")
    async def test_attribution_filters_by_org_when_scoped(self, mock_find):
        """Security: attribution results are scoped to caller's org by default."""
        from app.services.unified_verify_service import run_attribution

        own_root = MagicMock()
        own_root.document_id = "doc-own"
        own_root.organization_id = "org-caller"
        own_root.root_hash = "hash-own"
        own_root.segmentation_level = "sentence"

        other_root = MagicMock()
        other_root.document_id = "doc-other"
        other_root.organization_id = "org-other"
        other_root.root_hash = "hash-other"
        other_root.segmentation_level = "sentence"

        sub1 = MagicMock(hash_value="h1")
        sub2 = MagicMock(hash_value="h2")
        mock_find.return_value = [(sub1, own_root), (sub2, other_root)]

        # Default scope = organization -> only own org's results
        result = await run_attribution(
            text="Some text",
            segmentation_level="sentence",
            db=AsyncMock(),
            organization_id="org-caller",
            search_scope="organization",
        )
        assert result["matches_found"] == 1
        assert result["sources"][0]["organization_id"] == "org-caller"

    @pytest.mark.asyncio
    @patch("app.services.merkle_service.MerkleService.find_sources")
    async def test_attribution_cross_org_when_scope_all(self, mock_find):
        """When search_scope=all (Enterprise), cross-org results are included."""
        from app.services.unified_verify_service import run_attribution

        root1 = MagicMock(document_id="d1", organization_id="org-a", root_hash="h1", segmentation_level="sentence")
        root2 = MagicMock(document_id="d2", organization_id="org-b", root_hash="h2", segmentation_level="sentence")
        sub1 = MagicMock(hash_value="s1")
        sub2 = MagicMock(hash_value="s2")
        mock_find.return_value = [(sub1, root1), (sub2, root2)]

        result = await run_attribution(
            text="Some text",
            segmentation_level="sentence",
            db=AsyncMock(),
            organization_id="org-a",
            search_scope="all",
        )
        assert result["matches_found"] == 2


class TestRunPlagiarism:
    @pytest.mark.asyncio
    @patch("app.services.merkle_service.MerkleService.generate_attribution_report")
    async def test_plagiarism_returns_report(self, mock_report):
        from app.services.unified_verify_service import run_plagiarism

        mock_report.return_value = MagicMock(
            id="report-1",
            total_segments=10,
            matched_segments=3,
            source_documents=[{"doc": "src-1", "match_percentage": 30.0}],
            heat_map_data=None,
            scan_timestamp="2026-03-23T00:00:00Z",
        )

        result = await run_plagiarism(
            text="Some text",
            segmentation_level="sentence",
            organization_id="org-1",
            include_heat_map=False,
            min_match_percentage=0.0,
            db=AsyncMock(),
        )
        assert result["total_segments"] == 10
        assert result["matched_segments"] == 3
        assert result["overall_match_percentage"] == 30.0


class TestRunFuzzySearch:
    @pytest.mark.asyncio
    @patch("app.services.fuzzy_fingerprint_service.fuzzy_fingerprint_service.search")
    async def test_fuzzy_search_returns_matches(self, mock_search):
        from app.services.unified_verify_service import run_fuzzy_search

        mock_search.return_value = {
            "matches_found": 2,
            "matches": [{"doc_id": "d1"}, {"doc_id": "d2"}],
            "processing_time_ms": 50,
        }

        result = await run_fuzzy_search(
            text="Some text",
            organization_id="org-1",
            search_scope="organization",
            similarity_threshold=0.82,
            max_candidates=20,
            fallback_when_no_binding=False,
            embeddings_found=0,
            db=AsyncMock(),
        )
        assert result["matches_found"] == 2

    @pytest.mark.asyncio
    async def test_fuzzy_search_fallback_skip(self):
        from app.services.unified_verify_service import run_fuzzy_search

        result = await run_fuzzy_search(
            text="Some text",
            organization_id="org-1",
            search_scope="organization",
            similarity_threshold=0.82,
            max_candidates=20,
            fallback_when_no_binding=True,
            embeddings_found=5,
            db=AsyncMock(),
        )
        assert result["skipped_reason"] == "embeddings_found"
        assert result["matches_found"] == 0


class TestRunPrintFingerprint:
    def test_fingerprint_detected(self):
        from app.services.unified_verify_service import run_print_fingerprint

        # Encode a known fingerprint using thin spaces
        from app.utils.print_stego import encode_print_fingerprint, build_payload

        payload = build_payload("org-1", "doc-1")
        text = "word " * 200  # enough spaces for 128 bits
        encoded = encode_print_fingerprint(text, payload)

        result = run_print_fingerprint(encoded)
        assert result["detected"] is True
        assert result["payload_hex"] is not None

    def test_no_fingerprint(self):
        from app.services.unified_verify_service import run_print_fingerprint

        result = run_print_fingerprint("Plain text with no fingerprint")
        assert result["detected"] is False
        assert result["payload_hex"] is None


class TestResolveRights:
    @pytest.mark.asyncio
    async def test_rights_found(self):
        from app.services.unified_verify_service import resolve_rights

        mock_db = AsyncMock()
        mock_row = MagicMock()
        mock_row.rights_resolution_url = "https://example.com/rights"
        mock_row.rights_snapshot = {"license": "CC-BY"}
        mock_result = MagicMock()
        mock_result.first.return_value = mock_row
        mock_db.execute.return_value = mock_result

        result = await resolve_rights("doc-1", mock_db)
        assert result["resolution_url"] == "https://example.com/rights"
        assert result["snapshot"]["license"] == "CC-BY"

    @pytest.mark.asyncio
    async def test_rights_not_found(self):
        from app.services.unified_verify_service import resolve_rights

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = await resolve_rights("doc-1", mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_rights_no_document_id(self):
        from app.services.unified_verify_service import resolve_rights

        result = await resolve_rights(None, AsyncMock())
        assert result is None


class TestVerifyTextAdvanced:
    """Test that verify_text runs advanced features when options are set."""

    @pytest.mark.asyncio
    @patch("app.services.verification_logic.execute_verification")
    @patch("app.services.verification_logic.determine_reason_code")
    @patch("app.services.verification_logic.build_verdict")
    @patch("app.services.unified_verify_service.run_print_fingerprint")
    async def test_print_fingerprint_always_runs(self, mock_fp, mock_build, mock_reason, mock_exec):
        from types import SimpleNamespace
        from app.models.response_models import VerifyVerdict

        mock_exec.return_value = SimpleNamespace(
            is_valid=True,
            signer_id="org_demo",
            manifest={},
            resolved_cert=None,
            trust_status="trusted",
        )
        mock_reason.return_value = "OK"
        mock_build.return_value = VerifyVerdict(
            valid=True,
            tampered=False,
            reason_code="OK",
            signer_id="org_demo",
            signer_name="Demo Org",
            timestamp=None,
            details={"manifest": {}},
        )
        mock_fp.return_value = {"detected": False, "payload_hex": None}

        resp = await verify_text(
            "Hello world",
            options=VerifyOptions(),
            core_db=AsyncMock(),
            content_db=AsyncMock(),
        )

        mock_fp.assert_called_once()
        assert "print_fingerprint" in resp.details

    @pytest.mark.asyncio
    @patch("app.services.verification_logic.execute_verification")
    @patch("app.services.verification_logic.determine_reason_code")
    @patch("app.services.verification_logic.build_verdict")
    @patch("app.services.unified_verify_service.run_print_fingerprint")
    async def test_print_fingerprint_skipped_when_disabled(self, mock_fp, mock_build, mock_reason, mock_exec):
        from types import SimpleNamespace
        from app.models.response_models import VerifyVerdict

        mock_exec.return_value = SimpleNamespace(
            is_valid=True,
            signer_id=None,
            manifest={},
            resolved_cert=None,
            trust_status=None,
        )
        mock_reason.return_value = "NO_SIGNATURE"
        mock_build.return_value = VerifyVerdict(
            valid=False,
            tampered=False,
            reason_code="NO_SIGNATURE",
            signer_id=None,
            signer_name=None,
            timestamp=None,
            details={"manifest": {}},
        )

        resp = await verify_text(
            "Hello",
            options=VerifyOptions(detect_print_fingerprint=False),
            core_db=AsyncMock(),
        )

        mock_fp.assert_not_called()
        assert "print_fingerprint" not in resp.details

    @pytest.mark.asyncio
    @patch("app.services.verification_logic.execute_verification")
    @patch("app.services.verification_logic.determine_reason_code")
    @patch("app.services.verification_logic.build_verdict")
    @patch("app.services.unified_verify_service.run_merkle_verification")
    @patch("app.services.unified_verify_service.run_print_fingerprint")
    async def test_merkle_runs_when_document_id_found(self, mock_fp, mock_merkle, mock_build, mock_reason, mock_exec):
        from types import SimpleNamespace
        from app.models.response_models import VerifyVerdict

        mock_exec.return_value = SimpleNamespace(
            is_valid=True,
            signer_id="org_demo",
            manifest={"custom_metadata": {"document_id": "doc-1", "organization_id": "org-1"}},
            resolved_cert=None,
            trust_status="trusted",
        )
        mock_reason.return_value = "OK"
        mock_build.return_value = VerifyVerdict(
            valid=True,
            tampered=False,
            reason_code="OK",
            signer_id="org_demo",
            signer_name="Demo",
            timestamp=None,
            details={"manifest": {"custom_metadata": {"document_id": "doc-1", "organization_id": "org-1"}}},
        )
        mock_merkle.return_value = {
            "tamper_detection": {"status": "computed", "root_match": True},
        }
        mock_fp.return_value = {"detected": False, "payload_hex": None}

        resp = await verify_text(
            "Signed text",
            options=VerifyOptions(),
            core_db=AsyncMock(),
            content_db=AsyncMock(),
        )

        mock_merkle.assert_called_once()
        assert "tamper_detection" in resp.details


# ---------------------------------------------------------------------------
# Security hardening tests (TEAM_273 Phase 2 -- security review fixes)
# ---------------------------------------------------------------------------


class TestSearchScopeValidation:
    """Verify search_scope is validated at schema level to prevent Enterprise gate bypass."""

    def test_requires_enterprise_catches_all(self):
        from app.api.v1.public.verify import _requires_enterprise

        opts = VerifyOptions(search_scope="all")
        assert _requires_enterprise(opts) is True

        opts = VerifyOptions(search_scope="organization")
        assert _requires_enterprise(opts) is False

    def test_valid_scopes_accepted(self):
        """All three valid scopes should be accepted by VerifyOptions."""
        for scope in ("organization", "public", "all"):
            opts = VerifyOptions(search_scope=scope)
            assert opts.search_scope == scope

    def test_invalid_scope_rejected_by_pydantic(self):
        """Invalid scopes (including case variants) are rejected at parse time."""
        from pydantic import ValidationError

        for bad_scope in ("ALL", "All", "invalid", "  all  "):
            with pytest.raises(ValidationError):
                VerifyOptions(search_scope=bad_scope)


class TestAttributionOrgScoping:
    """Verify attribution results are filtered by caller's organization."""

    @pytest.mark.asyncio
    @patch("app.services.merkle_service.MerkleService.find_sources")
    async def test_no_org_id_returns_all(self, mock_find):
        """When no org_id is provided (unauthenticated), all results returned."""
        from app.services.unified_verify_service import run_attribution

        root = MagicMock(
            document_id="d1",
            organization_id="org-x",
            root_hash="h1",
            segmentation_level="sentence",
        )
        mock_find.return_value = [(MagicMock(hash_value="s1"), root)]

        # No org_id + default scope -> no filtering (org_id is None)
        result = await run_attribution(
            text="text",
            segmentation_level="sentence",
            db=AsyncMock(),
            organization_id=None,
            search_scope="organization",
        )
        # With no org_id to filter against, results pass through
        assert result["matches_found"] == 1
