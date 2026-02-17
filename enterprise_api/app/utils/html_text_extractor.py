"""
HTML text extractor for CMS content signing (TEAM_169).

Extracts only the text that would be rendered in a browser from HTML content,
stripping all tags while preserving paragraph/section structure. This produces
clean text suitable for signing with micro mode.

Key design decisions:
- Block elements (h1-h6, p, div, li, blockquote, etc.) produce paragraph breaks
- Inline elements (b, i, em, strong, a, span) preserve their text content
- img elements are completely ignored (not rendered as text)
- Link anchor text is preserved; href URLs are stripped
- Whitespace is normalized (no double-spaces, clean line breaks)
"""

from __future__ import annotations

from typing import Set

from bs4 import BeautifulSoup, NavigableString, Tag

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


def extract_text_from_html(html: str) -> str:
    """Extract rendered text from HTML, preserving paragraph structure.

    Args:
        html: Raw HTML string.

    Returns:
        Plain text with block elements separated by newlines.
        Empty string for empty/whitespace-only input.
    """
    if not html or not html.strip():
        return ""

    soup = BeautifulSoup(html, "html.parser")
    chunks: list[str] = []
    _walk(soup, chunks)

    lines = _normalize_output(chunks)
    return lines


def extract_segments_from_html(html: str) -> list[str]:
    """Extract text from HTML and split into signable segments.

    Each segment is a non-empty line of text (paragraph, heading, list item, etc.)
    suitable for per-sentence signing with micro mode.

    Args:
        html: Raw HTML string.

    Returns:
        List of non-empty text segments.
    """
    text = extract_text_from_html(html)
    if not text:
        return []

    segments = [line.strip() for line in text.split("\n") if line.strip()]
    return segments


def _walk(node: Tag | NavigableString, chunks: list[str]) -> None:
    """Recursively walk the DOM tree, collecting text chunks."""
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
        _walk(child, chunks)

    if is_block and chunks and chunks[-1] != "\n":
        chunks.append("\n")


def _normalize_output(chunks: list[str]) -> str:
    """Join chunks and normalize whitespace."""
    raw = "".join(chunks)

    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        normalized = " ".join(line.split())
        if normalized:
            cleaned.append(normalized)

    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# In-place HTML signing: inject signed text back into HTML structure
# ---------------------------------------------------------------------------


def _get_vs_char_set() -> Set[str]:
    """Lazily import the VS256 character set used by invisible markers.

    Includes U+FEFF (BOM / ZWNBSP) which is used as the start marker for
    the C2PA text manifest wrapper block.
    """
    from app.utils.vs256_crypto import VS_CHAR_SET

    chars = set(VS_CHAR_SET)
    chars.add("\uFEFF")
    return chars


def _collect_text_nodes(soup: BeautifulSoup) -> list[tuple[NavigableString, str]]:
    """Collect all renderable text nodes from the DOM in order.

    Returns list of (NavigableString, normalized_text) tuples.
    """
    nodes: list[tuple[NavigableString, str]] = []

    def _walk_collect(node: Tag | NavigableString) -> None:
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
            _walk_collect(child)

    _walk_collect(soup)
    return nodes


def embed_signed_text_in_html(original_html: str, signed_text: str) -> str:
    """Inject API-signed text back into the original HTML structure.

    Takes the original HTML and the signed text returned by the API
    (which contains invisible Unicode markers) and produces HTML where
    each text node carries its corresponding markers while all tags,
    attributes, images, etc. remain untouched.

    The output is a valid HTML string that can be served by a CMS.
    When a user copies text from the rendered page, the invisible
    markers come along in the clipboard.

    Args:
        original_html: The original HTML content.
        signed_text: Signed text from the API (with invisible markers).

    Returns:
        HTML string with invisible markers embedded in text nodes.
    """
    if not original_html or not original_html.strip():
        return original_html
    if not signed_text:
        return original_html

    vs_chars = _get_vs_char_set()
    soup = BeautifulSoup(original_html, "html.parser")
    text_nodes = _collect_text_nodes(soup)

    if not text_nodes:
        return original_html

    cursor = 0
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

        # Match this node's visible text against the signed text,
        # skipping over any embedded VS chars in the signed version
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
            # Could not match — attach any collected gap VS chars to the
            # previous node so they are not lost.
            if gap_vs and last_replaced_node is not None:
                current = str(last_replaced_node)
                last_replaced_node.replace_with(
                    NavigableString(current + "".join(gap_vs))
                )
            continue

        # Consume trailing VS chars that belong to this node's signature
        while si < len(signed_text) and signed_text[si] in vs_chars:
            si += 1

        signed_chunk = signed_text[match_start:si]
        cursor = si

        # Reconstruct the replacement preserving original leading/trailing whitespace
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

    return str(soup)
