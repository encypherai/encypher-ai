# YouTube Demo Script

The EncypherAI YouTube demo script is a comprehensive, visually engaging demonstration of EncypherAI's core functionality. This interactive demo is designed for creating introductory videos about the project, showcasing all major features with rich visual elements.

> Note: Timestamps are optional across all metadata formats, including C2PA. When you omit a timestamp, C2PA action assertions that normally include a `when` field will simply omit it.

## Overview

The demo script (`youtube_demo.py`) provides a step-by-step walkthrough of EncypherAI's capabilities with colorful terminal output, visual comparisons, and detailed explanations.

![YouTube Demo Preview](../../assets/youtube-demo-preview.png)

## Features Demonstrated

The demo covers all key EncypherAI functionalities:

1. **Basic Metadata Encoding**
   - Visual comparison of original vs encoded text
   - Explanation of zero-width characters

2. **Metadata Extraction and Verification**
   - Extracting embedded metadata
   - Viewing and interpreting metadata contents

3. **Tamper Detection with Digital Signatures**
   - How digital signature verification ensures data integrity
   - Demonstration of tampering detection
   - Simulation of different attack vectors

4. **Streaming Support**
   - Simulating chunk-by-chunk LLM responses
   - Handling metadata in streaming scenarios

5. **Real-world Use Cases**
   - Content authentication
   - AI output provenance tracking
   - Data attribution

## Running the Demo

To run the YouTube demo:

```bash
# From your EncypherAI installation directory
python -m encypher_ai.examples.youtube_demo
```

## Demo Structure

The demo is organized into clear sections with dramatic pauses and visual elements to maintain viewer engagement:

```python
# Section structure example
console.rule("3. Tamper Detection with Digital Signatures")
console.print()

# Informational panel
console.print(Panel(
    "**Digital Signature Security in EncypherAI**\n\n"
    "EncypherAI uses Ed25519 digital signatures to ensure:\n\n"
    "1. **Data Integrity** - Detect if content has been modified\n"
    "2. **Authentication** - Verify the content came from a trusted source\n"
    "3. **Tamper Protection** - Prevent unauthorized manipulation\n\n"
    "The signature is created using the metadata and a private key, then embedded alongside the metadata.",
    title="", border_style="blue", padding=(1, 2)
))
```

## Code Example

Here's a simplified example of the code used in the YouTube demo:

