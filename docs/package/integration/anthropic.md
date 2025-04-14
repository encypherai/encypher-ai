# Anthropic Integration

This guide explains how to integrate EncypherAI with Anthropic's Claude models to embed metadata in AI-generated content.

## Prerequisites

Before you begin, make sure you have:

1. An Anthropic API key
2. The Anthropic Python package installed
3. EncypherAI installed

```bash
uv pip install encypher-ai anthropic
```

## Basic Integration

### Non-Streaming Response

For standard (non-streaming) responses from Anthropic:

```python
import anthropic
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair (replace with your actual key management)
private_key, public_key = generate_key_pair()

# Example public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "anthropic-nonstream-key":
        return public_key
    return None

# Create a message
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ]
)

# Get the response text
text = response.content[0].text

# Create metadata
metadata = {
    "model": response.model,
    "organization": "YourOrganization",
    "timestamp": time.time(),
    "input_tokens": response.usage.input_tokens,
    "output_tokens": response.usage.output_tokens,
    "key_id": "anthropic-nonstream-key" # Identifier for the key
}

# Embed metadata using UnicodeMetadata
encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)

print("Original response:")
print(text)
print("\nResponse with embedded metadata:")
print(encoded_text)

# Later, extract and verify the metadata
# Verify the metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    encoded_text,
    public_key_resolver=resolve_public_key
)

print("\nExtracted metadata:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

### Streaming Response

For streaming responses, use the `StreamingHandler`:

```python
import anthropic
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "anthropic-stream-key":
        return public_key
    return None

# Create metadata
metadata = {
    "model": "claude-3-opus-20240229",
    "organization": "YourOrganization",
    "timestamp": time.time(),
    "key_id": "anthropic-stream-key"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key # Use the private key
)

# Create a streaming message
with client.messages.stream(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ]
) as stream:
    # Process each chunk
    full_response = ""
    for text_delta in stream.text_deltas:
        # Process the chunk
        processed_chunk = handler.process_chunk(chunk=text_delta)

        # Print and accumulate the processed chunk if available
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream to process any remaining buffer
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True) # Print the final chunk too
    full_response += final_chunk

print("\n\nStreaming completed!")

# Extract and verify the metadata
# Verify the metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    full_response,
    public_key_resolver=resolve_public_key
)

