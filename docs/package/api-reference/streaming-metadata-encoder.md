# StreamingMetadataEncoder

**DEPRECATED**: The `StreamingMetadataEncoder` class is deprecated as of version 1.1.0. Please use the [`StreamingHandler`](../streaming/handlers.md) class with digital signatures instead, which provides stronger security through Ed25519 signatures rather than HMAC. See the [Streaming Support](../user-guide/streaming.md) guide for details on the new approach.

The `StreamingMetadataEncoder` class provides specialized functionality for embedding metadata in streaming content, such as text generated chunk by chunk from an LLM.

## Overview

When working with streaming content, embedding metadata presents unique challenges:

1. The content arrives in chunks, not all at once
2. Each chunk may not have suitable locations for embedding metadata
3. The metadata must be consistently verifiable across the entire content

The `StreamingMetadataEncoder` addresses these challenges by:

- Buffering content as needed
- Intelligently distributing metadata across chunks
- Ensuring HMAC verification works on the complete content

## Class Definition

```python
class StreamingMetadataEncoder:
    def __init__(
        self,
        secret_key: Optional[str] = None,
        target: Union[str, MetadataTarget] = "whitespace",
        encode_first_chunk_only: bool = True
    ):
        """
        Initialize a StreamingMetadataEncoder for handling streaming content.

        Args:
            secret_key: Optional secret key for HMAC verification. If not provided,
                        a random key will be generated.
            target: Where to embed metadata. Can be a string ("whitespace", "punctuation",
                   "first_letter", "last_letter", "all_characters", "file_end", "file_end_zwnbsp")
                   or a MetadataTarget enum. End-of-file targets append selectors at the end of
                   the content; "file_end_zwnbsp" prefixes a zero-width no-break space (U+FEFF).
            encode_first_chunk_only: If True, metadata will only be embedded in the first
                                    non-empty chunk that contains suitable targets.
        """
```

## Methods

### initialize_stream

```python
def initialize_stream(
    self,
    metadata: Dict[str, Any]
) -> str:
    """
    Initialize a new streaming session with the provided metadata.

    Args:
        metadata: Dictionary containing the metadata to embed

    Returns:
        stream_id: A unique identifier for this streaming session
    """
```

### process_chunk

```python
def process_chunk(
    self,
    stream_id: str,
    chunk: str,
    is_first: bool = False,
    is_last: bool = False
) -> str:
    """
    Process a chunk of streaming content.

    Args:
        stream_id: The stream ID returned by initialize_stream
        chunk: The text chunk to process
        is_first: Whether this is the first chunk in the stream
        is_last: Whether this is the last chunk in the stream

    Returns:
        The processed chunk with metadata embedded (if applicable)
    """
```

### finalize_stream

```python
def finalize_stream(
    self,
    stream_id: str
) -> Dict[str, Any]:
    """
    Finalize a streaming session.

    Args:
        stream_id: The stream ID returned by initialize_stream

    Returns:
        A dictionary containing information about the completed stream
    """
```

### get_stream_info

```python
def get_stream_info(
    self,
    stream_id: str
) -> Dict[str, Any]:
    """
    Get information about a streaming session.

    Args:
        stream_id: The stream ID returned by initialize_stream

    Returns:
        A dictionary containing information about the stream
    """
```

## Usage Example

```python
from encypher.streaming.encoders import StreamingMetadataEncoder
from encypher.core.unicode_metadata import MetadataTarget
import time

# Initialize the encoder
encoder = StreamingMetadataEncoder(
    target=MetadataTarget.WHITESPACE,
    encode_first_chunk_only=True
)

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "MyCompany",
    "timestamp": int(time.time())  # Unix/Epoch timestamp
}

# Initialize a streaming session
stream_id = encoder.initialize_stream(metadata)

# Process chunks as they arrive
chunks = [
    "This is the first chunk of text. ",
    "This is the second chunk. ",
    "And this is the final chunk."
]

processed_chunks = []
for i, chunk in enumerate(chunks):
    is_first = i == 0
    is_last = i == len(chunks) - 1

    processed_chunk = encoder.process_chunk(
        stream_id=stream_id,
        chunk=chunk,
        is_first=is_first,
        is_last=is_last
    )

    processed_chunks.append(processed_chunk)
    print(f"Processed chunk {i+1}: {processed_chunk}")

# If the last chunk wasn't marked as is_last=True, finalize the stream
if not chunks:  # If no chunks were processed with is_last=True
    encoder.finalize_stream(stream_id)

# Combine all processed chunks
full_text = "".join(processed_chunks)

# Now you can extract and verify the metadata using the standard MetadataEncoder
from encypher.core.metadata_encoder import MetadataEncoder

standard_encoder = MetadataEncoder()
is_valid, metadata_dict, clean_text = standard_encoder.verify_text(full_text)

print(f"Extracted metadata: {metadata_dict}")
print(f"Verification result: {is_valid}")
```

## Streaming with OpenAI

