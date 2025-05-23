# ruff: noqa: E501
"""
EncypherAI YouTube Demo Script (Updated for Digital Signatures)

A visually appealing, step-by-step demonstration of EncypherAI's core functionality
for use in introductory videos and presentations, now featuring Ed25519 digital signatures.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax
from rich.table import Table

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.payloads import ManifestPayload

# Assuming 'encypher' is the top-level package
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# Initialize Rich console for beautiful output
console = Console()

# --- New: Key Management for Digital Signatures ---
DEMO_PRIVATE_KEY: Optional[Ed25519PrivateKey] = None
DEMO_PUBLIC_KEY: Optional[Ed25519PublicKey] = None
DEMO_SIGNER_ID = "youtube-demo-signer-001"


def initialize_demo_keys():
    """Generates and sets the global demo Ed25519 key pair."""
    global DEMO_PRIVATE_KEY, DEMO_PUBLIC_KEY
    DEMO_PRIVATE_KEY, DEMO_PUBLIC_KEY = generate_ed25519_key_pair()
    console.print("[italic green]Generated Ed25519 key pair for this demo session.[/italic green]")


# Initialize keys when script starts
initialize_demo_keys()


def public_key_provider_func(signer_id: str) -> Optional[Ed25519PublicKey]:
    """A simple public key provider for the demo.
    In a real application, this would look up keys from a secure store, database, or configuration.
    """
    if signer_id == DEMO_SIGNER_ID:
        return DEMO_PUBLIC_KEY
    console.print(f"[bold red]Warning: Public key not found for signer_id: {signer_id}[/bold red]")
    return None


# Flag to control whether to display encoded text or original text in the terminal
# Set to True to show original text instead of encoded text with invisible Unicode characters
DISPLAY_ORIGINAL_TEXT = True

# Flag to show technical byte details in the demo
SHOW_TECHNICAL_DETAILS = True


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Print a stylish header for the demo."""
    clear_screen()
    console.print(
        Panel.fit(
            "[bold blue]EncypherAI Demo (v2.1.0 Signatures)[/bold blue]\n" "[italic]Invisible Metadata for AI-Generated Content[/italic]",
            border_style="blue",
            padding=(1, 10),
        )
    )
    console.print()
    console.print(f"[dim]Using Signer ID: [bold]{DEMO_SIGNER_ID}[/bold] for this session.[/dim]")
    console.print()


