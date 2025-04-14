"""
Command Line Interface Example for EncypherAI

This example demonstrates how to use EncypherAI from the command line
to encode and decode metadata in text.
"""

import json
import sys
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from encypher.core.metadata_encoder import MetadataEncoder
from encypher.core.unicode_metadata import MetadataTarget


def count_metadata_occurrences(text):
    """
    Count how many times metadata appears in the text.

    Args:
        text: The text to analyze

    Returns:
        int: Number of metadata occurrences
    """
    # Count zero-width characters which are used for encoding
    zwc_count = text.count(MetadataEncoder.ZERO_WIDTH_SPACE) + text.count(MetadataEncoder.ZERO_WIDTH_NON_JOINER)

    # If there are zero-width characters, we have at least one metadata embedding
    # This is a simplified approach - in reality, we'd need to parse the text to find actual metadata blocks
    return 1 if zwc_count > 0 else 0


def encode_metadata_with_count(encoder, text, model_id, timestamp, custom_metadata, target):
    """
    Wrapper around MetadataEncoder.encode_metadata that also returns the count of embeddings.

    Returns:
        tuple: (encoded_text, embed_count)
    """
    # Create metadata dictionary first
    metadata = {
        "model_id": model_id,
        "timestamp": (timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp),
    }

    # Add custom metadata if provided
    if custom_metadata:
        metadata["custom_metadata"] = custom_metadata

    # Now call encode_metadata with the correct parameters
    # Note: MetadataEncoder doesn't accept target parameter
    encoded_text = encoder.encode_metadata(text=text, metadata=metadata)

    # Count the number of embeddings
    embed_count = count_metadata_occurrences(encoded_text)

    return encoded_text, embed_count


def encode_text(args):
    """
    Encode metadata into text.

    Args:
        args: Command line arguments
    """
    console = Console()

    # Get text from file or stdin
    if args.input_file:
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            console.print(f"[bold red]Error reading file:[/] {str(e)}")
            sys.exit(1)
    else:
        text = args.text

    # Parse custom metadata if provided
    custom_metadata = None
    if args.custom_metadata:
        try:
            custom_metadata = json.loads(args.custom_metadata)
        except json.JSONDecodeError:
            console.print("[bold red]Error:[/] Custom metadata must be a valid JSON string")
            sys.exit(1)

    # Get timestamp
    timestamp = None
    if args.timestamp:
        timestamp = datetime.fromtimestamp(args.timestamp)
    else:
        timestamp = datetime.now()

    # Parse target
    try:
        target = MetadataTarget(args.target)
    except ValueError:
        console.print(f"[bold red]Error:[/] Invalid target: {args.target}")
        sys.exit(1)

    try:
        # Encode metadata into text
        encoder = MetadataEncoder()
        encoded_text, embed_count = encode_metadata_with_count(
            encoder=encoder,
            text=text,
            model_id=args.model_id,
            timestamp=timestamp,  # Pass as datetime object
            custom_metadata=custom_metadata,
            target=target,
        )

        # Output the result
        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(encoded_text)
            console.print(f"[bold green]Success![/] Encoded text saved to {args.output_file}")
            console.print(f"[bold blue]Embedded metadata[/] {embed_count} times in the text")
        else:
            # Create a temporary file to view the encoded text
            import os
            import tempfile

            # Show a clean version of the text (original text)
            console.print("[bold green]Original Text:[/]")
            print(text)

            # Save encoded text to temp file with a consistent naming pattern
            fd, temp_path = tempfile.mkstemp(suffix="_encypher.txt")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(encoded_text)

            console.print(f"[bold green]Encoded text saved to:[/] {temp_path}")
            console.print(f"[bold blue]Embedded metadata[/] {embed_count} times in the text")
            console.print(
                "[bold yellow]Note:[/] The encoded text contains invisible Unicode characters that may not display correctly in the terminal."
            )

            # Also show metadata that was embedded
            metadata = {
                "model_id": args.model_id,
                "timestamp": timestamp.isoformat(),
            }
            if custom_metadata:
                metadata["custom"] = custom_metadata

            console.print(
                Panel(
                    Syntax(json.dumps(metadata, indent=2), "json", theme="monokai"),
                    title="[bold]Embedded Metadata[/]",
                    border_style="blue",
                )
            )

    except Exception as e:
        console.print(f"[bold red]Error encoding metadata:[/] {str(e)}")
        sys.exit(1)


