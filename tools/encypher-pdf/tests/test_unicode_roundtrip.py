# TEAM_154: Tests proving variation selectors and zero-width chars survive PDF round-trip
"""
These tests verify the core guarantee of encypher-pdf: that invisible Unicode
characters (variation selectors, zero-width chars) written into a PDF can be
extracted back with full fidelity.

Two extraction methods are used:
  1. PyMuPDF (fitz) — for single-paragraph tests where it works reliably.
  2. Content stream CID verification — for multi-paragraph/page tests where
     MuPDF has a known bug dropping zero-width glyphs across merged spans.
     The content stream is the ground truth; the actual production extractor
     (pdfjs-dist) does not have this MuPDF bug.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import fitz  # pymupdf
import pytest

from encypher_pdf import Document
from encypher_pdf.writer import (
    STYLE_BODY,
    STYLE_TITLE,
    STYLE_HEADING,
    STYLE_ABSTRACT,
    TextStyle,
    _text_to_hex,
    _measure_text,
    _split_tokens_lossless,
)
from encypher_pdf.fonttools_subset import get_font_metrics


def _extract_text_from_pdf(path: str) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    doc = fitz.open(path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    doc.close()
    return "\n".join(texts)


def _count_codepoints(text: str, codepoint_ranges: list[tuple[int, int]]) -> int:
    """Count characters in the given Unicode ranges."""
    count = 0
    for ch in text:
        cp = ord(ch)
        for lo, hi in codepoint_ranges:
            if lo <= cp <= hi:
                count += 1
                break
    return count


def _count_cids_in_content_stream(
    path: str, target_gids: set[int]
) -> dict[int, int]:
    """
    Count occurrences of specific GID values in all Tj/TJ operations across
    all pages of a PDF. This verifies the content stream directly, bypassing
    MuPDF's text extraction which has bugs with zero-width glyphs.

    Handles both ``<hex> Tj`` and ``[<hex> <hex> ...] TJ`` operators.
    """
    pdf = fitz.open(path)
    counts: dict[int, int] = {gid: 0 for gid in target_gids}

    def _scan_hex(hex_str: str) -> None:
        for i in range(0, len(hex_str), 4):
            cid = int(hex_str[i : i + 4], 16)
            if cid in counts:
                counts[cid] += 1

    for page_num in range(pdf.page_count):
        page = pdf[page_num]
        for cx in page.get_contents():
            stream = pdf.xref_stream(cx)
            text_stream = stream.decode("latin-1")
            # Match individual <hex> Tj
            for m in re.finditer(r"<([0-9A-Fa-f]+)>\s*Tj", text_stream):
                _scan_hex(m.group(1))
            # Match TJ arrays: [<hex> <hex> ...] TJ
            for m in re.finditer(r"\[([^\]]+)\]\s*TJ", text_stream):
                for hex_match in re.finditer(r"<([0-9A-Fa-f]+)>", m.group(1)):
                    _scan_hex(hex_match.group(1))
    pdf.close()
    return counts


def _get_invisible_gids(path: str) -> dict[int, int]:
    """
    Read the ToUnicode CMap from a PDF to find which GIDs map to invisible
    Unicode codepoints (VS and ZW chars).
    Returns dict mapping Unicode codepoint -> GID.
    """
    pdf = fitz.open(path)
    cp_to_gid: dict[int, int] = {}
    for i in range(1, pdf.xref_length()):
        try:
            stream = pdf.xref_stream(i)
            if stream and b"beginbfchar" in stream:
                text = stream.decode("ascii", errors="replace")
                entries = re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", text)
                for gid_hex, cp_hex in entries:
                    gid = int(gid_hex, 16)
                    cp = int(cp_hex, 16)
                    if 0xFE00 <= cp <= 0xFE0F or cp in (0x200B, 0x200C, 0x200D, 0xFEFF):
                        cp_to_gid[cp] = gid
        except Exception:
            pass
    pdf.close()
    return cp_to_gid


# ---------------------------------------------------------------------------
# Core round-trip tests
# ---------------------------------------------------------------------------


class TestVariationSelectorRoundTrip:
    """Variation selectors (U+FE00–FE0F) must survive write → extract."""

    def test_single_variation_selector(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "vs_single.pdf")
        doc = Document()
        doc.add_text("Hello\ufe01World", STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        assert "\ufe01" in extracted, f"VS1 (U+FE01) not found in extracted text: {[hex(ord(c)) for c in extracted]}"

    def test_multiple_variation_selectors(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "vs_multi.pdf")
        text = "A\ufe01B\ufe02C\ufe03D\ufe0e E\ufe0f"
        doc = Document()
        doc.add_text(text, STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        vs_count = _count_codepoints(extracted, [(0xFE00, 0xFE0F)])
        assert vs_count == 5, f"Expected 5 variation selectors, got {vs_count}: {[hex(ord(c)) for c in extracted]}"

    def test_all_bmp_variation_selectors(self, tmp_path: Path) -> None:
        """All 16 BMP variation selectors (U+FE00–FE0F) must round-trip."""
        pdf_path = str(tmp_path / "vs_all.pdf")
        chars = [f"X{chr(0xFE00 + i)}" for i in range(16)]
        text = " ".join(chars)
        doc = Document()
        doc.add_text(text, STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        vs_count = _count_codepoints(extracted, [(0xFE00, 0xFE0F)])
        assert vs_count == 16, f"Expected 16 VS chars, got {vs_count}"


class TestZeroWidthCharRoundTrip:
    """Zero-width characters must survive write → extract."""

    def test_zero_width_space(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "zwsp.pdf")
        doc = Document()
        doc.add_text("Hello\u200bWorld", STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        assert "\u200b" in extracted, f"ZWSP not found: {[hex(ord(c)) for c in extracted]}"

    def test_zero_width_joiner(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "zwj.pdf")
        doc = Document()
        doc.add_text("Hello\u200dWorld", STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        assert "\u200d" in extracted, f"ZWJ not found: {[hex(ord(c)) for c in extracted]}"

    def test_zero_width_non_joiner(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "zwnj.pdf")
        doc = Document()
        doc.add_text("Hello\u200cWorld", STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        assert "\u200c" in extracted, f"ZWNJ not found: {[hex(ord(c)) for c in extracted]}"

    def test_byte_order_mark(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "bom.pdf")
        doc = Document()
        doc.add_text("Hello\ufeffWorld", STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        assert "\ufeff" in extracted, f"BOM not found: {[hex(ord(c)) for c in extracted]}"

    def test_all_zero_width_chars(self, tmp_path: Path) -> None:
        """All zero-width characters we care about must round-trip."""
        pdf_path = str(tmp_path / "zw_all.pdf")
        zw_chars = ["\u200b", "\u200c", "\u200d", "\ufeff"]
        text = "A" + "".join(zw_chars) + "B"
        doc = Document()
        doc.add_text(text, STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        for zw in zw_chars:
            assert zw in extracted, f"U+{ord(zw):04X} not found in extracted text"


class TestMixedInvisibleChars:
    """Mixed variation selectors and zero-width chars in the same document."""

    def test_mixed_invisible_chars(self, tmp_path: Path) -> None:
        pdf_path = str(tmp_path / "mixed.pdf")
        text = "Hello\ufe01\u200b World\ufe02\u200c end\u200d"
        doc = Document()
        doc.add_text(text, STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        assert "\ufe01" in extracted
        assert "\ufe02" in extracted
        assert "\u200b" in extracted
        assert "\u200c" in extracted
        assert "\u200d" in extracted

    def test_heavy_invisible_payload(self, tmp_path: Path) -> None:
        """Simulate a real encypher payload with many invisible chars."""
        pdf_path = str(tmp_path / "heavy.pdf")
        # Build text with VS chars after every visible char (worst case)
        visible = "The quick brown fox jumps over the lazy dog."
        signed = ""
        for i, ch in enumerate(visible):
            signed += ch
            # Add a variation selector after each letter
            if ch.isalpha():
                signed += chr(0xFE00 + (i % 16))

        doc = Document()
        doc.add_text(signed, STYLE_BODY)
        doc.save(pdf_path)

        extracted = _extract_text_from_pdf(pdf_path)
        vs_count = _count_codepoints(extracted, [(0xFE00, 0xFE0F)])
        expected_vs = sum(1 for c in visible if c.isalpha())
        assert vs_count == expected_vs, f"Expected {expected_vs} VS chars, got {vs_count}"


class TestMultiPageDocument:
    """Invisible chars must survive across multiple pages."""

    def test_multipage_preserves_invisible_chars(self, tmp_path: Path) -> None:
        """
        Verify invisible chars are present in the PDF content stream across
        multiple pages. Uses content stream CID verification because MuPDF
        has a known bug dropping zero-width glyphs when merging text spans
        across multiple BT/ET blocks on the same page.
        """
        pdf_path = str(tmp_path / "multipage.pdf")
        doc = Document()
        doc.add_text("Document Title", STYLE_TITLE)

        # Generate enough text to span multiple pages
        for i in range(50):
            text = f"Paragraph {i}: This is a test sentence\ufe01 with invisible\u200b characters\ufe02 embedded."
            doc.add_text(text, STYLE_BODY)

        doc.save(pdf_path)

        # Verify via content stream (ground truth, not affected by MuPDF bugs)
        cp_to_gid = _get_invisible_gids(pdf_path)
        assert 0xFE01 in cp_to_gid, "FE01 not in ToUnicode CMap"
        assert 0xFE02 in cp_to_gid, "FE02 not in ToUnicode CMap"
        assert 0x200B in cp_to_gid, "200B not in ToUnicode CMap"

        target_gids = {cp_to_gid[0xFE01], cp_to_gid[0xFE02], cp_to_gid[0x200B]}
        counts = _count_cids_in_content_stream(pdf_path, target_gids)

        fe01_count = counts[cp_to_gid[0xFE01]]
        fe02_count = counts[cp_to_gid[0xFE02]]
        zw_count = counts[cp_to_gid[0x200B]]

        assert fe01_count == 50, f"Expected 50 FE01 CIDs in content stream, got {fe01_count}"
        assert fe02_count == 50, f"Expected 50 FE02 CIDs in content stream, got {fe02_count}"
        assert zw_count == 50, f"Expected 50 ZWSP CIDs in content stream, got {zw_count}"


# ---------------------------------------------------------------------------
# Unit tests for internal functions
# ---------------------------------------------------------------------------


class TestTextToHex:
    """_text_to_hex must encode all codepoints as UTF-16BE hex."""

    def test_ascii(self) -> None:
        assert _text_to_hex("A") == "0041"

    def test_variation_selector(self) -> None:
        result = _text_to_hex("\ufe01")
        assert result == "FE01"

    def test_zero_width_space(self) -> None:
        result = _text_to_hex("\u200b")
        assert result == "200B"

    def test_mixed(self) -> None:
        result = _text_to_hex("A\ufe01")
        assert result == "0041FE01"


class TestSplitTokensLossless:
    """_split_tokens_lossless must keep invisible chars attached and preserve all chars."""

    def test_simple(self) -> None:
        tokens = _split_tokens_lossless("Hello World")
        assert tokens == ["Hello ", "World"]
        assert "".join(tokens) == "Hello World"

    def test_invisible_stays_attached(self) -> None:
        tokens = _split_tokens_lossless("Hello\ufe01 World\ufe02")
        assert len(tokens) == 2
        assert "\ufe01" in tokens[0]
        assert "\ufe02" in tokens[1]
        assert "".join(tokens) == "Hello\ufe01 World\ufe02"

    def test_zero_width_stays_attached(self) -> None:
        tokens = _split_tokens_lossless("Hello\u200bWorld")
        # No space between them, so they stay as one token
        assert len(tokens) == 1
        assert "\u200b" in tokens[0]

    def test_lossless_roundtrip(self) -> None:
        text = "The quick brown fox jumps over the lazy dog"
        assert "".join(_split_tokens_lossless(text)) == text