```python
from openai import OpenAI
from encypher.streaming.encoders import StreamingMetadataEncoder
import time

# Initialize OpenAI client
client = OpenAI(api_key="your-api-key")

# Initialize the streaming encoder
encoder = StreamingMetadataEncoder(
    target="whitespace",
    encode_first_chunk_only=True
)

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "MyCompany",
    "timestamp": int(time.time())  # Unix/Epoch timestamp
}

# Initialize a streaming session
stream_id = encoder.initialize_stream(metadata)

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
        processed_chunk = encoder.process_chunk(
            stream_id=stream_id,
            chunk=content
        )

        # Print and accumulate the processed chunk
        print(processed_chunk, end="", flush=True)
        full_response += processed_chunk

# Finalize the stream
encoder.finalize_stream(stream_id)

print("\n\nStreaming completed!")
```

## Streaming Handler Alternative

For a higher-level interface, you can also use the [`StreamingHandler`](../streaming/handlers.md) class, which provides a simpler API for common streaming scenarios.

## Implementation Details

### Metadata Distribution

The `StreamingMetadataEncoder` uses different strategies for embedding metadata depending on the `encode_first_chunk_only` setting:

- When `encode_first_chunk_only=True` (default), it waits for a chunk with suitable targets and embeds all metadata there
- When `encode_first_chunk_only=False`, it distributes metadata across multiple chunks as needed

### Buffering

If a chunk doesn't have enough suitable targets for embedding metadata, the encoder may buffer it and combine it with subsequent chunks until there are enough targets.

### HMAC Verification

The HMAC signature is calculated based on the entire content, not just individual chunks. This ensures that the verification will detect if any part of the content is modified.

## Related Classes

- [`MetadataEncoder`](./metadata-encoder.md) - Base class for embedding and extracting metadata
- [`StreamingHandler`](../streaming/handlers.md) - Higher-level interface for streaming scenarios
- [`UnicodeMetadata`](./unicode-metadata.md) - Low-level utilities for working with Unicode variation selectors

## StreamingHandler

The `StreamingHandler` class provides specialized functionality for embedding metadata in streaming content, such as text generated chunk by chunk from an LLM.

## Overview

When working with streaming content, embedding metadata presents unique challenges:

1. The content arrives in chunks, not all at once
2. Each chunk may not have suitable locations for embedding metadata
3. The metadata must be consistently verifiable across the entire content

The `StreamingHandler` addresses these challenges by:

- Buffering content as needed
- Intelligently distributing metadata across chunks
- Ensuring HMAC verification works on the complete content

## Class Definition

```python
class StreamingHandler:
    def __init__(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        target: Union[str, MetadataTarget] = "whitespace",
        encode_first_chunk_only: bool = True,
        hmac_secret_key: Optional[str] = None
    ):
        """
        Initialize a StreamingHandler for handling streaming content.

        Args:
            metadata: Dictionary containing the metadata to embed
            target: Where to embed metadata. Can be a string ("whitespace", "punctuation",
                   "first_letter", "last_letter", "all_characters") or a MetadataTarget enum.
            encode_first_chunk_only: If True, metadata will only be embedded in the first
                                    non-empty chunk that contains suitable targets.
            hmac_secret_key: Optional secret key for HMAC verification. Only needed if
                            you want to verify the integrity of the metadata.
        """
```

## Methods

### process_chunk

```python
def process_chunk(
    self,
    chunk: Union[str, Dict[str, Any]]
) -> Union[str, Dict[str, Any]]:
    """
    Process a chunk of streaming content.

    Args:
        chunk: The text chunk to process or a dictionary containing a text chunk

    Returns:
        The processed chunk with metadata embedded (if applicable)
    """
```

### finalize

```python
def finalize(self) -> Optional[str]:
    """
    Finalize the streaming process.

    This method should be called after all chunks have been processed to ensure
    that any remaining buffered content is properly processed.

    Returns:
        Any remaining processed content, or None if there is none
    """
```

## Usage Example

```python
from encypher.streaming.handlers import StreamingHandler
import time

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "1.0.0"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    target="whitespace",
    encode_first_chunk_only=True,
    hmac_secret_key="your-secret-key"  # Optional: Only needed for HMAC verification
)

# Process chunks as they arrive
chunks = [
    "This is the first chunk of text. ",
    "This is the second chunk. ",
    "And this is the final chunk."
]

full_text = ""
for chunk in chunks:
    # Process the chunk
    processed_chunk = handler.process_chunk(chunk=chunk)

    # Print and accumulate the processed chunk
    print(processed_chunk, end="", flush=True)
    full_text += processed_chunk

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    full_text += final_chunk

# Extract and verify the metadata
from encypher.core.unicode_metadata import UnicodeMetadata

# Verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_text,
    hmac_secret_key="your-secret-key"  # Use the same secret key as above
)
print(f"\nMetadata: {verified_metadata}")
print(f"Verified: {is_valid}")
