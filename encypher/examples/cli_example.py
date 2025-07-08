"""
Command Line Interface Example for EncypherAI

This example demonstrates how to use EncypherAI from the command line
to encode and decode metadata in text.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Callable, Optional, Union

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from encypher.core.exceptions import EncypherError, PrivateKeyLoadingError, PublicKeyLoadingError
from encypher.pdf_generator import ConversionError, EncypherPDF, FontError, ImageError, PDFGenerationError
from encypher.core.keys import generate_ed25519_key_pair, load_ed25519_private_key, load_ed25519_public_key, save_ed25519_key_pair_to_files
from encypher.core.payloads import BasicPayload, ManifestPayload
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.pdf_generator import EncypherPDF, FontError, PDFGenerationError

console = Console()

# --- Key Management ---


def generate_keys_command(args):
    """Handles the 'generate-keys' command."""
    private_key, public_key = generate_ed25519_key_pair()

    private_key_path = os.path.join(args.output_dir, "private_key.pem")
    public_key_filename = f"{args.signer_id}.pem" if args.signer_id else "public_key.pem"
    public_key_path = os.path.join(args.output_dir, public_key_filename)

    os.makedirs(args.output_dir, exist_ok=True)

    try:
        save_ed25519_key_pair_to_files(private_key, public_key, private_key_path, public_key_path)
        console.print("[green]Keys generated successfully![/green]")
        console.print(f"Private key saved to: {os.path.abspath(private_key_path)}")
        console.print(f"Public key saved to: {os.path.abspath(public_key_path)}")
        if args.signer_id:
            console.print(f"Signer ID for this public key: [bold cyan]{args.signer_id}[/bold cyan]")
        console.print(
            Panel(
                (
                    f"To use these keys:\n"
                    f"- Keep the [bold red]private_key.pem[/bold red] secure and use its path with the '--private-key-file' option for encoding.\n"
                    f"- Distribute the [bold green]public key file ({public_key_filename})[/bold green] and use its directory path with the "
                    f"'--public-key-dir' option for decoding."
                ),
                title="Key Usage Instructions",
                border_style="blue",
                expand=False,
            )
        )
    except EncypherError as e:
        console.print(f"[red]Error generating or saving keys: {e}[/red]")
        sys.exit(1)


def _load_private_key(filepath: str) -> Optional[Ed25519PrivateKey]:
    try:
        return load_ed25519_private_key(filepath)
    except PrivateKeyLoadingError as e:
        console.print(f"[bold red]Error loading private key from {filepath}:[/] {e}")
        return None
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred while loading the private key from {filepath}:[/] {e}")
        return None


def _load_public_key(filepath: str) -> Optional[Ed25519PublicKey]:
    try:
        return load_ed25519_public_key(filepath)
    except PublicKeyLoadingError:
        # console.print(f"[bold red]Error loading public key from {filepath}:[/] {e}")
        return None
    except Exception:
        # console.print(f"[bold red]An unexpected error occurred while loading the public key from {filepath}:[/] {e}")
        return None


def create_public_key_provider(key_dir_path: str) -> Callable[[str], Optional[Ed25519PublicKey]]:
    """Creates a public key provider function that loads keys from a directory."""
    if not os.path.isdir(key_dir_path):
        console.print(f"[bold red]Error:[/] Public key directory '{key_dir_path}' not found or not a directory.")
        return lambda signer_id: None

    def public_key_provider_func(signer_id_to_lookup: str) -> Optional[Ed25519PublicKey]:
        key_file_path = os.path.join(key_dir_path, f"{signer_id_to_lookup}.pem")
        if os.path.exists(key_file_path):
            return _load_public_key(key_file_path)
        return None

    return public_key_provider_func


# --- Encode/Decode Logic ---


def encode_text(args):
    """Encode metadata into text using UnicodeMetadata and digital signatures."""
    if args.input_file:
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            console.print(f"[bold red]Error reading input file:[/] {e}")
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        console.print("[bold red]Error:[/] Either --text or --input-file must be provided for encoding.")
        sys.exit(1)

    private_key = _load_private_key(args.private_key_file)
    if not private_key:
        sys.exit(1)

    signer_id = args.signer_id

    timestamp_int = args.timestamp
    if timestamp_int is None:
        timestamp_int = int(datetime.now(timezone.utc).timestamp())

    custom_metadata_dict = {}
    if args.custom_metadata:
        try:
            with open(args.custom_metadata, "r", encoding="utf-8") as f:
                custom_metadata_dict = json.load(f)
        except FileNotFoundError:
            console.print(f"[bold red]Error: Custom metadata file not found: {args.custom_metadata}[/]")
            sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[bold red]Error: Invalid JSON in custom metadata file {args.custom_metadata}:[/] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Error reading custom metadata file {args.custom_metadata}:[/] {e}")
            sys.exit(1)

    if args.model_id:
        custom_metadata_dict["model_id"] = args.model_id

    try:
        console.print(f"Embedding with signer_id: {signer_id}, timestamp: {timestamp_int}")
        encoded_text = UnicodeMetadata.embed_metadata(
            text=text,
            private_key=private_key,
            signer_id=signer_id,
            custom_metadata=custom_metadata_dict,
            timestamp=timestamp_int,
        )

        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(encoded_text)
            console.print(f"[bold green]Success![/] Encoded text saved to {args.output_file}")
        else:
            console.print("[bold green]Original Text:[/]")
            print(text)
            console.print("[bold green]\nEncoded Text (contains invisible characters):[/]")
            print(encoded_text)
            timestamp_str = datetime.fromtimestamp(timestamp_int, timezone.utc).isoformat()
            panel_title = f"[bold]Custom Metadata Embedded (Signer ID: {signer_id}, Timestamp: {timestamp_str})[/]"
            console.print(
                Panel(
                    Syntax(json.dumps(custom_metadata_dict, indent=2), "json", theme="monokai"),
                    title=panel_title,
                    border_style="blue",
                )
            )

    except Exception as e:
        console.print(f"[bold red]Error encoding metadata:[/] {e}")
        sys.exit(1)


def decode_text(args):
    """Decode and verify metadata from text using UnicodeMetadata."""
    if args.input_file:
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                encoded_text = f.read()
        except Exception as e:
            console.print(f"[bold red]Error reading input file:[/] {e}")
            sys.exit(1)
    elif args.text:
        encoded_text = args.text
    else:
        console.print("[bold red]Error:[/] Either --text or --input-file must be provided for decoding.")
        sys.exit(1)

    public_key_provider = create_public_key_provider(args.public_key_dir)

    try:
        is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(text=encoded_text, public_key_resolver=public_key_provider)

        if is_valid:
            console.print("[bold green]Success: Signature is valid![/]")
            console.print(f"  [bold]Signer ID:[/bold] {signer_id}")
            if payload:
                console.print(
                    Panel(
                        Syntax(json.dumps(payload, indent=2), "json", theme="monokai"),
                        title="[bold]Verified Payload[/]",
                        border_style="green",
                    )
                )
            else:
                console.print("[yellow]No payload was extracted.[/yellow]")
        else:
            console.print("[bold red]Failure: Signature is invalid or metadata not found.[/]")
            if signer_id:
                console.print(f"  [bold]Signer ID found in text:[/bold] {signer_id} (but verification failed)")

    except Exception as e:
        console.print(f"[bold red]Error decoding metadata:[/] {e}")
        sys.exit(1)


def convert_to_pdf(args):
    """Convert text to PDF with embedded metadata."""
    try:
        # Read input text (unless it's a docx)
        text = None
        if args.input_file:
            with open(args.input_file, "r", encoding="utf-8") as f:
                text = f.read()
        elif args.text:
            text = args.text
        elif not args.docx_file:
            console.print("[bold red]Error:[/] Either --text, --input-file, or --docx-file must be provided.")
            sys.exit(1)

        # Load private key
        private_key = _load_private_key(args.private_key_file)
        if not private_key:
            sys.exit(1)

        # Set timestamp
        timestamp = args.timestamp or int(datetime.now(timezone.utc).timestamp())
        
        # Set target for metadata embedding
        target = None
        if args.target:
            if args.target == "whitespace":
                target = MetadataTarget.WHITESPACE
            elif args.target == "first_letter":
                target = MetadataTarget.FIRST_LETTER
            elif args.target == "punctuation":
                target = MetadataTarget.PUNCTUATION
            elif args.target == "all":
                target = MetadataTarget.ALL

        # Prepare image data if provided
        images = None
        if args.image_path:
            images = [{
                "path": args.image_path,
                "x": args.image_x,
                "y": args.image_y,
                "width": args.image_width,
                "height": args.image_height,
                "preserve_aspect_ratio": not args.no_preserve_aspect_ratio,
            }]

        # Prepare margins if provided
        margins = None
        if any(m != 1.0 for m in [args.margin_left, args.margin_right, args.margin_top, args.margin_bottom]):
            from reportlab.lib.units import inch

            margins = {
                "left": args.margin_left * inch,
                "right": args.margin_right * inch,
                "top": args.margin_top * inch,
                "bottom": args.margin_bottom * inch,
            }

        # Generate the PDF
        if args.docx_file:
            output_path = EncypherPDF.from_docx(
                docx_file=args.docx_file,  # Note: parameter is docx_file, not docx_path
                output_file=args.output_file,  # Note: parameter is output_file, not output_path
                private_key=private_key,
                signer_id=args.signer_id,
                timestamp=timestamp,
                target=target,  # Add target parameter
                metadata_format=args.metadata_format,
                font_path=args.font_path,
                font_size=args.font_size,
                images=images,
                margins=margins,
            )
            console.print(f"[bold green]Success:[/bold green] Word document converted to PDF at {output_path}")
        else:
            output_path = EncypherPDF.from_text(
                text=text,
                output_file=args.output_file,  # Note: parameter is output_file, not output_path
                private_key=private_key,
                signer_id=args.signer_id,
                timestamp=timestamp,
                target=target,  # Add target parameter
                metadata_format=args.metadata_format,
                font_path=args.font_path,
                font_size=args.font_size,
                images=images,
                margins=margins,
            )
            console.print(f"[bold green]Success:[/bold green] PDF created at {output_path}")
    except (PDFGenerationError, FontError, ImageError, ConversionError) as e:
        console.print(f"[bold red]Error generating PDF:[/] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/] {e}")
        sys.exit(1)

# --- Main CLI Parsing ---

def main():
    parser = argparse.ArgumentParser(description="EncypherAI CLI - Encode and Decode Unicode Metadata with Digital Signatures.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Generate Keys Command ---
    parser_gen_keys = subparsers.add_parser("generate-keys", help="Generate Ed25519 key pair.")
    parser_gen_keys.add_argument("--output-dir", type=str, default=".", help="Directory to save the key files (default: current directory).")
    parser_gen_keys.add_argument("--signer-id", type=str, help="Optional signer ID. If provided, public key will be named <signer-id>.pem.")
    parser_gen_keys.set_defaults(func=generate_keys_command)

    # --- Encode Command ---
    parser_encode = subparsers.add_parser("encode", help="Encode metadata into text.")
    group_encode_input = parser_encode.add_mutually_exclusive_group(required=True)
    group_encode_input.add_argument("--text", type=str, help="Text to encode metadata into.")
    group_encode_input.add_argument("--input-file", type=str, help="Path to a UTF-8 text file to encode metadata into.")
    parser_encode.add_argument("--output-file", type=str, help="Path to save the encoded text. If not provided, prints to stdout.")
    parser_encode.add_argument("--private-key-file", type=str, required=True, help="Path to the Ed25519 private key PEM file.")
    parser_encode.add_argument("--signer-id", type=str, required=True, help="Signer ID (key identifier) associated with the private key.")
    parser_encode.add_argument("--timestamp", type=int, help="Optional. Integer Unix timestamp (seconds since epoch). Defaults to current time.")
    parser_encode.add_argument(
        "--custom-metadata",
        type=str,
        default=None,
        help="Path to a JSON file containing custom metadata.",
    )
    parser_encode.add_argument(
        "--model-id", type=str, help="Optional. Model ID to include in metadata (convenience, will be part of custom_metadata)."
    )
    parser_encode.set_defaults(func=encode_text)

    # --- Decode Command ---
    parser_decode = subparsers.add_parser("decode", help="Decode and verify metadata from text.")
    group_decode_input = parser_decode.add_mutually_exclusive_group(required=True)
    group_decode_input.add_argument("--text", type=str, help="Text to decode metadata from.")
    group_decode_input.add_argument("--input-file", type=str, help="Path to a UTF-8 text file to decode metadata from.")
    parser_decode.add_argument("--public-key-dir", type=str, required=True, help="Directory containing public key PEM files (e.g., <signer-id>.pem).")
    parser_decode.set_defaults(func=decode_text)
    
    # --- Convert to PDF Command ---
    parser_pdf = subparsers.add_parser("convert-to-pdf", help="Convert a text file or Word document to a PDF with embedded metadata")
    group_pdf_input = parser_pdf.add_mutually_exclusive_group(required=True)
    group_pdf_input.add_argument("--text", type=str, help="Text to convert to PDF")
    group_pdf_input.add_argument("--input-file", type=str, help="Input text file to convert to PDF")
    group_pdf_input.add_argument("--docx-file", type=str, help="Input Word document (.docx) file to convert to PDF")
    parser_pdf.add_argument("--output-file", required=True, help="Output PDF file path")
    parser_pdf.add_argument("--private-key-file", type=str, required=True, help="Path to private key file")
    parser_pdf.add_argument("--signer-id", type=str, required=True, help="Signer ID for metadata")
    parser_pdf.add_argument("--timestamp", type=int, help="Timestamp for metadata (default: current time)")
    parser_pdf.add_argument(
        "--target",
        type=str,
        choices=["whitespace", "first_letter", "punctuation", "all"],
        default="whitespace",
        help="Where to embed metadata (default: whitespace)"
    )
    parser_pdf.add_argument(
        "--metadata-format",
        type=str,
        choices=["basic", "manifest", "cbor_manifest", "c2pa_v2_2"],
        default="c2pa_v2_2",
        help="Metadata format to use (default: c2pa_v2_2)."
    )
    parser_pdf.add_argument("--font-path", type=str, help="Path to a TrueType font file")
    parser_pdf.add_argument("--font-size", type=int, default=12, help="Font size in points (default: 12)")
    # Margin settings
    parser_pdf.add_argument(
        "--margin-left", type=float, default=1.0, help="Left margin in inches (default: 1.0)"
    )
    parser_pdf.add_argument(
        "--margin-right", type=float, default=1.0, help="Right margin in inches (default: 1.0)"
    )
    parser_pdf.add_argument(
        "--margin-top", type=float, default=1.0, help="Top margin in inches (default: 1.0)"
    )
    parser_pdf.add_argument(
        "--margin-bottom", type=float, default=1.0, help="Bottom margin in inches (default: 1.0)"
    )
    # Image settings
    parser_pdf.add_argument(
        "--image-path", type=str, help="Path to an image file to embed in the PDF"
    )
    parser_pdf.add_argument(
        "--image-x", type=float, default=72, help="X position of the image in points (default: 72)"
    )
    parser_pdf.add_argument(
        "--image-y", type=float, default=400, help="Y position of the image in points (default: 400)"
    )
    parser_pdf.add_argument(
        "--image-width", type=float, help="Width of the image in points"
    )
    parser_pdf.add_argument(
        "--image-height", type=float, help="Height of the image in points"
    )
    parser_pdf.add_argument(
        "--no-preserve-aspect-ratio", action="store_true", help="Do not preserve aspect ratio of the image"
    )
    parser_pdf.set_defaults(func=convert_to_pdf)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
