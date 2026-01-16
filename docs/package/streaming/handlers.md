# Streaming Handlers

The streaming module in Encypher provides specialized handlers for working with streaming content from LLMs and other sources. These handlers make it easy to embed metadata in content that arrives chunk by chunk.

## StreamingHandler

The `StreamingHandler` class is the primary interface for handling streaming content. It provides a simple API for processing chunks of text and embedding metadata.

### Class Definition

```python
class StreamingHandler:
    def __init__(
        self,
        custom_metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[Union[str, datetime, date, int, float]] = None,
        target: Union[str, MetadataTarget] = "whitespace",
        encode_first_chunk_only: bool = True,
        private_key: Optional[Ed25519PrivateKey] = None,
        signer_id: Optional[str] = None,
        metadata_format: Literal["basic", "manifest", "c2pa"] = "c2pa",
        omit_keys: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize a StreamingHandler for processing streaming content.

        Args:
            custom_metadata: User metadata to embed into the payload.
            timestamp: Optional timestamp to embed. When omitted, the library will generate one.
            target: Where to embed metadata.
            target: Where to embed metadata. Can be a string ("whitespace", "punctuation",
                   "first_letter", "last_letter", "all_characters", "file_end", "file_end_zwnbsp")
                   or a MetadataTarget enum. End-of-file targets append selectors at the end of
                   the content; "file_end_zwnbsp" prefixes a zero-width no-break space (U+FEFF).
            encode_first_chunk_only: If True (default), metadata is embedded entirely within
                                    the first suitable chunk(s). If False, metadata can be
                                    distributed across multiple chunks if needed.
            private_key: The private key (Ed25519PrivateKey) used for signing the metadata.
            signer_id: Key identifier embedded into the payload and later used for verification.
            metadata_format: The metadata format to embed. For streaming, `basic` is the typical choice.
            omit_keys: Optional list of metadata keys to omit from the payload prior to signing.
            metadata: Deprecated alias for providing metadata; prefer `custom_metadata`.
        """
```

### Methods

#### process_chunk

```python
def process_chunk(
    self,
    chunk: Union[str, dict[str, Any]]
) -> Union[str, dict[str, Any]]:
    """
    Process a chunk of streaming content, embedding metadata if possible.

    Accumulates the chunk in an internal buffer. If the buffer contains enough
    characters and suitable target locations, and metadata hasn't been fully
    embedded yet (respecting `encode_first_chunk_only`), it embeds the metadata
    and returns the processed text from the buffer.

    Args:
        chunk: The text chunk to process.

    Returns:
        The processed chunk with embedded metadata, preserving the input chunk type.
    """
```

#### finalize

```python
def finalize(self) -> Optional[str]:
    """
    Finalize the streaming session, processing any remaining buffered content.

    This *must* be called after all chunks have been passed to `process_chunk`
    to ensure any remaining text in the buffer is processed and returned,
    potentially containing the last part of the embedded metadata.

    Returns:
        The remaining processed text from the buffer, potentially containing
        metadata, or None if the buffer was empty.
    """
```

#### reset

```python
def reset(self) -> None:
    """Reset internal handler state so it can be reused for a new stream."""
```

### Usage Example

```python
from datetime import datetime, timezone
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Generate key pair (replace with your actual key management)
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-1"

# Example public key resolver function
def resolve_public_key(key_id: str) -> Optional[Ed25519PublicKey]:
    if key_id == signer_id:
        return public_key
    return None

# Initialize the streaming handler
handler = StreamingHandler(
    custom_metadata={"model": "gpt-4", "organization": "MyCompany"},
    private_key=private_key,
    signer_id=signer_id,
    timestamp=datetime.now(timezone.utc),
    target="whitespace",
    encode_first_chunk_only=True,
    metadata_format="basic",
)

# Process chunks as they arrive
chunks = [
    "This is the first chunk of text. ",
    "This is the second chunk. ",
    "And this is the final chunk."
]

processed_chunks = []
for i, chunk in enumerate(chunks):
    # Process the chunk
    processed_chunk = handler.process_chunk(chunk=chunk)
    if processed_chunk:
        processed_chunks.append(processed_chunk)
        print(f"Processed chunk {i+1}: {processed_chunk}")

# Finalize the stream to process any remaining buffer
final_chunk = handler.finalize()
if final_chunk:
    processed_chunks.append(final_chunk)
    print(f"Final chunk: {final_chunk}")

# Combine all processed chunks
full_text = "".join(processed_chunks)

# Now you can extract and verify the metadata using UnicodeMetadata
print(f"\nFull text:\n{full_text}")

# Extract metadata (optional, verification does this too)
extracted_metadata = UnicodeMetadata.extract_metadata(full_text)
print(f"\nExtracted metadata: {extracted_metadata}")

# Verify the metadata using the public key resolver
is_valid, extracted_signer_id, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_text,
    public_key_resolver=resolve_public_key,
    require_hard_binding=False,
)

print(f"\nVerification result: {'✅ Verified' if is_valid else '❌ Failed'}")
if is_valid:
    print(f"Signer ID: {extracted_signer_id}")
    print(f"Verified metadata: {verified_metadata}")
```

