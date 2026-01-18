"""
Markdown embedding utility for injecting signed references into Markdown content.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class MarkdownEmbedder:
    """Embed references into Markdown content."""

    @staticmethod
    def embed_in_paragraphs(markdown: str, embeddings: List, method: str = "reference-link") -> str:
        """
        Embed references into Markdown paragraphs.

        Args:
            markdown: Markdown content
            embeddings: List of EmbeddingReference objects
            method: Embedding method (reference-link, html-comment, invisible-link)

        Returns:
            Markdown with embedded references

        Raises:
            ValueError: If method is invalid
        """
        if method not in ["reference-link", "html-comment", "invisible-link"]:
            raise ValueError(f"Invalid embedding method: {method}")

        try:
            # Split into paragraphs (separated by blank lines)
            paragraphs = re.split(r"\n\s*\n", markdown)

            # Filter out empty paragraphs and code blocks
            content_paragraphs = []
            for p in paragraphs:
                p = p.strip()
                if p and not p.startswith("```"):
                    content_paragraphs.append(p)

            # Embed references
            result_paragraphs = []
            for i, p in enumerate(paragraphs):
                p = p.strip()
                if not p:
                    result_paragraphs.append("")
                    continue

                # Skip code blocks
                if p.startswith("```"):
                    result_paragraphs.append(p)
                    continue

                # Find corresponding embedding
                embedding_idx = len([x for x in result_paragraphs if x and not x.startswith("```")])
                if embedding_idx < len(embeddings):
                    embedding = embeddings[embedding_idx]
                    compact_ref = embedding.to_compact_string()

                    if method == "reference-link":
                        # Markdown reference-style link (invisible)
                        result_paragraphs.append(f"{p}\n[{compact_ref}]: # ")

                    elif method == "html-comment":
                        # HTML comment (works in Markdown)
                        result_paragraphs.append(f"{p}\n<!-- {compact_ref} -->")

                    elif method == "invisible-link":
                        # Zero-width space link (invisible)
                        result_paragraphs.append(f'{p}[​]({compact_ref} "encypher-ref")')
                else:
                    result_paragraphs.append(p)

            logger.info(f"Embedded {min(len(content_paragraphs), len(embeddings))} references using {method} method")

            return "\n\n".join(result_paragraphs)

        except Exception as e:
            logger.error(f"Error embedding in Markdown: {e}")
            raise

    @staticmethod
    def extract_references(markdown: str) -> List[str]:
        """
        Extract all Encypher references from Markdown.

        Args:
            markdown: Markdown content

        Returns:
            List of reference strings (e.g., ["ency:v1/a3f9c2e1/8k3mP9xQ", ...])
        """
        references = []

        try:
            # Method 1: Reference-style links
            # Pattern: [ency:v1/...]: #
            ref_pattern = r"\[(ency:v1/[a-f0-9]{8}/[a-zA-Z0-9]{8})\]:\s*#"
            references.extend(re.findall(ref_pattern, markdown))

            # Method 2: HTML comments
            # Pattern: <!-- ency:v1/... -->
            comment_pattern = r"<!--\s*(ency:v1/[a-f0-9]{8}/[a-zA-Z0-9]{8})\s*-->"
            references.extend(re.findall(comment_pattern, markdown))

            # Method 3: Invisible links
            # Pattern: [​](ency:v1/... "encypher-ref")
            link_pattern = r'\[.\]\((ency:v1/[a-f0-9]{8}/[a-zA-Z0-9]{8})\s+"encypher-ref"\)'
            references.extend(re.findall(link_pattern, markdown))

            logger.info(f"Extracted {len(references)} references from Markdown")

            return references

        except Exception as e:
            logger.error(f"Error extracting references from Markdown: {e}")
            return []