def decode_text(args):
    """
    Decode metadata from text.
    """
    # Get text from file or stdin
    console = Console()

    if args.input_file:
        console.print(f"Reading from file: {args.input_file}")
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                encoded_text = f.read()
        except Exception as e:
            console.print(f"[bold red]Error reading file:[/] {str(e)}")
            sys.exit(1)
    else:
        encoded_text = args.text

    # Print debug info if requested
    if args.debug:
        console.print("Debug Info:")
        console.print(f"Text length: {len(encoded_text)}")
        # Fix the backslash issue by using regular strings instead of f-strings with escape sequences
        fe0f_count = encoded_text.count("\ufe0f")  # Standard variation selector
        e0100_count = encoded_text.count("\ue0100")  # Extended variation selector
        console.print(f"Standard variation selectors: {fe0f_count}")
        console.print(f"Extended variation selectors: {e0100_count}")

    # Count occurrences of metadata in the text
    metadata_count = count_metadata_occurrences(encoded_text)

    # Extract metadata
    decoder = MetadataEncoder()  # Use the same encoder class to decode
    metadata, clean_text = decoder.decode_metadata(encoded_text)

    # Display the results
    if not metadata:
        console.print("[bold yellow]No metadata found in the text.[/]")
        return
    else:
        console.print(f"[bold green]Found metadata[/] {metadata_count} times in the text")

        # Display metadata in a more readable format
        console.print(
            Panel(
                Syntax(json.dumps(metadata, indent=2), "json", theme="monokai"),
                title="[bold]Extracted Metadata[/]",
                border_style="blue",
            )
        )

        # Display clean text if requested
        if args.show_clean:
            console.print("\nClean text (with metadata removed):")
            console.print(clean_text)


def main():
    """Main entry point for the CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="EncypherAI CLI Example")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Encode command
    encode_parser = subparsers.add_parser("encode", help="Encode metadata into text")
    encode_parser.add_argument("--text", help="Text to encode metadata into")
    encode_parser.add_argument("--input-file", help="Input file containing text to encode")
    encode_parser.add_argument("--output-file", help="Output file to write encoded text to")
    encode_parser.add_argument("--model-id", required=True, help="Model ID to embed")
    encode_parser.add_argument("--timestamp", type=float, help="Timestamp to embed (defaults to current time)")
    encode_parser.add_argument("--custom-metadata", help="Custom metadata to embed (JSON string)")
    encode_parser.add_argument(
        "--target",
        default="whitespace",
        choices=[t.value for t in MetadataTarget],
        help="Target characters to encode metadata into",
    )

    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Decode metadata from text")
    decode_parser.add_argument("--text", help="Text to decode metadata from")
    decode_parser.add_argument("--input-file", help="Input file containing text to decode")
    decode_parser.add_argument("--debug", action="store_true", help="Show debug information")
    decode_parser.add_argument(
        "--show-clean",
        action="store_true",
        help="Show clean text with metadata removed",
    )

    # Decode from temp file command
    subparsers.add_parser("decode-temp", help="Decode metadata from the last temp file created")

    args = parser.parse_args()

    if args.command == "encode":
        if not args.text and not args.input_file:
            print("Error: Either --text or --input-file must be provided")
            sys.exit(1)
        encode_text(args)
    elif args.command == "decode":
        if not args.text and not args.input_file:
            print("Error: Either --text or --input-file must be provided")
            sys.exit(1)
        decode_text(args)
    elif args.command == "decode-temp":
        # Find the latest temp file with our suffix
        import glob
        import os
        import tempfile

        # Get all temp files with our suffix
        temp_dir = tempfile.gettempdir()
        temp_files = glob.glob(os.path.join(temp_dir, "*_encypher.txt"))

        if not temp_files:
            console = Console()
            console.print("[bold red]Error:[/] No temporary encoded files found")
            sys.exit(1)

        # Sort by modification time, newest first
        latest_temp = max(temp_files, key=os.path.getmtime)

        # Create args object with the input file
        class TempArgs:
            def __init__(self, input_file):
                self.input_file = input_file
                self.text = None

        decode_text(TempArgs(latest_temp))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