## Streaming with OpenAI

```python
import openai
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming import StreamingHandler

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_ed25519_key_pair()
signer_id = "openai-stream-key"

def resolve_public_key(key_id: str) -> Optional[Ed25519PublicKey]:
    if key_id == signer_id:
        return public_key
    return None

# Initialize the streaming handler
handler = StreamingHandler(
    custom_metadata={"model": "gpt-4", "organization": "MyCompany"},
    private_key=private_key,
    signer_id=signer_id,
    timestamp=datetime.now(timezone.utc),
    target="whitespace",
    metadata_format="basic",
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

        # Print and accumulate the processed chunk if available
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream to process any remaining buffer
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")

# Verify the final response
print("\nVerifying full response...")
is_valid, extracted_signer_id, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_response,
    public_key_resolver=resolve_public_key,
    require_hard_binding=False,
)

if is_valid:
    print("✅ Verification successful!")
    print(f"Signer ID: {extracted_signer_id}")
    print(f"Verified metadata: {verified_metadata}")
else:
    print("❌ Verification failed!")
```

## Streaming with Anthropic

```python
import anthropic
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_ed25519_key_pair()
signer_id = "anthropic-stream-key"

def resolve_public_key(key_id: str) -> Optional[Ed25519PublicKey]:
    if key_id == signer_id:
        return public_key
    return None

# Initialize the streaming handler
handler = StreamingHandler(
    custom_metadata={"model": "claude-3-opus-20240229", "organization": "MyCompany"},
    private_key=private_key,
    signer_id=signer_id,
    timestamp=datetime.now(timezone.utc),
    target="whitespace",
    metadata_format="basic",
)

# Create a streaming completion
with client.messages.stream(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ]
) as stream:
    full_response = ""
    for text in stream.text_stream:
        # Process the chunk
        processed_chunk = handler.process_chunk(chunk=text)

        # Print and accumulate the processed chunk if available
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream to process any remaining buffer
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")

# Verify the final response
print("\nVerifying full response...")
is_valid, extracted_signer_id, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_response,
    public_key_resolver=resolve_public_key,
    require_hard_binding=False,
)

if is_valid:
    print("✅ Verification successful!")
    print(f"Signer ID: {extracted_signer_id}")
    print(f"Verified metadata: {verified_metadata}")
else:
    print("❌ Verification failed!")
```

## LiteLLM Integration

