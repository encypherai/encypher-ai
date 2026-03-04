"""PDF round-trip test for invisible embedding modes.

Tests whether embedded markers survive:
  text -> embed markers -> render to PDF (reportlab) -> extract text (pdfminer) -> verify markers

Five configurations tested:
  A. VS256      (micro, ecc=False, legacy_safe=False)  36 chars/marker
  B. VS256-RS   (micro, ecc=True,  legacy_safe=False)  44 chars/marker  [DEFAULT]
  C. ZWC        (micro, ecc=False, legacy_safe=True)  100 chars/marker
  D. ZWC-RS     (micro, ecc=True,  legacy_safe=True)  112 chars/marker
  E. Baseline   (no markers embedded)                 sanity check

The test also inspects character-level survival: reports exactly which invisible
codepoints are preserved vs. dropped by the pdfminer extraction path.

Usage (standalone, no API required):
    uv run pytest tests/test_pdf_embedding_roundtrip.py -v -s
or
    uv run python tests/test_pdf_embedding_roundtrip.py
"""

from __future__ import annotations

import io
import os
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

import pytest

# ---------------------------------------------------------------------------
# Article fixture
# ---------------------------------------------------------------------------

ARTICLE_SENTENCES = [
    "The rise of generative AI has fundamentally changed how content is produced at scale.",
    "Publishers now face an unprecedented challenge: verifying that AI-generated text originated from their licensed corpus.",
    "Invisible Unicode embeddings offer a promising solution by encoding signed provenance markers directly into the text stream.",
    "Unlike visible watermarks, these markers survive normal reading, copy-paste, and formatting transformations.",
    "This article evaluates four embedding strategies across common document pipeline stages.",
]

ARTICLE_TEXT = " ".join(ARTICLE_SENTENCES)

# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------

FREEMONO_TTF = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
LIBERATION_MONO_TTF = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"


def _pick_font() -> Optional[str]:
    for path in (FREEMONO_TTF, LIBERATION_MONO_TTF):
        if os.path.exists(path):
            return path
    return None


def _render_to_pdf(text: str) -> bytes:
    """Render plain+embedded text to a PDF in memory using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate

    font_path = _pick_font()
    if font_path is None:
        pytest.skip("No suitable TTF font found for PDF rendering")

    pdfmetrics.registerFont(TTFont("TestMono", font_path))

    styles = getSampleStyleSheet()
    style = styles["Normal"].clone("EmbedStyle")
    style.fontName = "TestMono"
    style.fontSize = 10
    style.leading = 14

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    doc.build([Paragraph(text, style)])
    return buf.getvalue()


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pdfminer."""
    from pdfminer.high_level import extract_text

    return extract_text(io.BytesIO(pdf_bytes))


# ---------------------------------------------------------------------------
# Embedding helpers (direct crypto, no API)
# ---------------------------------------------------------------------------

def _make_signing_key() -> bytes:
    """Return a fixed 32-byte HMAC signing key for reproducibility."""
    import hashlib
    return hashlib.sha256(b"test-pdf-roundtrip-key").digest()


