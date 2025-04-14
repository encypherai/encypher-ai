# Quick Start Guide

This guide will help you get started with EncypherAI for embedding and extracting metadata from AI-generated text.

## Basic Usage

### 1. Import the Package

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import time
```

### 2. Initialize the Encoder

```python
# Generate a key pair for digital signatures
private_key, public_key = generate_key_pair()
key_id = "quickstart-key-1"

# In a real application, you would store these keys securely
# Here's a simple example of a public key store and resolver
public_keys_store = {key_id: public_key}

def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)
```

### 3. Embed Metadata in Text

```python
# Define your metadata (must include key_id)
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "2.0.0",
    "organization": "EncypherAI",
    "key_id": key_id  # Required for verification
}

# Original AI-generated text
text = "This is AI-generated content that will contain invisible metadata."

# Embed metadata into the text
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key,
    target="whitespace"
)

# The encoded_text looks identical to the original text when displayed,
# but contains invisible zero-width characters that encode the metadata
```

### 4. Extract and Verify Metadata

```python
# Extract metadata without verification (if you just need the data)
extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)
print(f"Extracted metadata (unverified): {extracted_metadata}")

# Verify the metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)

if is_valid:
    print("Metadata is valid and has not been tampered with.")
    print(f"Verified metadata: {verified_metadata}")
else:
    print("Metadata validation failed - content may have been tampered with.")
```

## Streaming Support

EncypherAI also supports streaming responses from LLM providers:

```python
from encypher.streaming.handlers import StreamingHandler
import time

# Initialize the streaming handler
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "key_id": key_id  # Required for verification
}

streaming_handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key,
    target="whitespace",
    encode_first_chunk_only=True
)

# Process chunks as they arrive
encoded_chunks = []
for chunk in streaming_response_chunks:  # From your LLM provider
    encoded_chunk = streaming_handler.process_chunk(chunk=chunk)
    if encoded_chunk:  # May be None if buffering
        encoded_chunks.append(encoded_chunk)
        # Send to client or process as needed

# Don't forget to finalize the stream to process any remaining buffer
final_chunk = streaming_handler.finalize()
if final_chunk:
    encoded_chunks.append(final_chunk)

# The complete encoded text with metadata
complete_encoded_text = "".join(encoded_chunks)

# Verify the complete text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=complete_encoded_text,
    public_key_resolver=resolve_public_key
)
```

## Integrating with OpenAI

Here's a quick example with OpenAI:

```python
from openai import OpenAI
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
import time

# Set up OpenAI client
client = OpenAI(api_key="your-openai-api-key")

# Generate keys for digital signatures
private_key, public_key = generate_key_pair()
key_id = "openai-example-key"

# Store public key (in a real application, use a secure database)
public_keys = {key_id: public_key}
def resolve_public_key(key_id):
    return public_keys.get(key_id)

# Get response from OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a short poem about technology."}]
)
text = response.choices[0].message.content

# Add metadata
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "organization": "Your Organization",
    "key_id": key_id  # Required for verification
}
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key
)

# The encoded_text now contains invisible metadata
print(encoded_text)  # Looks just like the original text

# Later, verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"Verified OpenAI response metadata: {verified_metadata}")
```

## Next Steps

Explore more advanced features in the User Guide:

- [Metadata Encoding](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
- [Tamper Detection](../user-guide/tamper-detection.md)
- [Streaming Support](../user-guide/streaming.md)
