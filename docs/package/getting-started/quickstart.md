# Quick Start Guide

This guide will help you get started with EncypherAI for embedding and extracting metadata from AI-generated text.

## Basic Usage

### 1. Import the Package

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core import generate_key_pair, BasicPayload
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, Any
import time
```

### 2. Initialize the Encoder

```python
# Generate a key pair for digital signatures
private_key, public_key = generate_key_pair()
signer_id = "quickstart-key-1"

# In a real application, you would store these keys securely
# Here's a simple example of a public key store and resolver
public_keys_store = {signer_id: public_key}

def resolve_public_key(id_val: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(id_val)
```

### 3. Embed Metadata in Text

```python
# Define your metadata components
model_id_val = "gpt-4"
timestamp_val = int(time.time())  # Unix/Epoch timestamp
custom_meta = {
    "version": "2.3.0",
    "organization": "EncypherAI"
}

# Original AI-generated text
text = "This is AI-generated content that will contain invisible metadata."

# Embed metadata into the text
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    model_id=model_id_val,
    timestamp=timestamp_val,
    custom_metadata=custom_meta,
    metadata_format="basic",
    target="whitespace"
)

# The encoded_text looks identical to the original text when displayed,
# but contains invisible zero-width characters that encode the metadata

# Extract metadata without verification (if you just need the data)
extracted_payload: Optional[BasicPayload] = UnicodeMetadata.extract_metadata(encoded_text)
print(f"Extracted metadata (unverified): {extracted_payload}")

# Verify the metadata using the public key resolver
is_valid, returned_signer_id, payload_object = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_provider=resolve_public_key
)

if is_valid and payload_object:
    print("Metadata is valid and has not been tampered with.")
    print(f"Returned Signer ID: {returned_signer_id}")
    print(f"Verified metadata payload: {payload_object}")
    # Example: Accessing specific fields from BasicPayload
    if "custom_metadata" in payload_object:
        print(f"  Custom Version: {payload_object.get('custom_metadata', {}).get('version')}")
    print(f"  Timestamp: {payload_object.get('timestamp')}")
else:
    print("Metadata validation failed - content may have been tampered with.")
    if payload_object:
        print(f"  (Payload on failure: {payload_object})")
```

## Streaming Support

EncypherAI also supports streaming responses from LLM providers:

```python
from encypher.streaming.handlers import StreamingHandler
from encypher.core import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, Any
import time

# Initialize the streaming handler
stream_payload_data = {
    "model_id": "gpt-4-stream",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "custom_metadata": {"stream_source": "example_llm"}
}

streaming_handler = StreamingHandler(
    private_key=private_key,
    signer_id=signer_id,
    metadata=stream_payload_data,
    metadata_format="basic",
    target="whitespace",
    encode_first_chunk_only=True
)

# Process chunks as they arrive
# Example: simulate streaming response chunks
streaming_response_chunks = ["This is the first chunk ", "of a streamed response, ", "and this is the final part."]
encoded_chunks = []
for chunk in streaming_response_chunks:  # From your LLM provider
    encoded_chunk = streaming_handler.process_chunk(chunk=chunk)
    if encoded_chunk:  # May be None if buffering
        encoded_chunks.append(encoded_chunk)
        # Send to client or process as needed

# Don't forget to finalize the stream to process any remaining buffer
final_chunk = streaming_handler.finalize_stream()
if final_chunk:
    encoded_chunks.append(final_chunk)

# The complete encoded text with metadata
complete_encoded_text = "".join(encoded_chunks)
print(f"\nComplete streamed text: {complete_encoded_text}")

# Verify the complete text
is_valid, returned_signer_id, payload_object = UnicodeMetadata.verify_metadata(
    text=complete_encoded_text,
    public_key_provider=resolve_public_key
)

if is_valid and payload_object:
    print("Streamed metadata is valid.")
    print(f"  Returned Signer ID: {returned_signer_id}")
    print(f"  Verified payload: {payload_object}")
else:
    print("Streamed metadata validation failed.")
    if payload_object:
        print(f"  (Payload on failure: {payload_object})")
```

## Integrating with OpenAI

Here's a quick example with OpenAI:

```python
from openai import OpenAI
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, Any
import time

# Set up OpenAI client
# client = OpenAI(api_key="your-openai-api-key") # User needs to fill this

# Generate keys for digital signatures
private_key_openai, public_key_openai = generate_key_pair()
signer_id_openai = "openai-example-key"

# Store public key (in a real application, use a secure database)
public_keys_openai_store = {signer_id_openai: public_key_openai}
def resolve_public_key_openai(id_val: str) -> Optional[PublicKeyTypes]:
    return public_keys_openai_store.get(id_val)

# Get response from OpenAI (Example, replace with actual call if running)
# response = client.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": "Write a short poem about technology."}]
# )
# text_openai = response.choices[0].message.content
text_openai = "A short poem about technology, generated by an AI."

# Add metadata
openai_model_id = "gpt-4-openai"
openai_timestamp = int(time.time())
openai_custom_meta = {
    "organization": "Your Organization",
    "usage_info": "example_call"
}

encoded_text_openai = UnicodeMetadata.embed_metadata(
    text=text_openai,
    private_key=private_key_openai,
    signer_id=signer_id_openai,
    model_id=openai_model_id,
    timestamp=openai_timestamp,
    custom_metadata=openai_custom_meta,
    metadata_format="basic"
)

# The encoded_text now contains invisible metadata
print(f"\nOpenAI example encoded text: {encoded_text_openai}")

# Later, verify the metadata
is_valid, returned_signer_id, payload_object = UnicodeMetadata.verify_metadata(
    text=encoded_text_openai,
    public_key_provider=resolve_public_key_openai
)

if is_valid and payload_object:
    print(f"Verified OpenAI response metadata: {payload_object}")
    print(f"  Signer ID: {returned_signer_id}")
else:
    print("OpenAI response metadata validation failed.")
    if payload_object:
        print(f"  (Payload on failure: {payload_object})")
```

## Next Steps

Explore more advanced features in the User Guide:

- [Metadata Encoding](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
- [Tamper Detection](../user-guide/tamper-detection.md)
- [Streaming Support](../user-guide/streaming.md)
