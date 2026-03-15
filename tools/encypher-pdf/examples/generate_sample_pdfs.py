from __future__ import annotations

from pathlib import Path

from encypher_pdf.writer import (
    STYLE_ABSTRACT,
    STYLE_BODY,
    STYLE_HEADING,
    STYLE_REFERENCE,
    STYLE_SUBTITLE,
    STYLE_TITLE,
    Alignment,
    Document,
    TextStyle,
)

OUT_DIR = Path(__file__).resolve().parent / "output"


def build_word_style_document(font_family: str, filename: str) -> Path:
    doc = Document(footer_text="Encypher PDF sample")

    title_style = TextStyle(
        font_size=18,
        font_family=font_family,
        line_height=1.2,
        alignment=Alignment.CENTER,
        bold=True,
        space_after=6,
    )
    subtitle_style = TextStyle(
        font_size=11,
        font_family=font_family,
        line_height=1.3,
        alignment=Alignment.CENTER,
        space_after=10,
    )
    heading_style = TextStyle(
        font_size=13,
        font_family=font_family,
        line_height=1.2,
        bold=True,
        space_before=14,
        space_after=6,
    )
    body_style = TextStyle(
        font_size=11,
        font_family=font_family,
        line_height=1.45,
        alignment=Alignment.JUSTIFY,
        space_after=8,
        first_line_indent=22,
    )
    abstract_style = TextStyle(
        font_size=9.5,
        font_family=font_family,
        line_height=1.35,
        alignment=Alignment.JUSTIFY,
        left_indent=36,
        right_indent=36,
        space_after=8,
    )
    ref_style = TextStyle(
        font_size=8.5,
        font_family=font_family,
        line_height=1.25,
        left_indent=18,
        first_line_indent=-18,
        space_after=4,
    )

    doc.add_text("A Visually Normal Editorial PDF", title_style)
    doc.add_text("Generated with provenance-preserving Unicode text output", subtitle_style)
    doc.add_text(
        "This sample demonstrates a conventional document layout with typographic hierarchy, paragraph spacing, and body text that should feel familiar to anyone used to Microsoft Word, Google Docs, or Apple Pages.",
        abstract_style,
    )

    doc.add_text("1. Introduction", heading_style)
    doc.add_text(
        "Publishing-grade PDFs must do two things at once: preserve the visual expectations of a normal editor-produced document and retain the exact text semantics needed for downstream verification. In this document, invisible provenance markers are embedded after selected characters, such as in the phrase Hello\ufe01 World and in the zero-width pair A\u200bB, while the visual appearance remains normal.",
        body_style,
    )
    doc.add_text(
        "The line spacing, margins, paragraph rhythm, and typography are deliberately conservative so the output resembles a default word-processing export rather than a developer-centric diagnostic artifact.",
        body_style,
    )

    doc.add_text("2. Body Layout", heading_style)
    doc.add_text(
        "Headings use a modest size increase and bold weight. Body text is readable, justified, and indented at the first line. The footer is centered and muted. These choices are typical of editorial and enterprise report PDFs. The font family can be swapped between sans and serif stacks such as Roboto, Arial-like, and Times-like rendering paths.",
        body_style,
    )
    doc.add_text(
        "Because invisible provenance characters are represented through a custom CID font strategy with ToUnicode mapping, copy-paste fidelity can coexist with aesthetically pleasing layout. The underlying extraction path should preserve the embedded markers even though they remain visually absent.",
        body_style,
    )

    doc.add_text("References", heading_style)
    doc.add_text("[1] EncypherAI. Unicode-faithful PDF generation architecture.", ref_style)
    doc.add_text("[2] ISO 32000 / Adobe PDF text extraction guidance.", ref_style)
    doc.add_text("[3] C2PA text provenance working materials.", ref_style)

    signed_text = (
        "A Visually Normal Editorial PDF\n\n"
        "Generated with provenance-preserving Unicode text output\n\n"
        "This sample demonstrates a conventional document layout with typographic hierarchy, paragraph spacing, and body text that should feel familiar to anyone used to Microsoft Word, Google Docs, or Apple Pages.\n\n"
        "Publishing-grade PDFs must do two things at once: preserve the visual expectations of a normal editor-produced document and retain the exact text semantics needed for downstream verification. Hello\ufe01 World. A\u200bB."
    )
    doc.set_signed_text(signed_text)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / filename
    doc.save(str(output_path))
    return output_path


def main() -> None:
    outputs = [
        build_word_style_document("roboto", "sample_roboto.pdf"),
        build_word_style_document("arial", "sample_arial.pdf"),
        build_word_style_document("times", "sample_times.pdf"),
    ]
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
