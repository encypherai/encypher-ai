# TEAM_154: Font embedding with full Unicode support
"""
Embeds a TrueType font into a PDF using Identity-H CID encoding.

Key design:
  - The font is pre-processed to inject synthetic zero-width glyphs for
    invisible Unicode characters (variation selectors, zero-width chars).
    Each invisible codepoint gets a unique GID in the font.
  - CIDToGIDMap /Identity is used (CID = GID), so the text stream contains
    GID values directly.
  - A ToUnicode CMap maps each GID back to its Unicode codepoint for
    copy-paste fidelity.
  - The FontMapping translates Unicode codepoints to GIDs for text encoding.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from encypher_pdf.fonttools_subset import (
    get_font_metrics,
    prepare_font_with_invisible_glyphs,
)
from encypher_pdf.pdf_objects import PdfStream, PdfWriter


@dataclass
class FontMapping:
    """Mapping between Unicode codepoints and font GIDs (used as CID values)."""

    unicode_to_gid: dict[int, int]
    gid_to_unicode: dict[int, int]
    max_gid: int
    metrics: dict


def build_font_mapping(
    used_codepoints: set[int],
    metrics: dict,
) -> FontMapping:
    """
    Build a mapping from Unicode codepoints to font GIDs.

    The font has already been prepared with synthetic glyphs for invisible
    chars, so every used codepoint (visible or invisible) has a real GID
    in the font's cmap table.
    """
    cmap_table = metrics["cmap"]
    unicode_to_gid: dict[int, int] = {}
    gid_to_unicode: dict[int, int] = {}

    for cp in sorted(used_codepoints):
        gid = cmap_table.get(cp, 0)
        unicode_to_gid[cp] = gid
        gid_to_unicode[gid] = cp

    max_gid = max(gid_to_unicode.keys()) if gid_to_unicode else 0

    return FontMapping(
        unicode_to_gid=unicode_to_gid,
        gid_to_unicode=gid_to_unicode,
        max_gid=max_gid,
        metrics=metrics,
    )


def build_tounicode_cmap(mapping: FontMapping) -> bytes:
    """
    Build a ToUnicode CMap that maps GID values to Unicode codepoints.
    This is what makes copy-paste work — PDF viewers use this to convert
    GIDs (= CIDs with Identity mapping) back to Unicode text.
    """
    lines: list[str] = [
        "/CIDInit /ProcSet findresource begin",
        "12 dict begin",
        "begincmap",
        "/CIDSystemInfo",
        "<< /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
        "/CMapName /Adobe-Identity-UCS def",
        "/CMapType 2 def",
        "1 begincodespacerange",
        f"<0000> <{mapping.max_gid + 1:04X}>",
        "endcodespacerange",
    ]

    entries = sorted(mapping.gid_to_unicode.items())
    for chunk_start in range(0, len(entries), 100):
        chunk = entries[chunk_start : chunk_start + 100]
        lines.append(f"{len(chunk)} beginbfchar")
        for gid, cp in chunk:
            if cp <= 0xFFFF:
                lines.append(f"<{gid:04X}> <{cp:04X}>")
            else:
                # Supplementary plane: encode as UTF-16 surrogate pair
                hi = 0xD800 + ((cp - 0x10000) >> 10)
                lo = 0xDC00 + ((cp - 0x10000) & 0x3FF)
                lines.append(f"<{gid:04X}> <{hi:04X}{lo:04X}>")
        lines.append("endbfchar")

    lines.extend(["endcmap", "CMapSpaceUsed", "end", "end"])
    return "\n".join(lines).encode("ascii")


def embed_font(
    writer: PdfWriter,
    font_path: str,
    used_codepoints: set[int],
) -> tuple[int, FontMapping]:
    """
    Embed a TTF font into the PDF with Identity-H encoding.

    Steps:
      1. Inject synthetic zero-width glyphs for invisible codepoints
      2. Extract metrics (including new GIDs for invisible chars)
      3. Build GID-based ToUnicode CMap
      4. Embed font with CIDToGIDMap /Identity

    Returns (font_object_id, font_mapping).
    """
    font_bytes_raw = Path(font_path).read_bytes()

    # Step 1: Inject invisible glyphs into the font
    font_bytes = prepare_font_with_invisible_glyphs(font_bytes_raw)

    # Step 2: Get metrics from the modified font (includes invisible GIDs)
    metrics = get_font_metrics(font_bytes)

    # Step 3: Build Unicode -> GID mapping
    mapping = build_font_mapping(used_codepoints, metrics)

    # Reserve object IDs
    type0_id = writer.reserve_id()
    cidfont_id = writer.reserve_id()
    descriptor_id = writer.reserve_id()
    fontfile_id = writer.reserve_id()
    tounicode_id = writer.reserve_id()

    # Font file stream
    font_stream = PdfStream(
        data=font_bytes,
        extra_dict={"Length1": str(len(font_bytes))},
        compress=True,
    )
    writer.set_object(fontfile_id, font_stream.serialize_dict_and_body())

    # ToUnicode CMap
    tounicode_data = build_tounicode_cmap(mapping)
    writer.set_object(
        tounicode_id,
        PdfStream(data=tounicode_data, compress=True).serialize_dict_and_body(),
    )

    # Font descriptor — values are in font design units (units_per_em)
    units_per_em = metrics.get("units_per_em", 1000)
    default_width = metrics.get("default_width", 600)
    bbox = metrics.get("bbox", [0, 0, 0, 0])
    bbox_str = f"[{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}]"

    descriptor_dict = (
        f"<< /Type /FontDescriptor"
        f" /FontName /{metrics['ps_name']}"
        f" /Flags 32"
        f" /FontBBox {bbox_str}"
        f" /ItalicAngle {metrics.get('italic_angle', 0)}"
        f" /Ascent {metrics.get('ascent', 800)}"
        f" /Descent {metrics.get('descent', -200)}"
        f" /CapHeight {metrics.get('cap_height', 700)}"
        f" /StemV {metrics.get('stem_v', 80)}"
        f" /FontFile2 {writer.ref(fontfile_id)}"
        f" >>"
    )
    writer.set_object(descriptor_id, descriptor_dict.encode())

    # TEAM_156: Build W array for ALL mapped GIDs.
    # PDF CIDFont W array widths must be in 1/1000 text-space units,
    # but the font's hmtx widths are in font design units (units_per_em,
    # typically 2048 for TrueType).  We scale each width to the 1000-unit
    # coordinate system so pdf.js and other viewers position glyphs correctly.
    #
    # Invisible chars get width 1 (not 0!) — pdfjs-dist filters out
    # zero-width glyphs during text extraction, so we use the smallest
    # non-zero width (1/1000 em ≈ 0.01pt at 10pt) to keep them
    # extractable while remaining visually invisible.
    from encypher_pdf.fonttools_subset import INVISIBLE_CODEPOINTS

    invisible_gids = {
        metrics["cmap"].get(cp)
        for cp in INVISIBLE_CODEPOINTS
        if cp in metrics["cmap"]
    }
    w_entries: list[str] = []
    widths = metrics["widths"]
    for gid in sorted(mapping.gid_to_unicode.keys()):
        if gid == 0:
            continue
        if gid in invisible_gids:
            w_entries.append(f"{gid} [1]")
        else:
            width = widths.get(gid, default_width)
            scaled = round(width * 1000 / units_per_em)
            w_entries.append(f"{gid} [{scaled}]")
    w_array = " ".join(w_entries)

    default_scaled = round(default_width * 1000 / units_per_em)
    # DW 1: fallback for any unmapped CIDs (tiny, non-zero)
    cidfont_dict = (
        f"<< /Type /Font"
        f" /Subtype /CIDFontType2"
        f" /BaseFont /{metrics['ps_name']}"
        f" /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >>"
        f" /FontDescriptor {writer.ref(descriptor_id)}"
        f" /DW {default_scaled}"
        f" /W [{w_array}]"
        f" /CIDToGIDMap /Identity"
        f" >>"
    )
    writer.set_object(cidfont_id, cidfont_dict.encode())

    # Type0 font
    type0_dict = (
        f"<< /Type /Font"
        f" /Subtype /Type0"
        f" /BaseFont /{metrics['ps_name']}"
        f" /Encoding /Identity-H"
        f" /DescendantFonts [{writer.ref(cidfont_id)}]"
        f" /ToUnicode {writer.ref(tounicode_id)}"
        f" >>"
    )
    writer.set_object(type0_id, type0_dict.encode())

    return type0_id, mapping
