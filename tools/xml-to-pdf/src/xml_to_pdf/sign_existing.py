# TEAM_157/158: Sign existing PDFs without changing visual appearance
"""
Sign a pre-existing PDF by extracting its text, signing via the enterprise API,
and injecting provenance data:

1. **EncypherSignedText metadata stream** — stored in the PDF catalog for
   lossless extraction by the browser/server-side verifier.
2. **Zero-width characters in the text layer** — invisible Unicode characters
   (variation selectors, ZW joiners, etc.) are injected directly into the
   PDF content stream Tj/TJ operators using a custom embedded CID font
   (Identity-H + ToUnicode CMap).  Font-switching commands interleave the
   invisible chars with the original visible text so that copy-paste from
   any PDF viewer preserves the correct character ordering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import fitz
from encypher_pdf.font import FontMapping, build_font_mapping, build_tounicode_cmap
from encypher_pdf.fonttools_subset import (
    INVISIBLE_CODEPOINTS,
    get_font_metrics,
    prepare_font_with_invisible_glyphs,
)

from xml_to_pdf.signer import SignResult, sign_text

# TEAM_158: Default font for unified CID font embedding
_DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# TEAM_158: Name used for our unified CID font in the PDF Resources/Font dict.
# This replaces the original page font so that visible AND invisible chars
# share a single CID font — critical for copy-paste preservation of VS chars.
_UNIFIED_FONT_NAME = "EncSgn"

# Keep old name as alias for backward compat in tests
_INVIS_FONT_NAME = _UNIFIED_FONT_NAME


class SignExistingError(Exception):
    """Raised when signing an existing PDF fails."""


@dataclass
class _InvisInsertion:
    """An invisible character to insert after a specific visible-char index."""

    after_visible_idx: int
    char: str


@dataclass
class _FontAssets:
    """Cached font data for embedding into PDFs."""

    prepared_font: bytes
    metrics: dict
    mapping: FontMapping
    tounicode_data: bytes
    w_array: str  # pre-built PDF W array string


def _is_invisible(cp: int) -> bool:
    return cp in INVISIBLE_CODEPOINTS


# TEAM_158: Cache the prepared font binary (expensive fonttools operation).
# The mapping/W-array are rebuilt per-PDF because visible codepoints vary.
_PREPARED_FONT_CACHE: tuple[bytes, dict] | None = None


def _get_prepared_font() -> tuple[bytes, dict]:
    """Return (prepared_font_bytes, metrics) — cached."""
    global _PREPARED_FONT_CACHE
    if _PREPARED_FONT_CACHE is None:
        raw = Path(_DEFAULT_FONT_PATH).read_bytes()
        prepared = prepare_font_with_invisible_glyphs(raw)
        metrics = get_font_metrics(prepared)
        _PREPARED_FONT_CACHE = (prepared, metrics)
    return _PREPARED_FONT_CACHE


def _build_font_assets(visible_codepoints: set[int]) -> _FontAssets:
    """Build font assets for a unified CID font with visible + invisible glyphs.

    Args:
        visible_codepoints: Set of Unicode codepoints used in the PDF's
            existing content streams (e.g. ASCII chars from Helvetica).

    Returns:
        _FontAssets with a single CID font covering both visible and
        invisible characters.
    """
    prepared, metrics = _get_prepared_font()
    units_per_em = metrics.get("units_per_em", 1000)
    default_width = metrics.get("default_width", 600)
    widths = metrics["widths"]
    cmap = metrics["cmap"]

    # Combine visible + invisible codepoints that exist in the font's cmap
    all_cps = set(visible_codepoints)
    all_cps.update(cp for cp in INVISIBLE_CODEPOINTS if cp in cmap)
    # Always include basic ASCII
    all_cps.update(range(0x20, 0x7F))

    mapping = build_font_mapping(all_cps, metrics)
    tounicode_data = build_tounicode_cmap(mapping)

    # Build W array — invisible glyphs get width 1 (not 0, pdfjs filters
    # zero-width glyphs); visible glyphs get their real scaled width.
    invisible_gids = {
        cmap.get(cp) for cp in INVISIBLE_CODEPOINTS if cp in cmap
    }
    w_entries: list[str] = []
    for gid in sorted(mapping.gid_to_unicode.keys()):
        if gid == 0:
            continue
        if gid in invisible_gids:
            w_entries.append(f"{gid} [1]")
        else:
            w = widths.get(gid, default_width)
            scaled = round(w * 1000 / units_per_em)
            w_entries.append(f"{gid} [{scaled}]")

    return _FontAssets(
        prepared_font=prepared,
        metrics=metrics,
        mapping=mapping,
        tounicode_data=tounicode_data,
        w_array=" ".join(w_entries),
    )


def _get_font_assets() -> _FontAssets:
    """Build font assets with invisible codepoints only.

    Used for font-switching injection (invisible chars only) and by
    extract_signed_text_from_streams for gid_to_unicode decoding.

    Invisible glyphs get width 1 (in 1/1000 em units) — tiny but non-zero
    so text extractors (Chrome PDFium, pdftotext) maintain position ordering
    for copy-paste interleaving.  The visual displacement is compensated by
    TJ negative kern in _rewrite_content_stream.
    """
    prepared, metrics = _get_prepared_font()
    invis_cps = {cp for cp in INVISIBLE_CODEPOINTS if cp in metrics["cmap"]}
    mapping = build_font_mapping(invis_cps, metrics)
    tounicode_data = build_tounicode_cmap(mapping)
    w_entries: list[str] = []
    for gid in sorted(mapping.gid_to_unicode.keys()):
        if gid == 0:
            continue
        w_entries.append(f"{gid} [1]")
    return _FontAssets(
        prepared_font=prepared,
        metrics=metrics,
        mapping=mapping,
        tounicode_data=tounicode_data,
        w_array=" ".join(w_entries),
    )


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


def extract_signed_text_from_streams(pdf_path: str) -> str:
    """
    Extract text from a signed PDF by parsing content streams directly.

    Unlike :func:`extract_text_from_pdf` (which delegates to MuPDF's
    ``get_text()``), this function walks the raw content stream operators
    and decodes hex Tj strings using the font's ToUnicode / GID mapping.
    This achieves **100 %** invisible-character extraction — MuPDF's text
    engine drops ~1 % of zero-width glyphs when many overlap at the same
    position.

    The function requires that the PDF was signed with our custom
    ``EncInv`` CID font (i.e. via :func:`sign_existing_pdf`).

    Args:
        pdf_path: Path to a signed PDF file.

    Returns:
        Full text including all invisible characters, pages joined with
        ``\\n\\n``.

    Raises:
        SignExistingError: If the file doesn't exist or can't be opened.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise SignExistingError(f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise SignExistingError(f"Cannot open PDF: {exc}") from exc

    # Build a full gid→unicode mapping from the prepared font (covers all
    # codepoints the font knows about, not just invisible ones).
    # When multiple codepoints share the same GID (e.g. space 0x20 and
    # NBSP 0xA0 both → GID 3), prefer the lower codepoint.
    _, metrics = _get_prepared_font()
    full_gid_to_unicode: dict[int, int] = {}
    for cp, gid in metrics["cmap"].items():
        if gid not in full_gid_to_unicode or cp < full_gid_to_unicode[gid]:
            full_gid_to_unicode[gid] = cp

    def _decode_hex_cid(hex_str: str) -> list[str]:
        """Decode a 2-byte CID hex string using the full gid→unicode map."""
        chars: list[str] = []
        for i in range(0, len(hex_str), 4):
            gid = int(hex_str[i : i + 4], 16)
            cp = full_gid_to_unicode.get(gid, gid)
            chars.append(chr(cp))
        return chars

    def _decode_hex_simple(hex_str: str, bpc: int) -> list[str]:
        """Decode a simple (1-byte or 2-byte) hex string."""
        chars: list[str] = []
        hex_per_char = bpc * 2
        for i in range(0, len(hex_str), hex_per_char):
            val = int(hex_str[i : i + hex_per_char], 16)
            chars.append(chr(val))
        return chars

    try:
        pages_text: list[str] = []
        for page in doc:
            font_bpc = _detect_bytes_per_char(doc, page)
            page_chars: list[str] = []

            for cx in page.get_contents():
                stream = doc.xref_stream(cx)
                if not stream:
                    continue
                st = stream.decode("latin-1")
                current_font = ""

                for m in _ALL_OPS_RE.finditer(st):
                    if m.group(1):  # font switch
                        current_font = m.group(1)
                    elif m.group(2):  # single hex Tj
                        hex_str = _HEX_STRING_RE.search(m.group(2))
                        if not hex_str or not hex_str.group(1):
                            continue
                        hs = hex_str.group(1)
                        if current_font == _UNIFIED_FONT_NAME:
                            page_chars.extend(_decode_hex_cid(hs))
                        else:
                            bpc = font_bpc.get(current_font, 1)
                            page_chars.extend(_decode_hex_simple(hs, bpc))
                    elif m.group(3):  # TJ array
                        for hm in _HEX_STRING_RE.finditer(m.group(3)):
                            hs = hm.group(1)
                            if not hs:
                                continue
                            if current_font == _UNIFIED_FONT_NAME:
                                page_chars.extend(_decode_hex_cid(hs))
                            else:
                                bpc = font_bpc.get(current_font, 1)
                                page_chars.extend(
                                    _decode_hex_simple(hs, bpc)
                                )

            page_text = "".join(page_chars).strip()
            if page_text:
                pages_text.append(page_text)
    finally:
        doc.close()

    return "\n\n".join(pages_text)


def _diff_for_insertions(
    original: str,
    signed: str,
) -> list[_InvisInsertion]:
    """
    Walk the original and signed text in parallel to find where invisible
    characters were **inserted** by the signing API.

    Returns a list of insertions, each recording the visible-char index
    (0-based, counting only non-whitespace chars that appear in rawdict)
    after which the invisible char should be placed.

    Characters that already exist in the original (including newlines) are
    not treated as insertions — only characters added by the signing process.

    Handles whitespace normalization: the signing API may convert ``\\n``
    to a space.  Such conversions are treated as matching the original
    newline (not as a new visible character).
    """
    insertions: list[_InvisInsertion] = []

    oi = 0  # index into original
    visible_idx = 0  # counts visible chars (those in rawdict)

    for ch in signed:
        cp = ord(ch)
        if oi < len(original) and ch == original[oi]:
            # Exact match
            if ch not in ("\n", "\r"):
                visible_idx += 1
            oi += 1
        elif (
            oi < len(original)
            and ch == " "
            and original[oi] in ("\n", "\r")
        ):
            # TEAM_158: Signing API normalised newline → space.
            # The newline doesn't exist in the content stream, so the
            # replacement space also doesn't — do NOT advance visible_idx.
            oi += 1
            # Skip a following \n if the original has \r\n
            if oi < len(original) and original[oi] == "\n":
                oi += 1
        elif _is_invisible(cp) or ch in ("\n", "\r"):
            if ch in ("\n", "\r"):
                continue
            if visible_idx > 0:
                insertions.append(
                    _InvisInsertion(
                        after_visible_idx=visible_idx - 1,
                        char=ch,
                    )
                )
        else:
            # Visible character — advance both indices
            visible_idx += 1
            oi += 1

    return insertions


def _redistribute_insertions(
    insertions: list[_InvisInsertion],
    total_visible_chars: int,
) -> list[_InvisInsertion]:
    """
    Redistribute invisible-char insertions so each visible-char index gets
    at most **one** invisible character.

    The signing API may place all VS chars as a contiguous block (e.g. 36
    chars all after the same base glyph).  Poppler deduplicates variation
    selectors per base glyph, so we spread them evenly across the visible
    text to guarantee 100 % copy-paste preservation.

    If there are more invisible chars than visible chars, the extras wrap
    around (multiple passes).
    """
    if not insertions or total_visible_chars <= 0:
        return insertions

    # Collect all invisible chars in order
    all_chars = [ins.char for ins in insertions]

    if len(all_chars) <= 1:
        return insertions

    # Distribute evenly: place one invisible char after each visible char,
    # cycling through visible indices.
    redistributed: list[_InvisInsertion] = []
    for i, ch in enumerate(all_chars):
        target_idx = i % total_visible_chars
        redistributed.append(_InvisInsertion(after_visible_idx=target_idx, char=ch))

    return redistributed


# ---------------------------------------------------------------------------
# Content stream regex patterns
# ---------------------------------------------------------------------------

# TEAM_158: Regex to match hex-string Tj/TJ operators in PDF content streams.
# Matches patterns like:
#   <48656c6c6f> Tj
#   [<0026...> <02A9>] TJ
_HEX_TJ_RE = re.compile(
    r"(\[(?:\s*<[0-9A-Fa-f]*>\s*(?:-?\d+\s*)*)+\]\s*TJ"
    r"|<[0-9A-Fa-f]+>\s*Tj)",
    re.IGNORECASE,
)

# Matches individual hex strings inside a TJ array or Tj operand
_HEX_STRING_RE = re.compile(r"<([0-9A-Fa-f]*)>")

# Matches /FontName Size Tf commands to track current font
_FONT_TF_RE = re.compile(r"/(\S+)\s+(\d+(?:\.\d+)?)\s+Tf")

# Combined regex: font switches, single-string Tj, and TJ arrays (in order)
_ALL_OPS_RE = re.compile(
    r"/(\S+)\s+\S+\s+Tf"  # group(1): font switch
    r"|(<[0-9A-Fa-f]+>)\s*Tj"  # group(2): single hex Tj
    r"|(\[(?:\s*<[0-9A-Fa-f]*>\s*(?:-?\d+\s*)*)+\])\s*TJ",  # group(3): TJ array
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Content stream analysis
# ---------------------------------------------------------------------------


def _collect_visible_codepoints(doc: fitz.Document) -> set[int]:
    """Scan all content streams and return the set of Unicode codepoints used.

    For simple (1-byte) fonts, each hex byte IS the codepoint.
    For CID (2-byte) fonts we'd need the ToUnicode CMap, but pymupdf's
    ``insert_text`` always uses simple fonts so this handles the common case.
    """
    codepoints: set[int] = set()
    for page in doc:
        font_bpc = _detect_bytes_per_char(doc, page)
        for cx in page.get_contents():
            stream = doc.xref_stream(cx)
            if not stream:
                continue
            st = stream.decode("latin-1")
            current_font = ""
            for m in _ALL_OPS_RE.finditer(st):
                if m.group(1):  # font switch
                    current_font = m.group(1)
                elif m.group(2) or m.group(3):  # Tj or TJ
                    bpc = font_bpc.get(current_font, 1)
                    hex_per_char = bpc * 2
                    text_part = m.group(2) or m.group(3)
                    for hm in _HEX_STRING_RE.finditer(text_part):
                        hs = hm.group(1)
                        if not hs:
                            continue
                        for i in range(0, len(hs), hex_per_char):
                            val = int(hs[i : i + hex_per_char], 16)
                            codepoints.add(val)
    return codepoints


# ---------------------------------------------------------------------------
# Content stream rewriting
# ---------------------------------------------------------------------------


def _count_chars_in_hex(hex_str: str, bytes_per_char: int) -> int:
    """Count the number of characters encoded in a hex string."""
    hex_chars_per_char = bytes_per_char * 2
    return len(hex_str) // hex_chars_per_char if hex_chars_per_char else 0


def _detect_bytes_per_char(doc: fitz.Document, page: fitz.Page) -> dict[str, int]:
    """
    Detect bytes-per-character for each font on a page.

    Identity-H CID fonts use 2 bytes per char; simple fonts use 1 byte.
    Returns {font_name: bytes_per_char}.
    """
    result: dict[str, int] = {}
    page_xref = page.xref

    # Get the Resources dict
    res_result = doc.xref_get_key(page_xref, "Resources")
    if res_result[0] == "xref":
        res_xref = int(res_result[1].split()[0])
        font_result = doc.xref_get_key(res_xref, "Font")
    elif res_result[0] == "dict":
        font_result = doc.xref_get_key(page_xref, "Resources/Font")
    else:
        return result

    if font_result[0] != "dict":
        return result

    # Parse font dict entries like "/F0 18 0 R /helv 5 0 R"
    font_dict_str = font_result[1]
    font_entries = re.findall(r"/(\S+)\s+(\d+)\s+0\s+R", font_dict_str)

    for font_name, xref_str in font_entries:
        font_xref = int(xref_str)
        try:
            encoding = doc.xref_get_key(font_xref, "Encoding")
            if encoding[0] == "name" and "Identity" in encoding[1]:
                result[font_name] = 2
            else:
                subtype = doc.xref_get_key(font_xref, "Subtype")
                if subtype[0] == "name" and subtype[1] == "/Type0":
                    result[font_name] = 2
                else:
                    result[font_name] = 1
        except Exception:
            result[font_name] = 1

    return result


def _rewrite_content_stream(
    stream_bytes: bytes,
    insertions_by_idx: dict[int, list[str]],
    font_bytes_per_char: dict[str, int],
    mapping: FontMapping,
    unified_font_name: str,
) -> bytes:
    """
    Inject invisible characters into a PDF content stream using
    **font-switching** — the original content is left completely intact.

    For each Tj/TJ operator, we count visible characters to track the
    global char index.  When an insertion is needed after a visible char,
    we append a font-switch sequence *after* the original Tj/TJ:

        /{EncSgn} {size} Tf <XXXX> Tj /{origFont} {size} Tf

    This preserves the original font encoding (critical for Type3 and
    custom-encoded fonts) while placing invisible chars inline in the
    content stream for copy-paste preservation.

    Args:
        stream_bytes: Raw content stream bytes.
        insertions_by_idx: {visible_char_idx: [list of invisible chars]}.
        font_bytes_per_char: {font_name: 1 or 2} for each font on the page.
        mapping: FontMapping for the invisible CID font.
        unified_font_name: PDF resource name for the invisible font.

    Returns:
        Modified content stream bytes (original text intact, invisible
        chars injected via font switches).
    """
    if not insertions_by_idx:
        return stream_bytes

    stream_text = stream_bytes.decode("latin-1")

    current_font = ""
    current_size = "12"
    global_char_idx = 0
    output_parts: list[str] = []
    last_end = 0

    all_ops: list[tuple[int, int, str, object]] = []
    for m in _FONT_TF_RE.finditer(stream_text):
        all_ops.append((m.start(), m.end(), "font", m))
    for m in _HEX_TJ_RE.finditer(stream_text):
        all_ops.append((m.start(), m.end(), "text", m))
    all_ops.sort(key=lambda x: x[0])

    for start, end, op_type, match in all_ops:
        if op_type == "font":
            current_font = match.group(1)
            current_size = match.group(2)
            # Keep original font command verbatim
            continue

        # Text operator (Tj or TJ) — keep original verbatim
        bpc = font_bytes_per_char.get(current_font, 1)
        op_text = match.group(0)

        hex_matches = list(_HEX_STRING_RE.finditer(op_text))
        if not hex_matches:
            continue

        total_chars = sum(
            _count_chars_in_hex(hm.group(1), bpc) for hm in hex_matches
        )
        op_start_idx = global_char_idx
        op_end_idx = op_start_idx + total_chars - 1

        # Check if any insertions fall within this operator's char range
        has_insertions = any(
            op_start_idx <= idx <= op_end_idx
            for idx in insertions_by_idx
        )

        if has_insertions:
            # Emit everything up to and including this Tj/TJ verbatim
            output_parts.append(stream_text[last_end:end])

            # Build invisible char injection sequence after this Tj/TJ
            invis_parts: list[str] = []
            for idx in sorted(insertions_by_idx):
                if op_start_idx <= idx <= op_end_idx:
                    for ic in insertions_by_idx[idx]:
                        ic_gid = mapping.unicode_to_gid.get(ord(ic), 0)
                        # TJ array: emit glyph then kern back by its width (1)
                        # so the invisible char doesn't displace visible text.
                        invis_parts.append(f"[<{ic_gid:04X}> -1] TJ")

            if invis_parts:
                # Font-switch: EncSgn → emit invisible chars → restore original font
                inject = (
                    f"\n/{unified_font_name} {current_size} Tf "
                    + " ".join(invis_parts)
                    + f" /{current_font} {current_size} Tf"
                )
                output_parts.append(inject)

            last_end = end

        global_char_idx += total_chars

    output_parts.append(stream_text[last_end:])
    return "".join(output_parts).encode("latin-1")


# ---------------------------------------------------------------------------
# Font embedding via pymupdf xref API
# ---------------------------------------------------------------------------


def _embed_invisible_font(
    doc: fitz.Document,
    assets: _FontAssets,
) -> int:
    """
    Embed our unified CID font into the PDF.

    Creates all required PDF objects (FontFile2, ToUnicode, FontDescriptor,
    CIDFont, Type0) via pymupdf's xref API.  The font contains both visible
    and invisible glyphs so that VS chars share the same text run as base
    glyphs — critical for copy-paste preservation.

    Returns the xref of the Type0 font object.
    """
    metrics = assets.metrics
    bbox = metrics.get("bbox", [0, 0, 0, 0])
    units_per_em = metrics.get("units_per_em", 1000)
    default_width = metrics.get("default_width", 600)
    default_scaled = round(default_width * 1000 / units_per_em)

    # FontFile2 stream (uncompressed — pymupdf handles /Length)
    fontfile_xref = doc.get_new_xref()
    doc.update_object(
        fontfile_xref,
        f"<< /Length1 {len(assets.prepared_font)} >>",
    )
    doc.update_stream(fontfile_xref, assets.prepared_font)

    # ToUnicode CMap stream
    tounicode_xref = doc.get_new_xref()
    doc.update_object(tounicode_xref, "<< >>")
    doc.update_stream(tounicode_xref, assets.tounicode_data)

    # Font descriptor
    descriptor_xref = doc.get_new_xref()
    doc.update_object(
        descriptor_xref,
        f"<< /Type /FontDescriptor"
        f" /FontName /EncypherSigned"
        f" /Flags 32"
        f" /FontBBox [{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}]"
        f" /ItalicAngle 0"
        f" /Ascent {metrics.get('ascent', 800)}"
        f" /Descent {metrics.get('descent', -200)}"
        f" /CapHeight {metrics.get('cap_height', 700)}"
        f" /StemV 80"
        f" /FontFile2 {fontfile_xref} 0 R >>",
    )

    # CIDFont
    cidfont_xref = doc.get_new_xref()
    doc.update_object(
        cidfont_xref,
        f"<< /Type /Font"
        f" /Subtype /CIDFontType2"
        f" /BaseFont /EncypherSigned"
        f" /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >>"
        f" /FontDescriptor {descriptor_xref} 0 R"
        f" /DW {default_scaled}"
        f" /W [{assets.w_array}]"
        f" /CIDToGIDMap /Identity >>",
    )

    # Type0 font
    type0_xref = doc.get_new_xref()
    doc.update_object(
        type0_xref,
        f"<< /Type /Font"
        f" /Subtype /Type0"
        f" /BaseFont /EncypherSigned"
        f" /Encoding /Identity-H"
        f" /DescendantFonts [{cidfont_xref} 0 R]"
        f" /ToUnicode {tounicode_xref} 0 R >>",
    )

    return type0_xref


def _register_font_on_page(
    doc: fitz.Document,
    page: fitz.Page,
    font_name: str,
    font_xref: int,
) -> None:
    """
    Add a font reference to a page's Resources/Font dictionary.
    """
    page_xref = page.xref
    res_result = doc.xref_get_key(page_xref, "Resources")

    if res_result[0] == "xref":
        res_xref = int(res_result[1].split()[0])
        doc.xref_set_key(res_xref, f"Font/{font_name}", f"{font_xref} 0 R")
    else:
        # Resources is a direct dict — try setting through the page
        # Create an indirect Resources if needed
        doc.xref_set_key(
            page_xref, f"Resources/Font/{font_name}", f"{font_xref} 0 R"
        )


def _inject_into_content_streams(
    doc: fitz.Document,
    insertions: list[_InvisInsertion],
    mapping: FontMapping,
) -> None:
    """
    Rewrite content streams across all pages using the unified CID font.

    ALL content streams are re-encoded (visible chars converted from 1-byte
    to 2-byte CID hex) so the entire PDF uses the unified font.  Invisible
    chars are injected inline in the same font — no font switching.
    """
    # Group insertions by visible-char index
    insertions_by_idx: dict[int, list[str]] = {}
    for ins in insertions:
        insertions_by_idx.setdefault(ins.after_visible_idx, []).append(ins.char)

    # First pass: count total chars across all content streams so we can
    # clamp out-of-range insertions to the last valid index.
    total_stream_chars = 0
    page_stream_info: list[list[tuple[int, int, dict[str, int]]]] = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        font_bpc = _detect_bytes_per_char(doc, page)
        page_streams: list[tuple[int, int, dict[str, int]]] = []

        contents = page.get_contents()
        for cx in contents:
            stream = doc.xref_stream(cx)
            if not stream:
                page_streams.append((cx, 0, font_bpc))
                continue

            stream_text = stream.decode("latin-1")
            char_count = 0
            temp_font = ""
            for m_op in sorted(
                list(_FONT_TF_RE.finditer(stream_text))
                + list(_HEX_TJ_RE.finditer(stream_text)),
                key=lambda x: x.start(),
            ):
                if _FONT_TF_RE.fullmatch(m_op.group(0)):
                    temp_font = m_op.group(1)
                else:
                    bpc = font_bpc.get(temp_font, 1)
                    for hm in _HEX_STRING_RE.finditer(m_op.group(0)):
                        char_count += _count_chars_in_hex(hm.group(1), bpc)

            page_streams.append((cx, char_count, font_bpc))
            total_stream_chars += char_count

        page_stream_info.append(page_streams)

    # TEAM_158: Clamp out-of-range insertions to the last valid char index.
    if total_stream_chars > 0 and insertions_by_idx:
        last_valid = total_stream_chars - 1
        clamped: dict[int, list[str]] = {}
        for idx, chars in insertions_by_idx.items():
            clamped_idx = min(idx, last_valid)
            clamped.setdefault(clamped_idx, []).extend(chars)
        insertions_by_idx = clamped

    # Second pass: inject invisible chars via font-switching
    global_char_offset = 0
    for page_num, page_streams in enumerate(page_stream_info):
        for cx, char_count, font_bpc in page_streams:
            if char_count == 0:
                continue

            stream_start = global_char_offset
            stream_end = global_char_offset + char_count - 1

            # Collect insertions relevant to this stream (local indices)
            relevant: dict[int, list[str]] = {}
            for idx, chars in insertions_by_idx.items():
                if stream_start <= idx <= stream_end:
                    relevant[idx - stream_start] = chars

            # Only touch streams that have insertions — original content
            # is left completely intact (font-switching approach).
            if relevant:
                stream = doc.xref_stream(cx)
                new_stream = _rewrite_content_stream(
                    stream,
                    relevant,
                    font_bpc,
                    mapping,
                    _UNIFIED_FONT_NAME,
                )
                doc.update_stream(cx, new_stream)

            global_char_offset += char_count


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
    3. Embed a custom CID font and rewrite content streams to inject
       invisible characters (VS/ZW) inline within Tj/TJ operators.
    4. Inject the ``EncypherSignedText`` metadata stream into the catalog.

    The original visual appearance is completely preserved — only invisible
    characters and a metadata stream are added.  The inline injection
    ensures copy-paste from any PDF viewer preserves the invisible chars
    in the correct positions relative to visible text.

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

    # 4. Inject invisible chars + metadata stream into the PDF.
    #
    # TEAM_158: Only rewrite content streams for VS/ZW embedding modes
    # where invisible chars must survive copy-paste.  C2PA manifest modes
    # (full, lightweight_uuid, minimal_uuid, hybrid) embed thousands of
    # invisible chars that would make the PDF unreadable if injected into
    # content streams — those modes only get the metadata stream.
    from xml_to_pdf.signer import EMBEDDING_MODES

    mode_cfg = EMBEDDING_MODES.get(mode, {})
    manifest_mode = mode_cfg.get("manifest_mode", "")
    _CONTENT_STREAM_MODES = {"zw_embedding", "vs256_embedding", "vs256_rs_embedding"}
    needs_content_rewrite = manifest_mode in _CONTENT_STREAM_MODES

    doc = fitz.open(pdf_path)
    try:
        if needs_content_rewrite:
            # Find where invisible chars were inserted by the signing API
            insertions = _diff_for_insertions(text, result.signed_text)

            # TEAM_158: Redistribute VS chars so each base glyph gets at most
            # 1 invisible char.  This prevents poppler from deduplicating
            # repeated VS codepoints that follow the same base character.
            total_visible = sum(
                1 for c in text if c not in ("\n", "\r") and not _is_invisible(ord(c))
            )
            insertions = _redistribute_insertions(insertions, total_visible)

            # Build invisible-only CID font (no visible glyphs needed —
            # we use font-switching and leave original fonts untouched)
            assets = _get_font_assets()

            # Embed the invisible CID font
            font_xref = _embed_invisible_font(doc, assets)

            # Register invisible font on every page
            for page_num in range(doc.page_count):
                _register_font_on_page(
                    doc, doc[page_num], _UNIFIED_FONT_NAME, font_xref
                )

            # Inject invisible chars via font-switching (original streams intact)
            _inject_into_content_streams(doc, insertions, assets.mapping)

        # Add EncypherSignedText metadata stream (always — all modes)
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
