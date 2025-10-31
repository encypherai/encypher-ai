"""
HTML embedding utility - DEPRECATED.

Embeddings are now invisible using Unicode variation selectors from encypher-ai.
No need to inject visible markers into HTML.

This module is kept for backward compatibility but should not be used.
"""
from typing import List
import logging

logger = logging.getLogger(__name__)


class HTMLEmbedder:
    """
    DEPRECATED: Embeddings are now invisible using encypher-ai.
    
    The encypher-ai package embeds metadata invisibly using Unicode variation
    selectors. No HTML manipulation is needed - embeddings are already in the text.
    """
    
    @staticmethod
    def embed_in_paragraphs(
        html: str,
        embeddings: List,
        method: str = "data-attribute"
    ) -> str:
        """
        DEPRECATED: Returns HTML as-is since embeddings are already invisible.
        
        Args:
            html: HTML content (already has invisible embeddings)
            embeddings: List of EmbeddingReference objects (not used)
            method: Embedding method (not used)
        
        Returns:
            HTML unchanged (embeddings already invisible)
        """
        logger.warning(
            "HTMLEmbedder.embed_in_paragraphs is deprecated. "
            "Embeddings are now invisible using encypher-ai. "
            "No HTML manipulation needed."
        )
        
        # Return HTML unchanged - embeddings are already invisible in the text
        return html
    
    @staticmethod
    def extract_references(html: str) -> List[str]:
        """
        DEPRECATED: Use encypher-ai's UnicodeMetadata.extract_metadata() instead.
        
        Extracts invisible embeddings from HTML text using encypher-ai.
        
        Args:
            html: HTML content with invisible embeddings
        
        Returns:
            Empty list (use encypher-ai directly for extraction)
        """
        logger.warning(
            "HTMLEmbedder.extract_references is deprecated. "
            "Use encypher-ai's UnicodeMetadata.extract_metadata() to extract "
            "invisible embeddings from text."
        )
        
        # Return empty list - users should use encypher-ai directly
        return []
