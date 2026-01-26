#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
"""
Lightweight signing example demonstrating copy-paste survival.

This script uses the most minimal embedding configuration:
- lightweight_uuid manifest mode (smallest metadata footprint)
- single_point embedding strategy (non-distributed)
- C2PA disabled (basic metadata only)
- Sentence-level segmentation (optimal for copy-paste survival)

Usage:
    uv run scripts/example_lightweight_sign.py --api-key YOUR_API_KEY

    # With custom text file
    uv run scripts/example_lightweight_sign.py --api-key YOUR_API_KEY --file article.txt

    # Output embedded content to file
    uv run scripts/example_lightweight_sign.py --api-key YOUR_API_KEY -o signed_article.txt
"""

import argparse
import json
import sys
import uuid

import requests

DEFAULT_BASE_URL = "https://api.encypherai.com"

# Example 1-page article for demonstration
EXAMPLE_ARTICLE = """The Future of Content Authentication

In an era of rapidly advancing artificial intelligence, the ability to verify the authenticity and origin of digital content has become critically important. Publishers, journalists, and content creators face unprecedented challenges in protecting their work and establishing trust with their audiences.

Traditional methods of content protection, such as watermarks and metadata, have proven insufficient against modern threats. Visible watermarks can be cropped or edited out, while metadata can be easily stripped or modified. What the industry needs is a more robust solution that embeds authentication directly into the content itself.

Invisible steganographic embeddings offer a promising approach. By encoding cryptographic signatures into the text using Unicode variation selectors, content can carry its provenance information in a way that survives copy-paste operations, reformatting, and even partial extraction. Each sentence becomes independently verifiable, allowing readers to confirm authenticity even when only a portion of the original content is shared.

The technology works by inserting invisible Unicode characters between visible characters in the text. These characters encode a compressed digital signature that links each segment to its original source. When the text is copied and pasted, these invisible markers travel with it, maintaining the chain of provenance.

For publishers, this means being able to track how their content spreads across the internet. For readers, it provides a mechanism to verify that what they're reading actually came from the claimed source. And for the broader ecosystem, it establishes a foundation for accountability in digital content distribution.

As AI-generated content becomes increasingly sophisticated and difficult to distinguish from human-created work, these authentication mechanisms will become essential infrastructure for maintaining trust in our information landscape."""


def sign_document(base_url: str, api_key: str, text: str, document_id: str) -> dict:
    """Sign document with lightweight embeddings."""
    response = requests.post(
        f"{base_url}/api/v1/sign/advanced",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "document_id": document_id,
            "text": text,
            "segmentation_level": "sentence",
            "manifest_mode": "lightweight_uuid",
            "embedding_strategy": "single_point",
            "disable_c2pa": True,
            "embedding_options": {
                "format": "plain",
                "include_text": True,
            },
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Sign content with lightweight embeddings for copy-paste survival demo",
    )
    parser.add_argument("--api-key", required=True, help="API key")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--output", "-o", help="Write signed content to file")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")
    args = parser.parse_args()

    # Get text content
    if args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        text = EXAMPLE_ARTICLE

    document_id = f"demo_{uuid.uuid4().hex[:8]}"

    print(f"Signing document: {document_id}")
    print(f"Text length: {len(text)} chars")
    print(f"Configuration: lightweight_uuid + single_point + no C2PA\n")

    try:
        result = sign_document(args.base_url, args.api_key, text, document_id)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Success: {result.get('success')}")
            print(f"Segments signed: {len(result.get('embeddings', []))}")

            merkle = result.get("merkle_tree", {})
            if merkle:
                print(f"Merkle root: {merkle.get('root_hash', '')[:32]}...")

            embedded = result.get("embedded_content", "")
            overhead = len(embedded) - len(text)
            print(f"\nOriginal length: {len(text)} chars")
            print(f"Embedded length: {len(embedded)} chars")
            print(f"Overhead: {overhead} chars ({overhead/len(text)*100:.1f}%)")

        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(result.get("embedded_content", ""))
            print(f"\nSigned content written to: {args.output}")
            print("Try copying text from this file to test copy-paste survival!")

    except requests.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        try:
            print(e.response.json(), file=sys.stderr)
        except Exception:
            print(e.response.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
