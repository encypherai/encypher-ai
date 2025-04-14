# Basic Usage

This guide covers the fundamental operations of EncypherAI, providing a quick overview of how to embed, extract, and verify metadata in text.

## Installation

Before using EncypherAI, make sure it's installed in your environment:

```bash
uv pip install encypher-ai
```

For more installation options, see the [Installation Guide](../getting-started/installation.md).

## Importing EncypherAI

To use EncypherAI in your Python code, import the necessary components:

```python
# Import the core modules
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional

# For streaming support
from encypher.streaming.handlers import StreamingHandler

# For timestamp handling
import time
```

## Generating Key Pairs

EncypherAI uses Ed25519 digital signatures for secure metadata verification. You'll need to generate and manage key pairs:

> **Tip:** You can use the provided helper script `encypher/examples/generate_keys.py` to generate your first key pair and get detailed setup instructions.

```python
# Generate a key pair
private_key, public_key = generate_key_pair()
key_id = "example-key-1"  # A unique identifier for this key pair

# Create a public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # In a real application, this would look up the key in a secure storage
    if key_id == "example-key-1":
        return public_key
    return None
```

## Embedding Metadata

To embed metadata into text:

```python
# Sample text
text = "This is a sample text that will have metadata embedded within it."

# Create metadata dictionary
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "2.0.0",
    "key_id": key_id  # Required for verification
}

# Embed metadata
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key
)

print("Original text:")
print(text)
print("\nEncoded text (looks identical but contains invisible zero-width characters that encode the metadata):")
print(encoded_text)
```

The encoded text will look identical to the original text to human readers, but it contains invisible metadata that can be extracted programmatically.

*Note: You can specify a target for embedding using the `target` parameter (e.g., "whitespace", "punctuation", "first_letter", "last_letter", "all_characters").*

## Extracting Metadata

To extract metadata from encoded text (without verification):

```python
# Extract metadata using extract_metadata
# Returns: metadata_dict or None
extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)

if extracted_metadata:
    print("Extracted metadata:")
    print(extracted_metadata)
else:
    print("No metadata found or failed to decode.")
```

## Verifying Metadata

To verify that the text hasn't been tampered with:

```python
# Verify the text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)

print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
if is_valid:
    print("Verified metadata:", verified_metadata)
```

This method automatically handles metadata extraction and signature verification, providing a simple boolean result and the extracted metadata if valid.