Encypher works seamlessly with [LiteLLM](https://github.com/BerriAI/litellm), which provides a unified interface for multiple LLM providers:

```python
import litellm
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair

# Configure LiteLLM
litellm.api_key = "your-api-key"

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_ed25519_key_pair()
signer_id = "litellm-stream-key"

def resolve_public_key(key_id: str) -> Optional[Ed25519PublicKey]:
    # In a real application, this would look up the key in a secure storage
    if key_id == signer_id:
        return public_key
    return None

# Initialize the streaming handler
handler = StreamingHandler(
    custom_metadata={"model": "gpt-4", "provider": "openai"},
    private_key=private_key,
    signer_id=signer_id,
    timestamp=datetime.now(timezone.utc),
    target="whitespace",
    metadata_format="basic",
)

# Create a streaming completion
response = litellm.completion(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ],
    stream=True
)

# Process each chunk
full_response = ""
for chunk in response:
    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
        content = chunk.choices[0].delta.content
        if content:
            # Process the chunk
            processed_chunk = handler.process_chunk(chunk=content)

            # Print and accumulate the processed chunk if available
            if processed_chunk:
                print(processed_chunk, end="", flush=True)
                full_response += processed_chunk

# Finalize the stream to process any remaining buffer
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")

# Verify the final response
print("\nVerifying full response...")
is_valid, extracted_signer_id, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_response,
    public_key_resolver=resolve_public_key,
    require_hard_binding=False,
)

if is_valid:
    print("✅ Verification successful!")
    print(f"Signer ID: {extracted_signer_id}")
    print(f"Verified metadata: {verified_metadata}")
else:
    print("❌ Verification failed!")
```

## Implementation Details

### Buffering Strategy

The `StreamingHandler` uses an internal buffer to accumulate chunks until there are enough suitable targets for embedding metadata:

1. When a chunk arrives, it's added to the buffer
2. If there are enough targets in the buffer, metadata is embedded
3. The processed buffer is returned, and the buffer is cleared
4. If there aren't enough targets, the chunk is kept in the buffer until more chunks arrive

### Metadata Distribution

The handler uses different strategies for embedding metadata depending on the `encode_first_chunk_only` setting:

- When `encode_first_chunk_only=True` (default), it waits for a chunk with suitable targets and embeds all metadata there
- When `encode_first_chunk_only=False`, it distributes metadata across multiple chunks as needed

### Digital Signature Verification

The digital signature is calculated based on the entire metadata, not just individual chunks. This ensures that the verification will detect if any part of the content is modified.

To verify content with embedded metadata from a `StreamingHandler`, use the `UnicodeMetadata.verify_metadata()` method:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Define a public key resolver function
def resolve_public_key(key_id: str) -> Optional[Ed25519PublicKey]:
    # In a real application, this would look up the key in a secure storage
    if key_id == "example-key-1":
        return public_key  # The public key corresponding to the private key used for signing
    return None

# After processing all chunks and obtaining the full response
is_valid, extracted_signer_id, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_response,
    public_key_resolver=resolve_public_key,  # Provide the resolver function
    require_hard_binding=False,
)

if is_valid:
    print("✅ Verification successful!")
    print(f"Signer ID: {extracted_signer_id}")
    print(f"Metadata: {verified_metadata}")
else:
    print("❌ Verification failed - content may have been tampered with or the key_id is not recognized.")
```

## Advanced Usage: Custom Streaming Handler

You can create a custom streaming handler by extending the `StreamingHandler` class:

```python
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import MetadataTarget
import json

class CustomStreamingHandler(StreamingHandler):
    def __init__(self, *args, **kwargs):
        # Add custom tracking
        self.chunks_processed = 0
        self.total_characters = 0

        # Initialize the parent class
        super().__init__(*args, **kwargs)

    def process_chunk(self, chunk):
        # Track statistics
        self.chunks_processed += 1
        self.total_characters += len(str(chunk))

        # Add chunk number to metadata
        self.metadata["chunk_number"] = self.chunks_processed
        self.metadata["total_characters"] = self.total_characters

        # Use the parent implementation to process the chunk
        return super().process_chunk(chunk)

    def finalize(self):
        # Add final statistics to metadata
        self.metadata["final_chunk_count"] = self.chunks_processed
        self.metadata["final_character_count"] = self.total_characters

        # Use the parent implementation to finalize
        return super().finalize()

    def get_statistics(self):
        """Custom method to get processing statistics"""
        return {
            "chunks_processed": self.chunks_processed,
            "total_characters": self.total_characters,
            "average_chunk_size": self.total_characters / max(1, self.chunks_processed)
        }

# Usage example
handler = CustomStreamingHandler(custom_metadata={"model": "custom-model"}, metadata_format="basic")

# Process chunks
for chunk in chunks:
    processed = handler.process_chunk(chunk)
    # ...

# Get statistics
stats = handler.get_statistics()
print(f"Streaming statistics: {json.dumps(stats, indent=2)}")
```

## Related Classes

- [`MetadataEncoder`](../api-reference/metadata-encoder.md) - Base class for embedding and extracting metadata
- [`StreamingMetadataEncoder`](../api-reference/streaming-metadata-encoder.md) - Lower-level interface for streaming scenarios
- [`UnicodeMetadata`](../api-reference/unicode_metadata.md) - Low-level utilities for working with Unicode variation selectors
