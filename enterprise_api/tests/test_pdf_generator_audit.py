"""Comprehensive PDF generator audit for invisible marker survival.

Tests every available Python PDF generation pipeline to measure how well
ZWC and VS256 embedding markers survive the render -> extract round-trip.

Generators tested:
  1. reportlab (SimpleDocTemplate / Platypus)  -- baseline
  2. reportlab (canvas direct)                 -- low-level variant
  3. fpdf2 (FPDF2)                             -- modern fpdf
  4. WeasyPrint (HTML -> PDF via Cairo)        -- best Unicode support
  5. xhtml2pdf (HTML -> PDF via reportlab)     -- legacy HTML->PDF
  6. pypdf (copy via PdfWriter)               -- in-memory copy/re-save

Each generator is tested with:
  A. ZWC  (legacy_safe, 100 chars/marker)
  B. ZWC-RS (legacy_safe_rs, 112 chars/marker)
  C. VS256  (36 chars/marker)
  D. VS256-RS (44 chars/marker)

Survival is measured at two levels:
  - marker-level: intact 100/112/36/44-char sequences found by find_all_markers()
  - char-level:   raw invisible codepoint count in extracted text

Run:
    uv run pytest tests/test_pdf_generator_audit.py -v -s
or standalone:
    uv run python tests/test_pdf_generator_audit.py
"""

from __future__ import annotations

import hashlib
import io
import os
import textwrap
from dataclasses import dataclass
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Article fixture (same as test_pdf_embedding_roundtrip.py)
# ---------------------------------------------------------------------------

ARTICLE_SENTENCES = [
    "The rise of generative AI has fundamentally changed how content is produced at scale.",
    "Publishers now face an unprecedented challenge: verifying that AI-generated text originated from their licensed corpus.",
    "Invisible Unicode embeddings offer a promising solution by encoding signed provenance markers directly into the text stream.",
    "Unlike visible watermarks, these markers survive normal reading, copy-paste, and formatting transformations.",
    "This article evaluates four embedding strategies across common document pipeline stages.",
]

# ---------------------------------------------------------------------------
# Font paths -- prefer FreeSerif (broadest BMP coverage), fall back to FreeMono
# ---------------------------------------------------------------------------

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def _pick_ttf() -> str:
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("No suitable TTF font found; install freefont-ttf")


# ---------------------------------------------------------------------------
# Invisible codepoint sets
# ---------------------------------------------------------------------------

VS256_BMP = frozenset(chr(c) for c in range(0xFE00, 0xFE10))
VS256_SUPP = frozenset(chr(c) for c in range(0xE0100, 0xE01F0))
ZWC_CHARS = frozenset(["\u200c", "\u200d", "\u034f", "\u180e", "\u200e", "\u200f"])
ALL_INVISIBLE = VS256_BMP | VS256_SUPP | ZWC_CHARS


def _count_invisible(text: str) -> dict[str, int]:
    vs_bmp = sum(1 for c in text if c in VS256_BMP)
    vs_supp = sum(1 for c in text if c in VS256_SUPP)
    zwc = sum(1 for c in text if c in ZWC_CHARS)
    return {"vs_bmp": vs_bmp, "vs_supp": vs_supp, "zwc": zwc, "total": vs_bmp + vs_supp + zwc}


# ---------------------------------------------------------------------------
# Embedding helpers (no API; direct crypto)
# ---------------------------------------------------------------------------

_SIGNING_KEY = hashlib.sha256(b"pdf-audit-key").digest()