> **Detailed Example:** For a more comprehensive walkthrough covering key generation, basic and manifest formats, and tamper detection, check out the [**v2.0 Demo Jupyter Notebook**](https://colab.research.google.com/drive/1MAlmz2kca7kIHq4MaIuGG3HNIY0cMgzw?usp=sharing).

## Working with Streaming Content

For content that arrives in chunks (e.g., from an LLM), use the `StreamingHandler`:

```python
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import time

# Generate key pair
private_key, public_key = generate_key_pair()
key_id = "streaming-key-1"

# Create a public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "streaming-key-1":
        return public_key
    return None

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "key_id": key_id  # Required for verification
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key,
    encode_first_chunk_only=True
)

# Process chunks as they arrive
chunks = [
    "This is the first chunk of text. ",
    "This is the second chunk. ",
    "And this is the final chunk."
]

processed_chunks = []
for chunk in chunks:
    # Process the chunk
    processed_chunk = handler.process_chunk(chunk)

    processed_chunks.append(processed_chunk)
    print(f"Processed chunk: {processed_chunk}")

# Combine all processed chunks
full_text = "".join(processed_chunks)

# Verify the text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_text,
    public_key_resolver=resolve_public_key
)

print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
if is_valid:
    print("Verified metadata:", verified_metadata)
```

## Integration with OpenAI

```python
from openai import OpenAI
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import time

# Initialize OpenAI client
client = OpenAI(api_key="your-api-key")

# Generate key pair
private_key, public_key = generate_key_pair()
key_id = "openai-key-1"

# Create a public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "openai-key-1":
        return public_key
    return None

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "key_id": key_id  # Required for verification
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key
)

# Create a streaming completion
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ],
    stream=True
)

# Process each chunk
full_response = ""
for chunk in completion:
    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content

        # Process the chunk
        processed_chunk = handler.process_chunk(chunk=content)

        # Print and accumulate the processed chunk
        print(processed_chunk, end="", flush=True)
        full_response += processed_chunk

# Finalize the stream
handler.finalize()

print("\n\nStreaming completed!")
```

## Common Patterns

### Adding Timestamp Automatically

```python
import time

# Create metadata with automatic timestamp
def create_metadata(model_id="gpt-4", organization="EncypherAI"):
    return {
        "model_id": model_id,
        "organization": organization,
        "timestamp": int(time.time()),  # Unix/Epoch timestamp
        "version": "2.0.0"
    }

# Use the function
metadata = create_metadata()
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key
)
```

### Handling Multiple Texts

```python
# Process multiple texts
texts = [
    "This is the first text.",
    "This is the second text.",
    "This is the third text."
]

# Embed metadata in all texts
encoded_texts = []
for i, text in enumerate(texts):
    # Create unique metadata for each text
    metadata = {
        "model_id": "gpt-4",
        "organization": "EncypherAI",
        "timestamp": int(time.time()),  # Unix/Epoch timestamp
        "text_id": i + 1,
        "version": "2.0.0",
        "key_id": key_id  # Required for verification
    }

    # Embed metadata
    encoded_text = UnicodeMetadata.embed_metadata(
        text=text,
        metadata=metadata,
        private_key=private_key
    )
    encoded_texts.append(encoded_text)

    print(f"Text {i+1} encoded with metadata")

# Later, extract and verify metadata
for i, encoded_text in enumerate(encoded_texts):
    # Use verify_metadata for combined extraction and verification
    is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
        text=encoded_text,
        public_key_resolver=resolve_public_key
    )
    print(f"Text {i+1}:")
    if is_valid:
        print(f"  Verified: ✅")
        print(f"  Metadata: {verified_metadata}")
    else:
        # Check if metadata was present but failed verification, or simply not present
        metadata_only = UnicodeMetadata.extract_metadata(encoded_text)
        if metadata_only:
            print(f"  Verified: ❌ (Verification Failed)")
            print(f"  Metadata: {metadata_only}")
        else:
            print(f"  Verified: ❌ (No Metadata Found)")
```

### Error Handling

```python
def safe_process_text(text, private_key, public_key_resolver):
    """Safely process text, attempting verification."""
    result = {
        "has_metadata": False,
        "metadata": None,
        "verified": False,
        "error": None
    }

    # Attempt to verify the text using the private key
    try:
        is_valid, metadata = UnicodeMetadata.verify_metadata(
            text=text,
            public_key_resolver=public_key_resolver
        )
        if metadata: # Metadata was found
            result["has_metadata"] = True
            result["metadata"] = metadata
            result["verified"] = is_valid
        # If metadata is None, it means no valid encoded block was found
    except Exception as e:
        # General error during processing
        result["error"] = str(e)

    return result

# Example usage
result = safe_process_text(encoded_text, private_key, resolve_public_key)
if result["has_metadata"]:
    if result["verified"]:
        print("✅ Verified metadata:", result["metadata"])
    else:
        print("❌ Metadata found but verification failed:", result["metadata"])
else:
    print("No metadata found:", result["error"])
```

## Next Steps

Now that you understand the basics of EncypherAI, you can explore more advanced topics:

- [Metadata Encoding](./metadata-encoding.md) - Learn more about how metadata is embedded
- [Extraction and Verification](./extraction-verification.md) - Dive deeper into extracting and verifying metadata
- [Tamper Detection](./tamper-detection.md) - Understand how EncypherAI detects tampering
- [Streaming Support](./streaming.md) - Learn more about working with streaming content

For practical examples, check out:

- [Jupyter Notebook Examples](../examples/jupyter.md)
- [Streamlit Demo App](../examples/streamlit.md)
- [YouTube Demo](../examples/youtube-demo.md)
