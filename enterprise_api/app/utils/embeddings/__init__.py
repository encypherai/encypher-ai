"""
Embedding utilities for injecting signed references into content.

Note: HTMLEmbedder was removed as embeddings are now invisible using
Unicode variation selectors from encypher-ai. No HTML manipulation needed.
"""

from app.utils.embeddings.markdown_embedder import MarkdownEmbedder
from app.utils.embeddings.text_embedder import TextEmbedder

__all__ = [
    "MarkdownEmbedder",
    "TextEmbedder",
]