```python
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time
import json

from encypher_ai.core.unicode_metadata import UnicodeMetadata
from encypher_ai.core.keys import generate_key_pair
from encypher_ai.streaming.handlers import StreamingHandler
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional

# Initialize rich console for pretty output
console = Console()

# Generate key pair for digital signatures
private_key, public_key = generate_key_pair()
key_id = "demo-key-1"

# Create a public key resolver
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "demo-key-1":
        return public_key
    return None

# Sample text
text = "This is a sample text that will have metadata embedded within it."

# Create metadata
metadata = {
    "model": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),
    "version": "2.3.0",
    "key_id": key_id  # Required for verification
}

# Display the original text
console.print("\n[bold]Original Text:[/bold]")
console.print(Panel(text, border_style="green"))

# Display the metadata
console.print("\n[bold]Metadata to Embed:[/bold]")
console.print(Panel(json.dumps(metadata, indent=2), border_style="blue"))

# Embed metadata
console.print("\n[bold]Embedding metadata...[/bold]")
time.sleep(1)  # Dramatic pause
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    custom_metadata=metadata,
    private_key=private_key,
    signer_id=key_id,
    timestamp=metadata.get("timestamp")
)

# Display the encoded text
console.print("\n[bold]Text with Embedded Metadata:[/bold]")
console.print(Panel(encoded_text, border_style="yellow"))

# Extract metadata
console.print("\n[bold]Extracting metadata...[/bold]")
time.sleep(1)  # Dramatic pause
extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)

# Display extracted metadata
console.print("\n[bold]Extracted Metadata:[/bold]")
console.print(Panel(json.dumps(extracted_metadata, indent=2), border_style="blue"))

# Verify the text
console.print("\n[bold]Verifying content integrity...[/bold]")
time.sleep(1)  # Dramatic pause
is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_provider=resolve_public_key
)

if is_valid:
    console.print(f"\n✅ [bold green]Verification successful! Signer ID: {signer_id}[/bold green]")
    if payload_dict:
        console.print("[bold]Verified Payload:[/bold]")
        console.print(Panel(json.dumps(payload_dict, indent=2), border_style="cyan"))
else:
    console.print(f"\n❌ [bold red]Verification failed! Signer ID (if found): {signer_id}[/bold red]")

# Demonstrate tampering
console.print("\n\n[bold]Demonstrating Tamper Detection:[/bold]")
tampered_text = encoded_text + " This text was added after embedding."

console.print("\n[bold]Tampered Text:[/bold]")
console.print(Panel(tampered_text, border_style="red"))

# Verify the tampered text
console.print("\n[bold]Verifying tampered content...[/bold]")
time.sleep(1)  # Dramatic pause
is_valid_tampered, signer_id_tampered, payload_dict_tampered = UnicodeMetadata.verify_metadata(
    text=tampered_text,
    public_key_provider=resolve_public_key
)

if is_valid_tampered:
    console.print(f"\n✅ [bold green]Verification successful (tampered text)! Signer ID: {signer_id_tampered}[/bold green]") # Should not happen
else:
    console.print(f"\n❌ [bold red]Tampering detected! (Verification failed for tampered text) Signer ID (if found): {signer_id_tampered}[/bold red]")

    # Explain what happened
    console.print(Panel(
        "[bold]What happened:[/bold]\n\n"
        "1. The text was modified after the metadata and digital signature were embedded\n"
        "2. The signature verification failed because:\n"
        "   - The content no longer matches what was originally signed\n"
        "   - The attacker doesn't have the private key to create a valid signature\n\n"
        "This security feature ensures that any modification to the text will be detected,\n"
        "even if the attacker tries to preserve the invisible metadata.",
        title="Tamper Detection Explanation", border_style="red", padding=(1, 2)
    ))

# Demonstrate streaming
console.print("\n\n[bold]Demonstrating Streaming Support:[/bold]")

# Create streaming metadata
streaming_metadata = {
    "model": "streaming-demo",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),
    "version": "2.3.0",
    "key_id": key_id  # Required for verification
}

# Create a streaming handler
handler = StreamingHandler(
    custom_metadata=streaming_metadata,
    private_key=private_key,
    signer_id=streaming_metadata.get("key_id"),
    timestamp=streaming_metadata.get("timestamp")
)

# Simulate streaming chunks
chunks = [
    "The quick ",
    "brown fox ",
    "jumps over ",
    "the lazy dog. ",
    "This is an example ",
    "of streaming text ",
    "with embedded metadata."
]

# Process chunks
console.print("\n[bold]Processing streaming chunks:[/bold]")
full_text = ""

for i, chunk in enumerate(chunks):
    console.print(f"\nChunk {i+1}: [italic]\"{chunk}\"[/italic]")
    time.sleep(0.5)

    processed_chunk = handler.process_chunk(chunk)
    full_text += processed_chunk

    console.print(f"Processed {i+1}/{len(chunks)} chunks")

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    full_text += final_chunk

# Display the final text
console.print("\n[bold]Final Text with Embedded Metadata:[/bold]")
console.print(Panel(full_text, border_style="green"))

# Extract metadata from streaming text
extracted_streaming = UnicodeMetadata.extract_metadata(full_text)
console.print("\n[bold]Extracted Streaming Metadata:[/bold]")
console.print(Panel(json.dumps(extracted_streaming, indent=2), border_style="blue"))

# Verify streaming text
is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
    text=full_text,
    public_key_provider=resolve_public_key
)

if is_valid:
    console.print(f"\n✅ [bold green]Streaming verification successful! Signer ID: {signer_id}[/bold green]")
    if payload_dict:
        console.print("[bold]Verified Streaming Payload:[/bold]")
        console.print(Panel(json.dumps(payload_dict, indent=2), border_style="cyan"))
else:
    console.print(f"\n❌ [bold red]Streaming verification failed! Signer ID (if found): {signer_id}[/bold red]")

## Tamper Detection Demonstration

The tamper detection section provides a particularly clear example of EncypherAI's security features:

1. First, it shows normal verification of untampered content
2. Then it simulates tampering by modifying the text content
3. It demonstrates how the verification detects the tampering
4. Finally, it shows another attack vector where someone tries to create fake metadata with a different key

### Example Output

```
🚨 Tampering detected!

     **What happened:**

     1. The text was modified after the metadata and digital signature were embedded
     2. The signature verification failed because:
        - The content no longer matches what was originally signed
        - The attacker doesn't have the private key to create a valid signature

     This security feature ensures that any modification to the text will be detected,
     even if the attacker tries to preserve the invisible metadata.
```

## Customizing the Demo

You can customize the demo for your own presentations:

```python
# Generate key pairs for digital signature verification
from encypher_ai.core.keys import generate_key_pair
private_key, public_key = generate_key_pair()
key_id = "your-custom-key-id"

# Modify the example metadata
metadata = {
    "model": "your-model-name",
    "organization": "Your Organization",
    "timestamp": int(time.time()),  # Unix timestamp
    "custom_field": "custom value",
    "key_id": key_id  # Required for verification
}

# Adjust timing between sections
time.sleep(custom_delay)  # Change pause duration

```

## Source Code

You can find the full source code for the YouTube demo in the `docs/package/examples/youtube_demo.py` file in the EncypherAI repository.
