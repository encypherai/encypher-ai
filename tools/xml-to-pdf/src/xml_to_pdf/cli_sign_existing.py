# TEAM_157: CLI entry point for signing existing PDFs
"""Command-line interface for signing pre-existing PDFs with EncypherAI provenance."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xml_to_pdf.sign_existing import SignExistingError, sign_existing_pdf
from xml_to_pdf.signer import EMBEDDING_MODES, SigningError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sign-pdf",
        description=(
            "Sign an existing PDF with EncypherAI content provenance. "
            "Extracts text, signs via the enterprise API, and injects a "
            "metadata stream — without changing the PDF's visual appearance."
        ),
    )
    parser.add_argument(
        "pdf_file",
        help="Path to the existing PDF to sign.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output path for the signed PDF. Defaults to <name>_signed.pdf.",
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(EMBEDDING_MODES.keys()),
        default="minimal",
        help="Signing / embedding mode. Default: minimal",
    )
    parser.add_argument(
        "-t", "--title",
        default=None,
        help="Document title for the signing request. Defaults to the PDF filename.",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="Enterprise API base URL. Default: ENCYPHER_API_URL env or http://localhost:8000",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key. Default: ENCYPHER_API_KEY env var.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the original PDF instead of creating a new file.",
    )

    args = parser.parse_args(argv)
    pdf_path = Path(args.pdf_file)

    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        return 1

    # Determine output path
    if args.in_place:
        output_path = str(pdf_path)
    elif args.output:
        output_path = args.output
    else:
        output_path = str(pdf_path.parent / f"{pdf_path.stem}_signed.pdf")

    mode_label = EMBEDDING_MODES[args.mode]["label"]
    print(f"Signing {pdf_path.name} [{args.mode}] {mode_label}")

    try:
        result = sign_existing_pdf(
            str(pdf_path),
            output_path,
            mode=args.mode,
            document_title=args.title,
            api_url=args.api_url,
            api_key=args.api_key,
        )
    except (SignExistingError, SigningError) as e:
        print(f"Error: {e}")
        return 1

    print(f"  Document ID: {result.document_id}")
    print(f"  Segments: {result.total_segments}")
    print(f"  Signed text: {len(result.signed_text)} chars")
    if result.instance_id:
        print(f"  Instance ID: {result.instance_id}")

    visible_len = sum(1 for c in result.signed_text if c.isprintable() or c in "\n\r\t")
    invisible_len = len(result.signed_text) - visible_len
    overhead_pct = (invisible_len / visible_len * 100) if visible_len else 0
    print(f"  Invisible chars: {invisible_len} ({overhead_pct:.1f}% overhead)")
    print(f"  Output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
