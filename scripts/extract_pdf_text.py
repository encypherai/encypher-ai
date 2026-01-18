#!/usr/bin/env python3
"""Extract text from a PDF file for review.

Usage:
    uv run python scripts/extract_pdf_text.py /path/to/file.pdf --pages 6
    uv run python scripts/extract_pdf_text.py /path/to/file.pdf --all --output /path/to/output.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text from a PDF file.")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    parser.add_argument("--pages", type=int, default=6, help="Number of pages to extract")
    parser.add_argument("--all", action="store_true", help="Extract all pages")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output markdown file path (defaults to stdout)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.pdf_path.exists():
        print(f"File not found: {args.pdf_path}", file=sys.stderr)
        return 1

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        print("Missing dependency: pypdf. Install with: uv add pypdf", file=sys.stderr)
        return 1

    reader = PdfReader(str(args.pdf_path))
    page_count = len(reader.pages) if args.all else min(args.pages, len(reader.pages))
    output_lines: list[str] = []
    for idx in range(page_count):
        output_lines.append(f"## Page {idx + 1}\n")
        output_lines.append(reader.pages[idx].extract_text() or "")
        output_lines.append("\n")

    output_text = "\n".join(output_lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text, encoding="utf-8")
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
