# TEAM_157: Tests for signing existing PDFs
"""Tests for sign_existing module — sign pre-existing PDFs without visual changes."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import fitz
import pytest

from xml_to_pdf.sign_existing import (
    SignExistingError,
    _ZwInsertion,
    _build_char_position_map,
    _diff_for_insertions,
    _inject_zw_chars_into_pages,
    extract_text_from_pdf,
    inject_signed_text_stream,
    sign_existing_pdf,
)
from xml_to_pdf.signer import SignResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a simple multi-page PDF for testing."""
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Hello World", fontsize=14)
    page1.insert_text((72, 100), "This is page one.", fontsize=11)
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Page Two", fontsize=14)
    page2.insert_text((72, 100), "Second page content.", fontsize=11)
    out = tmp_path / "sample.pdf"
    doc.save(str(out))
    doc.close()
    return out


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    """Create a PDF with no text content."""
    doc = fitz.open()
    doc.new_page()
    out = tmp_path / "empty.pdf"
    doc.save(str(out))
    doc.close()
    return out


# ---------------------------------------------------------------------------
# extract_text_from_pdf
# ---------------------------------------------------------------------------

class TestExtractTextFromPdf:
    def test_extracts_text_from_sample(self, sample_pdf: Path):
        text = extract_text_from_pdf(str(sample_pdf))
        assert "Hello World" in text
        assert "This is page one." in text
        assert "Page Two" in text
        assert "Second page content." in text

    def test_multipage_text_joined(self, sample_pdf: Path):
        text = extract_text_from_pdf(str(sample_pdf))
        # Pages should be separated (not concatenated without separator)
        assert len(text) > 0

    def test_empty_pdf_raises(self, empty_pdf: Path):
        with pytest.raises(SignExistingError, match="No text"):
            extract_text_from_pdf(str(empty_pdf))

    def test_nonexistent_file_raises(self):
        with pytest.raises(SignExistingError, match="not found"):
            extract_text_from_pdf("/nonexistent/path.pdf")

    def test_non_pdf_file_raises(self, tmp_path: Path):
        txt = tmp_path / "not_a.pdf"
        txt.write_text("just text")
        with pytest.raises(SignExistingError):
            extract_text_from_pdf(str(txt))


# ---------------------------------------------------------------------------
# inject_signed_text_stream
# ---------------------------------------------------------------------------

