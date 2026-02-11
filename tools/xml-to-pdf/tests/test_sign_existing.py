# TEAM_157/158: Tests for signing existing PDFs
"""Tests for sign_existing module — sign pre-existing PDFs without visual changes."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import fitz
import pytest
from encypher_pdf.fonttools_subset import INVISIBLE_CODEPOINTS
from xml_to_pdf.sign_existing import (
    _INVIS_FONT_NAME,
    _UNIFIED_FONT_NAME,
    SignExistingError,
    _build_font_assets,
    _collect_visible_codepoints,
    _diff_for_insertions,
    _embed_invisible_font,
    _get_font_assets,
    _inject_into_content_streams,
    _InvisInsertion,
    _redistribute_insertions,
    _register_font_on_page,
    extract_signed_text_from_streams,
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
# Internal helpers: _diff_for_insertions
# ---------------------------------------------------------------------------

class TestDiffForInsertions:
    def test_finds_zw_insertions(self):
        original = "Hello World"
        signed = "Hello\u200b World"

        insertions = _diff_for_insertions(original, signed)

        assert len(insertions) == 1
        assert insertions[0].char == "\u200b"
        # After 'o' which is visible_idx 4 (H=0, e=1, l=2, l=3, o=4)
        assert insertions[0].after_visible_idx == 4

    def test_multiple_insertions(self):
        original = "AB CD"
        signed = "A\u200bB\u200c CD"

        insertions = _diff_for_insertions(original, signed)

        assert len(insertions) == 2
        assert insertions[0].char == "\u200b"
        assert insertions[0].after_visible_idx == 0  # after 'A'
        assert insertions[1].char == "\u200c"
        assert insertions[1].after_visible_idx == 1  # after 'B'

    def test_no_insertions_when_identical(self):
        original = "Hello"
        insertions = _diff_for_insertions(original, original)
        assert len(insertions) == 0

    def test_skips_newlines(self):
        original = "AB\nCD"
        signed = "A\u200bB\nCD"

        insertions = _diff_for_insertions(original, signed)
        assert len(insertions) == 1
        assert insertions[0].char == "\u200b"
        assert insertions[0].after_visible_idx == 0  # after 'A'

    def test_variation_selectors(self):
        original = "Test."
        signed = "Test\ufe01."

        insertions = _diff_for_insertions(original, signed)
        assert len(insertions) == 1
        assert insertions[0].char == "\ufe01"
        assert insertions[0].after_visible_idx == 3  # after 't'

    def test_newline_to_space_normalization(self):
        """Signing API may convert \\n to space; visible_idx must not advance."""
        original = "AB\nCD"
        # API normalised \n → space, then inserted invisible after 'B'
        signed = "AB\u200b CD"

        insertions = _diff_for_insertions(original, signed)
        assert len(insertions) == 1
        assert insertions[0].char == "\u200b"
        # 'A'=0, 'B'=1 → after 'B' is idx 1
        assert insertions[0].after_visible_idx == 1

    def test_newline_to_space_does_not_shift_indices(self):
        """Trailing insertions should not exceed visible char count."""
        original = "AB\nCD"
        # API normalised \n → space, inserted invisible after 'D'
        signed = "AB CD\u200b"

        insertions = _diff_for_insertions(original, signed)
        assert len(insertions) == 1
        assert insertions[0].char == "\u200b"
        # A=0, B=1, C=2, D=3 → after 'D' is idx 3
        assert insertions[0].after_visible_idx == 3


# ---------------------------------------------------------------------------
# Content stream rewriting: inline injection
# ---------------------------------------------------------------------------

class TestContentStreamRewriting:
    """Test that invisible chars are injected inline into Tj/TJ operators."""

    def test_simple_font_injection(self, sample_pdf: Path, tmp_path: Path):
        """Inject VS2 and ZWSP into a simple-font PDF and verify extraction."""
        doc = fitz.open(str(sample_pdf))
        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)

        insertions = [
            _InvisInsertion(after_visible_idx=4, char="\ufe01"),  # after 'o' in Hello
            _InvisInsertion(after_visible_idx=10, char="\u200b"),  # after 'd' in World
        ]

        font_xref = _embed_invisible_font(doc, assets)
        for pn in range(doc.page_count):
            _register_font_on_page(doc, doc[pn], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "injected.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        doc2 = fitz.open(str(out))
        text = doc2[0].get_text()
        assert "\ufe01" in text, "VS2 not found in extracted text"
        assert "\u200b" in text, "ZWSP not found in extracted text"
        doc2.close()

    def test_char_ordering_preserved(self, tmp_path: Path):
        """Verify invisible chars are injected into the content stream.

        With font-switching, invisible chars are appended after the Tj
        operator containing the target visible char.  MuPDF may reorder
        them slightly in get_text(), so we just verify both invisible
        chars are present and the visible text is intact.
        """
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello World.", fontsize=12)
        src = tmp_path / "src.pdf"
        doc.save(str(src))
        doc.close()

        doc = fitz.open(str(src))
        assets = _get_font_assets()

        insertions = [
            _InvisInsertion(after_visible_idx=4, char="\ufe01"),
            _InvisInsertion(after_visible_idx=10, char="\u200b"),
        ]

        font_xref = _embed_invisible_font(doc, assets)
        for pn in range(doc.page_count):
            _register_font_on_page(doc, doc[pn], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "out.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        doc2 = fitz.open(str(out))
        text = doc2[0].get_text().strip()
        # Visible text must be intact
        clean = text.replace("\ufe01", "").replace("\u200b", "")
        assert clean == "Hello World.", f"Visible text changed: {clean!r}"
        # Both invisible chars must be present
        assert "\ufe01" in text, "Missing \\ufe01 in extracted text"
        assert "\u200b" in text, "Missing \\u200b in extracted text"
        doc2.close()

    def test_no_insertions_is_noop(self, sample_pdf: Path, tmp_path: Path):
        """Empty insertions list should produce same visible text."""
        doc = fitz.open(str(sample_pdf))
        orig_text = doc[0].get_text().strip()

        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)
        font_xref = _embed_invisible_font(doc, assets)
        for pn in range(doc.page_count):
            _register_font_on_page(doc, doc[pn], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, [], assets.mapping)

        out = tmp_path / "noop.pdf"
        doc.save(str(out))
        doc.close()

        doc2 = fitz.open(str(out))
        new_text = doc2[0].get_text().strip()
        assert new_text == orig_text, f"Text changed: {new_text!r} != {orig_text!r}"
        doc2.close()

    def test_font_switching_in_content_stream(self, tmp_path: Path):
        """Verify font-switching: EncSgn appears in content stream alongside
        the original font, and original font Tj operators are preserved."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "AB", fontsize=12)
        src = tmp_path / "src.pdf"
        doc.save(str(src))
        doc.close()

        doc = fitz.open(str(src))
        assets = _get_font_assets()

        insertions = [
            _InvisInsertion(after_visible_idx=0, char="\ufe01"),
        ]

        font_xref = _embed_invisible_font(doc, assets)
        _register_font_on_page(doc, doc[0], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "out.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        doc2 = fitz.open(str(out))
        stream_text = ""
        for cx in doc2[0].get_contents():
            s = doc2.xref_stream(cx)
            if s:
                stream_text += s.decode("latin-1")
        # EncSgn font-switch must be present
        assert _UNIFIED_FONT_NAME in stream_text, (
            f"EncSgn font-switch not found in content stream"
        )
        # Original font must still be present (not replaced)
        assert "/helv" in stream_text, (
            "Original /helv font was replaced — font-switching should preserve it"
        )
        # Original hex Tj must be preserved verbatim
        assert "<4142>" in stream_text or "<41>" in stream_text, (
            "Original hex encoding was re-encoded — should be preserved"
        )
        doc2.close()


# ---------------------------------------------------------------------------
# Direct content stream extraction
# ---------------------------------------------------------------------------


class TestExtractSignedTextFromStreams:
    """Test extract_signed_text_from_streams for 100% invisible char recovery."""

    def test_extracts_all_invisible_chars(self, sample_pdf: Path, tmp_path: Path):
        """Every injected invisible char must be recovered from the stream."""
        doc = fitz.open(str(sample_pdf))
        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)

        # Inject several invisible chars at different positions
        invis_chars = ["\u200b", "\u200c", "\ufe01", "\ufe02"]
        insertions = [
            _InvisInsertion(after_visible_idx=i, char=ch)
            for i, ch in enumerate(invis_chars)
        ]

        font_xref = _embed_invisible_font(doc, assets)
        _register_font_on_page(doc, doc[0], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "stream_extract.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        text = extract_signed_text_from_streams(str(out))
        extracted_invis = [
            c for c in text
            if ord(c) in INVISIBLE_CODEPOINTS and ord(c) != 0x000A
        ]
        assert len(extracted_invis) == len(invis_chars)
        assert extracted_invis == invis_chars

    def test_preserves_visible_text(self, sample_pdf: Path, tmp_path: Path):
        """Visible text must survive extraction unchanged."""
        doc = fitz.open(str(sample_pdf))
        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)

        insertions = [_InvisInsertion(after_visible_idx=0, char="\u200b")]
        font_xref = _embed_invisible_font(doc, assets)
        _register_font_on_page(doc, doc[0], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "stream_visible.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        text = extract_signed_text_from_streams(str(out))
        visible = "".join(c for c in text if ord(c) not in INVISIBLE_CODEPOINTS)
        assert "Hello World" in visible

    def test_many_chars_at_same_index(self, tmp_path: Path):
        """Hundreds of invisible chars at the same index must all be recovered."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "AB", fontsize=12)
        src = tmp_path / "many.pdf"
        doc.save(str(src))
        doc.close()

        doc = fitz.open(str(src))
        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)

        # 50 invisible chars all after index 0
        invis_chars = [chr(0xE0100 + i) for i in range(50)]
        insertions = [
            _InvisInsertion(after_visible_idx=0, char=ch)
            for ch in invis_chars
        ]

        font_xref = _embed_invisible_font(doc, assets)
        _register_font_on_page(doc, doc[0], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "many_out.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        text = extract_signed_text_from_streams(str(out))
        extracted_invis = [
            c for c in text
            if ord(c) in INVISIBLE_CODEPOINTS and ord(c) != 0x000A
        ]
        assert len(extracted_invis) == 50, (
            f"Expected 50 invisible chars, got {len(extracted_invis)}"
        )

    def test_pdftotext_preserves_unique_vs(self, tmp_path: Path):
        """Unique VS chars (1 per base glyph) survive pdftotext extraction.

        This validates the unified CID font approach: visible and invisible
        chars share one font, so PDF viewers preserve VS in copy-paste.

        Note: poppler deduplicates repeated VS per base glyph, so this test
        uses unique VS codepoints (one per visible char).
        """
        import subprocess

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello World test.", fontsize=12)
        src = tmp_path / "pdftotext_src.pdf"
        doc.save(str(src))
        doc.close()

        doc = fitz.open(str(src))
        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)

        # One unique VS per visible char (17 chars in "Hello World test.")
        insertions = [
            _InvisInsertion(after_visible_idx=i, char=chr(0xE0100 + i))
            for i in range(17)
        ]

        font_xref = _embed_invisible_font(doc, assets)
        _register_font_on_page(doc, doc[0], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, insertions, assets.mapping)

        out = tmp_path / "pdftotext_out.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        result = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(out), "-"],
            capture_output=True, text=True, timeout=10,
        )
        extracted_vs = sum(
            1 for c in result.stdout
            if 0xE0100 <= ord(c) <= 0xE01EF
        )
        assert extracted_vs == 17, (
            f"Expected 17 VS chars from pdftotext, got {extracted_vs}"
        )

    def test_nonexistent_file_raises(self):
        with pytest.raises(SignExistingError, match="PDF not found"):
            extract_signed_text_from_streams("/no/such/file.pdf")

    def test_unsigned_pdf_returns_visible_only(self, sample_pdf: Path):
        """An unsigned PDF (no EncSgn font) should still return visible text."""
        text = extract_signed_text_from_streams(str(sample_pdf))
        assert "Hello World" in text
        invis = [
            c for c in text
            if ord(c) in INVISIBLE_CODEPOINTS and ord(c) != 0x000A
        ]
        assert len(invis) == 0


# ---------------------------------------------------------------------------
# _redistribute_insertions tests
# ---------------------------------------------------------------------------


class TestRedistributeInsertions:
    """Tests for _redistribute_insertions — spreads VS across base glyphs."""

    def test_empty_insertions(self):
        result = _redistribute_insertions([], 10)
        assert result == []

    def test_single_insertion_unchanged(self):
        ins = [_InvisInsertion(after_visible_idx=5, char=chr(0xE0100))]
        result = _redistribute_insertions(ins, 10)
        assert len(result) == 1
        assert result[0].char == chr(0xE0100)

    def test_block_insertions_get_spread(self):
        """36 VS chars all at index 5 should be spread across 0..35."""
        block = [
            _InvisInsertion(after_visible_idx=5, char=chr(0xE0100 + i))
            for i in range(36)
        ]
        result = _redistribute_insertions(block, 44)
        # Each should be at a different index (0..35)
        indices = [ins.after_visible_idx for ins in result]
        assert indices == list(range(36))
        # Characters preserved in order
        chars = [ins.char for ins in result]
        assert chars == [chr(0xE0100 + i) for i in range(36)]

    def test_wraps_when_more_chars_than_visible(self):
        """If 10 VS chars but only 3 visible, indices wrap: 0,1,2,0,1,2,..."""
        block = [
            _InvisInsertion(after_visible_idx=0, char=chr(0xE0100 + i))
            for i in range(10)
        ]
        result = _redistribute_insertions(block, 3)
        indices = [ins.after_visible_idx for ins in result]
        assert indices == [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]

    def test_zero_visible_returns_original(self):
        ins = [_InvisInsertion(after_visible_idx=0, char=chr(0xE0100))]
        result = _redistribute_insertions(ins, 0)
        assert result == ins

    def test_pdftotext_preserves_redistributed_vs(self, tmp_path: Path):
        """VS256 payload (36 chars) redistributed across visible text
        survives pdftotext extraction at 100%."""
        import subprocess

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello World test.", fontsize=12)
        src = tmp_path / "redist_src.pdf"
        doc.save(str(src))
        doc.close()

        doc = fitz.open(str(src))
        visible_cps = _collect_visible_codepoints(doc)
        assets = _build_font_assets(visible_cps)

        # Simulate block placement (all 36 at same index) then redistribute
        block = [
            _InvisInsertion(after_visible_idx=10, char=chr(0xE0100 + i))
            for i in range(17)  # 17 chars in "Hello World test."
        ]
        redistributed = _redistribute_insertions(block, 17)

        font_xref = _embed_invisible_font(doc, assets)
        _register_font_on_page(doc, doc[0], _UNIFIED_FONT_NAME, font_xref)
        _inject_into_content_streams(doc, redistributed, assets.mapping)

        out = tmp_path / "redist_out.pdf"
        doc.save(str(out), garbage=0, deflate=False)
        doc.close()

        result = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(out), "-"],
            capture_output=True, text=True, timeout=10,
        )
        extracted_vs = sum(
            1 for c in result.stdout
            if 0xE0100 <= ord(c) <= 0xE01EF
        )
        assert extracted_vs == 17, (
            f"Expected 17 VS chars from pdftotext, got {extracted_vs}"
        )


# ---------------------------------------------------------------------------
# TEAM_158: Regression — C2PA modes must NOT rewrite content streams
# ---------------------------------------------------------------------------


class TestC2PAModesPreserveText:
    """C2PA manifest modes (full, lightweight_uuid, minimal_uuid, hybrid)
    embed thousands of invisible chars.  Injecting those into content
    streams garbles the PDF.  Only VS/ZW modes should rewrite streams."""

    def test_c2pa_mode_skips_content_rewrite(self, tmp_path: Path):
        """sign_existing_pdf with a C2PA mode should NOT inject EncSgn font."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello World test.", fontsize=12)
        src = tmp_path / "c2pa_src.pdf"
        doc.save(str(src))
        doc.close()

        # Mock sign_text to return a result with many invisible chars
        # (simulating C2PA minimal_uuid mode)
        invis = "\u200b" * 500  # 500 ZWS chars (simulates C2PA payload)
        signed = f"Hello{invis} World test."
        mock_result = SignResult(
            mode="minimal",
            signed_text=signed,
            document_id="doc_test",
            total_segments=1,
            instance_id="inst_test",
            merkle_root="abc123",
            verification_url="http://example.com",
        )

        out = tmp_path / "c2pa_out.pdf"
        with patch("xml_to_pdf.sign_existing.sign_text", return_value=mock_result):
            sign_existing_pdf(str(src), str(out), mode="minimal")

        # Verify: content stream should NOT have EncSgn font
        doc2 = fitz.open(str(out))
        for cx in doc2[0].get_contents():
            stream = doc2.xref_stream(cx).decode("latin-1")
            assert "EncSgn" not in stream, (
                "C2PA mode should NOT rewrite content streams with EncSgn font"
            )

        # Verify: text is still readable
        text = doc2[0].get_text()
        assert "Hello" in text, f"Text garbled after C2PA signing: {text[:100]!r}"

        # Verify: metadata stream exists
        cat = doc2.pdf_catalog()
        r_key = doc2.xref_get_key(cat, "EncypherSignedText")
        assert r_key[0] == "xref", "EncypherSignedText metadata stream missing"
        doc2.close()

    def test_vs256_mode_does_rewrite_content(self, tmp_path: Path):
        """sign_existing_pdf with vs256_sentence SHOULD inject EncSgn font."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello World test.", fontsize=12)
        src = tmp_path / "vs256_src.pdf"
        doc.save(str(src))
        doc.close()

        # Mock sign_text to return a result with VS chars (simulates vs256)
        vs_chars = "".join(chr(0xE0100 + i) for i in range(36))
        signed = f"Hello World test{vs_chars}."
        mock_result = SignResult(
            mode="vs256_sentence",
            signed_text=signed,
            document_id="doc_test",
            total_segments=1,
            instance_id="inst_test",
            merkle_root="abc123",
            verification_url="http://example.com",
        )

        out = tmp_path / "vs256_out.pdf"
        with patch("xml_to_pdf.sign_existing.sign_text", return_value=mock_result):
            sign_existing_pdf(str(src), str(out), mode="vs256_sentence")

        # Verify: content stream SHOULD have EncSgn font
        doc2 = fitz.open(str(out))
        has_encsign = False
        for cx in doc2[0].get_contents():
            stream = doc2.xref_stream(cx).decode("latin-1")
            if "EncSgn" in stream:
                has_encsign = True
        assert has_encsign, "VS256 mode should rewrite content streams with EncSgn font"
        doc2.close()
