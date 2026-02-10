# TEAM_154: PDF renderer using encypher-pdf for Unicode-faithful output
"""
Render a Paper dataclass to a styled PDF using encypher-pdf.

When signed_text is provided, the full signed content (including invisible
provenance characters) is rendered directly into the PDF text stream using
encypher-pdf's Identity-H CID encoding. This ensures variation selectors
and zero-width characters survive PDF generation and can be extracted by
pdfjs-dist for verification.
"""

from __future__ import annotations

from pathlib import Path

from encypher_pdf import Document
from encypher_pdf.writer import (
    STYLE_BODY,
    STYLE_TITLE,
    STYLE_HEADING,
    STYLE_ABSTRACT,
    TextStyle,
    Alignment,
)

from xml_to_pdf.parser import Paper


# Custom styles matching the research paper layout
STYLE_AUTHORS = TextStyle(
    font_size=11,
    line_height=1.3,
    space_after=4,
    alignment=Alignment.CENTER,
)

STYLE_AFFILIATION = TextStyle(
    font_size=9,
    line_height=1.2,
    space_after=16,
    alignment=Alignment.CENTER,
    color=(0.4, 0.4, 0.4),
)

STYLE_BADGE = TextStyle(
    font_size=8,
    line_height=1.25,
    space_after=12,
    alignment=Alignment.CENTER,
    color=(0.145, 0.388, 0.922),
)

STYLE_ABSTRACT_HEADING = TextStyle(
    font_size=10,
    line_height=1.2,
    space_after=4,
    bold=True,
)

STYLE_PAPER_ABSTRACT = TextStyle(
    font_size=9,
    line_height=1.3,
    space_after=6,
    left_indent=36,
    right_indent=36,
)

STYLE_KEYWORDS = TextStyle(
    font_size=9,
    line_height=1.2,
    space_after=20,
    left_indent=36,
    right_indent=36,
)

STYLE_SECTION = TextStyle(
    font_size=13,
    line_height=1.2,
    space_before=14,
    space_after=6,
    bold=True,
)

STYLE_SUBSECTION = TextStyle(
    font_size=11,
    line_height=1.3,
    space_before=10,
    space_after=4,
    bold=True,
    italic=True,
)

STYLE_PAPER_BODY = TextStyle(
    font_size=10,
    line_height=1.3,
    space_after=6,
    first_line_indent=18,
)

STYLE_REFERENCE = TextStyle(
    font_size=8,
    line_height=1.25,
    space_after=3,
    left_indent=18,
)

STYLE_META = TextStyle(
    font_size=8,
    line_height=1.3,
    space_after=4,
    left_indent=36,
    right_indent=36,
)


def _build_style_map(paper: Paper) -> list[TextStyle]:
    """Build a list of styles matching the paragraph order of ``paper.plain_text()``.

    TEAM_156: ``plain_text()`` joins parts with ``"\\n\\n"``, producing a
    deterministic sequence of paragraphs.  This function mirrors that
    sequence so we can apply the correct visual style to each paragraph
    of the signed text while keeping the content byte-identical.
    """
    styles: list[TextStyle] = []

    # Frontmatter: title, "", authors, "", abstract, ""
    styles.append(STYLE_TITLE)       # title
    styles.append(STYLE_PAPER_BODY)  # "" (empty separator)
    styles.append(STYLE_AUTHORS)     # authors
    styles.append(STYLE_PAPER_BODY)  # "" (empty separator)
    styles.append(STYLE_PAPER_ABSTRACT)  # abstract
    styles.append(STYLE_PAPER_BODY)  # "" (empty separator)

    # Body sections
    for section in paper.sections:
        styles.append(STYLE_SECTION)  # section heading
        for _para in section.paragraphs:
            styles.append(STYLE_PAPER_BODY)  # body paragraph
        for sub in section.subsections:
            styles.append(STYLE_SUBSECTION)  # subsection heading
            for _para in sub.paragraphs:
                styles.append(STYLE_PAPER_BODY)  # body paragraph
        styles.append(STYLE_PAPER_BODY)  # "" (empty separator after section)

    # References
    if paper.references:
        styles.append(STYLE_SECTION)  # "References" heading
        for _ref in paper.references:
            styles.append(STYLE_REFERENCE)  # reference text

    return styles


def render_pdf(
    paper: Paper,
    output_path: str,
    signed_text: str | None = None,
    provenance_mode: str | None = None,
    provenance_meta: dict | None = None,
) -> str:
    """
    Render a Paper to PDF using encypher-pdf.

    If signed_text is provided, it is rendered directly into the PDF text
    stream with full Unicode fidelity, preserving invisible provenance
    characters (variation selectors, zero-width chars).

    Returns the output file path.
    """
    # TEAM_156: Skip footer when signed_text is provided — the footer text
    # would be extracted by the PDF text extractor and break the C2PA hash.
    footer = None
    if provenance_mode and not signed_text:
        footer = f"Provenance: {provenance_mode}"

    doc = Document(footer_text=footer)

    if signed_text:
        # TEAM_156: Render signed text with proper visual formatting.
        # The signed text is split by "\n\n" (matching plain_text() output),
        # and each paragraph gets the style from the Paper structure.
        # The "\n\n" separators are re-attached so they survive as zero-width
        # glyphs in the PDF text stream — required for C2PA hash fidelity.
        style_map = _build_style_map(paper)
        parts = signed_text.split("\n\n")
        for i, part in enumerate(parts):
            text_to_render = part + "\n\n" if i < len(parts) - 1 else part
            style = style_map[i] if i < len(style_map) else STYLE_PAPER_BODY
            if text_to_render:
                doc.add_text(text_to_render, style)
        doc.set_signed_text(signed_text)
    else:
        # Unsigned rendering — use the paper structure directly
        for section in paper.sections:
            doc.add_text(section.heading, STYLE_SECTION)
            for para in section.paragraphs:
                doc.add_text(para, STYLE_PAPER_BODY)

            for sub in section.subsections:
                doc.add_text(sub.heading, STYLE_SUBSECTION)
                for para in sub.paragraphs:
                    doc.add_text(para, STYLE_PAPER_BODY)

        # --- References ---
        if paper.references:
            doc.add_spacer(12)
            doc.add_text("References", STYLE_SECTION)
            for i, ref in enumerate(paper.references, 1):
                doc.add_text(f"[{i}] {ref.text}", STYLE_REFERENCE)

    # --- Provenance metadata ---
    # TEAM_156: Skip provenance metadata when signed_text is provided.
    # Any extra text appended after the signed content would be extracted
    # by the PDF text extractor and break the C2PA hard-binding hash.
    if provenance_meta and not signed_text:
        doc.add_spacer(20)
        doc.add_text("Provenance Record", STYLE_SECTION)
        for key, value in provenance_meta.items():
            display_val = str(value)
            if len(display_val) > 120:
                display_val = display_val[:120] + "..."
            doc.add_text(f"{key}: {display_val}", STYLE_META)

    # --- Save ---
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output))

    return str(output)