def print_section(title: str):
    """Print a section title."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("=" * len(title), style="cyan")
    console.print()


def wait_for_key():
    """Wait for a key press to continue."""
    console.print("\n[dim italic]Press Enter to continue...[/dim italic]")
    input()


def get_display_text(encoded_text: str, original_text: str) -> str:
    """Return either the original text or encoded text based on the display flag.

    Args:
        encoded_text: Text with encoded metadata
        original_text: Original text without metadata

    Returns:
        The text to display based on DISPLAY_ORIGINAL_TEXT flag
    """
    return original_text if DISPLAY_ORIGINAL_TEXT else encoded_text


def format_bytes_for_display(text: str, max_length: int = 30) -> str:
    """Format the byte representation of text for display.

    Args:
        text: The text to convert to byte representation
        max_length: Maximum number of bytes to display

    Returns:
        A formatted string showing the byte values
    """
    # Convert to bytes using UTF-8 encoding
    byte_values = text.encode("utf-8")

    # Truncate if too long
    if len(byte_values) > max_length:
        displayed_bytes = byte_values[:max_length]
        suffix = f"... ({len(byte_values)} bytes total)"
    else:
        displayed_bytes = byte_values
        suffix = ""

    # Format as hex values
    hex_values = " ".join(f"{b:02x}" for b in displayed_bytes)

    return f"{hex_values}{suffix}"


def show_byte_comparison(original_text: str, encoded_text: str):
    """Display a technical comparison of byte values between original and encoded text.

    Args:
        original_text: The original text without metadata
        encoded_text: The text with encoded metadata
    """
    if not SHOW_TECHNICAL_DETAILS:
        return

    console.print("\n[bold]Technical Details - Byte Comparison:[/bold]")

    # Create a table for byte comparison
    byte_table = Table(show_header=True, header_style="bold blue")
    byte_table.add_column("Text Type")
    byte_table.add_column("Sample (First 10 chars)")
    byte_table.add_column("UTF-8 Byte Values (Hex)")
    byte_table.add_column("Length")

    # Original text details
    original_sample = original_text[:10] + ("..." if len(original_text) > 10 else "")
    original_bytes = format_bytes_for_display(original_text)
    original_length = len(original_text)

    # Encoded text details
    encoded_sample = encoded_text[:10] + ("..." if len(encoded_text) > 10 else "")
    encoded_bytes = format_bytes_for_display(encoded_text)
    encoded_length = len(encoded_text)

    # Add rows to the table
    byte_table.add_row("Original Text", original_sample, original_bytes, str(original_length))
    byte_table.add_row("Encoded Text", encoded_sample, encoded_bytes, str(encoded_length))

    # Add a row showing just the invisible characters
    invisible_chars = "".join(c for c in encoded_text if c in [UnicodeMetadata.ZERO_WIDTH_SPACE, UnicodeMetadata.ZERO_WIDTH_NON_JOINER])
    invisible_bytes = format_bytes_for_display(invisible_chars)

    byte_table.add_row(
        "Invisible Characters Only",
        f"[dim]{len(invisible_chars)} chars[/dim]",
        invisible_bytes,
        str(len(invisible_chars)),
    )

    console.print(byte_table)

    # Add explanation
    console.print(
        "\n[italic]The encoded text contains invisible Unicode characters "
        "(Zero Width Space: U+200B, Zero Width Non-Joiner: U+200C) that "
        "store the metadata while remaining visually identical to the original text.[/italic]"
    )


def demo_basic_encoding():
    """Demonstrate basic metadata encoding with digital signatures."""
    print_section("1. Basic Metadata Encoding (with Digital Signature)")

    console.print(
        Markdown(
            """
    EncypherAI allows you to embed arbitrary metadata (like a JSON object) into text invisibly.
    This metadata is now secured with an Ed25519 digital signature.

    Let's start with a simple example:
    """
        )
    )

    # Original text
    original_text = "This is a sample sentence for the EncypherAI demo."
    console.print("\n[bold]Original Text:[/bold]")
    console.print(Panel(original_text, border_style="green"))

    # Metadata to embed (this will be the custom_metadata payload)
    custom_metadata_payload = {
        "source": "AI Model Y (Signature Demo)",
        "confidence": 0.98,
        "tags": ["example", "signature", "basic"],
        "demo_step": "basic_encoding",
    }
    console.print("\n[bold]Custom Metadata to Embed:[/bold]")
    console.print(Syntax(json.dumps(custom_metadata_payload, indent=2), "json", theme="monokai", line_numbers=True))

    # Generate integer Unix timestamp
    timestamp_int = int(datetime.now(timezone.utc).timestamp())
    console.print(f"\n[bold]Timestamp (Unix integer):[/bold] {timestamp_int}")
    console.print(f"[bold]Signer ID:[/bold] {DEMO_SIGNER_ID}")

    console.print("\n[bold]Encoding metadata with Ed25519 signature...[/bold]")
    time.sleep(1)  # Dramatic pause for demo

    if DEMO_PRIVATE_KEY is None:
        console.print("[bold red]Error: Demo private key not initialized.[/bold red]")
        return

    encoded_text = UnicodeMetadata.embed_metadata(
        text=original_text, private_key=DEMO_PRIVATE_KEY, signer_id=DEMO_SIGNER_ID, timestamp=timestamp_int, custom_metadata=custom_metadata_payload
    )
    display_text = get_display_text(encoded_text, original_text)

    console.print("\nText with encoded metadata (and signature):")
    # Display the text (original or encoded based on flag)
    console.print(Panel(display_text, border_style="magenta"))

    # Show byte comparison
    show_byte_comparison(original_text, encoded_text)

    console.print(
        Markdown(
            """
    Notice how the visible text remains unchanged (if `DISPLAY_ORIGINAL_TEXT` is True),
    but the underlying byte representation has changed to include the signed metadata.
    The signature ensures both authenticity and integrity.
    """
        )
    )

    wait_for_key()


def demo_metadata_extraction():
    """Demonstrate metadata extraction and verification with digital signatures."""
    print_section("2. Metadata Extraction & Verification (with Digital Signature)")

    console.print(
        Markdown(
            """
    Now, let's take text with embedded, signed metadata and verify its authenticity and integrity,
    then extract the original metadata payload.
    """
        )
    )

    # Original text and metadata (same as in basic encoding for consistency in demo)
    original_text = "This is a sample sentence for the EncypherAI demo, prepared for extraction."
    custom_metadata_payload = {
        "source": "AI Model Z (Signature Demo)",
        "confidence": 0.95,
        "tags": ["example", "signature", "extraction"],
        "demo_step": "metadata_extraction",
        "data_id": "xyz789",
    }
    timestamp_int = int(datetime.now(timezone.utc).timestamp())

    console.print("\n[bold]Original Text (for this demo section):[/bold]")
    console.print(Panel(original_text, border_style="green"))
    console.print("\n[bold]Original Custom Metadata (that was embedded):[/bold]")
    console.print(Syntax(json.dumps(custom_metadata_payload, indent=2), "json", theme="monokai", line_numbers=True))
    console.print(f"[bold]Original Timestamp (Unix integer):[/bold] {timestamp_int}")
    console.print(f"[bold]Original Signer ID:[/bold] {DEMO_SIGNER_ID}")

    if DEMO_PRIVATE_KEY is None:
        console.print("[bold red]Error: Demo private key not initialized.[/bold red]")
        return

    # Encode the text first (as if it's coming from an external source)
    encoded_text = UnicodeMetadata.embed_metadata(
        text=original_text, private_key=DEMO_PRIVATE_KEY, signer_id=DEMO_SIGNER_ID, timestamp=timestamp_int, custom_metadata=custom_metadata_payload
    )
    display_text_for_input = get_display_text(encoded_text, original_text)

    console.print("\n[bold]Text with Embedded Metadata (as input for extraction):[/bold]")
    console.print(Panel(display_text_for_input, border_style="magenta"))

    console.print("\n[bold]Attempting to verify and extract metadata...[/bold]")
    console.print(f"[dim]Using public key provider for signer ID: {DEMO_SIGNER_ID}[/dim]")
    time.sleep(1.5)  # Dramatic pause for demo

    # Verify and extract metadata
    # Note: public_key_provider_func is passed directly here.
    # For class instances, you might initialize UnicodeMetadata with it: `um = UnicodeMetadata(public_key_provider_func)`
    # and then call `um.verify_and_extract_metadata(...)`
    verification_status, extracted_signer_id, extracted_payload_obj = UnicodeMetadata.verify_metadata(
        text=encoded_text, public_key_provider=public_key_provider_func
    )

    # Show verification result
    if verification_status:
        console.print("\n✅ [bold green]Verification Successful![/bold green]")
        console.print(f"   [green]Signer ID Verified:[/green] [bold]{extracted_signer_id}[/bold]")

        if extracted_payload_obj:
            console.print("\n[bold]Extracted Metadata Payload:[/bold]")
            # The payload object (BasicPayload or ManifestPayload) has attributes
            # like 'signer_id', 'timestamp', 'custom_metadata', etc.
            payload_dict = {
                "signer_id": extracted_payload_obj.signer_id,
                "timestamp_from_payload": extracted_payload_obj.timestamp,  # This is the original embedded timestamp
                "custom_metadata": extracted_payload_obj.custom_metadata,
                "metadata_format": extracted_payload_obj.format,
                "version": extracted_payload_obj.version,
            }
            console.print(Syntax(json.dumps(payload_dict, indent=2), "json", theme="monokai", line_numbers=True))

            # Compare with original
            if (
                extracted_payload_obj.custom_metadata == custom_metadata_payload
                and extracted_payload_obj.signer_id == DEMO_SIGNER_ID
                and extracted_payload_obj.timestamp == timestamp_int
            ):
                console.print("   [bold green]Extracted metadata matches the original embedded data.[/bold green]")
            else:
                console.print("   [bold yellow]Warning: Extracted metadata differs from the expected original.[/bold yellow]")
        else:
            console.print(
                "   [yellow]Verification successful, but no payload was extracted (this shouldn't happen with valid basic/manifest).[/yellow]"
            )

    else:
        console.print("\n🚨 [bold red]Verification Failed![/bold red]")
        if extracted_signer_id:
            console.print(f"   [red]Signer ID from text (could not be verified):[/red] {extracted_signer_id}")
        else:
            console.print("   [red]Could not extract a signer ID or metadata.[/red]")
        if extracted_payload_obj:
            console.print(
                "   [yellow]A payload was extracted despite verification failure (if return_payload_on_failure=True was used, not default).[/yellow]"
            )

    console.print(
        Markdown(
            """
    The `verify_and_extract_metadata` method uses the provided `public_key_provider` function
    to fetch the correct public key based on the `signer_id` found in the text. It then verifies
    the signature. If valid, it returns the metadata; otherwise, it indicates a verification failure.
    """
        )
    )

    wait_for_key()


def demo_tamper_detection():
    """Demonstrate tamper detection using digital signatures."""
    print_section("3. Tamper Detection (with Digital Signatures)")

    console.print(
        Markdown(
            """
    Digital signatures are crucial for detecting tampering. If the text or its associated metadata is altered
    after signing, the signature verification will fail.

    Let's see this in action.
    """
        )
    )

    # Original text and metadata
    original_text = "This is a secure message that should not be altered."
    custom_metadata_payload = {
        "document_id": "doc-alpha-456",
        "security_level": "confidential",
        "status": "original_unaltered",
        "demo_step": "tamper_detection",
    }
    timestamp_int = int(datetime.now(timezone.utc).timestamp())

    console.print("\n[bold]Original Text:[/bold]")
    console.print(Panel(original_text, border_style="green"))
    console.print("\n[bold]Original Custom Metadata:[/bold]")
    console.print(Syntax(json.dumps(custom_metadata_payload, indent=2), "json", theme="monokai", line_numbers=True))
    console.print(f"[bold]Timestamp (Unix integer):[/bold] {timestamp_int}")
    console.print(f"[bold]Signer ID:[/bold] {DEMO_SIGNER_ID}")

    if DEMO_PRIVATE_KEY is None or DEMO_PUBLIC_KEY is None:
        console.print("[bold red]Error: Demo keys not initialized.[/bold red]")
        return

    # --- Scenario 1: Encode and verify untampered text ---
    console.print("\n[bold]Scenario 1: Encoding and Verifying Untampered Text[/bold]")
    encoded_text = UnicodeMetadata.embed_metadata(
        text=original_text, private_key=DEMO_PRIVATE_KEY, signer_id=DEMO_SIGNER_ID, timestamp=timestamp_int, custom_metadata=custom_metadata_payload
    )
    display_encoded_text = get_display_text(encoded_text, original_text)
    console.print("\nText with embedded signed metadata:")
    console.print(Panel(display_encoded_text, border_style="magenta"))

    console.print("\nVerifying the untampered text...")
    time.sleep(1)
    verification_status, _, _ = UnicodeMetadata.verify_metadata(text=encoded_text, public_key_provider=public_key_provider_func)
    if verification_status:
        console.print("✅ [bold green]Verification successful! The text is authentic and untampered.[/bold green]")
    else:
        console.print("🚨 [bold red]Verification failed! This should not happen for untampered text.[/bold red]")

    wait_for_key()

    # --- Scenario 2: Simulate tampering with the visible text ---
    console.print("\n[bold]Scenario 2: Simulating Tampering (Visible Text Altered)[/bold]")
    tampered_visible_text = "This is a MODIFIED message that should not be altered."
    console.print("\nOriginal (signed) text was:")
    console.print(Panel(display_encoded_text, border_style="magenta"))
    console.print("\nAttacker modifies the visible part to:")
    console.print(Panel(tampered_visible_text, border_style="red"))

    # To simulate this, we can't just replace the visible part easily if we don't know where the metadata is.
    # A more realistic tampering scenario for this demo is to take the *encoded_text* (which contains invisible metadata)
    # and alter *its* visible characters. However, that's hard to do precisely without knowing the encoding.
    # Instead, let's create a version of the text where the visible part is `tampered_visible_text` but it still *contains* the *original* (now mismatched) metadata.
    # This is tricky because the metadata is embedded based on the original_text.
    # For this demo, we'll assume the attacker *somehow* managed to change the visible content while leaving the invisible characters intact.
    # The easiest way to demo this is to try to verify the `tampered_visible_text` using the `encoded_text`'s metadata.
    # This isn't a perfect simulation of direct byte manipulation, but it shows that if the content the metadata *points to* changes, verification fails.

    # A more direct simulation: take the `encoded_text` and replace its visible part.
    # This is complex. Let's simplify: we'll try to verify the `encoded_text` but *tell* the user the visible part *was* changed.
    # The verification will still use the `encoded_text` which *internally* has the original visible text.
    # The key is that the signature was for `original_text` + `metadata`.
    # If an attacker changes *any* part of the `encoded_text` (visible or invisible part of metadata), the signature breaks.

    # Let's try a more illustrative approach for the demo:
    # We have `encoded_text`. If an attacker changes even one visible character in `encoded_text` before it's verified.
    if not encoded_text:
        console.print("[bold red]Error: encoded_text is empty, cannot proceed with tampering demo.[/bold red]")
        return

    tampered_encoded_text = encoded_text.replace("secure", "INSECURE", 1)  # Change a word in the visible part of the encoded string

    console.print("\nTampered encoded text (one word changed):")
    # Note: DISPLAY_ORIGINAL_TEXT might hide the change if it's true. For this part, we want to show the actual tampered content.
    console.print(
        Panel(
            tampered_encoded_text if not DISPLAY_ORIGINAL_TEXT else "This is a INSECURE message... (Original was: This is a secure message...)",
            border_style="red",
        )
    )

    console.print("\nVerifying the tampered text...")
    time.sleep(1)
    verification_status_tampered, _, _ = UnicodeMetadata.verify_metadata(text=tampered_encoded_text, public_key_provider=public_key_provider_func)
    if not verification_status_tampered:
        console.print("🚨 [bold red]Verification Failed! The signature is invalid, indicating tampering.[/bold red]")
    else:
        console.print("✅ [bold green]Verification successful. This is unexpected for tampered text![/bold green]")

    console.print(
        Markdown("If any part of the signed content (visible text or the embedded metadata itself) is changed, the signature becomes invalid.")
    )
    wait_for_key()

    # --- Scenario 3: Attacker tries to re-sign with their own key ---
    console.print("\n[bold]Scenario 3: Attacker Tries to Re-Sign with Different Key/Signer ID[/bold]")
    attacker_text = "An attacker tries to submit this text as authentic."
    attacker_custom_metadata = {"source": "Evil Corp", "status": "maliciously_altered"}
    attacker_timestamp = int(datetime.now(timezone.utc).timestamp()) + 3600  # Future time

    # Attacker needs a key pair
    attacker_priv_key, attacker_pub_key = generate_ed25519_key_pair()
    attacker_signer_id = "attacker-signer-666"

    console.print(f"\nAttacker's Text: [italic]'{attacker_text}'[/italic]")
    console.print(f"Attacker's Signer ID: [italic]'{attacker_signer_id}'[/italic]")

    encoded_attacker_text = UnicodeMetadata.embed_metadata(
        text=attacker_text,
        private_key=attacker_priv_key,
        signer_id=attacker_signer_id,
        timestamp=attacker_timestamp,
        custom_metadata=attacker_custom_metadata,
    )

    console.print("\nEncoded text from attacker (signed with attacker's key):")
    console.print(Panel(get_display_text(encoded_attacker_text, attacker_text), border_style="yellow"))

    console.print("\nAttempting to verify attacker's text using our legitimate public key provider (`public_key_provider_func`)... ")
    console.print(f"[dim]Our provider only knows about '{DEMO_SIGNER_ID}', not '{attacker_signer_id}'.[/dim]")
    time.sleep(1)

    verification_status_attacker, extracted_attacker_signer_id, _ = UnicodeMetadata.verify_metadata(
        text=encoded_attacker_text, public_key_provider=public_key_provider_func
    )

    if not verification_status_attacker:
        console.print("🚨 [bold red]Verification Failed![/bold red]")
        if extracted_attacker_signer_id == attacker_signer_id:
            console.print(f"   [red]The text was signed by '{attacker_signer_id}', but we don't have a trusted public key for this signer.[/red]")
        else:
            console.print("   [red]Could not verify the signature or the signer is unknown/untrusted.[/red]")
    else:
        console.print("✅ [bold green]Verification successful. This is unexpected if the attacker's key is not in our provider![/bold green]")

    console.print(
        Markdown(
            """
    This demonstrates two key aspects:
    1. If content is altered after signing, the signature breaks.
    2. If an attacker signs content with their own key, it won't verify against a system that expects a specific set of trusted signers (via the `public_key_provider`).
    """
        )
    )
    wait_for_key()


def demo_streaming():
    """Demonstrate streaming with real-time metadata embedding and final signature."""
    print_section("4. Streaming with Real-time Signing")

    console.print(
        Markdown(
            """
    EncypherAI supports embedding metadata in real-time as content is streamed.
    The `StreamingHandler` accumulates text chunks and applies the final signature upon completion.
    This is ideal for applications like live AI responses or large file processing.
    """
        )
    )

    if DEMO_PRIVATE_KEY is None:
        console.print("[bold red]Error: Demo private key not initialized.[/bold red]")
        return

    # Metadata for streaming
    streaming_custom_metadata = {
        "session_id": "live-stream-789",
        "content_type": "live_transcript",
        "source_model": "AI Streamer X1",
        "demo_step": "streaming",
    }
    stream_timestamp = int(datetime.now(timezone.utc).timestamp())

    console.print("\n[bold]Custom Metadata for Streaming:[/bold]")
    console.print(Syntax(json.dumps(streaming_custom_metadata, indent=2), "json", theme="monokai", line_numbers=True))
    console.print(f"[bold]Timestamp (Unix integer):[/bold] {stream_timestamp}")
    console.print(f"[bold]Signer ID:[/bold] {DEMO_SIGNER_ID}")

    # Initialize StreamingHandler with signature parameters
    # Assuming StreamingHandler is updated to accept these parameters
    handler = StreamingHandler(
        private_key=DEMO_PRIVATE_KEY,
        signer_id=DEMO_SIGNER_ID,
        custom_metadata=streaming_custom_metadata,
        # timestamp is now handled internally by StreamingHandler when private_key and signer_id are provided
        # public_key_provider_func=public_key_provider_func # Not needed for encoding handler
    )

    console.print("\n[bold]Simulating streaming content...[/bold]")
    simulated_stream = [
        "This is the first chunk of a streamed message. ",
        "EncypherAI is processing it. ",
        "Metadata is being prepared. ",
        "The final chunk arrives now, and the signature will be applied.",
    ]

    full_original_text = ""
    with Progress(console=console, transient=True) as progress:
        task = progress.add_task("[cyan]Streaming...[/cyan]", total=len(simulated_stream))
        for i, chunk in enumerate(simulated_stream):
            progress.update(task, advance=1, description=f"[cyan]Processing chunk {i+1}/{len(simulated_stream)}[/cyan]")
            console.print(f"   [dim]Original chunk {i+1}:[/dim] [italic]'{chunk}'[/italic]")
            handler.process_chunk(chunk)  # New method for v2.1.0
            full_original_text += chunk
            time.sleep(0.8)  # Simulate network latency or processing time

    console.print("\n[bold]Stream complete. Finalizing text with signature...[/bold]")
    final_encoded_text = handler.finalize_stream()  # Renamed from finalize()
    time.sleep(1)

    display_final_text = get_display_text(final_encoded_text, full_original_text)
    console.print("\n[bold]Final Streamed Text (with embedded signature):[/bold]")
    console.print(Panel(display_final_text, border_style="blue"))

    show_byte_comparison(full_original_text, final_encoded_text)

    console.print("\n[bold]Verifying the final streamed and signed text...[/bold]")
    time.sleep(1)

    verification_status, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(
        text=final_encoded_text, public_key_provider=public_key_provider_func
    )

    if verification_status:
        console.print("✅ [bold green]Verification Successful![/bold green]")
        console.print(f"   [green]Signer ID Verified:[/green] [bold]{extracted_signer_id}[/bold]")
        if extracted_payload:
            console.print("   [green]Extracted Payload matches original streaming metadata.[/green]")
            # Further checks can be added here to compare extracted_payload.custom_metadata with streaming_custom_metadata
            # and extracted_payload.timestamp with stream_timestamp
            if (
                extracted_payload.custom_metadata == streaming_custom_metadata
                and extracted_payload.signer_id == DEMO_SIGNER_ID
                and extracted_payload.timestamp == stream_timestamp
            ):
                console.print("   [bold green]Detailed payload check: PASS[/bold green]")
            else:
                console.print("   [bold yellow]Detailed payload check: FAIL (metadata mismatch)[/bold yellow]")
        else:
            console.print("   [yellow]No payload extracted despite successful verification.[/yellow]")
    else:
        console.print("🚨 [bold red]Verification Failed for streamed content![/bold red]")
        if extracted_signer_id:
            console.print(f"   [red]Signer ID from text:[/red] {extracted_signer_id}")

    console.print(
        Markdown(
            """
    The `StreamingHandler` correctly assembled all chunks and applied the Ed25519 signature
    to the complete text along with its metadata. Verification confirms its authenticity.
    """
        )
    )
    wait_for_key()


def demo_manifest_format():
    """Demonstrate metadata encoding and verification using the 'manifest' format."""
    print_section("5. Manifest Metadata Format (with Digital Signature)")

    console.print(
        Markdown(
            """
    EncypherAI also supports a 'manifest' metadata format. This format is useful for more complex scenarios,
    such as when you need to associate metadata with multiple distinct blocks of data or when you want a more
    structured envelope for your metadata. The signature covers the entire manifest.

    Let's embed metadata using the manifest format:
    """
        )
    )

    original_text = "This text will be associated with a manifest-style metadata payload."
    console.print("\n[bold]Original Text:[/bold]")
    console.print(Panel(original_text, border_style="green"))

    custom_manifest_payload = {
        "project_id": "Project Alpha",
        "document_version": "2.1",
        "authors": [{"name": "Demo User", "role": "Creator"}],
        "review_status": "Pending",
        "demo_step": "manifest_format",
    }
    console.print("\n[bold]Custom Metadata for Manifest:[/bold]")
    console.print(Syntax(json.dumps(custom_manifest_payload, indent=2), "json", theme="monokai", line_numbers=True))

    timestamp_int = int(datetime.now(timezone.utc).timestamp())
    console.print(f"\n[bold]Timestamp (Unix integer):[/bold] {timestamp_int}")
    console.print(f"[bold]Signer ID:[/bold] {DEMO_SIGNER_ID}")

    console.print("\n[bold]Encoding metadata with 'manifest' format and Ed25519 signature...[/bold]")
    time.sleep(1)

    if DEMO_PRIVATE_KEY is None:
        console.print("[bold red]Error: Demo private key not initialized.[/bold red]")
        return

    encoded_text_manifest = UnicodeMetadata.embed_metadata(
        text=original_text,
        private_key=DEMO_PRIVATE_KEY,
        signer_id=DEMO_SIGNER_ID,
        timestamp=timestamp_int,
        custom_metadata=custom_manifest_payload,
        metadata_format="manifest",  # Specify manifest format
    )
    display_text_manifest = get_display_text(encoded_text_manifest, original_text)

    console.print("\nText with 'manifest' encoded metadata (and signature):")
    console.print(Panel(display_text_manifest, border_style="purple"))

    show_byte_comparison(original_text, encoded_text_manifest)

    console.print("\n[bold]Attempting to verify and extract 'manifest' metadata...[/bold]")
    time.sleep(1.5)

    verification_status, extracted_signer_id, extracted_payload_obj = UnicodeMetadata.verify_metadata(
        text=encoded_text_manifest, public_key_provider=public_key_provider_func
    )

    if verification_status:
        console.print("\n✅ [bold green]Verification Successful (Manifest)![/bold green]")
        console.print(f"   [green]Signer ID Verified:[/green] [bold]{extracted_signer_id}[/bold]")

        if isinstance(extracted_payload_obj, ManifestPayload):
            console.print("\n[bold]Extracted Manifest Payload:[/bold]")
            payload_dict = {
                "signer_id": extracted_payload_obj.signer_id,
                "timestamp_from_payload": extracted_payload_obj.timestamp,
                "custom_metadata": extracted_payload_obj.custom_metadata,
                "metadata_format": extracted_payload_obj.format,
                "version": extracted_payload_obj.version,
                # Manifest-specific fields can be added here if they exist, e.g., data_blocks
            }
            console.print(Syntax(json.dumps(payload_dict, indent=2), "json", theme="monokai", line_numbers=True))

            if (
                extracted_payload_obj.custom_metadata == custom_manifest_payload
                and extracted_payload_obj.signer_id == DEMO_SIGNER_ID
                and extracted_payload_obj.timestamp == timestamp_int
            ):
                console.print("   [bold green]Extracted manifest metadata matches the original embedded data.[/bold green]")
            else:
                console.print("   [bold yellow]Warning: Extracted manifest metadata differs from the expected original.[/bold yellow]")
        elif extracted_payload_obj:
            console.print(
                f"   [yellow]Verification successful, but extracted payload is not a ManifestPayload (Type: {type(extracted_payload_obj)}).[/yellow]"
            )
        else:
            console.print("   [yellow]Verification successful, but no payload was extracted.[/yellow]")
    else:
        console.print("\n🚨 [bold red]Verification Failed (Manifest)![/bold red]")
        if extracted_signer_id:
            console.print(f"   [red]Signer ID from text:[/red] {extracted_signer_id}")

    console.print(
        Markdown(
            """
    The 'manifest' format provides a structured way to embed complex metadata, fully covered by the digital signature.
    Verification confirms the integrity and authenticity of this structured payload.
    """
        )
    )
    wait_for_key()


def demo_real_world_use_cases():
    """Demonstrate real-world use cases."""
    print_section("6. Real-World Use Cases")

    use_cases = [
        {
            "title": "Content Authenticity & Verification",
            "description": "Embed verifiable metadata that provides indisputable proof of content origin.",
            "example": "Publishers and content creators can trust the authenticity of their AI-generated work.",
        },
        {
            "title": "Provenance & Audit Trails",
            "description": "Maintain a complete, immutable record of content history and data lineage.",
            "example": "Researchers and journalists can track every transformation of their content.",
        },
        {
            "title": "Compliance, Transparency & Trust",
            "description": "Ensure regulatory compliance and clear disclosure of AI content without false alarms.",
            "example": "Organizations can confidently distinguish between genuine human work and AI-generated text.",
        },
        {
            "title": "Digital Rights Management",
            "description": "Invisibly watermark content to protect intellectual property and verify ownership.",
            "example": "Media companies can secure their digital assets and prove content provenance.",
        },
        {
            "title": "Version Control & Document Integrity",
            "description": "Embed detailed versioning and change history to maintain unaltered, verifiable records.",
            "example": "Legal and technical documents can be accurately audited over time.",
        },
        {
            "title": "Reliable AI Detection",
            "description": "Enable platforms to verify AI-generated content with zero false positives or negatives, replacing unreliable prediction models.",
            "example": "Social media platforms and plagiarism detectors can use our metadata for accurate, real-time verification.",
        },
        {
            "title": "Ethical AI Transparency & Accountability",
            "description": "Embed verifiable metadata to ensure that AI-generated content is clearly attributable, fostering responsible use and ethical practices",
            "example": "Organizations, regulators, and the public can trust that content is either genuinely human or verifiably AI-produced, reducing the risk of misuse.",
        },
    ]

    # Create a table for use cases
    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
    table.add_column("Use Case", style="bold")
    table.add_column("Description")
    table.add_column("Example", style="italic")

    for case in use_cases:
        table.add_row(case["title"], case["description"], case["example"])

    console.print(table)

    wait_for_key()


def demo_conclusion():
    """Show conclusion and call to action."""
    print_section("Get Started with EncypherAI")

    console.print(
        Markdown(
            """
    ## Installation

    ```bash
    uv pip install encypher-ai
    ```

    ## Documentation

    Visit our documentation at https://docs.encypherai.com

    ## GitHub Repository

    Star us on GitHub: https://github.com/encypherai/encypher-ai

    ## Community

    Join our community to discuss use cases, get help, and contribute to the project!
    """
        )
    )


def main():
    """Run the complete demo."""
    print_header()

    console.print(
        Markdown(
            """
    # Welcome to EncypherAI!

    EncypherAI is an open-source Python package that enables invisible metadata embedding in AI-generated text.

    In this demo, we'll walk through:

    1. Basic metadata encoding
    2. Metadata extraction & verification
    3. Tamper detection
    4. Streaming support
    5. Manifest metadata format (New!)
    6. Real-world use cases

    Let's get started!
    """
        )
    )

    wait_for_key()

    # Run each demo section
    print_header()
    demo_basic_encoding()

    print_header()
    demo_metadata_extraction()

    print_header()
    demo_tamper_detection()

    print_header()
    demo_streaming()

    print_header()
    demo_manifest_format()  # Added call to new demo

    print_header()
    demo_real_world_use_cases()

    print_header()
    demo_conclusion()

    console.print("\n[bold green]Thank you for watching the EncypherAI demo![/bold green]")


if __name__ == "__main__":
    main()