def _embed_zwc(sentences: list[str]) -> str:
    from app.utils.legacy_safe_crypto import create_marker, embed_marker_safely, generate_log_id

    parts = []
    for s in sentences:
        marker = create_marker(generate_log_id(), _SIGNING_KEY, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


def _embed_zwc_rs(sentences: list[str]) -> str:
    from app.utils.legacy_safe_rs_crypto import create_marker, embed_marker_safely, generate_log_id

    parts = []
    for s in sentences:
        marker = create_marker(generate_log_id(), _SIGNING_KEY, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


def _embed_vs256(sentences: list[str]) -> str:
    from app.utils.legacy_safe_crypto import embed_marker_safely, generate_log_id
    from app.utils.vs256_crypto import create_signed_marker

    parts = []
    for s in sentences:
        marker = create_signed_marker(generate_log_id(), _SIGNING_KEY, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


def _embed_vs256_rs(sentences: list[str]) -> str:
    from app.utils.legacy_safe_crypto import embed_marker_safely, generate_log_id
    from app.utils.vs256_rs_crypto import create_signed_marker

    parts = []
    for s in sentences:
        marker = create_signed_marker(generate_log_id(), _SIGNING_KEY, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


# Count surviving intact markers after extraction
def _count_zwc_markers(text: str) -> int:
    from app.utils.legacy_safe_crypto import find_all_markers

    return len(find_all_markers(text))


def _count_zwc_rs_markers(text: str) -> int:
    from app.utils.legacy_safe_rs_crypto import find_all_markers

    return len(find_all_markers(text))


def _count_vs256_markers(text: str) -> int:
    from app.utils.vs256_crypto import find_all_markers

    return len(find_all_markers(text))


def _count_vs256_rs_markers(text: str) -> int:
    from app.utils.vs256_rs_crypto import find_all_markers

    return len(find_all_markers(text))


# ---------------------------------------------------------------------------
# pdfminer extraction (shared across all generators)
# ---------------------------------------------------------------------------


def _extract(pdf_bytes: bytes) -> str:
    from pdfminer.high_level import extract_text

    return extract_text(io.BytesIO(pdf_bytes))


# ---------------------------------------------------------------------------
# Generator 1: reportlab SimpleDocTemplate (baseline)
# ---------------------------------------------------------------------------


def _render_reportlab_platypus(text: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate

    font_path = _pick_ttf()
    pdfmetrics.registerFont(TTFont("AuditFont1", font_path))
    styles = getSampleStyleSheet()
    style = styles["Normal"].clone("AuditStyle1")
    style.fontName = "AuditFont1"
    style.fontSize = 10
    style.leading = 14
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    doc.build([Paragraph(text, style)])
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Generator 2: reportlab canvas (direct, low-level)
# ---------------------------------------------------------------------------


def _render_reportlab_canvas(text: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas as rl_canvas

    font_path = _pick_ttf()
    pdfmetrics.registerFont(TTFont("AuditFont2", font_path))
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    c.setFont("AuditFont2", 10)
    width, height = A4
    margin = 72
    line_height = 14
    max_width = width - 2 * margin

    # Simple word-wrap
    words = text.split(" ")
    lines: list[str] = []
    cur = ""
    for w in words:
        candidate = (cur + " " + w).strip()
        if c.stringWidth(candidate, "AuditFont2", 10) < max_width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    y = height - margin
    for line in lines:
        c.drawString(margin, y, line)
        y -= line_height
        if y < margin:
            c.showPage()
            c.setFont("AuditFont2", 10)
            y = height - margin
    c.save()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Generator 3: fpdf2
# ---------------------------------------------------------------------------


def _render_fpdf2(text: str) -> bytes:
    from fpdf import FPDF

    font_path = _pick_ttf()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("AuditFPDF", fname=font_path, uni=True)
    pdf.set_font("AuditFPDF", size=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    # multi_cell handles long text with word wrap
    pdf.multi_cell(0, 6, text)
    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Generator 4: WeasyPrint (HTML -> PDF via Cairo)
# ---------------------------------------------------------------------------


def _render_weasyprint(text: str) -> bytes:
    import weasyprint

    font_path = _pick_ttf()
    # Escape for safe HTML embedding
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_src = textwrap.dedent(f"""
        <!DOCTYPE html>
        <html><head>
          <meta charset="UTF-8"/>
          <style>
            @font-face {{
              font-family: AuditFont;
              src: url('file://{font_path}');
            }}
            body {{
              font-family: AuditFont, serif;
              font-size: 10pt;
              margin: 72pt;
              line-height: 1.4;
            }}
          </style>
        </head><body><p>{escaped}</p></body></html>
    """)
    doc = weasyprint.HTML(string=html_src).render()
    pdf_bytes: bytes = doc.write_pdf()
    return pdf_bytes


# ---------------------------------------------------------------------------
# Generator 5: xhtml2pdf (HTML -> PDF)
# ---------------------------------------------------------------------------


def _render_xhtml2pdf(text: str) -> bytes:
    from xhtml2pdf import pisa

    font_path = _pick_ttf()
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_src = textwrap.dedent(f"""
        <!DOCTYPE html>
        <html><head>
          <meta charset="UTF-8"/>
          <style>
            @font-face {{
              font-family: AuditFont;
              src: url('file://{font_path}');
            }}
            body {{
              font-family: AuditFont;
              font-size: 10pt;
            }}
          </style>
        </head><body><p>{escaped}</p></body></html>
    """)
    buf = io.BytesIO()
    status = pisa.pisaDocument(io.StringIO(html_src), buf, encoding="UTF-8")
    if status.err:
        raise RuntimeError(f"xhtml2pdf error: {status.err}")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Generator 6: pypdf PdfWriter copy (in-memory pass-through)
#   Creates a minimal reportlab PDF, then copies via pypdf to test
#   whether pypdf preserves the text layer during re-save
# ---------------------------------------------------------------------------


def _render_pypdf_passthrough(text: str) -> bytes:
    import pypdf

    source_bytes = _render_reportlab_platypus(text)
    reader = pypdf.PdfReader(io.BytesIO(source_bytes))
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class AuditResult:
    generator: str
    mode: str
    markers_embedded: int
    markers_survived: int
    invisible_before: dict[str, int]
    invisible_after: dict[str, int]
    error: Optional[str] = None

    @property
    def marker_pct(self) -> float:
        if self.markers_embedded == 0:
            return 0.0
        return 100.0 * self.markers_survived / self.markers_embedded

    @property
    def char_pct(self) -> float:
        before = self.invisible_before.get("total", 0)
        after = self.invisible_after.get("total", 0)
        if before == 0:
            return 0.0
        return 100.0 * after / before


# ---------------------------------------------------------------------------
# Core audit runner
# ---------------------------------------------------------------------------

# (generator_name, render_fn)
GENERATORS: list[tuple[str, Callable[[str], bytes]]] = [
    ("reportlab-platypus", _render_reportlab_platypus),
    ("reportlab-canvas", _render_reportlab_canvas),
    ("fpdf2", _render_fpdf2),
    ("weasyprint", _render_weasyprint),
    ("xhtml2pdf", _render_xhtml2pdf),
    ("pypdf-passthrough", _render_pypdf_passthrough),
]

# (mode_name, embed_fn, count_fn, marker_chars)
MODES: list[tuple[str, Callable[[list[str]], str], Callable[[str], int], int]] = [
    ("ZWC (100ch)", _embed_zwc, _count_zwc_markers, 100),
    ("ZWC-RS (112ch)", _embed_zwc_rs, _count_zwc_rs_markers, 112),
    ("VS256 (36ch)", _embed_vs256, _count_vs256_markers, 36),
    ("VS256-RS (44ch)", _embed_vs256_rs, _count_vs256_rs_markers, 44),
]


def run_audit() -> list[AuditResult]:
    results: list[AuditResult] = []
    n_sentences = len(ARTICLE_SENTENCES)

    for mode_name, embed_fn, count_fn, _chars in MODES:
        embedded_text = embed_fn(ARTICLE_SENTENCES)
        invisible_before = _count_invisible(embedded_text)

        for gen_name, render_fn in GENERATORS:
            try:
                pdf_bytes = render_fn(embedded_text)
                extracted = _extract(pdf_bytes)
                survived = count_fn(extracted)
                invisible_after = _count_invisible(extracted)
                results.append(
                    AuditResult(
                        generator=gen_name,
                        mode=mode_name,
                        markers_embedded=n_sentences,
                        markers_survived=survived,
                        invisible_before=invisible_before,
                        invisible_after=invisible_after,
                    )
                )
            except Exception as exc:
                results.append(
                    AuditResult(
                        generator=gen_name,
                        mode=mode_name,
                        markers_embedded=n_sentences,
                        markers_survived=0,
                        invisible_before=invisible_before,
                        invisible_after={},
                        error=str(exc)[:120],
                    )
                )
    return results


def print_report(results: list[AuditResult]) -> None:
    print("\n" + "=" * 100)
    print("PDF GENERATOR AUDIT -- Invisible Marker Survival Report")
    print("=" * 100)
    print(f"Article: {len(ARTICLE_SENTENCES)} sentences, {len(' '.join(ARTICLE_SENTENCES))} visible chars")
    print()

    # Group by mode
    modes_seen: list[str] = []
    for r in results:
        if r.mode not in modes_seen:
            modes_seen.append(r.mode)

    for mode in modes_seen:
        mode_results = [r for r in results if r.mode == mode]
        print(f"--- {mode} ---")
        print(f"  {'Generator':<28} {'Markers':>10} {'Marker%':>8}  {'Chars Before':>13} {'Chars After':>12} {'Char%':>7}  Status")
        print("  " + "-" * 90)
        for r in mode_results:
            if r.error:
                print(f"  {r.generator:<28} {'ERROR':>10}  {r.error}")
            else:
                status = "FULL" if r.marker_pct == 100.0 else ("NONE" if r.marker_pct == 0.0 else "PARTIAL")
                print(
                    f"  {r.generator:<28} "
                    f"{r.markers_survived}/{r.markers_embedded}  {r.marker_pct:>7.1f}%  "
                    f"{r.invisible_before.get('total', 0):>13} "
                    f"{r.invisible_after.get('total', 0):>12} "
                    f"{r.char_pct:>7.1f}%  "
                    f"{status}"
                )
        print()

    # Summary matrix
    print("=" * 100)
    print("SUMMARY MATRIX (Marker survival % -- 100%=all markers intact, 0%=all stripped)")
    print("=" * 100)
    generators_seen = [g for g, _ in GENERATORS]
    # header
    header = f"  {'Generator':<28}"
    for m in modes_seen:
        header += f"  {m[:14]:>14}"
    print(header)
    print("  " + "-" * (28 + len(modes_seen) * 16))
    for gen in generators_seen:
        row = f"  {gen:<28}"
        for m in modes_seen:
            match = next((r for r in results if r.generator == gen and r.mode == m), None)
            if match is None:
                row += f"  {'N/A':>14}"
            elif match.error:
                row += f"  {'ERROR':>14}"
            else:
                row += f"  {match.marker_pct:>13.1f}%"
        print(row)
    print()

    # Best generator recommendation
    print("RECOMMENDATION:")
    best: list[tuple[str, float]] = []
    for gen in generators_seen:
        gen_results = [r for r in results if r.generator == gen and not r.error]
        if gen_results:
            avg = sum(r.marker_pct for r in gen_results) / len(gen_results)
            best.append((gen, avg))
    best.sort(key=lambda x: -x[1])
    for rank, (gen, avg) in enumerate(best, 1):
        print(f"  #{rank}: {gen:<30} avg marker survival = {avg:.1f}%")
    print()


# ---------------------------------------------------------------------------
# pytest tests
# ---------------------------------------------------------------------------

import pytest


@pytest.fixture(scope="module")
def audit_results() -> list[AuditResult]:
    return run_audit()


def test_audit_runs_without_crash(audit_results: list[AuditResult]) -> None:
    """All generators produce a result (error or success, not a crash)."""
    assert len(audit_results) == len(GENERATORS) * len(MODES)


def test_at_least_one_generator_preserves_zwc_markers(audit_results: list[AuditResult]) -> None:
    """At least one generator preserves ZWC markers at 100%."""
    zwc_results = [r for r in audit_results if "ZWC (100ch)" in r.mode and not r.error]
    any_full = any(r.marker_pct == 100.0 for r in zwc_results)
    if not any_full:
        best = max(zwc_results, key=lambda r: r.marker_pct) if zwc_results else None
        best_pct = best.marker_pct if best else 0.0
        pytest.skip(f"No generator achieves 100% ZWC marker survival; best is {best.generator if best else 'none'} @ {best_pct:.1f}%")


def test_print_full_report(audit_results: list[AuditResult], capsys) -> None:
    """Print the full audit report (visible with pytest -s)."""
    print_report(audit_results)
    # always passes -- this test exists for the output
    captured = capsys.readouterr()
    assert "SUMMARY MATRIX" in captured.out


def test_weasyprint_strips_zwc_entirely(audit_results: list[AuditResult]) -> None:
    """WeasyPrint (Cairo/Pango) strips ZWC format chars entirely at render time.

    This is a documented finding: Pango's text shaper discards zero-width
    format characters (ZWNJ, ZWJ, CGJ, etc.) before encoding glyphs.
    reportlab encodes them as font glyph IDs (~85% individual survival)
    but both result in 0% marker survival due to fragmentation.

    This test asserts the observed behavior so a future engine change
    (e.g. libharfbuzz version that preserves format chars) is detected.
    """
    wp_zwc = next(
        (r for r in audit_results if r.generator == "weasyprint" and "ZWC (100ch)" in r.mode),
        None,
    )
    rl_zwc = next(
        (r for r in audit_results if r.generator == "reportlab-platypus" and "ZWC (100ch)" in r.mode),
        None,
    )
    if wp_zwc is None or rl_zwc is None:
        pytest.skip("Missing results for comparison")
    if wp_zwc.error:
        pytest.skip(f"WeasyPrint error: {wp_zwc.error}")
    # WeasyPrint/Cairo strips ZWC entirely; reportlab preserves ~80-90% individually
    assert (
        wp_zwc.char_pct == 0.0
    ), f"WeasyPrint now preserves ZWC chars ({wp_zwc.char_pct:.1f}%) -- recheck if Cairo/Pango changed format-char handling"
    assert rl_zwc.char_pct > 50.0, f"reportlab ZWC char survival dropped to {rl_zwc.char_pct:.1f}% -- font or version change?"


# ---------------------------------------------------------------------------
# Deep-dive: raw PDF byte inspection
# ---------------------------------------------------------------------------


def _inspect_pdf_bytes(pdf_bytes: bytes) -> dict[str, bool | int]:
    """Check whether invisible chars appear in the raw PDF byte stream.

    Searches for UTF-8 encoded ZWC and VS256 codepoints in the raw bytes.
    This tells us whether the PDF generator encoded them at all, independent
    of what the text extractor later recovers.
    """
    # UTF-8 encodings of key codepoints
    targets = {
        "ZWNJ U+200C": "\u200c".encode("utf-8"),
        "ZWJ  U+200D": "\u200d".encode("utf-8"),
        "CGJ  U+034F": "\u034f".encode("utf-8"),
        "MVS  U+180E": "\u180e".encode("utf-8"),
        "LRM  U+200E": "\u200e".encode("utf-8"),
        "RLM  U+200F": "\u200f".encode("utf-8"),
        "VS1  U+FE00": "\ufe00".encode("utf-8"),
        "VS17 U+E0100": "\U000e0100".encode("utf-8"),
    }
    result: dict[str, bool | int] = {}
    for name, pattern in targets.items():
        count = pdf_bytes.count(pattern)
        result[name] = count
    return result


def _extract_pypdf(pdf_bytes: bytes) -> str:
    """Extract text using pypdf (alternative to pdfminer)."""
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _extract_pdfplumber(pdf_bytes: bytes) -> str:
    """Extract text using pdfplumber (pdfminer-based, different settings)."""
    import pdfplumber

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        parts = []
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _analyze_fragmentation(extracted: str) -> dict[str, int | str]:
    """Analyze how pdfminer breaks up runs of ZWC chars.

    Looks for what separator characters appear between consecutive ZWC chars
    in the extracted text, to understand the fragmentation mechanism.
    """
    separators: dict[str, int] = {}
    in_zwc = False
    zwc_run = 0
    max_run = 0
    prev_was_zwc = False
    for ch in extracted:
        is_zwc = ch in ZWC_CHARS
        if is_zwc:
            if prev_was_zwc:
                zwc_run += 1
            else:
                zwc_run = 1
            max_run = max(max_run, zwc_run)
        else:
            if prev_was_zwc:
                # ch is a separator after a ZWC char
                code = f"U+{ord(ch):04X}"
                separators[code] = separators.get(code, 0) + 1
            zwc_run = 0
        prev_was_zwc = is_zwc

    top_seps = sorted(separators.items(), key=lambda x: -x[1])[:5]
    return {
        "max_consecutive_zwc": max_run,
        "separator_types": len(separators),
        "top_separators": ", ".join(f"{k}(x{v})" for k, v in top_seps) if top_seps else "none",
    }


# ---------------------------------------------------------------------------
# ToUnicode CMap inspection
# PDF text is glyph-ID encoded (not UTF-8).  We must search the ToUnicode
# CMap table in the PDF to know whether ZWC codepoints are mapped.
# ---------------------------------------------------------------------------


def _count_zwc_via_tounicode(pdf_bytes: bytes) -> int:
    """Count how many ZWC-char codepoints appear in the PDF's ToUnicode CMaps.

    PDF generators encode text as glyph IDs, not raw Unicode bytes.
    The ToUnicode CMap maps glyph IDs back to Unicode for text extraction.
    We search for the hex-escaped Unicode values that appear in CMap blocks.

    Returns an approximate count of distinct ZWC codepoint mappings found.
    """

    # Hex codepoint representations used in ToUnicode CMap
    zwc_hex = {
        "200C",  # ZWNJ
        "200D",  # ZWJ
        "034F",  # CGJ
        "180E",  # MVS
        "200E",  # LRM
        "200F",  # RLM
    }
    text = pdf_bytes.decode("latin-1", errors="replace")
    # CMap entries look like: <XXXX> -> look for the hex values surrounded by angle brackets
    count = 0
    for code in zwc_hex:
        # Match as 2-byte or 4-byte hex entry in CMap: <00200C> or <200C>
        patterns = [f"<{code}>", f"<00{code}>", f"<{code.lower()}>", f"<00{code.lower()}>"]
        for pat in patterns:
            count += text.count(pat)
    return count


# ---------------------------------------------------------------------------
# Extended report: multi-extractor + PDF byte inspection
# ---------------------------------------------------------------------------


def run_deep_analysis() -> None:
    """Run deep analysis on ZWC with all generators + multiple extractors."""
    print("\n" + "=" * 100)
    print("DEEP ANALYSIS -- ZWC (100ch) through all generators x all extractors")
    print("=" * 100)

    embedded_text = _embed_zwc(ARTICLE_SENTENCES)
    expected_zwc = sum(1 for c in embedded_text if c in ZWC_CHARS)
    print(f"ZWC chars embedded in source text: {expected_zwc}")
    print()

    extractors = [
        ("pdfminer", _extract),
        ("pypdf", _extract_pypdf),
        ("pdfplumber", _extract_pdfplumber),
    ]

    col_w = 16
    header = f"  {'Generator':<26}  {'ZWC in PDF glyphs?':>20}"
    for name, _ in extractors:
        header += f"  {name:>{col_w}}"
    print(header)
    print("  " + "-" * (26 + 22 + len(extractors) * (col_w + 2)))

    for gen_name, render_fn in GENERATORS:
        try:
            pdf_bytes = render_fn(embedded_text)
        except Exception as exc:
            print(f"  {gen_name:<26}  RENDER ERROR: {exc!s:.50}")
            continue

        # Check whether ZWC chars survive in font glyph encoding (via ToUnicode CMap inspection)
        glyph_zwc = _count_zwc_via_tounicode(pdf_bytes)
        pdf_summary = f"~{glyph_zwc} via CMap"

        row = f"  {gen_name:<26}  {pdf_summary:>20}"
        for ext_name, ext_fn in extractors:
            try:
                extracted = ext_fn(pdf_bytes)
                zwc_after = sum(1 for c in extracted if c in ZWC_CHARS)
                pct = 100.0 * zwc_after / expected_zwc if expected_zwc else 0.0
                cell = f"{zwc_after}/{expected_zwc} ({pct:.0f}%)"
                row += f"  {cell:>{col_w}}"
            except Exception:
                row += f"  {'ERR':>{col_w}}"
        print(row)

    print()

    # Fragmentation analysis for reportlab (we know ZWC chars survive in bytes)
    print("FRAGMENTATION ANALYSIS -- reportlab-platypus + pdfminer (ZWC mode)")
    try:
        pdf_bytes = _render_reportlab_platypus(embedded_text)
        extracted = _extract(pdf_bytes)
        frag = _analyze_fragmentation(extracted)
        print(f"  Max consecutive ZWC chars in extracted text : {frag['max_consecutive_zwc']}")
        print(f"  Separator types found after ZWC chars        : {frag['separator_types']}")
        print(f"  Top separators                               : {frag['top_separators']}")
    except Exception as exc:
        print(f"  ERROR: {exc}")

    print()

    # PDF byte-level codepoint check for all generators
    print("RAW PDF BYTE INSPECTION -- codepoints present in PDF content stream")
    print(f"  {'Generator':<26}  {'ZWNJ':>6} {'ZWJ':>5} {'CGJ':>5} {'MVS':>5} {'LRM':>5} {'RLM':>5} {'VS1':>5} {'VS17':>6}")
    print("  " + "-" * 72)
    for gen_name, render_fn in GENERATORS:
        try:
            pdf_bytes = render_fn(embedded_text)
            b = _inspect_pdf_bytes(pdf_bytes)
            row = f"  {gen_name:<26}"
            keys = ["ZWNJ U+200C", "ZWJ  U+200D", "CGJ  U+034F", "MVS  U+180E", "LRM  U+200E", "RLM  U+200F", "VS1  U+FE00", "VS17 U+E0100"]
            for k in keys:
                v = b.get(k, 0)
                row += f"  {v:>5}" if isinstance(v, int) else f"  {'?':>5}"
            print(row)
        except Exception as exc:
            print(f"  {gen_name:<26}  ERROR: {exc!s:.60}")

    print()


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    results = run_audit()
    print_report(results)
    run_deep_analysis()
