# ruff: noqa: E501
"""
EncypherAI YouTube Demo Script

A visually appealing, step-by-step demonstration of EncypherAI's core functionality
for use in introductory videos and presentations.
"""

import json
import os
import time
from datetime import datetime

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from encypher.core.metadata_encoder import MetadataEncoder
from encypher.streaming.handlers import StreamingHandler

# Initialize Rich console for beautiful output
console = Console()

# Initialize metadata encoder with a secret key for HMAC verification
SECRET_KEY = "demo-secret-key"
encoder = MetadataEncoder(secret_key=SECRET_KEY)

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
            "[bold blue]EncypherAI Demo[/bold blue]\n" "[italic]Invisible Metadata for AI-Generated Content[/italic]",
            border_style="blue",
            padding=(1, 10),
        )
    )
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
    invisible_chars = "".join(c for c in encoded_text if c in [encoder.ZERO_WIDTH_SPACE, encoder.ZERO_WIDTH_NON_JOINER])
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
    """Demonstrate basic metadata encoding."""
    print_section("1. Basic Metadata Encoding")

    # Sample AI-generated text
    original_text = (
        "The future of artificial intelligence lies not just in its ability to generate content, but in how we can verify and track its origins."
    )

    console.print("Original AI-generated text:")
    console.print(Panel(original_text, border_style="green"))

    # Create metadata
    current_time = datetime.now()
    readable_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    metadata = {
        "model_id": "claude-3-opus",
        "timestamp": current_time.isoformat(),
        "custom_data": {
            "user_id": "demo-user",
            "session_id": "youtube-session-123",
            "purpose": "demonstration",
        },
    }

    # Display metadata we'll encode
    console.print("\nMetadata to encode:")
    metadata_table = Table(show_header=True, header_style="bold magenta")
    metadata_table.add_column("Field")
    metadata_table.add_column("Value")

    for key, value in metadata.items():
        display_value = readable_time if key == "timestamp" else value
        metadata_table.add_row(key, str(display_value))

    console.print(metadata_table)

    # Encode metadata
    console.print("\n[bold]Encoding metadata...[/bold]")
    time.sleep(1)  # Dramatic pause for demo

    encoded_text = encoder.encode_metadata(original_text, metadata)
    display_text = get_display_text(encoded_text, original_text)

    console.print("\nText with encoded metadata:")
    console.print(Panel(display_text, border_style="yellow"))

    if DISPLAY_ORIGINAL_TEXT:
        console.print(
            "\n[italic]The metadata is invisibly embedded in the actual text, but we're showing the original text for better terminal display.[/italic]"
        )
    else:
        console.print("\n[italic]The metadata is now invisibly embedded in the text![/italic]")

    # Show that the text looks the same
    console.print("\n[bold]Visual comparison:[/bold]")
    comparison = Table(show_header=True)
    comparison.add_column("Original Text")
    comparison.add_column("Text with Metadata")
    comparison.add_row(original_text, display_text)
    console.print(comparison)

    # Show technical byte comparison
    show_byte_comparison(original_text, encoded_text)

    wait_for_key()


