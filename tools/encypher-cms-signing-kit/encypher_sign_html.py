#!/usr/bin/env python3
"""
Encypher — Sign HTML CMS content in-place.

Parses a full CMS HTML page, extracts article text content, signs it
via the Encypher API with invisible Unicode markers, and returns
the complete HTML page with markers embedded in the article's text
nodes. All HTML tags, attributes, images, scripts, styles, nav, and
footer remain untouched.

Usage:
    python encypher_sign_html.py INPUT.html OUTPUT.html [OPTIONS]

    # Sign with micro mode (default: ecc + C2PA embedded)
    python encypher_sign_html.py page.html page_signed.html

    # Sign with basic mode (full C2PA only)
    python encypher_sign_html.py page.html page_signed.html --mode basic

    # Custom content selector (default: article)
    python encypher_sign_html.py page.html page_signed.html --selector "main .content"

    # Use env file for API credentials
    python encypher_sign_html.py page.html page_signed.html --env-file .env

Environment variables (or via --env-file / CLI flags):
    ENCYPHER_API_KEY  - Your Encypher API key
    ENCYPHER_BASE_URL - API base URL (default: https://api.encypherai.com)
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

__all__ = ["sign_html"]


# =============================================================================
# HTML element classification
# =============================================================================

BLOCK_ELEMENTS = frozenset({
    "address", "article", "aside", "blockquote", "dd", "details", "dialog",
    "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "li",
    "main", "nav", "ol", "p", "pre", "section", "summary", "table", "ul",
    "tr", "td", "th", "thead", "tbody", "tfoot",
})

SKIP_ELEMENTS = frozenset({
    "img", "script", "style", "noscript", "svg", "math", "video", "audio",
    "canvas", "iframe", "object", "embed", "source", "track", "picture",
    "template",
})


# =============================================================================
# Unicode Variation Selector character set (invisible marker alphabet)
# =============================================================================

def _build_vs_char_set() -> frozenset[str]:
    """Build the set of all 256 Unicode Variation Selector characters.

    VS1-VS16  (BMP):          U+FE00 - U+FE0F   (byte values 0-15)
    VS17-VS256 (Supplementary): U+E0100 - U+E01EF (byte values 16-255)

    Also includes U+FEFF (ZWNBSP) which is used as the start marker for
    the C2PA text manifest wrapper block.
    """
    chars: set[str] = set()
    for i in range(16):
        chars.add(chr(0xFE00 + i))
    for i in range(240):
        chars.add(chr(0xE0100 + i))
    chars.add("\uFEFF")
    return frozenset(chars)


VS_CHARS = _build_vs_char_set()


# =============================================================================
# HTML text extraction
# =============================================================================

def _collect_text_nodes(root: Tag) -> list[tuple[NavigableString, str]]:
    """Collect renderable text nodes from a DOM subtree in document order."""
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


# =============================================================================
# Embed signed text back into HTML
# =============================================================================

def _embed_signed_text_in_element(
    root: Tag,
    signed_text: str,
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
            signed_text[cursor] in VS_CHARS
            or signed_text[cursor] in " \t\n\r"
        ):
            if signed_text[cursor] in VS_CHARS:
                gap_vs.append(signed_text[cursor])
            cursor += 1

        # Match visible text, skipping embedded VS chars
        match_start = cursor
        ti = 0
        si = cursor
        while si < len(signed_text) and ti < len(normalized):
            ch = signed_text[si]
            if ch in VS_CHARS:
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
        while si < len(signed_text) and signed_text[si] in VS_CHARS:
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
        if signed_text[cursor] in VS_CHARS:
            remaining_vs.append(signed_text[cursor])
        cursor += 1

    if remaining_vs and last_replaced_node is not None:
        current = str(last_replaced_node)
        last_replaced_node.replace_with(
            NavigableString(current + "".join(remaining_vs))
        )

    return matched


# =============================================================================
# Main signing function
# =============================================================================

def sign_html(
    html: str,
    api_key: str,
    base_url: str = "https://api.encypherai.com",
    manifest_mode: str = "micro",
    content_selector: str = "article",
    document_title: str | None = None,
) -> str:
    """Sign the text content of an HTML page via the Encypher API.

    Args:
        html: Full HTML page content.
        api_key: Encypher API key.
        base_url: API base URL.
        manifest_mode: Signing mode (micro or basic).
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
    # which joins segments with spaces.  This ensures the hash of the
    # text we send matches the hash of the signed output.
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

    if manifest_mode == "basic":
        payload["options"] = {"document_type": "article"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Signing with mode: {manifest_mode}")
    print(f"Document ID: {document_id}")
    print(f"API: {base_url}/api/v1/sign")

    session = requests.Session()

    # --- Sign ---
    sign_response = session.post(
        f"{base_url}/api/v1/sign",
        headers=headers,
        json=payload,
        timeout=60,
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

    # --- Embed signed text back into the content area ---
    matched = _embed_signed_text_in_element(content_root, signed_text)
    print(f"Replaced {matched} text nodes in HTML")

    # --- Verify (signed text) ---
    verify_response = session.post(
        f"{base_url}/api/v1/verify",
        headers=headers,
        json={"text": signed_text},
        timeout=60,
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

    # --- Verify (HTML round-trip) ---
    text_from_html = _extract_text_from_element(content_root).replace("\n", " ")
    verify_html_response = session.post(
        f"{base_url}/api/v1/verify",
        headers=headers,
        json={"text": text_from_html},
        timeout=60,
    )
    if verify_html_response.status_code == 200:
        verify_html_data = verify_html_response.json()
        if verify_html_data.get("data", {}).get("valid"):
            print("Verification (HTML round-trip): PASSED")
        else:
            reason = verify_html_data.get("data", {}).get("reason_code", "unknown")
            print(f"Verification (HTML round-trip): FAILED (reason: {reason})", file=sys.stderr)
    else:
        print(f"HTML round-trip verification request failed: {verify_html_response.status_code}", file=sys.stderr)

    return str(soup)


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sign HTML CMS content with Encypher invisible markers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Input HTML file path")
    parser.add_argument("output", help="Output HTML file path")
    parser.add_argument(
        "--mode",
        default="micro",
        choices=["micro", "basic"],
        help="Signing mode (default: micro)",
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
        default=".env",
        help="Path to .env file (default: .env in current directory)",
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

    # Load config: CLI flags > env file > environment variables
    env: dict[str, str | None] = {}
    env_path = Path(args.env_file)
    if env_path.exists():
        try:
            from dotenv import dotenv_values
        except ImportError:
            print(
                "ERROR: python-dotenv is required for .env file support.\n"
                "  Run: uv sync   (or: pip install python-dotenv)",
                file=sys.stderr,
            )
            sys.exit(1)
        env = dotenv_values(env_path)
    elif args.env_file != ".env":
        print(f"WARNING: Env file not found: {env_path}", file=sys.stderr)

    api_key = (
        args.api_key
        or env.get("ENCYPHER_API_KEY")
        or os.environ.get("ENCYPHER_API_KEY")
    )
    base_url = (
        args.base_url
        or env.get("ENCYPHER_BASE_URL")
        or os.environ.get("ENCYPHER_BASE_URL", "https://api.encypherai.com")
    )

    if not api_key:
        print(
            "ERROR: API key not provided.\n"
            "  Set ENCYPHER_API_KEY in your .env file, or use --api-key, or\n"
            "  export ENCYPHER_API_KEY in your environment.",
            file=sys.stderr,
        )
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
