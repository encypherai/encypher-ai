# TEAM_154: Tests for PDF renderer (encypher-pdf based)
"""Tests for the PDF rendering engine with Unicode provenance preservation."""

import re
from pathlib import Path

import fitz
import pytest

from xml_to_pdf.parser import Author, Paper, Reference, Section, Subsection, parse_xml
from xml_to_pdf.renderer import render_pdf

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
SAMPLE_XML = EXAMPLES_DIR / "content_provenance_paper.xml"


@pytest.fixture
def sample_paper() -> Paper:
    return parse_xml(str(SAMPLE_XML))


@pytest.fixture
def minimal_paper() -> Paper:
    return Paper(
        title="Test Paper",
        authors=[Author(name="Test Author", affiliation="Test Org")],
        abstract="This is a test abstract.",
        keywords=["test", "paper"],
        sections=[
            Section(
                id="s1",
                heading="1. Introduction",
                paragraphs=["This is the introduction."],
                subsections=[
                    Subsection(
                        id="s1.1",
                        heading="1.1 Background",
                        paragraphs=["Some background."],
                    )
                ],
            )
        ],
        references=[Reference(id="ref1", text="Test reference.")],
    )


class TestRenderPDF:
    """Test PDF generation."""

    def test_unsigned_pdf_created(self, tmp_path, sample_paper):
        out = str(tmp_path / "test.pdf")
        result = render_pdf(sample_paper, out)
        assert Path(result).exists()
        assert Path(result).stat().st_size > 1000  # non-trivial PDF

    def test_unsigned_minimal_paper(self, tmp_path, minimal_paper):
        out = str(tmp_path / "minimal.pdf")
        result = render_pdf(minimal_paper, out)
        assert Path(result).exists()

    def test_pdf_with_provenance_mode(self, tmp_path, minimal_paper):
        out = str(tmp_path / "signed.pdf")
        result = render_pdf(
            minimal_paper,
            out,
            provenance_mode="ZW embedding (sentence-level)",
        )
        assert Path(result).exists()

    def test_pdf_with_signed_text(self, tmp_path, minimal_paper):
        out = str(tmp_path / "signed.pdf")
        signed_text = "Hello world\u200c\u200d\u034f" * 10  # fake ZW chars
        result = render_pdf(
            minimal_paper,
            out,
            signed_text=signed_text,
            provenance_mode="test",
        )
        assert Path(result).exists()

    def test_pdf_with_provenance_meta(self, tmp_path, minimal_paper):
        out = str(tmp_path / "meta.pdf")
        meta = {
            "mode": "c2pa_full",
            "document_id": "test-123",
            "total_segments": 5,
            "overhead_percent": "4.2%",
        }
        result = render_pdf(
            minimal_paper,
            out,
            provenance_mode="Default C2PA",
            provenance_meta=meta,
        )
        assert Path(result).exists()

    def test_creates_output_directory(self, tmp_path, minimal_paper):
        out = str(tmp_path / "subdir" / "nested" / "test.pdf")
        result = render_pdf(minimal_paper, out)
        assert Path(result).exists()

    def test_full_paper_renders(self, tmp_path, sample_paper):
        """The full sample paper should render successfully."""
        out = str(tmp_path / "full_paper.pdf")
        result = render_pdf(
            sample_paper,
            out,
            provenance_mode="Default C2PA (full manifest)",
            provenance_meta={"mode": "full", "segments": 25},
        )
        pdf_path = Path(result)
        assert pdf_path.exists()
        # Full paper should be multiple pages
        assert pdf_path.stat().st_size > 5000


class TestProvenanceRoundTrip:
    """End-to-end: signed text with invisible chars → PDF → extract → verify."""

    def test_invisible_chars_survive_render_extract(self, tmp_path, minimal_paper):
        """Variation selectors and zero-width chars in signed text must
        be present in the PDF content stream after rendering."""
        signed_text = (
            "Test Paper\n\n"
            "Test Author\n\n"
            "This is a test\ufe01 abstract\u200b.\n\n"
            "1. Introduction\n\n"
            "This is the\ufe02 introduction\u200c."
        )
        out = str(tmp_path / "provenance.pdf")
        render_pdf(minimal_paper, out, signed_text=signed_text, provenance_mode="test")

        # Verify content stream contains the invisible char GIDs
        pdf = fitz.open(out)
        # Read ToUnicode CMap to find GIDs for invisible codepoints
        cp_to_gid: dict[int, int] = {}
        for i in range(1, pdf.xref_length()):
            try:
                stream = pdf.xref_stream(i)
                if stream and b"beginbfchar" in stream:
                    text = stream.decode("ascii", errors="replace")
                    entries = re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", text)
                    for gid_hex, cp_hex in entries:
                        cp = int(cp_hex, 16)
                        if cp in (0xFE01, 0xFE02, 0x200B, 0x200C):
                            cp_to_gid[cp] = int(gid_hex, 16)
            except Exception:
                pass

        assert 0xFE01 in cp_to_gid, "FE01 not in ToUnicode CMap"
        assert 0xFE02 in cp_to_gid, "FE02 not in ToUnicode CMap"
        assert 0x200B in cp_to_gid, "200B not in ToUnicode CMap"
        assert 0x200C in cp_to_gid, "200C not in ToUnicode CMap"

        # Count invisible CIDs in all content streams (handles both Tj and TJ)
        target_gids = set(cp_to_gid.values())
        counts: dict[int, int] = {gid: 0 for gid in target_gids}

        def _scan_hex(hex_str: str) -> None:
            for j in range(0, len(hex_str), 4):
                cid = int(hex_str[j : j + 4], 16)
                if cid in counts:
                    counts[cid] += 1

        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            for cx in page.get_contents():
                stream = pdf.xref_stream(cx)
                text_stream = stream.decode("latin-1")
                for m in re.finditer(r"<([0-9A-Fa-f]+)>\s*Tj", text_stream):
                    _scan_hex(m.group(1))
                for m in re.finditer(r"\[([^\]]+)\]\s*TJ", text_stream):
                    for hex_match in re.finditer(r"<([0-9A-Fa-f]+)>", m.group(1)):
                        _scan_hex(hex_match.group(1))

        assert counts[cp_to_gid[0xFE01]] == 1, "FE01 not found in content stream"
        assert counts[cp_to_gid[0xFE02]] == 1, "FE02 not found in content stream"
        assert counts[cp_to_gid[0x200B]] == 1, "200B not found in content stream"
        assert counts[cp_to_gid[0x200C]] == 1, "200C not found in content stream"
        pdf.close()

    def test_single_paragraph_pymupdf_extraction(self, tmp_path, minimal_paper):
        """For single-paragraph signed text, PyMuPDF extraction must
        preserve invisible chars (no multi-span merging bug)."""
        signed_text = "Hello\ufe01 world\u200b end\ufe02."
        out = str(tmp_path / "single_para.pdf")
        render_pdf(minimal_paper, out, signed_text=signed_text, provenance_mode="test")

        pdf = fitz.open(out)
        extracted = ""
        for page in pdf:
            extracted += page.get_text()
        pdf.close()

        assert "\ufe01" in extracted, "FE01 not in PyMuPDF extraction"
        assert "\u200b" in extracted, "ZWSP not in PyMuPDF extraction"
        assert "\ufe02" in extracted, "FE02 not in PyMuPDF extraction"
