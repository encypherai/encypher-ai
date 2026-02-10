# TEAM_157: Sign existing PDFs without changing visual appearance
"""
Sign a pre-existing PDF by extracting its text, signing via the enterprise API,
and injecting provenance data:

1. **EncypherSignedText metadata stream** — stored in the PDF catalog for
   lossless extraction by the browser/server-side verifier.
2. **Zero-width characters in the text layer** — invisible Unicode characters
   (variation selectors, ZW joiners, etc.) are inserted at the correct
   positions in the PDF's visible text using a prepared font with synthetic
   zero-width glyphs.  This embeds provenance directly in the text layer
   without changing the PDF's visual appearance.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

import fitz

from encypher_pdf.fonttools_subset import (
    INVISIBLE_CODEPOINTS,
    prepare_font_with_invisible_glyphs,
)
from xml_to_pdf.signer import SignResult, sign_text

# TEAM_157: Default font for ZW glyph overlay
_DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
_PREPARED_FONT_CACHE: bytes | None = None


class SignExistingError(Exception):
    """Raised when signing an existing PDF fails."""


@dataclass
class _ZwInsertion:
    """A zero-width character to insert at a specific position in the PDF."""

    page_num: int
    x: float
    y: float
    char: str


def _is_invisible(cp: int) -> bool:
    return cp in INVISIBLE_CODEPOINTS


def _get_prepared_font() -> bytes:
    """Return a TTF font with synthetic zero-width glyphs (cached)."""
    global _PREPARED_FONT_CACHE
    if _PREPARED_FONT_CACHE is None:
        raw = Path(_DEFAULT_FONT_PATH).read_bytes()
        _PREPARED_FONT_CACHE = prepare_font_with_invisible_glyphs(raw)
    return _PREPARED_FONT_CACHE


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file, joining pages with ``\\n\\n``.

    Raises:
        SignExistingError: If the file doesn't exist, isn't a valid PDF,
            or contains no extractable text.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise SignExistingError(f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise SignExistingError(f"Cannot open PDF: {exc}") from exc

    try:
        pages: list[str] = []
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                pages.append(page_text)
    finally:
        doc.close()

    if not pages:
        raise SignExistingError(f"No text could be extracted from {pdf_path}")

    return "\n\n".join(pages)


def _build_char_position_map(
    doc: fitz.Document,
) -> list[dict]:
    """
    Build a flat list of character positions across all pages.

    Each entry: ``{"c": str, "x": float, "y": float, "page": int}``.
    Only visible characters are included (whitespace like ``\\n`` is skipped
    since pymupdf doesn't report positions for them).
    """
    chars: list[dict] = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("rawdict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    for c in span.get("chars", []):
                        chars.append(
                            {
                                "c": c["c"],
                                "x": c["bbox"][2],  # right edge
                                "y": c["origin"][1],  # baseline
                                "page": page_num,
                            }
                        )
    return chars


def _diff_for_insertions(
    original: str,
    signed: str,
    char_positions: list[dict],
) -> list[_ZwInsertion]:
    """
    Walk the original and signed text in parallel to find where invisible
    characters were **inserted** by the signing API.

    For each newly-inserted invisible char, record the page position of the
    preceding visible character so we can overlay it at the correct location.

    Characters that already exist in the original (including newlines) are
    not treated as insertions — only characters added by the signing process.
    """
    insertions: list[_ZwInsertion] = []

    # Walk both strings in parallel.  ``oi`` tracks position in ``original``,
    # ``visible_idx`` tracks position in ``char_positions`` (only printable
    # chars that pymupdf reports with coordinates).
    oi = 0  # index into original
    visible_idx = 0  # index into char_positions

    for ch in signed:
        cp = ord(ch)
        if oi < len(original) and ch == original[oi]:
            # Character matches the original — not an insertion.
            # Advance visible_idx only for chars that have positions
            # (newlines / control chars don't appear in rawdict).
            if ch not in ("\n", "\r"):
                visible_idx += 1
            oi += 1
        elif _is_invisible(cp) or ch in ("\n", "\r"):
            # Invisible char NOT in the original at this position — inserted.
            # Skip newlines that were inserted (they have no position).
            if ch in ("\n", "\r"):
                continue
            if visible_idx > 0 and visible_idx <= len(char_positions):
                prev = char_positions[visible_idx - 1]
                insertions.append(
                    _ZwInsertion(
                        page_num=prev["page"],
                        x=prev["x"],
                        y=prev["y"],
                        char=ch,
                    )
                )
        else:
            # Visible character — advance both indices
            visible_idx += 1
            oi += 1

    return insertions


def _inject_zw_chars_into_pages(
    doc: fitz.Document,
    insertions: list[_ZwInsertion],
) -> None:
    """
    Insert zero-width characters into the PDF text layer at the specified
    positions using a prepared font with synthetic ZW glyphs.

    The characters are rendered at font size 1 so they occupy no visual
    space but are present in the text extraction layer.
    """
    if not insertions:
        return

    prepared_font = _get_prepared_font()

    # Write prepared font to a temp file for pymupdf
    tmp = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
    try:
        tmp.write(prepared_font)
        tmp.close()

        font_registered: set[int] = set()
        for ins in insertions:
            page = doc[ins.page_num]

            # Register the font on this page (once per page)
            if ins.page_num not in font_registered:
                page.insert_text(
                    (0, 0),
                    "",
                    fontname="EncInv",
                    fontfile=tmp.name,
                    fontsize=1,
                )
                font_registered.add(ins.page_num)

            page.insert_text(
                (ins.x, ins.y),
                ins.char,
                fontname="EncInv",
                fontfile=tmp.name,
                fontsize=1,
            )
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def inject_signed_text_stream(
    pdf_path: str,
    output_path: str | None,
    signed_text: str,
) -> None:
    """
    Inject an ``EncypherSignedText`` stream into the PDF catalog.

    The stream contains the UTF-8 encoded signed text, stored uncompressed
    so browser-side extractors can read it with a simple byte-range slice.

    Args:
        pdf_path: Path to the source PDF.
        output_path: Where to write the signed PDF.  If ``None``, the source
            file is overwritten in place.
        signed_text: The signed text (with embedded invisible characters).
    """
    doc = fitz.open(pdf_path)

    try:
        signed_bytes = signed_text.encode("utf-8")

        # Create a new stream object in the PDF
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /EncypherSignedText >>")
        doc.update_stream(xref, signed_bytes)

        # Link from the catalog
        cat = doc.pdf_catalog()
        doc.xref_set_key(cat, "EncypherSignedText", f"{xref} 0 R")

        # Save — incremental when overwriting the source file
        dest = output_path or pdf_path
        if dest == pdf_path:
            doc.save(dest, incremental=True, encryption=0)
        else:
            doc.save(dest, garbage=0, deflate=False)
    finally:
        doc.close()


def sign_existing_pdf(
    pdf_path: str,
    output_path: str | None,
    *,
    mode: str = "minimal",
    document_title: str | None = None,
    api_url: str | None = None,
    api_key: str | None = None,
) -> SignResult:
    """
    Sign an existing PDF end-to-end:

    1. Extract plain text from the PDF.
    2. Sign via the enterprise API.
    3. Inject zero-width invisible characters into the PDF text layer.
    4. Inject the ``EncypherSignedText`` metadata stream into the catalog.

    The original visual appearance is completely preserved — only invisible
    characters and a metadata stream are added.

    Args:
        pdf_path: Path to the existing PDF to sign.
        output_path: Where to write the signed PDF.  ``None`` = overwrite.
        mode: Signing mode (see ``signer.EMBEDDING_MODES``).
        document_title: Title for the signing request.  Defaults to the
            PDF filename stem.
        api_url: Override enterprise API base URL.
        api_key: Override API key.

    Returns:
        The ``SignResult`` from the enterprise API.

    Raises:
        SignExistingError: If text extraction or injection fails.
        SigningError: If the enterprise API call fails.
    """
    # 1. Extract text
    text = extract_text_from_pdf(pdf_path)

    # 2. Determine title
    title = document_title or Path(pdf_path).stem

    # 3. Sign via API
    result = sign_text(text, title, mode, api_url=api_url, api_key=api_key)

    # 4. Inject ZW chars into text layer + metadata stream
    doc = fitz.open(pdf_path)
    try:
        # Build character position map from original PDF
        char_positions = _build_char_position_map(doc)

        # Find where invisible chars were inserted
        insertions = _diff_for_insertions(text, result.signed_text, char_positions)

        # Insert ZW chars into pages
        _inject_zw_chars_into_pages(doc, insertions)

        # Add EncypherSignedText metadata stream
        signed_bytes = result.signed_text.encode("utf-8")
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /EncypherSignedText >>")
        doc.update_stream(xref, signed_bytes)
        cat = doc.pdf_catalog()
        doc.xref_set_key(cat, "EncypherSignedText", f"{xref} 0 R")

        # Save
        dest = output_path or pdf_path
        if dest == pdf_path:
            doc.save(dest, incremental=True, encryption=0)
        else:
            doc.save(dest, garbage=0, deflate=False)
    finally:
        doc.close()

    return result
