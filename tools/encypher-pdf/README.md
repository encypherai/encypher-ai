# encypher-pdf

Unicode-faithful PDF writer that preserves **all** Unicode characters in PDF text streams — including variation selectors (U+FE00–FE0F), supplementary variation selectors (U+E0100–E01EF), and zero-width characters (U+200B, U+200C, U+200D, U+FEFF) — so they survive **copy-paste** from PDF viewers.

## Why

Standard PDF libraries (ReportLab, fpdf2, PyMuPDF) drop Unicode variation selectors and zero-width characters because standard fonts lack glyphs for them. EncypherAI's invisible provenance embedding relies on these characters persisting through the full round-trip: **sign → PDF → copy-paste → verify**.

## How it works

1. Uses **Identity-H CID encoding** where CID values equal Unicode codepoints
2. Writes raw **UTF-16BE hex** directly into PDF `Tj` text operators
3. Builds a **ToUnicode CMap** with identity mapping for all used codepoints
4. Embeds a **TTF font subset** for visible glyphs; invisible chars map to GID 0 (`.notdef`, zero-width)
5. The **CIDToGIDMap** explicitly sets width 0 for invisible codepoints

## Usage

```python
from encypher_pdf import Document, TextStyle, STYLE_BODY, STYLE_TITLE

doc = Document()
doc.add_text("My Document Title", STYLE_TITLE)
doc.add_text("Body text with invisible chars: Hello\ufe01 World\ufe02", STYLE_BODY)
doc.save("output.pdf")
```

## Installation

```bash
uv add encypher-pdf --path /path/to/encypher-pdf
```

## Development

```bash
cd tools/encypher-pdf
uv sync --all-extras
uv run pytest
```
