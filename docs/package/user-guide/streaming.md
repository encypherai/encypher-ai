# Streaming Support

EncypherAI provides robust support for embedding metadata in streaming content, such as text generated chunk by chunk from Large Language Models (LLMs). This guide explains how to use EncypherAI's streaming capabilities effectively.

## Understanding Streaming Challenges

When working with streaming content, embedding metadata presents unique challenges:

1. **Partial Content**: Content arrives in chunks, not all at once
2. **Target Availability**: Individual chunks may not have suitable locations for embedding metadata
3. **Verification Integrity**: Signature verification must work on the complete content
4. **Consistent Extraction**: Metadata must be extractable from the final combined content

EncypherAI addresses these challenges through specialized streaming handlers and encoders.

## Using the StreamingHandler

The `StreamingHandler` class provides a simple interface for processing streaming content:

```python
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import time

# Generate key pair (replace with your actual key management)
private_key, public_key = generate_key_pair()
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# Example public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # In a real application, fetch the public key based on key_id
    # For this example, we assume a single known key
    if key_id == "user-key-1": # Example key_id, often embedded in metadata
        return public_key
    return None

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "2.0.0",
    "key_id": "user-key-1" # Include an identifier for the key
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key, # Provide the private key for signing
    target="whitespace",  # Where to embed metadata
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
    processed_chunk = handler.process_chunk(chunk=chunk)
    if processed_chunk:
        processed_chunks.append(processed_chunk)
        print(f"Processed chunk: {processed_chunk}")

# Finalize the stream to process any remaining buffered text
final_chunk = handler.finalize()
if final_chunk:
    processed_chunks.append(final_chunk)
    print(f"Final chunk: {final_chunk}")

# Combine all processed chunks
full_text = "".join(processed_chunks)

# Verify the metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    full_text,
    public_key_resolver=resolve_public_key # Provide the resolver function
)
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
print(f"Verified metadata: {verified_metadata}")

# Note: StreamingHandler uses UnicodeMetadata for target-based embedding
# which enables precise metadata placement in streaming content
```

## How Streaming Works

The `StreamingHandler` uses an intelligent buffering strategy:

1. **Buffering**: Accumulates chunks until there are enough suitable targets for embedding metadata
2. **Embedding**: Embeds metadata when sufficient targets are available
3. **Flushing**: Returns processed content and clears the buffer
4. **Finalization**: Ensures all metadata is properly embedded by the end of the stream

## Integration with LLM Providers

### OpenAI

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

# Generate key pair and resolver (as in the main example)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "openai-key-1": return public_key
    return None

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),
    "version": "2.0.0",
    "key_id": "openai-key-1"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key,
    target="whitespace",
    encode_first_chunk_only=True
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

        # Print and accumulate the processed chunk if not None
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")
```

### Anthropic

```python
import anthropic
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import time

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair and resolver
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "anthropic-key-1": return public_key
    return None

# Create metadata
metadata = {
    "model_id": "claude-3-opus-20240229",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),
    "version": "2.0.0",
    "key_id": "anthropic-key-1"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key,
    target="whitespace",
    encode_first_chunk_only=True
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

        # Print and accumulate the processed chunk if not None
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")
```

### LiteLLM (Multi-Provider)

```python
import litellm
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import time

# Configure LiteLLM
litellm.api_key = "your-api-key"

# Generate key pair and resolver
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "litellm-key-1": return public_key
    return None

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "provider": "openai",
    "timestamp": int(time.time()),
    "version": "2.0.0",
    "key_id": "litellm-key-1"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key,
    target="whitespace",
    encode_first_chunk_only=True
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
    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content

        # Process the chunk
        processed_chunk = handler.process_chunk(chunk=content)

        # Print and accumulate the processed chunk if not None
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")
```

## Advanced Configuration

### Customizing Target Selection

You can customize where metadata is embedded in the streaming text:

```python
from encypher.streaming.handlers import StreamingHandler
from encypher.core.unicode_metadata import MetadataTarget
import time

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "2.0.0",
    "key_id": "user-key-1" # Include an identifier for the key
}

