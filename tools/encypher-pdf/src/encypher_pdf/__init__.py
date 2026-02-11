# TEAM_154: encypher-pdf — Unicode-faithful PDF writer
"""
PDF writer that preserves ALL Unicode characters including variation selectors
(U+FE00–FE0F) and zero-width characters in PDF text streams, ensuring they
survive copy-paste from PDF viewers.
"""

from encypher_pdf.writer import Document, Page, TextStyle

__all__ = ["Document", "Page", "TextStyle"]
__version__ = "0.1.0"
