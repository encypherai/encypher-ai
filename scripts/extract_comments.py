#!/usr/bin/env python3
"""
Extract UNRESOLVED comments from .docx files and output them in markdown format.

Usage:
    uv run scripts/extract_comments.py -f "path_to_doc.docx"
"""

import argparse
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

# Word XML namespaces
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
}


@dataclass
class Reply:
    """A reply to a comment."""

    author: str
    date: datetime | None
    text: str


@dataclass
class Comment:
    """A comment in a Word document."""

    id: str
    author: str
    date: datetime | None
    text: str
    referenced_text: str = ""
    replies: list[Reply] = field(default_factory=list)


def parse_datetime(date_str: str | None) -> datetime | None:
    """Parse ISO datetime string from Word XML."""
    if not date_str:
        return None
    try:
        # Word uses ISO format like 2024-01-06T10:30:00Z
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_text_from_element(element: ET.Element) -> str:
    """Extract all text content from an XML element recursively."""
    texts = []
    for elem in element.iter():
        if elem.tag == f"{{{NAMESPACES['w']}}}t":
            if elem.text:
                texts.append(elem.text)
    return "".join(texts)


def extract_referenced_text_from_range(content: str, comment_id: str) -> str:
    """Extract text between commentRangeStart and commentRangeEnd markers."""
    # Pattern to find text between range markers
    pattern = rf'<w:commentRangeStart[^>]*w:id="{comment_id}"[^>]*/>(.*?)<w:commentRangeEnd[^>]*w:id="{comment_id}"[^>]*/>'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        xml_content = match.group(1)
        # Find all <w:t> elements
        text_matches = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml_content)
        return "".join(text_matches)
    return ""


def extract_referenced_text_from_paragraph(content: str, comment_id: str) -> str:
    """Extract text from the paragraph containing a commentReference.

    This is a fallback when commentRangeStart/End markers aren't present.
    We extract only the text from the same paragraph as the comment reference,
    limiting to a reasonable length.
    """
    # Find the paragraph containing the comment reference
    # Look for <w:p> containing <w:commentReference w:id="{comment_id}"/>
    pattern = rf'<w:p[^>]*>(.*?<w:commentReference[^>]*w:id="{comment_id}"[^>]*/>.*?)</w:p>'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        para_content = match.group(1)
        # Extract text before the comment reference in this paragraph
        # Split at the comment reference and take text before it
        before_ref = para_content.split(f'w:id="{comment_id}"')[0]
        text_matches = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", before_ref)
        text = "".join(text_matches).strip()

        # Limit to last 500 chars if too long (take end of text as it's closest to comment)
        if len(text) > 500:
            text = "..." + text[-500:]

        # If we got text, return it
        if text:
            return text

        # Return all text in the paragraph (limited)
        all_text = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para_content)
        full_text = "".join(all_text).strip()
        if len(full_text) > 500:
            full_text = "..." + full_text[-500:]
        return full_text
    return ""