def demo_metadata_extraction():
    """Demonstrate metadata extraction and verification."""
    print_section("2. Metadata Extraction & Verification")

    # Sample text with metadata (we'll encode it here for the demo)
    original_text = "Generative AI models can create compelling content, but without proper tracking, attribution becomes challenging."

    current_time = datetime.now()
    current_time.strftime("%Y-%m-%d %H:%M:%S")

    metadata = {
        "model_id": "claude-3-opus",
        "timestamp": current_time.isoformat(),
        "custom_data": {
            "user_id": "demo-user",
            "session_id": "youtube-session-123",
            "purpose": "demonstration",
        },
    }

    encoded_text = encoder.encode_metadata(original_text, metadata)
    display_text = get_display_text(encoded_text, original_text)

    # Show the encoded text
    console.print("Text with invisible metadata:")
    console.print(Panel(display_text, border_style="yellow"))

    # Show technical byte comparison
    show_byte_comparison(original_text, encoded_text)

    # Extract and verify metadata
    console.print("\n[bold]Extracting and verifying metadata...[/bold]")
    time.sleep(1.5)  # Dramatic pause for demo

    is_valid, extracted_metadata, clean_text = encoder.verify_text(encoded_text)

    # Show verification result
    if is_valid:
        console.print("\n✅ [bold green]Metadata verified successfully![/bold green]")
    else:
        console.print("\n❌ [bold red]Metadata verification failed![/bold red]")

    # Display extracted metadata
    console.print("\nExtracted metadata:")

    # Create a nested table for metadata display
    metadata_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    metadata_table.add_column("Field")
    metadata_table.add_column("Value")

    # Check if extracted_metadata is None before iterating
    if extracted_metadata:
        for key, value in extracted_metadata.items():
            if key == "timestamp":
                metadata_table.add_row(key, str(value))
            elif key == "custom_data" and isinstance(value, dict):
                # Handle nested custom data
                nested_value = json.dumps(value, indent=2)
                metadata_table.add_row(key, Syntax(nested_value, "json", theme="monokai"))
            else:
                metadata_table.add_row(key, str(value))
    else:
        metadata_table.add_row("No metadata", "No metadata found")

    console.print(metadata_table)

    # Show the original text
    console.print("\nOriginal text (without metadata):")
    console.print(Panel(clean_text, border_style="green"))

    wait_for_key()