def _embed_vs256(sentences: list[str], signing_key: bytes) -> str:
    """Embed VS256 (36-char) markers into each sentence."""
    from app.utils.vs256_crypto import create_signed_marker, generate_log_id
    from app.utils.legacy_safe_crypto import embed_marker_safely
    parts = []
    for s in sentences:
        log_id = generate_log_id()
        marker = create_signed_marker(log_id, signing_key, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


def _embed_vs256_rs(sentences: list[str], signing_key: bytes) -> str:
    """Embed VS256-RS (44-char) markers into each sentence."""
    from app.utils.vs256_rs_crypto import create_signed_marker
    from app.utils.legacy_safe_crypto import embed_marker_safely, generate_log_id
    parts = []
    for s in sentences:
        log_id = generate_log_id()
        marker = create_signed_marker(log_id, signing_key, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


def _embed_zwc(sentences: list[str], signing_key: bytes) -> str:
    """Embed ZWC legacy_safe (100-char) markers into each sentence."""
    from app.utils.legacy_safe_crypto import create_marker, embed_marker_safely, generate_log_id
    parts = []
    for s in sentences:
        log_id = generate_log_id()
        marker = create_marker(log_id, signing_key, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


def _embed_zwc_rs(sentences: list[str], signing_key: bytes) -> str:
    """Embed ZWC-RS legacy_safe_rs (112-char) markers into each sentence."""
    from app.utils.legacy_safe_rs_crypto import create_marker, embed_marker_safely, generate_log_id
    parts = []
    for s in sentences:
        log_id = generate_log_id()
        marker = create_marker(log_id, signing_key, sentence_text=s)
        parts.append(embed_marker_safely(s, marker))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------

def _count_vs256_markers(text: str) -> int:
    from app.utils.vs256_crypto import find_all_markers
    return len(find_all_markers(text))


def _count_vs256_rs_markers(text: str) -> int:
    from app.utils.vs256_rs_crypto import find_all_markers
    return len(find_all_markers(text))


def _count_zwc_markers(text: str) -> int:
    from app.utils.legacy_safe_crypto import find_all_markers
    return len(find_all_markers(text))


def _count_zwc_rs_markers(text: str) -> int:
    from app.utils.legacy_safe_rs_crypto import find_all_markers
    return len(find_all_markers(text))


# ---------------------------------------------------------------------------
# Character-level survival analysis
# ---------------------------------------------------------------------------

VS256_BMP_CHARS = frozenset(chr(c) for c in range(0xFE00, 0xFE10))         # VS1-16
VS256_SUPP_CHARS = frozenset(chr(c) for c in range(0xE0100, 0xE01F0))      # VS17-256
ZWC_CHARS = frozenset(["\u200C", "\u200D", "\u034F", "\u180E", "\u200E", "\u200F"])
ALL_INVISIBLE = VS256_BMP_CHARS | VS256_SUPP_CHARS | ZWC_CHARS


def _count_invisible(text: str) -> dict[str, int]:
    vs_bmp = sum(1 for c in text if c in VS256_BMP_CHARS)
    vs_supp = sum(1 for c in text if c in VS256_SUPP_CHARS)
    zwc = sum(1 for c in text if c in ZWC_CHARS)
    return {"vs_bmp": vs_bmp, "vs_supp": vs_supp, "zwc": zwc, "total": vs_bmp + vs_supp + zwc}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class RoundTripResult:
    mode: str
    marker_chars: int
    embedded_markers: int
    embedded_invisible_chars: int = 0

    pdf_rendered: bool = False
    pdf_size_bytes: int = 0

    extracted_invisible_chars: dict = field(default_factory=dict)
    surviving_markers: int = 0
    survival_rate: float = 0.0

    notes: str = ""


# ---------------------------------------------------------------------------
# Core round-trip function
# ---------------------------------------------------------------------------

def _run_roundtrip(
    mode: str,
    embed_fn,
    count_fn,
    marker_chars: int,
    sentences: list[str],
    signing_key: bytes,
) -> RoundTripResult:
    result = RoundTripResult(mode=mode, marker_chars=marker_chars, embedded_markers=len(sentences))

    # 1. Embed
    embedded_text = embed_fn(sentences, signing_key)
    result.embedded_invisible_chars = _count_invisible(embedded_text)["total"]

    # 2. Render to PDF
    try:
        pdf_bytes = _render_to_pdf(embedded_text)
        result.pdf_rendered = True
        result.pdf_size_bytes = len(pdf_bytes)
    except Exception as exc:
        result.notes = f"PDF render failed: {exc}"
        return result

    # 3. Extract text from PDF
    try:
        extracted = _extract_text_from_pdf(pdf_bytes)
    except Exception as exc:
        result.notes = f"PDF extract failed: {exc}"
        return result

    # 4. Count surviving invisible characters
    result.extracted_invisible_chars = _count_invisible(extracted)

    # 5. Count surviving whole markers
    result.surviving_markers = count_fn(extracted)
    result.survival_rate = (
        result.surviving_markers / result.embedded_markers
        if result.embedded_markers > 0
        else 0.0
    )

    return result


# ---------------------------------------------------------------------------
# Pytest tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def signing_key() -> bytes:
    return _make_signing_key()


@pytest.fixture(scope="module")
def all_results(signing_key) -> list[RoundTripResult]:
    """Run all 4 modes and collect results. Cached at module scope."""
    configs = [
        ("VS256 (36 chars)",    _embed_vs256,    _count_vs256_markers,    36),
        ("VS256-RS (44 chars)", _embed_vs256_rs, _count_vs256_rs_markers, 44),
        ("ZWC (100 chars)",     _embed_zwc,      _count_zwc_markers,      100),
        ("ZWC-RS (112 chars)",  _embed_zwc_rs,   _count_zwc_rs_markers,   112),
    ]
    return [
        _run_roundtrip(mode, embed_fn, count_fn, marker_chars, ARTICLE_SENTENCES, signing_key)
        for mode, embed_fn, count_fn, marker_chars in configs
    ]


def test_pdf_renders_for_all_modes(all_results):
    """All modes must produce a valid PDF without errors."""
    for r in all_results:
        assert r.pdf_rendered, f"{r.mode}: PDF render failed — {r.notes}"
        assert r.pdf_size_bytes > 1_000, f"{r.mode}: PDF suspiciously small ({r.pdf_size_bytes} bytes)"


def test_embedded_invisible_chars_present(all_results):
    """Each mode must embed some invisible chars into the text before PDF rendering."""
    for r in all_results:
        assert r.embedded_invisible_chars > 0, f"{r.mode}: No invisible chars found in embedded text"


def test_baseline_text_survives_pdf(signing_key):
    """Sanity check: visible article text is recoverable from PDF."""
    pdf_bytes = _render_to_pdf(ARTICLE_TEXT)
    extracted = _extract_text_from_pdf(pdf_bytes)
    # pdfminer may insert newlines or adjust capitalisation at line breaks
    extracted_lower = extracted.lower()
    assert "generative ai" in extracted_lower
    assert "invisible unicode" in extracted_lower


def test_print_survival_report(all_results, capsys):
    """Print a full survival report table (always passes; read the output)."""
    lines = [
        "",
        "=" * 74,
        "  PDF ROUND-TRIP SURVIVAL REPORT",
        "  Article: {} sentences, {} visible chars".format(
            len(ARTICLE_SENTENCES), len(ARTICLE_TEXT)
        ),
        "=" * 74,
        "{:<22} {:>6} {:>9} {:>9} {:>9} {:>8}".format(
            "Mode", "Chars", "Embedded", "Survived", "Survive%", "PDF KB"
        ),
        "-" * 74,
    ]
    for r in all_results:
        lines.append(
            "{:<22} {:>6} {:>9} {:>9} {:>9.0%} {:>8.1f}".format(
                r.mode,
                r.marker_chars,
                r.embedded_markers,
                r.surviving_markers,
                r.survival_rate,
                r.pdf_size_bytes / 1024,
            )
        )

    lines += [
        "-" * 74,
        "",
        "  Invisible char survival by type:",
        "{:<22} {:>8} {:>10} {:>8}".format("Mode", "VS-BMP", "VS-Supp", "ZWC"),
        "-" * 50,
    ]
    for r in all_results:
        before = r.embedded_invisible_chars
        after_vs_bmp = r.extracted_invisible_chars.get("vs_bmp", 0)
        after_vs_supp = r.extracted_invisible_chars.get("vs_supp", 0)
        after_zwc = r.extracted_invisible_chars.get("zwc", 0)
        lines.append(
            "{:<22} {:>8} {:>10} {:>8}".format(
                r.mode, after_vs_bmp, after_vs_supp, after_zwc
            )
        )

    lines += ["", "  Notes:"]
    for r in all_results:
        if r.notes:
            lines.append(f"    {r.mode}: {r.notes}")
    if not any(r.notes for r in all_results):
        lines.append("    (none)")

    lines.append("=" * 74)

    report = "\n".join(lines)
    print(report)

    # Write to file for easy inspection
    import os
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "pdf_roundtrip_report.txt")
    with open(report_path, "w") as f:
        f.write(report + "\n")
    print(f"\n  Report saved to: {report_path}")


def test_zwc_chars_survive_individually_vs256_stripped_completely(all_results):
    """Confirm the known PDF pipeline behaviour:

    VS256 chars (variation selectors, incl. supplementary plane U+E01xx):
      - Completely stripped by reportlab/pdfminer — the font has no glyphs for
        them; they arrive as U+0000 null bytes in the extracted text.

    ZWC chars (ZWNJ, ZWJ, CGJ, MVS, LRM, RLM):
      - Individual chars survive (FreeMono has glyphs for them) but pdfminer
        inserts U+0000/U+000A between each one, fragmenting every 100-char run
        into isolated single chars. No whole marker is recoverable.

    Conclusion: with the reportlab → pdfminer pipeline, neither mode produces
    recoverable full markers. ZWC is strictly better (chars survive; VS256 chars
    are fully erased), but neither is suitable as-is for PDF-only workflows.
    See test_print_survival_report for the full quantified output.
    """
    vs256 = next(r for r in all_results if r.mode.startswith("VS256 "))
    zwc   = next(r for r in all_results if r.mode.startswith("ZWC "))

    # VS256 supplementary chars must be completely absent
    assert vs256.extracted_invisible_chars.get("vs_supp", 0) == 0, (
        "VS256 supplementary chars unexpectedly survived — font or extractor changed"
    )

    # ZWC chars must at least partially survive (individual chars, not whole markers)
    zwc_individual = zwc.extracted_invisible_chars.get("zwc", 0)
    assert zwc_individual > 0, (
        "ZWC chars did not survive at all — unexpected; check font coverage"
    )

    # No whole markers survive via either mode under this pipeline
    assert vs256.surviving_markers == 0
    assert zwc.surviving_markers == 0


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    key = _make_signing_key()
    configs = [
        ("VS256 (36 chars)",    _embed_vs256,    _count_vs256_markers,    36),
        ("VS256-RS (44 chars)", _embed_vs256_rs, _count_vs256_rs_markers, 44),
        ("ZWC (100 chars)",     _embed_zwc,      _count_zwc_markers,      100),
        ("ZWC-RS (112 chars)",  _embed_zwc_rs,   _count_zwc_rs_markers,   112),
    ]
    results = [
        _run_roundtrip(mode, embed_fn, count_fn, marker_chars, ARTICLE_SENTENCES, key)
        for mode, embed_fn, count_fn, marker_chars in configs
    ]

    print("\n" + "=" * 74)
    print("  PDF ROUND-TRIP SURVIVAL REPORT")
    print(f"  Article: {len(ARTICLE_SENTENCES)} sentences, {len(ARTICLE_TEXT)} visible chars")
    print("=" * 74)
    print(f"{'Mode':<22} {'Chars':>6} {'Embedded':>9} {'Survived':>9} {'Rate':>7} {'PDF KB':>8}")
    print("-" * 74)
    for r in results:
        print(
            f"{r.mode:<22} {r.marker_chars:>6} {r.embedded_markers:>9} "
            f"{r.surviving_markers:>9} {r.survival_rate:>7.0%} {r.pdf_size_bytes/1024:>8.1f}"
        )
    print("-" * 74)
    print("\n  Invisible char type survival:")
    print(f"{'Mode':<22} {'VS-BMP':>8} {'VS-Supp':>10} {'ZWC':>8}")
    print("-" * 50)
    for r in results:
        print(
            f"{r.mode:<22} "
            f"{r.extracted_invisible_chars.get('vs_bmp',0):>8} "
            f"{r.extracted_invisible_chars.get('vs_supp',0):>10} "
            f"{r.extracted_invisible_chars.get('zwc',0):>8}"
        )
