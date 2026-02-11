#!/usr/bin/env python3
"""
Sign HTML CMS content in-place via the Encypher AI Enterprise API.

Parses a full CMS HTML page, extracts article text content, signs it
via the live API with invisible Unicode markers (micro_c2pa or
micro_ecc_c2pa), and returns the complete HTML page with markers
embedded in the article's text nodes. All HTML tags, attributes,
images, scripts, styles, nav, and footer remain untouched.

Usage:
    python scripts/sign_html_cms.py INPUT.html OUTPUT.html [OPTIONS]

    # Sign with micro_c2pa (default)
    python scripts/sign_html_cms.py page.html page_signed.html

    # Sign with micro_ecc_c2pa (Reed-Solomon error correction)
    python scripts/sign_html_cms.py page.html page_signed.html --mode micro_ecc_c2pa

    # Custom content selector (default: article)
    python scripts/sign_html_cms.py page.html page_signed.html --selector "main .content"

    # Use env file for API credentials
    python scripts/sign_html_cms.py page.html page_signed.html --env-file .env.prod

Environment variables (or via --env-file):
    API_KEY     - Encypher AI API key
    BASE_URL    - API base URL (default: https://api.encypherai.com)
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import dotenv_values

# Re-use shared constants from the extractor module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.utils.html_text_extractor import (
    BLOCK_ELEMENTS,
    SKIP_ELEMENTS,
)


def _collect_text_nodes(
    root: Tag,
) -> list[tuple[NavigableString, str]]:
    """Collect renderable text nodes from a DOM subtree in order."""
    nodes: list[tuple[NavigableString, str]] = []

    def _walk(node: Tag | NavigableString) -> None:
        if isinstance(node, NavigableString):
            text = str(node).strip()
            if text:
                nodes.append((node, " ".join(text.split())))
            return
        if not isinstance(node, Tag):
            return
        tag_name = node.name.lower() if node.name else ""
        if tag_name in SKIP_ELEMENTS:
            return
        for child in node.children:
            _walk(child)

    _walk(root)
    return nodes


def _extract_text_from_element(root: Tag) -> str:
    """Extract rendered text from a DOM subtree, preserving paragraph structure."""
    chunks: list[str] = []

    def _walk(node: Tag | NavigableString) -> None:
        if isinstance(node, NavigableString):
            text = str(node)
            if text.strip():
                chunks.append(text)
            elif text and chunks and not chunks[-1].endswith("\n"):
                chunks.append(" ")
            return
        if not isinstance(node, Tag):
            return
        tag_name = node.name.lower() if node.name else ""
        if tag_name in SKIP_ELEMENTS:
            return
        is_block = tag_name in BLOCK_ELEMENTS
        if is_block and chunks and chunks[-1] != "\n":
            chunks.append("\n")
        for child in node.children:
            _walk(child)
        if is_block and chunks and chunks[-1] != "\n":
            chunks.append("\n")

    _walk(root)

    raw = "".join(chunks)
    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        normalized = " ".join(line.split())
        if normalized:
            cleaned.append(normalized)
    return "\n".join(cleaned)


def _get_vs_char_set() -> set[str]:
    """Get the VS256 character set used by invisible markers.

    Includes U+FEFF (BOM / ZWNBSP) which is used as the start marker for
    the C2PA text manifest wrapper block.
    """
    from app.utils.vs256_crypto import VS_CHAR_SET

    chars = set(VS_CHAR_SET)
    chars.add("\uFEFF")
    return chars


def _embed_signed_text_in_element(
    root: Tag,
    signed_text: str,
    vs_chars: set[str],
) -> int:
    """Embed signed text back into a DOM subtree's text nodes.

    Returns the number of text nodes successfully matched and replaced.
    """
    text_nodes = _collect_text_nodes(root)
    if not text_nodes:
        return 0

    cursor = 0
    matched = 0
    last_replaced_node: NavigableString | None = None

    for nav_str, normalized in text_nodes:
        # Collect inter-node VS chars (part of the C2PA manifest) instead
        # of discarding them.  These will be prepended to this text node.
        gap_vs: list[str] = []
        while cursor < len(signed_text) and (
            signed_text[cursor] in vs_chars
            or signed_text[cursor] in " \t\n\r"
        ):
            if signed_text[cursor] in vs_chars:
                gap_vs.append(signed_text[cursor])
            cursor += 1

        # Match visible text, skipping embedded VS chars
        match_start = cursor
        ti = 0
        si = cursor
        while si < len(signed_text) and ti < len(normalized):
            ch = signed_text[si]
            if ch in vs_chars:
                si += 1
                continue
            if ch == normalized[ti]:
                ti += 1
                si += 1
            elif ch == "\xa0" and normalized[ti] == " ":
                ti += 1
                si += 1
            else:
                break

        if ti != len(normalized):
            # Attach any collected gap VS chars to the previous node
            if gap_vs and last_replaced_node is not None:
                current = str(last_replaced_node)
                last_replaced_node.replace_with(
                    NavigableString(current + "".join(gap_vs))
                )
            continue

        # Consume trailing VS chars
        while si < len(signed_text) and signed_text[si] in vs_chars:
            si += 1

        signed_chunk = signed_text[match_start:si]
        cursor = si

        # Preserve original leading/trailing whitespace
        original_raw = str(nav_str)
        leading_ws = original_raw[: len(original_raw) - len(original_raw.lstrip())]
        trailing_ws = original_raw[len(original_raw.rstrip()) :]

        # Prepend any inter-node VS chars (C2PA manifest fragments)
        gap_prefix = "".join(gap_vs)
        replacement = NavigableString(
            leading_ws + gap_prefix + signed_chunk + trailing_ws
        )
        nav_str.replace_with(replacement)
        last_replaced_node = replacement
        matched += 1

    # Collect any remaining VS chars after the last text node
    remaining_vs: list[str] = []
    while cursor < len(signed_text):
        if signed_text[cursor] in vs_chars:
            remaining_vs.append(signed_text[cursor])
        cursor += 1

    if remaining_vs and last_replaced_node is not None:
        current = str(last_replaced_node)
        last_replaced_node.replace_with(
            NavigableString(current + "".join(remaining_vs))
        )

    return matched


def sign_html(
    html: str,
    api_key: str,
    base_url: str = "https://api.encypherai.com",
    manifest_mode: str = "micro_c2pa",
    content_selector: str = "article",
    document_title: str | None = None,
) -> str:
    """Sign the text content of an HTML page via the Encypher AI API.

    Args:
        html: Full HTML page content.
        api_key: Encypher AI API key.
        base_url: API base URL.
        manifest_mode: Signing mode (micro_c2pa, micro_ecc_c2pa, or basic).
        content_selector: CSS selector for the content area to sign.
        document_title: Optional document title for the API.

    Returns:
        Full HTML page with invisible markers embedded in the content area.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the content area
    content_root = soup.select_one(content_selector)
    if content_root is None:
        print(f"WARNING: No element found for selector '{content_selector}'", file=sys.stderr)
        print("Falling back to <body>", file=sys.stderr)
        content_root = soup.find("body")
        if content_root is None:
            raise ValueError("No <body> or content element found in HTML")

    # Extract text from the content area.
    # Replace newlines with spaces to match the API's signing pipeline,
    # which joins segments with spaces.  This ensures the NFC hash of
    # the text we send matches the hash of the signed output.
    extracted_text = _extract_text_from_element(content_root).replace("\n", " ")
    if not extracted_text.strip():
        raise ValueError("No text content found in the selected element")

    print(f"Content selector: {content_selector}")
    print(f"Extracted text: {len(extracted_text)} chars")

    # Auto-detect title from <h1> if not provided
    if document_title is None:
        h1 = content_root.find("h1")
        if h1:
            document_title = h1.get_text(strip=True)
        else:
            document_title = "Untitled"

    # Sign via the API
    document_id = f"cms_{uuid.uuid4().hex[:12]}"
    payload = {
        "document_id": document_id,
        "text": extracted_text,
        "document_title": document_title,
        "options": {
            "document_type": "article",
            "manifest_mode": manifest_mode,
            "segmentation_level": "sentence",
            "segmentation_levels": ["sentence", "paragraph"],
            "embedding_strategy": "single_point",
            "index_for_attribution": True,
        },
    }

    # Use basic options if manifest_mode is "basic"
    if manifest_mode == "basic":
        payload["options"] = {"document_type": "article"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Signing with mode: {manifest_mode}")
    print(f"Document ID: {document_id}")
    print(f"API: {base_url}/api/v1/sign")

    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        # Sign
        sign_response = client.post(
            "/api/v1/sign",
            headers=headers,
            json=payload,
        )
        if sign_response.status_code != 201:
            raise RuntimeError(
                f"Sign API returned {sign_response.status_code}: "
                f"{sign_response.text[:500]}"
            )

        sign_data = sign_response.json()
        if not sign_data.get("success"):
            raise RuntimeError(f"Sign API error: {sign_data}")

        signed_text = sign_data["data"]["document"]["signed_text"]
        print(f"Signed text: {len(signed_text)} chars (+{len(signed_text) - len(extracted_text)} markers)")

        # Embed signed text back into the content area
        vs_chars = _get_vs_char_set()
        matched = _embed_signed_text_in_element(content_root, signed_text, vs_chars)
        print(f"Replaced {matched} text nodes in HTML")

        # Verify using the original signed text (matches the hash from sign time)
        verify_response = client.post(
            "/api/v1/verify",
            headers=headers,
            json={"text": signed_text},
        )
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            if verify_data.get("data", {}).get("valid"):
                print("Verification (signed text): PASSED")
            else:
                reason = verify_data.get("data", {}).get("reason_code", "unknown")
                print(f"Verification (signed text): FAILED (reason: {reason})", file=sys.stderr)
        else:
            print(f"Verification request failed: {verify_response.status_code}", file=sys.stderr)

        # Secondary: verify the HTML-extracted text (simulates copy-paste)
        # Apply same newline→space normalization as the signing input
        text_from_html = _extract_text_from_element(content_root).replace("\n", " ")
        verify_html_response = client.post(
            "/api/v1/verify",
            headers=headers,
            json={"text": text_from_html},
        )
        if verify_html_response.status_code == 200:
            verify_html_data = verify_html_response.json()
            if verify_html_data.get("data", {}).get("valid"):
                print("Verification (HTML round-trip): PASSED")
            else:
                reason = verify_html_data.get("data", {}).get("reason_code", "unknown")
                print(f"Verification (HTML round-trip): FAILED (reason: {reason})", file=sys.stderr)
                print("  Note: HTML round-trip verification requires whitespace-normalized hashing on the server.", file=sys.stderr)
        else:
            print(f"HTML round-trip verification request failed: {verify_html_response.status_code}", file=sys.stderr)

    return str(soup)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sign HTML CMS content with Encypher AI invisible markers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Input HTML file path")
    parser.add_argument("output", help="Output HTML file path")
    parser.add_argument(
        "--mode",
        default="micro_c2pa",
        choices=["micro_c2pa", "micro_ecc_c2pa", "basic"],
        help="Manifest mode (default: micro_c2pa)",
    )
    parser.add_argument(
        "--selector",
        default="article",
        help="CSS selector for the content area to sign (default: article)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Document title (auto-detected from <h1> if not provided)",
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to .env file with API_KEY and BASE_URL",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (overrides env file / environment variable)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="API base URL (overrides env file / environment variable)",
    )

    args = parser.parse_args()

    # Load config
    env = {}
    if args.env_file:
        env = dotenv_values(args.env_file)

    import os

    api_key = args.api_key or env.get("API_KEY") or os.environ.get("API_KEY")
    base_url = args.base_url or env.get("BASE_URL") or os.environ.get("BASE_URL", "https://api.encypherai.com")

    if not api_key:
        print("ERROR: API_KEY not provided. Use --api-key, --env-file, or set API_KEY env var.", file=sys.stderr)
        sys.exit(1)

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    html = input_path.read_text(encoding="utf-8")
    print(f"Input: {input_path} ({len(html)} chars)")

    # Sign
    signed_html = sign_html(
        html=html,
        api_key=api_key,
        base_url=base_url,
        manifest_mode=args.mode,
        content_selector=args.selector,
        document_title=args.title,
    )

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(signed_html, encoding="utf-8")
    print(f"Output: {output_path} ({len(signed_html)} chars)")
    print("Done.")


if __name__ == "__main__":
    main()
