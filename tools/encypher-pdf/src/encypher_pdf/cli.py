from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from encypher_pdf.extractor import PdfExtractionError, extract_signed_text, extract_text
from encypher_pdf.font_registry import FontResolutionError, list_supported_font_families
from encypher_pdf.inspector import PdfInspectionError, inspect_pdf
from encypher_pdf.writer import STYLE_BODY, STYLE_TITLE, Document, TextStyle


class CliError(Exception):
    pass


def _read_text_input(input_path: str) -> str:
    path = Path(input_path)
    if not path.exists():
        raise CliError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def _build_generate_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("generate", help="Generate a PDF from UTF-8 text")
    parser.add_argument("input", help="Path to a UTF-8 text file")
    parser.add_argument("output", help="Path to the output PDF")
    parser.add_argument("--title", default=None, help="Optional title line")
    parser.add_argument("--font-family", default="roboto", choices=list_supported_font_families(), help="Font family")
    parser.add_argument("--font-size", type=float, default=10.0, help="Body font size")
    parser.add_argument("--title-size", type=float, default=18.0, help="Title font size")
    parser.add_argument("--footer-text", default=None, help="Optional footer text")
    parser.add_argument("--signed-text", default=None, help="Optional explicit signed text file to embed")


def _build_extract_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("extract", help="Extract text or signed text from a PDF")
    parser.add_argument("pdf", help="Path to the PDF")
    parser.add_argument("--signed-only", action="store_true", help="Extract only the embedded signed text stream")


def _build_inspect_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("inspect", help="Inspect fonts, ToUnicode coverage, and signed text presence")
    parser.add_argument("pdf", help="Path to the PDF")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")


def _build_verify_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("verify", help="Verify extracted text against an expected UTF-8 text file")
    parser.add_argument("pdf", help="Path to the PDF")
    parser.add_argument("expected_text", help="Path to the expected UTF-8 text file")
    parser.add_argument("--prefer-text-layer", action="store_true", help="Use the viewer-style extracted text instead of signed stream first")


def _run_generate(args: argparse.Namespace) -> int:
    source_text = _read_text_input(args.input)
    signed_text = _read_text_input(args.signed_text) if args.signed_text else source_text

    doc = Document(footer_text=args.footer_text)
    body_style = TextStyle(
        font_size=args.font_size,
        line_height=1.3,
        alignment=STYLE_BODY.alignment,
        space_after=STYLE_BODY.space_after,
        first_line_indent=STYLE_BODY.first_line_indent,
        font_family=args.font_family,
    )

    if args.title:
        title_style = TextStyle(
            font_size=args.title_size,
            line_height=STYLE_TITLE.line_height,
            alignment=STYLE_TITLE.alignment,
            bold=True,
            space_after=STYLE_TITLE.space_after,
            font_family=args.font_family,
        )
        doc.add_text(args.title, title_style)

    for chunk in source_text.split("\n\n"):
        doc.add_text(chunk, body_style)

    doc.set_signed_text(signed_text)
    doc.save(args.output)
    print(args.output)
    return 0


def _run_extract(args: argparse.Namespace) -> int:
    if args.signed_only:
        text = extract_signed_text(args.pdf)
        if text is None:
            raise CliError("No EncypherSignedText stream found")
    else:
        text = extract_text(args.pdf)
    print(text)
    return 0


def _run_inspect(args: argparse.Namespace) -> int:
    info = inspect_pdf(args.pdf)
    if args.pretty:
        print(json.dumps(info, indent=2, sort_keys=True))
    else:
        print(json.dumps(info, sort_keys=True))
    return 0


def _run_verify(args: argparse.Namespace) -> int:
    expected = _read_text_input(args.expected_text)
    actual = extract_text(args.pdf, prefer_signed_stream=not args.prefer_text_layer)
    if actual != expected:
        raise CliError(f"Verification failed: expected {len(expected)} chars, got {len(actual)} chars")
    print("verified")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="encypher-pdf", description="Unicode-faithful PDF generation, extraction, inspection, and verification")
    subparsers = parser.add_subparsers(dest="command", required=True)

    _build_generate_parser(subparsers)
    _build_extract_parser(subparsers)
    _build_inspect_parser(subparsers)
    _build_verify_parser(subparsers)

    args = parser.parse_args(argv)

    try:
        if args.command == "generate":
            return _run_generate(args)
        if args.command == "extract":
            return _run_extract(args)
        if args.command == "inspect":
            return _run_inspect(args)
        if args.command == "verify":
            return _run_verify(args)
    except (CliError, PdfExtractionError, PdfInspectionError, FontResolutionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