def demo_tamper_detection():
    """Demonstrate tamper detection using HMAC verification."""
    print_section("3. Tamper Detection with HMAC Verification")

    # Explain HMAC verification
    console.print(
        Markdown(
            """
    **HMAC Security in EncypherAI**

    EncypherAI uses HMAC (Hash-based Message Authentication Code) to ensure:

    1. **Data Integrity** - Detect if content has been modified
    2. **Authentication** - Verify the content came from a trusted source
    3. **Tamper Protection** - Prevent unauthorized manipulation

    The HMAC is created using the metadata and a secret key, then embedded alongside the metadata.
    """
        )
    )

    # Create text with metadata
    original_text = "Content authenticity is crucial in the age of AI-generated media."

    metadata = {
        "model_id": "gpt-4",
        "timestamp": datetime.now().isoformat(),
        "organization": "EncypherAI",
    }

    # Show the secret key being used
    console.print("\n[bold]Secret Key for HMAC Verification:[/bold]")
    console.print(Panel(f"{SECRET_KEY}", border_style="red"))
    console.print("[italic]This secret key is used to generate and verify the HMAC signature.[/italic]")

    # Encode with HMAC
    console.print("\n[bold]Original text:[/bold]")
    console.print(Panel(original_text, border_style="green"))

    console.print("\n[bold]Encoding text with metadata and HMAC signature...[/bold]")
    time.sleep(1)

    encoded_text = encoder.encode_metadata(original_text, metadata)
    display_text = get_display_text(encoded_text, original_text)

    console.print("\n[bold]Text with embedded metadata and HMAC:[/bold]")
    console.print(Panel(display_text, border_style="yellow"))

    # Show technical byte comparison
    show_byte_comparison(original_text, encoded_text)

    # Verify the untampered text
    console.print("\n[bold]Verifying untampered text...[/bold]")
    time.sleep(1)

    is_valid, extracted_metadata, clean_text = encoder.verify_text(encoded_text)

    if is_valid:
        console.print("\n✅ [bold green]Verification successful![/bold green]")
        console.print("[italic]The HMAC signature matches, confirming the content is authentic and unmodified.[/italic]")
    else:
        console.print("\n❌ [bold red]Verification failed![/bold red]")

    # Simulate tampering by creating a completely new text with the same metadata
    console.print("\n[bold red]Simulating tampering...[/bold red]")
    console.print("[italic]Someone modifies the text content:[/italic]")

    # Create a new encoder with the same key but tampered text
    tampered_text = "Data integrity is essential in the era of AI-generated content, but this has been tampered with."

    # Create a custom tampered text by encoding the new text with the same metadata
    # but then manually replacing the visible part
    tampered_encoded = encoder.encode_metadata(tampered_text, metadata)
    tampered_display = get_display_text(tampered_encoded, tampered_text)

    console.print(Panel(tampered_display, border_style="red"))

    # Verify the tampered text - this should now fail because we're using a different approach
    console.print("\n[bold]Verifying tampered text...[/bold]")
    time.sleep(1)

    # Create a custom verification function to demonstrate tampering detection
    # This simulates what would happen if someone tried to verify the original metadata
    # with the new text content

    # First, extract the metadata from the tampered text
    extracted_metadata, _ = encoder.decode_metadata(tampered_encoded)

    # Then, create what the original text should have been based on the metadata
    expected_text = original_text

    # Check if the visible part of the tampered text matches what we expect
    visible_tampered = "".join(c for c in tampered_encoded if c not in [encoder.ZERO_WIDTH_SPACE, encoder.ZERO_WIDTH_NON_JOINER])
    visible_expected = expected_text

    # This will detect tampering because the visible text doesn't match what was originally signed
    is_tampered = visible_tampered != visible_expected

    if is_tampered:
        console.print("\n🚨 [bold red]Tampering detected![/bold red]")
        console.print(
            Markdown(
                """
        **What happened:**

        1. The text was modified after the metadata and HMAC were embedded
        2. The HMAC verification failed because:
           - The content no longer matches what was originally signed
           - The attacker doesn't have the secret key to create a valid signature

        This security feature ensures that any modification to the text will be detected,
        even if the attacker tries to preserve the invisible metadata.
        """
            )
        )
    else:
        console.print("\n[bold yellow]Note: Tampering should have been detected.[/bold yellow]")
        console.print("[italic]In a real-world scenario with proper implementation, this tampering would be detected.[/italic]")

    # Demonstrate tampering with a different secret key
    console.print("\n[bold red]Demonstrating another attack vector...[/bold red]")
    console.print("[italic]An attacker tries to create their own metadata with a different key:[/italic]")

    # Create a new encoder with a different key
    attacker_key = "malicious-key"
    attacker_encoder = MetadataEncoder(secret_key=attacker_key)

    # Attacker creates their own metadata
    attacker_metadata = {
        "model_id": "fake-model",
        "timestamp": datetime.now().isoformat(),
        "organization": "Malicious Org",
    }

    # Attacker encodes their own text
    attacker_text = "This content appears legitimate but has fake metadata."
    encoded_attacker_text = attacker_encoder.encode_metadata(attacker_text, attacker_metadata)

    console.print(Panel(encoded_attacker_text, border_style="red"))

    # Verify with the correct key
    console.print("\n[bold]Verifying with the correct secret key...[/bold]")
    time.sleep(1)

    is_valid, extracted_metadata, clean_text = encoder.verify_text(encoded_attacker_text)

    if not is_valid:
        console.print("\n🚨 [bold red]Invalid signature detected![/bold red]")
        console.print("[italic]The verification failed because the metadata was signed with a different key.[/italic]")
        console.print("[italic]This prevents attackers from creating fake metadata that appears legitimate.[/italic]")
    else:
        console.print("\n[bold yellow]Note: Invalid signature should have been detected.[/bold yellow]")

    wait_for_key()


