"""Tests for Pipeline B C2PA verification (document, font, FLAC, JXL).

Tests the full verification chain: extract -> parse JUMBF -> verify COSE ->
verify assertion hashes -> verify content hash.
"""

import pytest
from pathlib import Path

from app.utils.c2pa_manifest_extractor import (
    extract_manifest,
    get_flac_c2pa_data_range,
    get_font_c2pa_table_range,
    get_jxl_c2pa_data_range,
)
from app.services.document_verification_service import verify_document_c2pa

# All signed test files from the conformance pipeline
SIGNED_DIR = Path(__file__).parent / "c2pa_conformance" / "signed"


# --- Extraction tests ---


class TestManifestExtraction:
    """Test that manifest bytes can be extracted from each Pipeline B format."""

    def test_extract_pdf(self):
        data = (SIGNED_DIR / "signed_test.pdf").read_bytes()
        manifest = extract_manifest(data, "application/pdf")
        assert manifest is not None
        assert len(manifest) > 100
        # JUMBF starts with a box: LBox(4) + TBox(4='jumb')
        assert b"jumb" in manifest[:20]

    def test_extract_epub(self):
        data = (SIGNED_DIR / "signed_test.epub").read_bytes()
        manifest = extract_manifest(data, "application/epub+zip")
        assert manifest is not None
        assert len(manifest) > 100

    def test_extract_docx(self):
        data = (SIGNED_DIR / "signed_test.docx").read_bytes()
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        manifest = extract_manifest(data, mime)
        assert manifest is not None
        assert len(manifest) > 100

    def test_extract_odt(self):
        data = (SIGNED_DIR / "signed_test.odt").read_bytes()
        manifest = extract_manifest(data, "application/vnd.oasis.opendocument.text")
        assert manifest is not None
        assert len(manifest) > 100

    def test_extract_otf(self):
        data = (SIGNED_DIR / "signed_test.otf").read_bytes()
        manifest = extract_manifest(data, "font/otf")
        assert manifest is not None
        assert len(manifest) > 100

    def test_extract_ttf(self):
        data = (SIGNED_DIR / "signed_test.ttf").read_bytes()
        manifest = extract_manifest(data, "font/ttf")
        assert manifest is not None
        assert len(manifest) > 100

    def test_extract_flac(self):
        data = (SIGNED_DIR / "signed_test.flac").read_bytes()
        manifest = extract_manifest(data, "audio/flac")
        assert manifest is not None
        assert len(manifest) > 100

    def test_extract_jxl(self):
        data = (SIGNED_DIR / "signed_test.jxl").read_bytes()
        manifest = extract_manifest(data, "image/jxl")
        assert manifest is not None
        assert len(manifest) > 100


class TestRangeHelpers:
    """Test that manifest byte ranges are correctly identified."""

    def test_font_c2pa_range(self):
        data = (SIGNED_DIR / "signed_test.otf").read_bytes()
        result = get_font_c2pa_table_range(data)
        assert result is not None
        offset, length = result
        assert offset > 0
        assert length > 0
        assert offset + length <= len(data)

    def test_flac_c2pa_range(self):
        data = (SIGNED_DIR / "signed_test.flac").read_bytes()
        result = get_flac_c2pa_data_range(data)
        assert result is not None
        offset, length = result
        assert offset > 0
        assert length > 0

    def test_jxl_c2pa_range(self):
        data = (SIGNED_DIR / "signed_test.jxl").read_bytes()
        result = get_jxl_c2pa_data_range(data)
        assert result is not None
        offset, length = result
        assert offset > 0
        assert length > 0


# --- Full verification tests ---


class TestPipelineBVerification:
    """Test full Pipeline B verification for each format."""

    def test_verify_pdf(self):
        data = (SIGNED_DIR / "signed_test.pdf").read_bytes()
        result = verify_document_c2pa(data, "application/pdf")
        assert result.error is None, f"PDF verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True
        assert result.c2pa_instance_id is not None

    def test_verify_epub(self):
        data = (SIGNED_DIR / "signed_test.epub").read_bytes()
        result = verify_document_c2pa(data, "application/epub+zip")
        assert result.error is None, f"EPUB verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_verify_docx(self):
        data = (SIGNED_DIR / "signed_test.docx").read_bytes()
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        result = verify_document_c2pa(data, mime)
        assert result.error is None, f"DOCX verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_verify_odt(self):
        data = (SIGNED_DIR / "signed_test.odt").read_bytes()
        result = verify_document_c2pa(data, "application/vnd.oasis.opendocument.text")
        assert result.error is None, f"ODT verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_verify_otf(self):
        data = (SIGNED_DIR / "signed_test.otf").read_bytes()
        result = verify_document_c2pa(data, "font/otf")
        assert result.error is None, f"OTF verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_verify_ttf(self):
        data = (SIGNED_DIR / "signed_test.ttf").read_bytes()
        result = verify_document_c2pa(data, "font/ttf")
        assert result.error is None, f"TTF verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_verify_flac(self):
        data = (SIGNED_DIR / "signed_test.flac").read_bytes()
        result = verify_document_c2pa(data, "audio/flac")
        assert result.error is None, f"FLAC verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_verify_jxl(self):
        data = (SIGNED_DIR / "signed_test.jxl").read_bytes()
        result = verify_document_c2pa(data, "image/jxl")
        assert result.error is None, f"JXL verification error: {result.error}"
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True


class TestTamperDetection:
    """Test that tampering is detected."""

    def test_tampered_pdf_detected(self):
        data = bytearray((SIGNED_DIR / "signed_test.pdf").read_bytes())
        # Flip a byte near the end (in the actual content, not the manifest)
        if len(data) > 200:
            data[-100] ^= 0xFF
        result = verify_document_c2pa(bytes(data), "application/pdf")
        # Either the extraction fails, the COSE fails, or the hash fails
        assert result.valid is False or result.hash_matches is False

    def test_tampered_otf_detected(self):
        data = bytearray((SIGNED_DIR / "signed_test.otf").read_bytes())
        if len(data) > 200:
            data[50] ^= 0xFF  # Flip a byte in the font header area
        result = verify_document_c2pa(bytes(data), "font/otf")
        assert result.valid is False or result.hash_matches is False

    def test_no_manifest_returns_invalid(self):
        """Unsigned file should return valid=False."""
        from app.utils.c2pa_manifest_extractor import _extract_from_font

        # Use an unsigned fixture
        fixture = Path(__file__).parent / "c2pa_conformance" / "fixtures" / "test.pdf"
        if fixture.exists():
            data = fixture.read_bytes()
            result = verify_document_c2pa(data, "application/pdf")
            assert result.valid is False
            assert "No C2PA manifest" in (result.error or "")
