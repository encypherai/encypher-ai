# TEAM_154: Font preparation with synthetic invisible glyphs
"""
Prepares TTF fonts for PDF embedding by:
  1. Injecting synthetic zero-width glyphs for invisible Unicode characters
     (variation selectors, zero-width chars) into the font's cmap and glyf tables.
  2. Extracting font metrics needed for PDF layout and embedding.

Each invisible codepoint gets a unique glyph (unique GID) so the ToUnicode
CMap can map each GID back to its specific Unicode codepoint for copy-paste.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph


# All invisible codepoints we need to preserve in PDFs
INVISIBLE_CODEPOINTS: set[int] = set()
# BMP variation selectors (U+FE00–FE0F)
INVISIBLE_CODEPOINTS.update(range(0xFE00, 0xFE10))
# Supplementary variation selectors (U+E0100–E01EF) — used by C2PA VS256 encoding
INVISIBLE_CODEPOINTS.update(range(0xE0100, 0xE01F0))
# Zero-width characters
INVISIBLE_CODEPOINTS.update({0x200B, 0x200C, 0x200D, 0xFEFF, 0x200E, 0x200F})
# ZW embedding base-4 chars (Word-compatible)
INVISIBLE_CODEPOINTS.add(0x034F)  # CGJ - Combining Grapheme Joiner
INVISIBLE_CODEPOINTS.add(0x180E)  # MVS - Mongolian Vowel Separator
# Soft hyphen
INVISIBLE_CODEPOINTS.add(0x00AD)
# TEAM_156: Newline — must survive in PDF text stream for C2PA hash fidelity.
# Rendered as zero-width glyph so it's invisible but preserved during copy-paste.
INVISIBLE_CODEPOINTS.add(0x000A)  # LF


def prepare_font_with_invisible_glyphs(
    font_bytes: bytes,
    invisible_codepoints: set[int] | None = None,
) -> bytes:
    """
    Inject synthetic zero-width glyphs into a TTF font for invisible codepoints.

    For each invisible codepoint, creates a unique glyph name (e.g., 'uniFE01'),
    adds an empty glyph outline with zero advance width, and maps the codepoint
    to this glyph in the font's cmap tables (format 4).

    Returns the modified font bytes.
    """
    if invisible_codepoints is None:
        invisible_codepoints = INVISIBLE_CODEPOINTS

    font = TTFont(BytesIO(font_bytes))
    glyf_table = font["glyf"]
    hmtx = font["hmtx"]
    glyph_order = list(font.getGlyphOrder())
    empty_glyph = Glyph()

    bmp_cps: list[int] = []
    supp_cps: list[int] = []
    for cp in sorted(invisible_codepoints):
        glyph_name = f"uni{cp:04X}"
        if glyph_name not in glyph_order:
            glyph_order.append(glyph_name)
            glyf_table[glyph_name] = empty_glyph
            hmtx.metrics[glyph_name] = (0, 0)

        if cp <= 0xFFFF:
            bmp_cps.append(cp)
        else:
            supp_cps.append(cp)

    # Add BMP codepoints to format 4 cmap subtables
    for cp in bmp_cps:
        glyph_name = f"uni{cp:04X}"
        for table in font["cmap"].tables:
            if hasattr(table, "cmap") and table.format == 4:
                table.cmap[cp] = glyph_name

    # Add supplementary codepoints to format 12 cmap subtable
    if supp_cps:
        fmt12 = None
        for table in font["cmap"].tables:
            if hasattr(table, "cmap") and table.format == 12:
                fmt12 = table
                break
        if fmt12 is None:
            from fontTools.ttLib.tables._c_m_a_p import cmap_format_12

            fmt12 = cmap_format_12(12)
            fmt12.platEncID = 10  # UCS-4 — getBestCmap prefers this over platEncID=3
            fmt12.platformID = 3
            fmt12.format = 12
            fmt12.reserved = 0
            fmt12.length = 0
            fmt12.language = 0
            fmt12.groups = []
            fmt12.cmap = {}
            # Copy existing BMP mappings so the format 12 table is complete
            best = font.getBestCmap()
            if best:
                fmt12.cmap.update(best)
            font["cmap"].tables.append(fmt12)
        for cp in supp_cps:
            fmt12.cmap[cp] = f"uni{cp:04X}"

    font.setGlyphOrder(glyph_order)

    out = BytesIO()
    font.save(out)
    font.close()
    return out.getvalue()


def get_font_metrics(font_bytes: bytes) -> dict[str, Any]:
    """
    Extract metrics from a TTF font needed for PDF embedding.

    Returns dict with:
        ps_name: PostScript name
        units_per_em: design units per em
        ascent, descent, cap_height, bbox, italic_angle, stem_v
        default_width: default glyph width
        widths: dict[gid -> width] for all glyphs
        cmap: dict[unicode_codepoint -> gid] mapping
    """
    font = TTFont(BytesIO(font_bytes))

    # PostScript name
    ps_name = "UnknownFont"
    for record in font["name"].names:
        if record.nameID == 6:
            ps_name = record.toUnicode()
            break
    ps_name = ps_name.replace(" ", "")

    head = font["head"]
    os2 = font.get("OS/2")
    hhea = font["hhea"]
    hmtx = font["hmtx"]

    units_per_em = head.unitsPerEm
    bbox = [head.xMin, head.yMin, head.xMax, head.yMax]
    ascent = hhea.ascent
    descent = hhea.descent
    cap_height = os2.sCapHeight if os2 and hasattr(os2, "sCapHeight") else int(ascent * 0.7)
    italic_angle = font["post"].italicAngle if "post" in font else 0
    stem_v = 80

    # Glyph widths
    widths: dict[int, int] = {}
    glyph_order = font.getGlyphOrder()
    for i, glyph_name in enumerate(glyph_order):
        if glyph_name in hmtx.metrics:
            advance_width, _lsb = hmtx.metrics[glyph_name]
            widths[i] = advance_width

    default_width = widths.get(0, 600)

    # Unicode -> GID cmap
    cmap: dict[int, int] = {}
    cmap_table = font.getBestCmap()
    if cmap_table:
        for cp, glyph_name in cmap_table.items():
            gid = font.getGlyphID(glyph_name)
            cmap[cp] = gid

    font.close()

    return {
        "ps_name": ps_name,
        "units_per_em": units_per_em,
        "ascent": ascent,
        "descent": descent,
        "cap_height": cap_height,
        "bbox": bbox,
        "italic_angle": italic_angle,
        "stem_v": stem_v,
        "default_width": default_width,
        "widths": widths,
        "cmap": cmap,
    }