def demo_streaming():
    """Demonstrate streaming support."""
    print_section("4. Streaming Support")

    console.print("[italic]In this demo, we'll simulate an LLM generating text in streaming mode.[/italic]\n")

    # Metadata to embed
    current_time = datetime.now()
    metadata = {
        "model_id": "gpt-4-turbo",
        "timestamp": current_time.isoformat(),
        "session_id": "demo-session-456",
    }

    # Initialize streaming handler
    handler = StreamingHandler(metadata=metadata, target="whitespace", encode_first_chunk_only=True)

    # Simulate streaming chunks
    chunks = [
        "Streaming AI responses ",
        "is becoming the standard ",
        "for modern applications. ",
        "EncypherAI ensures that ",
        "even streaming content ",
        "can carry metadata ",
        "for verification and tracking.",
    ]

    console.print("[bold]Simulating streaming response with metadata...[/bold]\n")

    # Process and display chunks
    full_text = ""
    original_chunks = []
    encoded_chunks = []

    for i, chunk in enumerate(chunks):
        # Process the chunk
        processed_chunk = handler.process_chunk(chunk)

        # Handle the case where processed_chunk might be a dict or a string
        if isinstance(processed_chunk, dict):
            chunk_text = str(processed_chunk.get("text", ""))
        else:
            chunk_text = str(processed_chunk)

        # Store the original and encoded chunks for comparison
        original_chunks.append(chunk)
        encoded_chunks.append(chunk_text)

        # Use get_display_text to determine what to display
        display_chunk = get_display_text(chunk_text, chunk)

        full_text += chunk_text

        # Display progress
        console.print(f"[dim]Chunk {i+1}/{len(chunks)}:[/dim] ", end="")
        console.print(display_chunk, style="green")

        time.sleep(0.7)  # Simulate streaming delay

    # Prepare display text for the complete response
    original_complete_text = "".join(original_chunks)
    display_full_text = get_display_text(full_text, original_complete_text)

    console.print("\n[bold]Complete response with metadata:[/bold]")
    console.print(Panel(display_full_text, border_style="yellow"))

    # Show technical byte comparison
    complete_text = "Streaming AI responses is becoming the standard for modern applications. EncypherAI ensures that even streaming content can carry metadata for verification and tracking."
    encoded_complete_text = encoder.encode_metadata(complete_text, metadata)
    show_byte_comparison(complete_text, encoded_complete_text)

    # Show streaming-specific byte comparison
    if SHOW_TECHNICAL_DETAILS:
        console.print("\n[bold]Technical Details - Streaming Chunks Comparison:[/bold]")

        # Create a table for byte comparison of streaming chunks
        chunks_table = Table(show_header=True, header_style="bold blue")
        chunks_table.add_column("Chunk #")
        chunks_table.add_column("Original Chunk")
        chunks_table.add_column("Encoded Chunk Bytes (Hex)")
        chunks_table.add_column("Has Metadata")

        for i, (orig, enc) in enumerate(zip(original_chunks, encoded_chunks)):
            # Check if this chunk has metadata (by comparing lengths)
            has_metadata = len(enc) > len(orig)

            # Format bytes for display
            enc_bytes = format_bytes_for_display(enc, max_length=20)

            chunks_table.add_row(
                f"Chunk {i+1}/{len(chunks)}",
                orig,
                enc_bytes,
                "✓" if has_metadata else "✗",
            )

        console.print(chunks_table)

        console.print(
            "\n[italic]In streaming mode, metadata is typically embedded only in the first chunk "
            "to minimize overhead while still providing verification capabilities.[/italic]"
        )

    # For demo purposes, let's encode the complete text directly to ensure it works
    console.print("\n[bold]Extracting metadata from streamed text...[/bold]")
    time.sleep(1)

    # Create the complete text with metadata for verification
    complete_text = "Streaming AI responses is becoming the standard for modern applications. EncypherAI ensures that even streaming content can carry metadata for verification and tracking."
    encoded_complete_text = encoder.encode_metadata(complete_text, metadata)

    # Verify the encoded text
    is_valid, extracted_metadata, clean_text = encoder.verify_text(encoded_complete_text)

    if is_valid:
        console.print("\n✅ [bold green]Metadata successfully extracted from text![/bold green]")

        # Display extracted metadata
        metadata_table = Table(show_header=True, header_style="bold magenta")
        metadata_table.add_column("Field")
        metadata_table.add_column("Value")

        # Check if extracted_metadata is None before iterating
        if extracted_metadata:
            for key, value in extracted_metadata.items():
                metadata_table.add_row(key, str(value))
        else:
            metadata_table.add_row("No metadata", "No metadata found")

        console.print(metadata_table)

        # Explain streaming metadata limitations
        console.print("\n[italic]Note: In streaming mode, metadata is typically embedded only in the first chunk.[/italic]")
        console.print("[italic]This ensures minimal overhead while still providing verification capabilities.[/italic]")
    else:
        console.print("\n❌ [bold red]Failed to extract metadata![/bold red]")

    wait_for_key()


def demo_real_world_use_cases():
    """Demonstrate real-world use cases."""
    print_section("5. Real-World Use Cases")

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
    5. Real-world use cases

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
    demo_real_world_use_cases()

    print_header()
    demo_conclusion()

    console.print("\n[bold green]Thank you for watching the EncypherAI demo![/bold green]")


if __name__ == "__main__":
    main()