class TestInjectSignedTextStream:
    def test_injects_stream_into_catalog(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "signed.pdf"
        signed_text = "Hello World\n\nThis is signed."
        inject_signed_text_stream(str(sample_pdf), str(out), signed_text)

        doc = fitz.open(str(out))
        cat = doc.pdf_catalog()
        result = doc.xref_get_key(cat, "EncypherSignedText")
        assert result[0] == "xref", f"Expected xref, got {result}"
        ref_xref = int(result[1].split()[0])
        stream_data = doc.xref_stream(ref_xref)
        assert stream_data == signed_text.encode("utf-8")
        doc.close()

    def test_preserves_page_count(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "signed.pdf"
        inject_signed_text_stream(str(sample_pdf), str(out), "test")

        orig = fitz.open(str(sample_pdf))
        signed = fitz.open(str(out))
        assert orig.page_count == signed.page_count
        orig.close()
        signed.close()

    def test_preserves_text_content(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "signed.pdf"
        inject_signed_text_stream(str(sample_pdf), str(out), "test")

        orig = fitz.open(str(sample_pdf))
        signed = fitz.open(str(out))
        for i in range(orig.page_count):
            assert orig[i].get_text() == signed[i].get_text()
        orig.close()
        signed.close()

    def test_in_place_when_no_output(self, sample_pdf: Path):
        original_bytes = sample_pdf.read_bytes()
        inject_signed_text_stream(str(sample_pdf), None, "test in-place")

        doc = fitz.open(str(sample_pdf))
        cat = doc.pdf_catalog()
        result = doc.xref_get_key(cat, "EncypherSignedText")
        assert result[0] == "xref"
        ref_xref = int(result[1].split()[0])
        stream_data = doc.xref_stream(ref_xref)
        assert stream_data == b"test in-place"
        doc.close()

    def test_unicode_signed_text(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "signed.pdf"
        # Include invisible chars like variation selectors and ZW chars
        signed_text = "Hello\ufe01 world\u200b end\ufe02."
        inject_signed_text_stream(str(sample_pdf), str(out), signed_text)

        doc = fitz.open(str(out))
        cat = doc.pdf_catalog()
        ref_xref = int(doc.xref_get_key(cat, "EncypherSignedText")[1].split()[0])
        stream_data = doc.xref_stream(ref_xref)
        assert stream_data == signed_text.encode("utf-8")
        doc.close()


# ---------------------------------------------------------------------------
# sign_existing_pdf (integration with mocked API)
# ---------------------------------------------------------------------------

class TestSignExistingPdf:
    @patch("xml_to_pdf.sign_existing.sign_text")
    def test_sign_existing_pdf_basic(self, mock_sign, sample_pdf: Path, tmp_path: Path):
        mock_sign.return_value = SignResult(
            mode="minimal",
            signed_text="Hello World signed\n\nPage two signed",
            document_id="doc-123",
            verification_url="https://verify.example.com/doc-123",
            total_segments=2,
        )

        out = tmp_path / "signed.pdf"
        result = sign_existing_pdf(
            str(sample_pdf),
            str(out),
            mode="minimal",
            api_key="test-key",
        )

        assert result.document_id == "doc-123"
        assert result.signed_text == "Hello World signed\n\nPage two signed"

        # Verify the stream was injected
        doc = fitz.open(str(out))
        cat = doc.pdf_catalog()
        ref = doc.xref_get_key(cat, "EncypherSignedText")
        assert ref[0] == "xref"
        ref_xref = int(ref[1].split()[0])
        stream = doc.xref_stream(ref_xref)
        assert stream == b"Hello World signed\n\nPage two signed"
        doc.close()

        # Verify sign_text was called with extracted text
        mock_sign.assert_called_once()
        call_kwargs = mock_sign.call_args
        assert call_kwargs[0][2] == "minimal"  # mode arg
        assert "test-key" == call_kwargs[1]["api_key"]

    @patch("xml_to_pdf.sign_existing.sign_text")
    def test_sign_injects_zw_into_text_layer(self, mock_sign, sample_pdf: Path, tmp_path: Path):
        # Signed text has a ZW space inserted after "Hello"
        mock_sign.return_value = SignResult(
            mode="zw_sentence",
            signed_text="Hello\u200b World\nThis is page one.\n\nPage Two\nSecond page content.",
            document_id="doc-456",
            verification_url="https://verify.example.com/doc-456",
            total_segments=1,
        )

        out = tmp_path / "signed.pdf"
        sign_existing_pdf(str(sample_pdf), str(out), mode="zw_sentence", api_key="k")

        # The ZW space should be extractable from the text layer
        doc = fitz.open(str(out))
        page_text = doc[0].get_text()
        zwsp = "\u200b"
        assert zwsp in page_text, "ZW space not found in text layer"
        doc.close()

    @patch("xml_to_pdf.sign_existing.sign_text")
    def test_custom_title(self, mock_sign, sample_pdf: Path, tmp_path: Path):
        mock_sign.return_value = SignResult(
            mode="minimal",
            signed_text="signed",
            document_id="doc-789",
            verification_url="https://verify.example.com/doc-789",
            total_segments=1,
        )

        out = tmp_path / "signed.pdf"
        sign_existing_pdf(
            str(sample_pdf), str(out),
            mode="minimal", api_key="k",
            document_title="My Custom Title",
        )

        # Verify title was passed to sign_text
        call_args = mock_sign.call_args
        assert call_args[0][1] == "My Custom Title"

    @patch("xml_to_pdf.sign_existing.sign_text")
    def test_default_title_from_filename(self, mock_sign, sample_pdf: Path, tmp_path: Path):
        mock_sign.return_value = SignResult(
            mode="minimal",
            signed_text="signed",
            document_id="doc-000",
            verification_url="https://verify.example.com/doc-000",
            total_segments=1,
        )

        out = tmp_path / "signed.pdf"
        sign_existing_pdf(str(sample_pdf), str(out), mode="minimal", api_key="k")

        call_args = mock_sign.call_args
        assert call_args[0][1] == "sample"  # filename stem as default title


# ---------------------------------------------------------------------------
# Internal helpers: _build_char_position_map, _diff_for_insertions
# ---------------------------------------------------------------------------

class TestBuildCharPositionMap:
    def test_returns_chars_with_positions(self, sample_pdf: Path):
        doc = fitz.open(str(sample_pdf))
        chars = _build_char_position_map(doc)
        doc.close()

        assert len(chars) > 0
        # First char should be 'H' from "Hello World"
        assert chars[0]["c"] == "H"
        assert chars[0]["page"] == 0
        assert "x" in chars[0]
        assert "y" in chars[0]

    def test_multipage_chars(self, sample_pdf: Path):
        doc = fitz.open(str(sample_pdf))
        chars = _build_char_position_map(doc)
        doc.close()

        pages = {c["page"] for c in chars}
        assert 0 in pages
        assert 1 in pages


class TestDiffForInsertions:
    def test_finds_zw_insertions(self):
        original = "Hello World"
        signed = "Hello\u200b World"
        # Simulate char positions for "Hello World" (11 chars)
        positions = [{"c": c, "x": float(i * 10), "y": 700.0, "page": 0} for i, c in enumerate(original)]

        insertions = _diff_for_insertions(original, signed, positions)

        assert len(insertions) == 1
        assert insertions[0].char == "\u200b"
        # Should be placed after 'o' (index 4, x=40.0)
        assert insertions[0].x == 40.0
        assert insertions[0].page_num == 0

    def test_multiple_insertions(self):
        original = "AB CD"
        signed = "A\u200bB\u200c CD"
        positions = [{"c": c, "x": float(i * 10), "y": 700.0, "page": 0} for i, c in enumerate(original)]

        insertions = _diff_for_insertions(original, signed, positions)

        assert len(insertions) == 2
        assert insertions[0].char == "\u200b"
        assert insertions[1].char == "\u200c"

    def test_no_insertions_when_identical(self):
        original = "Hello"
        positions = [{"c": c, "x": float(i * 10), "y": 700.0, "page": 0} for i, c in enumerate(original)]

        insertions = _diff_for_insertions(original, original, positions)
        assert len(insertions) == 0

    def test_skips_newlines(self):
        original = "AB\nCD"
        signed = "A\u200bB\nCD"
        # Only visible chars get positions (A, B, C, D = 4 chars)
        visible = [c for c in original if c != "\n"]
        positions = [{"c": c, "x": float(i * 10), "y": 700.0, "page": 0} for i, c in enumerate(visible)]

        insertions = _diff_for_insertions(original, signed, positions)
        assert len(insertions) == 1
        assert insertions[0].char == "\u200b"


class TestInjectZwCharsIntoPages:
    def test_injects_extractable_zw_chars(self, sample_pdf: Path, tmp_path: Path):
        doc = fitz.open(str(sample_pdf))
        chars = _build_char_position_map(doc)

        # Insert a ZW space after the first char on page 0
        insertions = [
            _ZwInsertion(page_num=0, x=chars[0]["x"], y=chars[0]["y"], char="\u200b"),
        ]
        _inject_zw_chars_into_pages(doc, insertions)

        out = tmp_path / "injected.pdf"
        doc.save(str(out))
        doc.close()

        # Verify the ZW char is extractable
        doc2 = fitz.open(str(out))
        text = doc2[0].get_text()
        zwsp = "\u200b"
        assert zwsp in text, "ZW space not found in extracted text"
        doc2.close()

    def test_no_insertions_is_noop(self, sample_pdf: Path, tmp_path: Path):
        doc = fitz.open(str(sample_pdf))
        orig_text = doc[0].get_text()

        _inject_zw_chars_into_pages(doc, [])

        out = tmp_path / "noop.pdf"
        doc.save(str(out))
        doc.close()

        doc2 = fitz.open(str(out))
        assert doc2[0].get_text() == orig_text
        doc2.close()