print("\nExtracted metadata:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## Advanced Integration

### Tool Use (Function Calling)

When using Anthropic's tool use feature:

```python
import anthropic
import json
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "anthropic-tool-key":
        return public_key
    return None

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature"
                }
            },
            "required": ["location"]
        }
    }
]

# Create a message with tool use
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ],
    tools=tools
)

# Get the response
content = response.content

# Check if the model wants to use a tool
tool_use = None
for item in content:
    if item.type == "tool_use":
        tool_use = item
        break

if tool_use:
    # Get the tool call
    tool_name = tool_use.name
    tool_input = json.loads(tool_use.input)

    print(f"Tool call: {tool_name}")
    print(f"Input: {tool_input}")

    # Simulate tool response
    tool_response = {
        "location": tool_input["location"],
        "temperature": 72,
        "unit": tool_input.get("unit", "fahrenheit"),
        "condition": "sunny"
    }

    # Continue the conversation with the tool result
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": "What's the weather like in San Francisco?"},
            {
                "role": "assistant",
                "content": [tool_use]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(tool_response)
                    }
                ]
            }
        ]
    )

    # Get the final response text
    final_text = ""
    for item in response.content:
        if item.type == "text":
            final_text = item.text
            break

    # Create metadata
    metadata = {
        "model": response.model,
        "tool_used": tool_name,
        "timestamp": time.time(),
        "key_id": "anthropic-tool-key"
    }

    # Embed metadata
    encoded_text = UnicodeMetadata.embed_metadata(final_text, metadata, private_key)

    print("\nFinal response with embedded metadata:")
    print(encoded_text)

    # Verify the metadata
    is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
        encoded_text,
        public_key_resolver=resolve_public_key
    )
    print(f"\nVerification result: {'✅ Verified' if is_valid else '❌ Failed'}")
    if is_valid:
        print(json.dumps(verified_metadata, indent=2))

else:
    # No tool use, process as a regular response
    text = ""
    for item in content:
        if item.type == "text":
            text = item.text
            break
    metadata = {
        "model": response.model,
        "timestamp": time.time(),
        "key_id": "anthropic-tool-key" # Use same key_id
    }
    encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)
    print("Response with embedded metadata:")
    print(encoded_text)
    # Verification would be the same as above
```

### Custom Metadata Extraction

You can create a helper function to extract metadata from Anthropic responses:

```python
def extract_anthropic_metadata(response):
    """Extract metadata from an Anthropic API response."""
    metadata = {
        "model": response.model,
        "organization": "YourOrganization",
        "timestamp": time.time(),
    }

    # Add usage information if available
    if hasattr(response, "usage"):
        metadata.update({
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        })

    # Add tool use information if available
    tool_use = None
    for item in response.content:
        if hasattr(item, "type") and item.type == "tool_use":
            tool_use = item
            break

    if tool_use:
        metadata.update({
            "tool_use": tool_use.name,
            "tool_input": json.loads(tool_use.input)
        })

    return metadata
```

## Web Application Integration

Here's an example of integrating Anthropic and EncypherAI in a FastAPI web application:

```python
from fastapi import FastAPI, Request
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import asyncio

app = FastAPI()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "fastapi-anthropic-key":
        return public_key
    return None

@app.post("/generate-stream")
async def generate_stream(request: Request):
    # Get request data
    data = await request.json()
    prompt = data.get('prompt', '')

    # Create metadata
    metadata = {
        "model": "claude-3-opus-20240229",
        "timestamp": time.time(),
        "user_id": data.get('user_id', 'anonymous'), # Example extra field
        "key_id": "fastapi-anthropic-key"
    }

    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key
    )

    async def generate():
        async with client.messages.stream(
            # ... (model, max_tokens, messages)
        ) as stream:
            async for text_delta in stream.text_deltas:
                processed_chunk = handler.process_chunk(chunk=text_delta)
                if processed_chunk:
                    yield processed_chunk
            # Finalize the stream
            final_chunk = handler.finalize()
            if final_chunk:
                yield final_chunk

    return StreamingResponse(generate(), media_type="text/plain")

# Example Verification Endpoint (add this to your FastAPI app)
@app.post("/verify-text")
async def verify_text(request: Request):
    data = await request.json()
    text_to_verify = data.get("text")

    if not text_to_verify:
        raise HTTPException(status_code=400, detail="Text is required")

    is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
        text_to_verify,
        public_key_resolver=resolve_public_key
    )

    return {
        "is_valid": is_valid,
        "metadata": verified_metadata
    }

# Run with: uvicorn your_app_file:app --reload
```

## Streaming in Web Applications

For streaming responses in a web application:

```python
from fastapi import FastAPI, Response, Request, stream_with_context
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import asyncio

app = FastAPI()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "fastapi-anthropic-key":
        return public_key
    return None

@app.post("/generate-stream")
async def generate_stream(request: Request):
    # Get request data
    data = await request.json()
    prompt = data.get('prompt', '')

    # Create metadata
    metadata = {
        "model": "claude-3-opus-20240229",
        "timestamp": time.time(),
        "user_id": data.get('user_id', 'anonymous'), # Example extra field
        "key_id": "fastapi-anthropic-key"
    }

    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key
    )

    async def generate():
        async with client.messages.stream(
            # ... (model, max_tokens, messages)
        ) as stream:
            async for text_delta in stream.text_deltas:
                processed_chunk = handler.process_chunk(chunk=text_delta)
                if processed_chunk:
                    yield processed_chunk
            # Finalize the stream
            final_chunk = handler.finalize()
            if final_chunk:
                yield final_chunk

    return StreamingResponse(generate(), media_type="text/plain")

# Run with: uvicorn your_app_file:app --reload
```

## Best Practices

1. **Include Model Information**: Always include the model name, version, and other relevant information in the metadata.

2. **Add Timestamps**: Include a UTC timestamp to track when the content was generated.

3. **Track Token Usage**: Include token counts to monitor API usage and costs.

4. **Use Secure Keys**: Store your Anthropic API key and EncypherAI secret key securely, using environment variables or a secure key management system.

5. **Handle Errors Gracefully**: Implement proper error handling for both Anthropic API calls and EncypherAI operations.

6. **Verify Before Trusting**: Always verify the metadata before relying on it, especially for security-sensitive applications.

7. **Choose Appropriate Targets**: For longer responses, using `whitespace` as the embedding target is usually sufficient. For shorter responses, consider using `all_characters` to ensure enough targets are available.

## Troubleshooting

### API Key Issues

If you encounter authentication errors with the Anthropic API:

```python
import os

# Set API key as environment variable
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

# Or configure the client with the key
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

### Rate Limiting

If you hit rate limits, implement exponential backoff:

```python
import time
import random

def call_with_retry(func, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except anthropic.RateLimitError:
            retries += 1
            if retries == max_retries:
                raise
            # Exponential backoff with jitter
            sleep_time = (2 ** retries) + random.random()
            print(f"Rate limited, retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

# Example usage
def make_anthropic_call():
    return client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": "Write a short paragraph about AI ethics."}
        ]
    )

response = call_with_retry(make_anthropic_call)
```

### Metadata Extraction Failures

If metadata extraction fails:

1. Ensure the text hasn't been modified after embedding
2. Check if the text has enough suitable targets for embedding
3. Verify you're using the same secret key for embedding and extraction

## Related Documentation

- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [EncypherAI Streaming Support](../user-guide/streaming.md)
- [Metadata Encoding Guide](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