def extract_comments_from_docx(docx_path: Path) -> list[Comment]:
    """Extract only UNRESOLVED comments from a .docx file."""
    comments: dict[str, Comment] = {}
    para_id_to_comment_id: dict[str, str] = {}  # Map paraId to comment ID
    comment_id_to_para_id: dict[str, str] = {}  # Map comment ID to paraId
    reply_relationships: dict[str, str] = {}  # child paraId -> parent paraId
    resolved_para_ids: set[str] = set()  # Track resolved (done="1") comments

    with zipfile.ZipFile(docx_path, "r") as zf:
        # First, parse commentsExtended.xml to get resolved status
        if "word/commentsExtended.xml" in zf.namelist():
            with zf.open("word/commentsExtended.xml") as f:
                tree = ET.parse(f)  # noqa: S314 - parsing trusted local .docx
                root = tree.getroot()

                for comment_ex in root.findall(".//w15:commentEx", NAMESPACES):
                    para_id = comment_ex.get(f"{{{NAMESPACES['w15']}}}paraId")
                    parent_para_id = comment_ex.get(f"{{{NAMESPACES['w15']}}}paraIdParent")
                    done = comment_ex.get(f"{{{NAMESPACES['w15']}}}done")

                    # Track resolved comments (done="1" means resolved)
                    if para_id and done == "1":
                        resolved_para_ids.add(para_id)

                    # Track reply relationships
                    if para_id and parent_para_id:
                        reply_relationships[para_id] = parent_para_id

        # Parse comments.xml if it exists
        if "word/comments.xml" in zf.namelist():
            with zf.open("word/comments.xml") as f:
                tree = ET.parse(f)  # noqa: S314 - parsing trusted local .docx
                root = tree.getroot()

                for comment_elem in root.findall(".//w:comment", NAMESPACES):
                    comment_id = comment_elem.get(f"{{{NAMESPACES['w']}}}id")
                    author = comment_elem.get(f"{{{NAMESPACES['w']}}}author", "Unknown")
                    date_str = comment_elem.get(f"{{{NAMESPACES['w']}}}date")
                    text = get_text_from_element(comment_elem)

                    # Get paraId from the first paragraph in the comment
                    para_id = None
                    first_para = comment_elem.find(".//w:p", NAMESPACES)
                    if first_para is not None:
                        para_id = first_para.get(f"{{{NAMESPACES['w14']}}}paraId")
                        if para_id and comment_id:
                            para_id_to_comment_id[para_id] = comment_id
                            comment_id_to_para_id[comment_id] = para_id

                    # Skip resolved comments
                    if para_id and para_id in resolved_para_ids:
                        continue

                    if comment_id:
                        comments[comment_id] = Comment(
                            id=comment_id,
                            author=author,
                            date=parse_datetime(date_str),
                            text=text,
                        )

        # Process replies - add them to parent comments (only if parent is unresolved)
        for child_para_id, parent_para_id in reply_relationships.items():
            child_comment_id = para_id_to_comment_id.get(child_para_id)
            parent_comment_id = para_id_to_comment_id.get(parent_para_id)

            if child_comment_id and parent_comment_id:
                child_comment = comments.get(child_comment_id)
                parent_comment = comments.get(parent_comment_id)

                if child_comment and parent_comment:
                    parent_comment.replies.append(
                        Reply(
                            author=child_comment.author,
                            date=child_comment.date,
                            text=child_comment.text,
                        )
                    )
                    # Remove the reply from main comments dict
                    del comments[child_comment_id]

        # Parse document.xml to find referenced text
        if "word/document.xml" in zf.namelist():
            with zf.open("word/document.xml") as f:
                content = f.read().decode("utf-8")

                for comment_id in list(comments.keys()):
                    # Try range-based extraction first
                    ref_text = extract_referenced_text_from_range(content, comment_id)

                    # If no range found, try paragraph-based extraction
                    if not ref_text:
                        ref_text = extract_referenced_text_from_paragraph(content, comment_id)

                    comments[comment_id].referenced_text = ref_text

    # Sort comments by ID (numeric order)
    sorted_comments = sorted(comments.values(), key=lambda c: int(c.id))
    return sorted_comments


def format_output(comments: list[Comment], output_path: Path, source_file: str) -> None:
    """Format comments as markdown and write to output file."""
    lines = []

    # Header with summary at the top
    lines.append("# Document Comments Extraction")
    lines.append("")
    lines.append(f"**Source:** `{source_file}`")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Total Open Comments:** {len(comments)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for idx, comment in enumerate(comments, start=1):
        lines.append(f"## Comment #{idx}")
        lines.append("")

        # Metadata
        date_str = comment.date.strftime("%Y-%m-%d %H:%M:%S") if comment.date else "Unknown"
        lines.append(f"- **Date:** {date_str}")
        lines.append(f"- **Author:** {comment.author}")
        lines.append("")

        # Comment text
        lines.append("### Comment")
        lines.append("")
        lines.append(comment.text)
        lines.append("")

        # Referenced content
        lines.append("### Referenced Content")
        lines.append("")
        if comment.referenced_text:
            ref_text = comment.referenced_text.strip()
            lines.append(f"> {ref_text}")
        else:
            lines.append("*[No referenced text found]*")
        lines.append("")

        # Replies
        if comment.replies:
            lines.append("### Replies")
            lines.append("")
            for reply_idx, reply in enumerate(comment.replies, start=1):
                reply_date = reply.date.strftime("%Y-%m-%d %H:%M:%S") if reply.date else "Unknown"
                lines.append(f"{reply_idx}. **{reply.author}** ({reply_date}):")
                lines.append(f"   {reply.text}")
                lines.append("")

        lines.append("---")
        lines.append("")

    output_text = "\n".join(lines)

    # Write to file
    output_path.write_text(output_text, encoding="utf-8")
    print(f"Output written to: {output_path}")

    # Also print to console
    print("\n" + output_text)


def main():
    parser = argparse.ArgumentParser(description="Extract comments from a .docx file")
    parser.add_argument("-f", "--file", required=True, help="Path to the .docx file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: <input>_comments.txt)",
    )

    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return 1

    if not input_path.suffix.lower() == ".docx":
        print(f"Error: File must be a .docx file: {input_path}")
        return 1

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_name(f"{input_path.stem}_comments.md")

    print(f"Extracting UNRESOLVED comments from: {input_path}")

    comments = extract_comments_from_docx(input_path)

    if not comments:
        print("No unresolved comments found in the document.")
        return 0

    print(f"Found {len(comments)} unresolved comment(s)")

    format_output(comments, output_path, input_path.name)

    return 0


if __name__ == "__main__":
    exit(main())
