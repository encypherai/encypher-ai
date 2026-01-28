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
EXAMPLE_ARTICLE = """As Co-Chair of the C2PA Text Provenance Task Force, I authored Section A.7 of the specification-published January 8, 2026-alongside Google, BBC, OpenAI, Adobe, and Microsoft. We built Encypher to implement it in production.

The Problem

Text on the open web has no cryptographic proof of origin. Creators can't prove their work is theirs when it's scraped, distributed, or used to train AI. AI companies can claim "we didn't know it was yours" as an innocent infringement defense. We enable proof of authorship.

What We Built

Cryptographic watermarking embedded directly into text. Invisible to readers. Survives copy-paste, B2B distribution, web scraping, and data processing. Mathematical proof of origin at sentence-level granularity.

For Publishers and Creators:

- Serve formal notice. Prove willful infringement after notification, 3x damages territory.
- Verify quote integrity when AI claims "According to [Your Publication]..."
- Protect your brand from hallucinations.
- Transform unmarked content into licensing-ready assets.

For AI Labs Building Responsibly:

- Compatible infrastructure for marked content in training pipelines
- Quote integrity verification to protect your reputation
- Performance intelligence from sentence-level attribution

Let's Connect If:

- You're actively managing AI copyright litigation or licensing negotiations
- You understand that infrastructure gets built collaboratively, not competitively
- You want to help define standards for content licensing

→ Publishers: encypherai.com/publisher-demo 
→ AI Labs: encypherai.com/ai-demo

P.S. Paste this into encypherai.com/tools/verify to see the embedded signature. That's the technology we're building for the entire web."""


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
            "segmentation_level": "document",
            "manifest_mode": "minimal_uuid",
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
