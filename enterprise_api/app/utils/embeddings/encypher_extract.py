"""
Encypher Extraction Library for Partners

Python library for extracting and verifying Encypher embeddings from web content.
Designed for web scraping partners and content monitoring services.

Usage:
    from encypher_extract import EncypherExtractor

    extractor = EncypherExtractor(api_key="your_partner_api_key")
    references = extractor.extract_from_html(html_content)
    results = extractor.verify_batch(references)
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast

import requests  # type: ignore[import-untyped]
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmbeddingReference:
    """Represents an extracted embedding reference."""

    ref_id: str
    signature: str
    embedding: str
    method: str
    context: Optional[str] = None
    element_tag: Optional[str] = None


class EncypherExtractor:
    """
    Extract and verify Encypher embeddings from web content.
    """

    def __init__(self, api_endpoint: str = "https://api.encypher.ai/api/v1/public", partner_api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize the extractor.

        Args:
            api_endpoint: Base URL for Encypher API
            partner_api_key: Optional partner API key for reporting findings
            timeout: Request timeout in seconds
        """
        self.api_endpoint = api_endpoint
        self.partner_api_key = partner_api_key
        self.timeout = timeout
        self.session = requests.Session()

        if partner_api_key:
            self.session.headers.update({"Authorization": f"Bearer {partner_api_key}"})

    def extract_from_html(self, html: str) -> List[EmbeddingReference]:
        """
        Extract all Encypher references from HTML content.

        Args:
            html: HTML content as string

        Returns:
            List of EmbeddingReference objects
        """
        references = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Method 1: Data attributes
            for el in soup.find_all(attrs={"data-encypher": True}):
                raw_embedding = el.get("data-encypher")
                embedding = self._coerce_embedding_value(raw_embedding)
                if embedding is None:
                    continue
                parsed = self._parse_embedding(embedding)
                if parsed:
                    references.append(
                        EmbeddingReference(
                            ref_id=parsed["ref_id"],
                            signature=parsed["signature"],
                            embedding=embedding,
                            method="data-attribute",
                            context=el.get_text()[:200],
                            element_tag=el.name,
                        )
                    )

            # Method 2: Hidden spans
            for span in soup.find_all("span", class_="ency-ref"):
                embedding = span.get_text()
                parsed = self._parse_embedding(embedding)
                if parsed:
                    parent = span.parent
                    references.append(
                        EmbeddingReference(
                            ref_id=parsed["ref_id"],
                            signature=parsed["signature"],
                            embedding=embedding,
                            method="span",
                            context=parent.get_text()[:200] if parent else None,
                            element_tag=parent.name if parent else None,
                        )
                    )

            # Method 3: HTML comments
            from bs4 import Comment

            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                if "ency:" in comment:
                    match = re.search(r"ency:v1/([a-f0-9]{8})/([a-zA-Z0-9]{8})", comment)
                    if match:
                        embedding = f"ency:v1/{match.group(1)}/{match.group(2)}"
                        parent = comment.parent
                        references.append(
                            EmbeddingReference(
                                ref_id=match.group(1),
                                signature=match.group(2),
                                embedding=embedding,
                                method="comment",
                                context=parent.get_text()[:200] if parent else None,
                                element_tag=parent.name if parent else None,
                            )
                        )

            logger.info(f"Extracted {len(references)} embeddings from HTML")
            return references

        except Exception as e:
            logger.error(f"Error extracting from HTML: {e}")
            return []

    def extract_from_markdown(self, markdown: str) -> List[EmbeddingReference]:
        """
        Extract all Encypher references from Markdown content.

        Args:
            markdown: Markdown content as string

        Returns:
            List of EmbeddingReference objects
        """
        references = []

        try:
            # Reference-style links
            pattern1 = r"\[(ency:v1/([a-f0-9]{8})/([a-zA-Z0-9]{8}))\]:\s*#"
            for match in re.finditer(pattern1, markdown):
                references.append(
                    EmbeddingReference(ref_id=match.group(2), signature=match.group(3), embedding=match.group(1), method="reference-link")
                )

            # HTML comments
            pattern2 = r"<!--\s*(ency:v1/([a-f0-9]{8})/([a-zA-Z0-9]{8}))\s*-->"
            for match in re.finditer(pattern2, markdown):
                references.append(
                    EmbeddingReference(ref_id=match.group(2), signature=match.group(3), embedding=match.group(1), method="html-comment")
                )

            logger.info(f"Extracted {len(references)} embeddings from Markdown")
            return references

        except Exception as e:
            logger.error(f"Error extracting from Markdown: {e}")
            return []

    def extract_from_text(self, text: str) -> List[EmbeddingReference]:
        """
        Extract all Encypher references from plain text.

        Args:
            text: Plain text content

        Returns:
            List of EmbeddingReference objects
        """
        references = []

        try:
            pattern = r"[\[\(](?:Ref:\s*)?(ency:v1/([a-f0-9]{8})/([a-zA-Z0-9]{8}))[\]\)]"
            for match in re.finditer(pattern, text):
                references.append(EmbeddingReference(ref_id=match.group(2), signature=match.group(3), embedding=match.group(1), method="inline"))

            logger.info(f"Extracted {len(references)} embeddings from text")
            return references

        except Exception as e:
            logger.error(f"Error extracting from text: {e}")
            return []

    def verify(self, ref_id: str, signature: str) -> Dict[str, Any]:
        """
        Verify a single embedding with the Encypher API.

        Args:
            ref_id: Reference ID (8 hex characters)
            signature: Signature (8+ hex characters)

        Returns:
            Verification result dictionary
        """
        try:
            url = f"{self.api_endpoint}/verify/{ref_id}"
            params = {"signature": signature}

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            return cast(Dict[str, Any], response.json())

        except requests.exceptions.RequestException as e:
            logger.error(f"Verification request failed: {e}")
            return {"valid": False, "error": str(e)}

    def verify_batch(self, references: List[EmbeddingReference]) -> Dict[str, Any]:
        """
        Verify multiple embeddings in batch.

        Args:
            references: List of EmbeddingReference objects

        Returns:
            Batch verification result dictionary
        """
        try:
            url = f"{self.api_endpoint}/verify/batch"
            payload = {"references": [{"ref_id": ref.ref_id, "signature": ref.signature} for ref in references]}

            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            return cast(Dict[str, Any], response.json())

        except requests.exceptions.RequestException as e:
            logger.error(f"Batch verification request failed: {e}")
            return {"results": [], "total": 0, "valid_count": 0, "invalid_count": 0, "error": str(e)}

    def report_findings(self, findings: List[Dict[str, Any]], partner_id: str, scan_date: str) -> Dict[str, Any]:
        """
        Report findings to Encypher (requires partner API key).

        Args:
            findings: List of finding dictionaries with ref_id, found_url, etc.
            partner_id: Partner identifier
            scan_date: Date of scan (ISO format)

        Returns:
            Report response dictionary

        Raises:
            ValueError: If partner_api_key not set
        """
        if not self.partner_api_key:
            raise ValueError("Partner API key required for reporting findings")

        try:
            url = f"{self.api_endpoint.replace('/public', '')}/partner/report-findings"
            payload = {"partner_id": partner_id, "scan_date": scan_date, "findings": findings}

            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            return cast(Dict[str, Any], response.json())

        except requests.exceptions.RequestException as e:
            logger.error(f"Report findings request failed: {e}")
            return {"success": False, "error": str(e)}

    def _parse_embedding(self, embedding: str) -> Optional[Dict[str, str]]:
        """
        Parse an embedding string into components.

        Args:
            embedding: Embedding string (e.g., "ency:v1/a3f9c2e1/8k3mP9xQ")

        Returns:
            Dictionary with version, ref_id, signature or None if invalid
        """
        if not embedding:
            return None

        match = re.match(r"^ency:(v\d+)/([a-f0-9]{8})/([a-zA-Z0-9]{8,})$", embedding)
        if not match:
            return None

        return {"version": match.group(1), "ref_id": match.group(2), "signature": match.group(3)}

    @staticmethod
    def _coerce_embedding_value(value: Any) -> Optional[str]:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join(str(item) for item in value)
        return None


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = EncypherExtractor()

    # Example HTML with embeddings
    html = """
    <html>
        <body>
            <p data-encypher="ency:v1/a3f9c2e1/8k3mP9xQ">
                This is a verified sentence.
            </p>
            <p>
                This is another sentence.
                <span class="ency-ref" style="display:none">ency:v1/b4a8d3f2/9m4nQ0yR</span>
            </p>
        </body>
    </html>
    """

    # Extract references
    references = extractor.extract_from_html(html)
    print(f"Found {len(references)} embeddings")

    # Verify in batch
    if references:
        results = extractor.verify_batch(references)
        print(f"Verified {results['valid_count']}/{results['total']} embeddings")

        for i, result in enumerate(results["results"]):
            ref = references[i]
            print(f"  {ref.embedding}: {'✓ Valid' if result['valid'] else '✗ Invalid'}")
