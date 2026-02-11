# TEAM_154: High-level PDF document writer with Unicode-faithful text
"""
Document/Page/TextStyle API for building PDFs that preserve all Unicode
characters — including variation selectors and zero-width chars — in the
PDF text stream so they survive copy-paste.

Architecture:
  1. Collect all text content and compute layout (word wrap, pagination)
  2. Gather every Unicode codepoint used across the document
  3. Embed the TTF font with Identity-H encoding (CID = codepoint)
  4. Write content streams using raw UTF-16BE hex in TJ operators
  5. Build ToUnicode CMap so extractors/copy-paste get correct Unicode
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from encypher_pdf.font import embed_font, FontMapping
from encypher_pdf.fonttools_subset import get_font_metrics
from encypher_pdf.pdf_objects import PdfStream, PdfWriter


# Default system fonts to search for
_FONT_SEARCH_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]


def _find_system_font(bold: bool = False, italic: bool = False) -> str:
    """Find a suitable system TTF font."""
    # Try specific variants first
    for path in _FONT_SEARCH_PATHS:
        if not os.path.exists(path):
            continue
        name = os.path.basename(path).lower()
        is_bold = "bold" in name
        is_italic = "italic" in name or "oblique" in name
        if is_bold == bold and is_italic == italic:
            return path

    # Fallback: any TTF font
    for path in _FONT_SEARCH_PATHS:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        "No suitable TTF font found. Install liberation-fonts or freefont-freefont."
    )


class Alignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclass
class TextStyle:
    """Style for a text block."""

    font_size: float = 10.0
    line_height: float = 1.3
    alignment: Alignment = Alignment.LEFT
    bold: bool = False
    italic: bool = False
    color: tuple[float, float, float] = (0.0, 0.0, 0.0)  # RGB 0-1
    space_before: float = 0.0
    space_after: float = 6.0
    left_indent: float = 0.0
    right_indent: float = 0.0
    first_line_indent: float = 0.0
    font_path: Optional[str] = None


# Predefined styles
STYLE_TITLE = TextStyle(font_size=18, line_height=1.2, alignment=Alignment.CENTER, bold=True, space_after=6)
STYLE_SUBTITLE = TextStyle(font_size=11, line_height=1.3, alignment=Alignment.CENTER, space_after=4)
STYLE_HEADING = TextStyle(font_size=13, line_height=1.2, bold=True, space_before=14, space_after=6)
STYLE_SUBHEADING = TextStyle(font_size=11, line_height=1.2, bold=True, italic=True, space_before=10, space_after=4)
STYLE_BODY = TextStyle(font_size=10, line_height=1.3, alignment=Alignment.JUSTIFY, space_after=6, first_line_indent=18)
STYLE_BODY_NO_INDENT = TextStyle(font_size=10, line_height=1.3, alignment=Alignment.JUSTIFY, space_after=6)
STYLE_ABSTRACT = TextStyle(font_size=9, line_height=1.3, alignment=Alignment.JUSTIFY, left_indent=36, right_indent=36, space_after=6)
STYLE_SMALL = TextStyle(font_size=8, line_height=1.2, space_after=3)
STYLE_BADGE = TextStyle(font_size=8, line_height=1.2, alignment=Alignment.CENTER, color=(0.145, 0.388, 0.922), space_after=12)
STYLE_REFERENCE = TextStyle(font_size=8, line_height=1.2, left_indent=18, first_line_indent=-18, space_after=3)


# Characters that are invisible / zero-width
_INVISIBLE_CODEPOINTS = set()
# Variation selectors
_INVISIBLE_CODEPOINTS.update(range(0xFE00, 0xFE10))
# Supplementary variation selectors
_INVISIBLE_CODEPOINTS.update(range(0xE0100, 0xE01F0))
# Zero-width chars
_INVISIBLE_CODEPOINTS.update({0x200B, 0x200C, 0x200D, 0xFEFF, 0x200E, 0x200F})
# ZW embedding base-4 chars
_INVISIBLE_CODEPOINTS.add(0x034F)  # CGJ
_INVISIBLE_CODEPOINTS.add(0x180E)  # MVS
# Soft hyphen
_INVISIBLE_CODEPOINTS.add(0x00AD)
# TEAM_156: Newline — preserved as zero-width glyph for C2PA hash fidelity
_INVISIBLE_CODEPOINTS.add(0x000A)  # LF


def _is_invisible(cp: int) -> bool:
    """Check if a codepoint is invisible/zero-width."""
    return cp in _INVISIBLE_CODEPOINTS


@dataclass
class _TextBlock:
    """Internal: a block of text with a style."""

    text: str
    style: TextStyle


@dataclass
class _Spacer:
    """Internal: vertical space."""

    height: float


_StoryItem = _TextBlock | _Spacer


@dataclass
class Page:
    """Represents a single page with its content stream operations."""

    width: float
    height: float
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float

    @property
    def content_width(self) -> float:
        return self.width - self.margin_left - self.margin_right

    @property
    def content_top(self) -> float:
        return self.height - self.margin_top

    @property
    def content_bottom(self) -> float:
        return self.margin_bottom


class Document:
    """
    High-level PDF document builder.

    Usage:
        doc = Document()
        doc.add_text("Title", STYLE_TITLE)
        doc.add_text("Body paragraph...", STYLE_BODY)
        doc.save("output.pdf")
    """

    def __init__(
        self,
        *,
        page_width: float = 612,  # US Letter
        page_height: float = 792,
        margin: float = 54,  # 0.75 inch
        margin_top: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_right: Optional[float] = None,
        footer_text: Optional[str] = None,
    ) -> None:
        self._page_width = page_width
        self._page_height = page_height
        self._margin_top = margin_top or margin
        self._margin_bottom = margin_bottom or margin
        self._margin_left = margin_left or margin
        self._margin_right = margin_right or margin
        self._footer_text = footer_text
        self._story: list[_StoryItem] = []
        self._signed_text: Optional[str] = None

    def set_signed_text(self, text: str) -> None:
        """Store the original signed text for lossless round-trip extraction.

        TEAM_156: PDF text streams are lossy — paragraph separators (\\n\\n)
        are lost during rendering and cannot be perfectly reconstructed from
        Y-position heuristics.  Storing the original text in a compressed
        metadata stream guarantees byte-identical extraction, which is
        required for C2PA hard-binding hash verification.
        """
        self._signed_text = text

    def add_text(self, text: str, style: Optional[TextStyle] = None) -> None:
        """Add a text block to the document."""
        self._story.append(_TextBlock(text=text, style=style or TextStyle()))

    def add_spacer(self, height: float) -> None:
        """Add vertical space."""
        self._story.append(_Spacer(height=height))

    def save(self, path: str) -> None:
        """Render and save the PDF."""
        # Phase 1: Collect all codepoints and resolve fonts
        all_codepoints: set[int] = set()
        font_variants_needed: set[tuple[bool, bool]] = set()  # (bold, italic)

        for item in self._story:
            if isinstance(item, _TextBlock):
                for ch in item.text:
                    all_codepoints.add(ord(ch))
                font_variants_needed.add((item.style.bold, item.style.italic))

        if self._footer_text:
            for ch in self._footer_text:
                all_codepoints.add(ord(ch))

        # Always include basic ASCII + common punctuation
        for cp in range(0x20, 0x7F):
            all_codepoints.add(cp)

        # Phase 2: Build PDF structure
        writer = PdfWriter()

        # Reserve catalog and pages objects
        catalog_id = writer.reserve_id()  # 1
        pages_id = writer.reserve_id()  # 2

        # Phase 3: Embed fonts
        # font_map: (bold, italic) -> (obj_id, label, metrics, mapping)
        font_map: dict[tuple[bool, bool], tuple[int, str, dict, FontMapping]] = {}
        font_label_counter = 0

        for bold, italic in sorted(font_variants_needed):
            font_path = _find_system_font(bold=bold, italic=italic)
            font_obj_id, mapping = embed_font(writer, font_path, all_codepoints)
            font_label = f"F{font_label_counter}"
            font_label_counter += 1
            font_map[(bold, italic)] = (font_obj_id, font_label, mapping.metrics, mapping)

        # Also embed a regular font for footer
        if (False, False) not in font_map:
            font_path = _find_system_font(bold=False, italic=False)
            font_obj_id, mapping = embed_font(writer, font_path, all_codepoints)
            font_label = f"F{font_label_counter}"
            font_label_counter += 1
            font_map[(False, False)] = (font_obj_id, font_label, mapping.metrics, mapping)

        # Phase 4: Layout and pagination
        pages_content = self._layout(font_map)

        # Phase 5: Write page objects
        page_obj_ids: list[int] = []
        for page_idx, page_ops in enumerate(pages_content):
            # Build font resource dict for this page
            font_resources = " ".join(
                f"/{label} {writer.ref(obj_id)}"
                for (_, _), (obj_id, label, _, _) in font_map.items()
            )

            content_stream = "\n".join(page_ops).encode("latin-1")
            content_id = writer.add_stream(PdfStream(data=content_stream, compress=True))

            page_id = writer.add_object(
                f"<< /Type /Page"
                f" /Parent {writer.ref(pages_id)}"
                f" /MediaBox [0 0 {self._page_width} {self._page_height}]"
                f" /Contents {writer.ref(content_id)}"
                f" /Resources << /Font << {font_resources} >> >>"
                f" >>".encode()
            )
            page_obj_ids.append(page_id)

        # Set pages object
        kids = " ".join(writer.ref(pid) for pid in page_obj_ids)
        writer.set_object(
            pages_id,
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_obj_ids)} >>".encode(),
        )

        # TEAM_156: Embed original signed text as an UNCOMPRESSED metadata stream
        # so the extractor can retrieve it losslessly (PDF text streams lose
        # paragraph separators like \n\n during rendering/extraction).
        # Stored uncompressed so the browser extractor can read it with a
        # simple byte-range slice — no decompression library needed.
        if self._signed_text is not None:
            signed_bytes = self._signed_text.encode("utf-8")
            signed_stream = PdfStream(data=signed_bytes, compress=False)
            signed_stream_id = writer.add_stream(signed_stream)
            writer.set_object(
                catalog_id,
                f"<< /Type /Catalog /Pages {writer.ref(pages_id)}"
                f" /EncypherSignedText {writer.ref(signed_stream_id)} >>".encode(),
            )
        else:
            writer.set_object(catalog_id, f"<< /Type /Catalog /Pages {writer.ref(pages_id)} >>".encode())

        # Write file
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        writer.write(path)

    def _layout(
        self,
        font_map: dict[tuple[bool, bool], tuple[int, str, dict, FontMapping]],
    ) -> list[list[str]]:
        """
        Lay out all story items into pages, returning a list of
        PDF content stream operations per page.
        """
        page_width = self._page_width
        content_width = page_width - self._margin_left - self._margin_right
        content_top = self._page_height - self._margin_top
        content_bottom = self._margin_bottom

        pages: list[list[str]] = [[]]
        cursor_y = content_top

        def new_page() -> None:
            nonlocal cursor_y
            # Add footer to current page if needed
            if self._footer_text and pages[-1]:
                _add_footer(pages[-1])
            pages.append([])
            cursor_y = content_top

        def _add_footer(ops: list[str]) -> None:
            if not self._footer_text:
                return
            _, label, metrics, fmap = font_map[(False, False)]
            footer_size = 7
            footer_y = self._margin_bottom * 0.5
            footer_text_hex = _text_to_cid_hex(self._footer_text, fmap)
            text_width = _measure_text(self._footer_text, metrics, footer_size)
            footer_x = self._margin_left + (content_width - text_width) / 2
            ops.append("BT")
            ops.append(f"/{label} {footer_size} Tf")
            ops.append("0.6 0.6 0.6 rg")
            ops.append(f"{footer_x:.2f} {footer_y:.2f} Td")
            ops.append(f"<{footer_text_hex}> Tj")
            ops.append("ET")

        for item in self._story:
            if isinstance(item, _Spacer):
                cursor_y -= item.height
                if cursor_y < content_bottom:
                    new_page()
                continue

            block = item
            style = block.style
            _, font_label, metrics, fmap = font_map[(style.bold, style.italic)]

            effective_width = content_width - style.left_indent - style.right_indent
            leading = style.font_size * style.line_height

            # Apply space_before
            cursor_y -= style.space_before
            if cursor_y < content_bottom:
                new_page()

            # Word-wrap the text into lines
            lines = _wrap_text(block.text, metrics, style.font_size, effective_width, style.first_line_indent)

            for line_idx, line_text in enumerate(lines):
                if cursor_y - leading < content_bottom:
                    new_page()

                cursor_y -= leading

                # Calculate x position based on alignment
                line_width = _measure_text(line_text, metrics, style.font_size)
                x = self._margin_left + style.left_indent

                if line_idx == 0:
                    x += style.first_line_indent

                if style.alignment == Alignment.CENTER:
                    x = self._margin_left + (content_width - line_width) / 2
                elif style.alignment == Alignment.RIGHT:
                    x = self._margin_left + content_width - style.right_indent - line_width

                # Emit PDF text operators using TJ array to keep all
                # chunks in a single text-showing operation.  This avoids
                # micro-spacing that PDF viewers introduce between separate
                # Tj calls (each Tj resets internal rounding state).
                hex_chunks = _text_to_cid_hex_chunks(line_text, fmap)
                r, g, b = style.color
                ops = pages[-1]
                ops.append("BT")
                ops.append(f"/{font_label} {style.font_size} Tf")
                if (r, g, b) != (0, 0, 0):
                    ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
                ops.append(f"{x:.2f} {cursor_y:.2f} Td")
                if len(hex_chunks) == 1:
                    ops.append(f"<{hex_chunks[0]}> Tj")
                else:
                    tj_array = " ".join(f"<{c}>" for c in hex_chunks)
                    ops.append(f"[{tj_array}] TJ")
                ops.append("ET")

            # Apply space_after
            cursor_y -= style.space_after

        # Add footer to last page
        if self._footer_text and pages[-1]:
            _add_footer(pages[-1])

        return pages


def _text_to_hex(text: str) -> str:
    """
    Encode text as UTF-16BE hex string (raw Unicode codepoints).
    Used only for tests; production code uses _text_to_cid_hex.
    """
    encoded = text.encode("utf-16-be")
    return encoded.hex().upper()


def _text_to_cid_hex(text: str, mapping: FontMapping) -> str:
    """
    Encode text as compact CID hex string for PDF Tj operators.

    Converts each Unicode codepoint to its compact CID value using the
    FontMapping, then encodes as big-endian 16-bit hex. This is the
    critical function that preserves invisible characters — every codepoint
    gets a CID, and the ToUnicode CMap maps CIDs back to Unicode for
    copy-paste fidelity.
    """
    parts: list[str] = []
    for ch in text:
        cp = ord(ch)
        cid = mapping.unicode_to_gid.get(cp, 0)
        parts.append(f"{cid:04X}")
    return "".join(parts)


def _text_to_cid_hex_chunks(text: str, mapping: FontMapping) -> list[str]:
    """
    Encode text as a list of CID hex strings, splitting at invisible char
    boundaries so each Tj operation contains at most one zero-width glyph.

    MuPDF has a bug where it truncates text extraction when a Tj operation
    contains multiple zero-width glyphs. By isolating each invisible char
    into its own Tj, we ensure perfect round-trip extraction.
    """
    from encypher_pdf.fonttools_subset import INVISIBLE_CODEPOINTS

    chunks: list[str] = []
    current: list[str] = []

    for ch in text:
        cp = ord(ch)
        if cp in INVISIBLE_CODEPOINTS:
            # Flush visible chars accumulated so far
            if current:
                chunks.append("".join(current))
                current = []
            # Emit invisible char as its own chunk
            gid = mapping.unicode_to_gid.get(cp, 0)
            chunks.append(f"{gid:04X}")
        else:
            gid = mapping.unicode_to_gid.get(cp, 0)
            current.append(f"{gid:04X}")

    if current:
        chunks.append("".join(current))

    return chunks if chunks else [_text_to_cid_hex(text, mapping)]


def _measure_text(text: str, metrics: dict, font_size: float) -> float:
    """Measure the width of text in points, skipping invisible chars."""
    units_per_em = metrics["units_per_em"]
    cmap = metrics["cmap"]
    widths = metrics["widths"]
    default_width = metrics["default_width"]

    total_units = 0
    for ch in text:
        cp = ord(ch)
        if _is_invisible(cp):
            continue  # Zero width
        gid = cmap.get(cp, 0)
        w = widths.get(gid, default_width)
        total_units += w

    return total_units * font_size / units_per_em


def _wrap_text(
    text: str,
    metrics: dict,
    font_size: float,
    max_width: float,
    first_line_indent: float,
) -> list[str]:
    """
    Word-wrap text to fit within max_width.

    TEAM_156: Lossless round-trip guarantee — concatenating all returned
    lines reproduces the original *text* exactly.  Spaces are kept as
    trailing characters on the preceding token so they survive in the
    PDF text stream and can be extracted during copy-paste.
    """
    if not text.strip():
        return [text]

    # Split into tokens where each trailing space stays with its word.
    # e.g. "hello world foo" -> ["hello ", "world ", "foo"]
    tokens = _split_tokens_lossless(text)
    lines: list[str] = []
    current_tokens: list[str] = []
    current_width = 0.0
    line_max = max_width - first_line_indent

    for token in tokens:
        token_width = _measure_text(token, metrics, font_size)

        if current_tokens and current_width + token_width > line_max:
            lines.append("".join(current_tokens))
            current_tokens = [token]
            current_width = token_width
            line_max = max_width
        else:
            current_tokens.append(token)
            current_width += token_width

    if current_tokens:
        lines.append("".join(current_tokens))

    return lines if lines else [""]


def _split_tokens_lossless(text: str) -> list[str]:
    """
    Split text into tokens for word-wrapping while preserving every
    character.  Each visible space is kept as a trailing char on the
    preceding token so that ``"".join(tokens) == text`` always holds.

    Invisible characters stay attached to their adjacent visible chars.
    """
    tokens: list[str] = []
    current: list[str] = []

    for ch in text:
        cp = ord(ch)
        if ch == " " and not _is_invisible(cp):
            # Attach the space to the current token, then flush
            current.append(ch)
            tokens.append("".join(current))
            current = []
        else:
            current.append(ch)

    if current:
        tokens.append("".join(current))

    return tokens
