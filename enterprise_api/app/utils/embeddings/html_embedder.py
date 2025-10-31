"""
HTML embedding utility for injecting signed references into HTML content.
"""
from typing import List
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class HTMLEmbedder:
    """Embed references into HTML content."""
    
    @staticmethod
    def embed_in_paragraphs(
        html: str,
        embeddings: List,
        method: str = "data-attribute"
    ) -> str:
        """
        Embed references into HTML paragraphs.
        
        Args:
            html: HTML content
            embeddings: List of EmbeddingReference objects (one per paragraph/sentence)
            method: Embedding method (data-attribute, span, comment)
        
        Returns:
            HTML with embedded references
        
        Raises:
            ValueError: If method is invalid
        """
        if method not in ['data-attribute', 'span', 'comment']:
            raise ValueError(f"Invalid embedding method: {method}")
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            
            # If we have more embeddings than paragraphs, we're embedding per sentence
            # For now, assume one embedding per paragraph
            for i, (p, embedding) in enumerate(zip(paragraphs, embeddings)):
                compact_ref = embedding.to_compact_string()
                
                if method == "data-attribute":
                    p['data-encypher'] = compact_ref
                
                elif method == "span":
                    span = soup.new_tag('span', attrs={
                        'class': 'ency-ref',
                        'style': 'display:none'
                    })
                    span.string = compact_ref
                    p.append(span)
                
                elif method == "comment":
                    from bs4 import Comment
                    comment = Comment(f"ency:{compact_ref}")
                    p.append(comment)
            
            logger.info(f"Embedded {min(len(paragraphs), len(embeddings))} references using {method} method")
            
            return str(soup)
            
        except Exception as e:
            logger.error(f"Error embedding in HTML: {e}")
            raise
    
    @staticmethod
    def extract_references(html: str) -> List[str]:
        """
        Extract all Encypher references from HTML.
        
        Args:
            html: HTML content
        
        Returns:
            List of reference strings (e.g., ["ency:v1/a3f9c2e1/8k3mP9xQ", ...])
        """
        references = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Method 1: Data attributes
            for el in soup.find_all(attrs={'data-encypher': True}):
                ref = el.get('data-encypher')
                if ref:
                    references.append(ref)
            
            # Method 2: Hidden spans
            for span in soup.find_all('span', class_='ency-ref'):
                ref = span.get_text()
                if ref:
                    references.append(ref)
            
            # Method 3: Comments
            from bs4 import Comment
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                if 'ency:' in comment:
                    # Extract reference from comment
                    ref = comment.strip()
                    if ref.startswith('ency:'):
                        references.append(ref)
            
            logger.info(f"Extracted {len(references)} references from HTML")
            
            return references
            
        except Exception as e:
            logger.error(f"Error extracting references from HTML: {e}")
            return []
