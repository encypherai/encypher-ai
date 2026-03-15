# encypher-pdf

Unicode-faithful PDF writer that preserves **all** Unicode characters in PDF text streams — including variation selectors (U+FE00–FE0F), supplementary variation selectors (U+E0100–U+E01EF), and zero-width characters (U+200B, U+200C, U+200D, U+FEFF) — so they survive **copy-paste** from PDF viewers.

## Why

Standard PDF libraries (ReportLab, fpdf2, PyMuPDF) drop Unicode variation selectors and zero-width characters because standard fonts lack glyphs for them. EncypherAI's invisible provenance embedding relies on these characters persisting through the full round-trip: **sign → PDF → copy-paste → verify**.

## How it works

1. Uses **Identity-H CID encoding** with deterministic Unicode-to-glyph mapping
2. Injects synthetic zero-width glyphs for invisible provenance codepoints into embedded fonts
3. Builds a **ToUnicode CMap** so viewers and extractors recover the intended Unicode sequence
4. Uses tiny non-zero widths for invisible glyphs where extractor compatibility requires it
5. Stores the original signed text in an **`EncypherSignedText`** metadata stream for exact recovery
6. Supports curated font-family resolution for Roboto-like, Arial-like, and Times-like output

## Usage

```python
from encypher_pdf import Document, TextStyle

doc = Document()
doc.add_text("My Document Title", TextStyle(font_size=18, font_family="roboto", bold=True))
doc.add_text(
    "Body text with invisible chars: Hello\ufe01 World\ufe02 and A\u200bB",
    TextStyle(font_family="times", font_size=11),
)
doc.set_signed_text("My Document Title\n\nBody text with invisible chars: Hello\ufe01 World\ufe02 and A\u200bB")
doc.save("output.pdf")
```

## Public API

- `Document`
- `TextStyle`
- `extract_text()`
- `extract_signed_text()`
- `inspect_pdf()`
- `list_supported_font_families()`
- `resolve_font_path()`

## CLI

The package exposes an `encypher-pdf` CLI with the following commands:

- `generate`
- `extract`
- `inspect`
- `verify`

Example:

```bash
encypher-pdf generate input.txt output.pdf --title "Sample" --font-family times
encypher-pdf inspect output.pdf --pretty
encypher-pdf extract output.pdf --signed-only
encypher-pdf verify output.pdf input.txt
```

## Supported font families

- `roboto`
- `arial`
- `times`
- `liberation_sans`
- `liberation_serif`
- `dejavu_sans`
- `dejavu_serif`

These families resolve to available system fonts with deterministic fallback behavior.

## Examples

Sample editorial PDFs can be generated with:

```bash
PYTHONPATH=src ./.venv/bin/python examples/generate_sample_pdfs.py
```

This writes example outputs to `examples/output/` including Roboto-like, Arial-like, and Times-like document styles.

## Browser verification harness

A lightweight browser harness is available under `browser/`:

- `viewer.html`
- `verify_pdf_clipboard.mjs`
- `compare_render.mjs`

This supports browser-side rendering checks, text/codepoint inspection, screenshot capture, and visual diff workflows for generated PDFs.

## Installation

```bash
uv add encypher-pdf --path /path/to/encypher-pdf
```

## Development

```bash
uv sync --all-extras
uv run pytest
```
