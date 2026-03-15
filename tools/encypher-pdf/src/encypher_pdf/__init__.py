# TEAM_154: encypher-pdf — Unicode-faithful PDF writer
"""
PDF writer that preserves ALL Unicode characters including variation selectors
(U+FE00–U+FE0F) and zero-width characters in PDF text streams, ensuring they
survive copy-paste from PDF viewers.
"""

from encypher_pdf.extractor import extract_signed_text, extract_text
from encypher_pdf.font_registry import list_supported_font_families, resolve_font_path
from encypher_pdf.inspector import inspect_pdf
from encypher_pdf.writer import Document, Page, TextStyle

__all__ = [
    "Document",
    "Page",
    "TextStyle",
    "extract_signed_text",
    "extract_text",
    "inspect_pdf",
    "list_supported_font_families",
    "resolve_font_path",
]
__version__ = "0.1.0"
