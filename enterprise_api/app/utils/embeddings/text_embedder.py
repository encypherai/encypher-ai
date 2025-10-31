"""
Plain text embedding utility for injecting signed references into text content.
"""
from typing import List
import re
import logging

logger = logging.getLogger(__name__)


class TextEmbedder:
    """Embed references into plain text content."""
    
    @staticmethod
    def embed_in_sentences(
        text: str,
        embeddings: List,
        method: str = "inline-bracket"
    ) -> str:
        """
        Embed references into plain text sentences.
        
        Args:
            text: Plain text content
            embeddings: List of EmbeddingReference objects
            method: Embedding method (inline-bracket, inline-parenthesis, end-of-line)
        
        Returns:
            Text with embedded references
        
        Raises:
            ValueError: If method is invalid
        """
        if method not in ['inline-bracket', 'inline-parenthesis', 'end-of-line']:
            raise ValueError(f"Invalid embedding method: {method}")
        
        try:
            # Split into sentences (simple approach)
            sentences = re.split(r'([.!?]+\s+)', text)
            
            # Reconstruct sentences with their punctuation
            full_sentences = []
            for i in range(0, len(sentences) - 1, 2):
                if i + 1 < len(sentences):
                    full_sentences.append(sentences[i] + sentences[i + 1])
                else:
                    full_sentences.append(sentences[i])
            
            # Handle last sentence if no punctuation
            if len(sentences) % 2 == 1 and sentences[-1].strip():
                full_sentences.append(sentences[-1])
            
            # Embed references
            result = []
            for i, sentence in enumerate(full_sentences):
                if i < len(embeddings):
                    embedding = embeddings[i]
                    compact_ref = embedding.to_compact_string()
                    
                    if method == "inline-bracket":
                        result.append(f"{sentence.rstrip()} [{compact_ref}] ")
                    
                    elif method == "inline-parenthesis":
                        result.append(f"{sentence.rstrip()} ({compact_ref}) ")
                    
                    elif method == "end-of-line":
                        result.append(f"{sentence.rstrip()}\n[Ref: {compact_ref}]\n")
                else:
                    result.append(sentence)
            
            logger.info(f"Embedded {min(len(full_sentences), len(embeddings))} references using {method} method")
            
            return ''.join(result).strip()
            
        except Exception as e:
            logger.error(f"Error embedding in plain text: {e}")
            raise
    
    @staticmethod
    def extract_references(text: str) -> List[str]:
        """
        Extract all Encypher references from plain text.
        
        Args:
            text: Plain text content
        
        Returns:
            List of reference strings (e.g., ["ency:v1/a3f9c2e1/8k3mP9xQ", ...])
        """
        references = []
        
        try:
            # Pattern for all methods
            # Matches: [ency:v1/...], (ency:v1/...), [Ref: ency:v1/...]
            pattern = r'[\[\(](?:Ref:\s*)?(ency:v1/[a-f0-9]{8}/[a-zA-Z0-9]{8})[\]\)]'
            references = re.findall(pattern, text)
            
            logger.info(f"Extracted {len(references)} references from plain text")
            
            return references
            
        except Exception as e:
            logger.error(f"Error extracting references from plain text: {e}")
            return []
