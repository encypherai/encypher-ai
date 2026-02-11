# TEAM_153: CLI entry point for xml-to-pdf
"""Command-line interface for the XML-to-PDF provenance rendering engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xml_to_pdf.parser import parse_xml
from xml_to_pdf.renderer import render_pdf
from xml_to_pdf.signer import (
    EMBEDDING_MODES,
    SigningError,
    sign_all_modes,
    sign_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="xml-to-pdf",
        description="Convert research paper XML to PDF with embedded content provenance.",
    )
    parser.add_argument(
        "xml_file",
        help="Path to the input XML file.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output PDF path. Defaults to <xml_basename>_<mode>.pdf in ./output/",
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(EMBEDDING_MODES.keys()) + ["all"],
        default="all",
        help="Embedding mode to use. 'all' generates one PDF per mode. Default: all",
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
        "--unsigned",
        action="store_true",
        help="Generate PDF without signing (for testing rendering only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse XML and show document structure without generating PDF.",
    )

    args = parser.parse_args(argv)
    xml_path = Path(args.xml_file)

    if not xml_path.exists():
        print(f"Error: XML file not found: {xml_path}")
        return 1

    # Parse XML
    print(f"Parsing {xml_path.name}...")
    paper = parse_xml(str(xml_path))
    print(f"  Title: {paper.title}")
    print(f"  Authors: {', '.join(a.name for a in paper.authors)}")
    print(f"  Sections: {len(paper.sections)}")
    print(f"  References: {len(paper.references)}")

    plain_text = paper.plain_text()
    print(f"  Plain text: {len(plain_text)} chars")

    if args.dry_run:
        print("\n--- Document plain text ---")
        print(plain_text[:2000])
        if len(plain_text) > 2000:
            print(f"\n... ({len(plain_text) - 2000} more chars)")
        return 0

    # Determine output directory
    output_dir = Path(args.output).parent if args.output else Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.unsigned:
        # Render without signing
        out_path = args.output or str(output_dir / f"{xml_path.stem}_unsigned.pdf")
        print(f"\nRendering unsigned PDF -> {out_path}")
        render_pdf(paper, out_path)
        print(f"  Done: {out_path}")
        return 0

    # Determine modes to process
    modes = list(EMBEDDING_MODES.keys()) if args.mode == "all" else [args.mode]

    print(f"\nSigning with {len(modes)} mode(s)...")
    results_generated = 0

    for mode in modes:
        mode_label = EMBEDDING_MODES[mode]["label"]
        out_path = args.output if len(modes) == 1 else None
        if not out_path:
            out_path = str(output_dir / f"{xml_path.stem}_{mode}.pdf")

        print(f"\n[{mode}] {mode_label}")
        print(f"  Signing via enterprise API...")

        try:
            result = sign_text(
                plain_text,
                paper.title,
                mode,
                api_url=args.api_url,
                api_key=args.api_key,
            )
        except SigningError as e:
            print(f"  FAILED: {e}")
            continue

        print(f"  Document ID: {result.document_id}")
        print(f"  Segments: {result.total_segments}")
        print(f"  Signed text: {len(result.signed_text)} chars")
        if result.instance_id:
            print(f"  Instance ID: {result.instance_id}")

        # Measure invisible character overhead
        visible_len = sum(1 for c in result.signed_text if c.isprintable() or c in "\n\r\t")
        invisible_len = len(result.signed_text) - visible_len
        overhead_pct = (invisible_len / visible_len * 100) if visible_len else 0
        print(f"  Invisible chars: {invisible_len} ({overhead_pct:.1f}% overhead)")

        provenance_meta = {
            "mode": mode_label,
            "manifest_mode": EMBEDDING_MODES[mode]["manifest_mode"],
            "segmentation_level": EMBEDDING_MODES[mode]["segmentation_level"],
            "document_id": result.document_id,
            "total_segments": result.total_segments,
            "verification_url": result.verification_url,
            "invisible_characters": invisible_len,
            "overhead_percent": f"{overhead_pct:.1f}%",
        }
        if result.merkle_root:
            provenance_meta["merkle_root"] = result.merkle_root
        if result.instance_id:
            provenance_meta["instance_id"] = result.instance_id

        print(f"  Rendering PDF -> {out_path}")
        render_pdf(
            paper,
            out_path,
            signed_text=result.signed_text,
            provenance_mode=mode_label,
            provenance_meta=provenance_meta,
        )
        print(f"  Done: {out_path}")
        results_generated += 1

    print(f"\nComplete: {results_generated}/{len(modes)} PDFs generated.")
    return 0 if results_generated > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