# Initialize with custom target
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key, # Provide the private key for signing
    target=MetadataTarget.PUNCTUATION,  # Embed after punctuation
    encode_first_chunk_only=True
)
```

### Controlling Embedding Strategy

The `encode_first_chunk_only` parameter determines whether metadata is embedded only in the first chunk or throughout the stream:

```python
# Embed only in the first chunk (default)
handler1 = StreamingHandler(
    metadata=metadata,
    private_key=private_key, # Provide the private key for signing
    encode_first_chunk_only=True
)

# Embed throughout the stream
handler2 = StreamingHandler(
    metadata=metadata,
    private_key=private_key, # Provide the private key for signing
    encode_first_chunk_only=False
)
```

### Custom Buffering Strategy

You can control the buffering behavior:

```python
# Wait for at least 50 characters before embedding
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key, # Provide the private key for signing
    min_buffer_size=50,
    encode_first_chunk_only=True
)
```

## Web Integration Examples

### FastAPI Streaming Endpoint

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import OpenAI
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
import time
import asyncio

app = FastAPI()

@app.post("/generate-signed-stream/")
async def generate_stream(request: Request):
    # Parse request
    data = await request.json()
    prompt = data.get("prompt", "Write something interesting.")

    # Initialize OpenAI client
    client = OpenAI(api_key="your-api-key")

    # Generate key pair and resolver (replace with proper key management)
    private_key, public_key = generate_key_pair()
    def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
        if key_id == "fastapi-key-1": return public_key
        return None

    # Create metadata
    metadata = {
        "prompt_hash": hash(prompt), # Example detail
        "timestamp": int(time.time()),
        "version": "2.0.0",
        "key_id": "fastapi-key-1"
    }

    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key, # Provide the private key for signing
        target="whitespace",
        encode_first_chunk_only=True
    )

    async def signed_stream():
        async for chunk in llm_stream_generator(prompt):
            processed_chunk = handler.process_chunk(chunk)
            if processed_chunk:
                yield processed_chunk
        # Finalize the stream
        final_chunk = handler.finalize()
        if final_chunk:
            yield final_chunk

    return StreamingResponse(signed_stream(), media_type="text/plain")

# Example verification endpoint (optional)
@app.post("/verify-text/")
async def verify_text(request: Request):
    data = await request.json()
    text_to_verify = data.get("text")

    if not text_to_verify:
        raise HTTPException(status_code=400, detail="Text is required")

    # Verify metadata using the public key resolver
    is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
        text_to_verify,
        public_key_resolver=resolve_public_key # Provide the resolver function
    )

    return {
        "is_valid": is_valid,
        "metadata": verified_metadata
    }

# Run with: uvicorn your_app_file:app --reload
```

### Flask Streaming Example

```python
from flask import Flask, Response, request, stream_with_context
from openai import OpenAI
from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
import time
import json

app = Flask(__name__)

@app.route("/generate-signed-stream", methods=["POST"])
def generate_stream():
    # Parse request
    data = request.json
    prompt = data.get("prompt", "Write something interesting.")

    # Initialize OpenAI client
    client = OpenAI(api_key="your-api-key")

    # Generate key pair and resolver (replace with proper key management)
    private_key, public_key = generate_key_pair()
    def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
        if key_id == "flask-key-1": return public_key
        return None

    # Create metadata
    metadata = {
        "prompt_hash": hash(prompt), # Example detail
        "timestamp": int(time.time()),
        "version": "2.0.0",
        "key_id": "flask-key-1"
    }

    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key, # Provide the private key for signing
        target="whitespace",
        encode_first_chunk_only=True
    )

    def signed_stream():
        for chunk in llm_stream_generator(prompt):
            processed_chunk = handler.process_chunk(chunk)
            if processed_chunk:
                yield processed_chunk
        # Finalize the stream
        final_chunk = handler.finalize()
        if final_chunk:
            yield final_chunk

    return Response(stream_with_context(signed_stream()), mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
