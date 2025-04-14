# LiteLLM Integration

This guide explains how to integrate EncypherAI with LiteLLM to embed metadata in AI-generated content from various LLM providers through a unified interface.

## Prerequisites

Before you begin, make sure you have:

1. API keys for the LLM providers you want to use
2. The LiteLLM Python package installed
3. EncypherAI installed

```bash
uv pip install encypher-ai litellm cryptography
```

## Basic Integration

LiteLLM provides a unified interface to multiple LLM providers, making it easy to switch between different models while maintaining the same code structure.

### Non-Streaming Response

For standard (non-streaming) responses using LiteLLM:

```python
import litellm
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json
import os

# Set up your API keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Generate key pair and resolver (replace with your actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "litellm-key-1":
        return public_key
    return None

# Create a completion using OpenAI
response = litellm.completion(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ]
)

# Get the response text
text = response.choices[0].message.content

# Create metadata
metadata = {
    "model": response.model,
    "provider": "openai",  # Determined based on the model
    "timestamp": time.time(),
    "key_id": "litellm-key-1", # Identifier for the key
    "prompt_tokens": response.usage.prompt_tokens,
    "completion_tokens": response.usage.completion_tokens,
    "total_tokens": response.usage.total_tokens
}

# Embed metadata
encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)

print("Original response:")
print(text)
print("\nResponse with embedded metadata:")
print(encoded_text)

# Later, extract and verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    encoded_text,
    public_key_resolver=resolve_public_key
)

print("\nExtracted metadata:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

### Streaming Response

For streaming responses, use the `StreamingHandler` with LiteLLM:

```python
import litellm
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import os

# Set up your API keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Generate key pair and resolver (replace with your actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "litellm-stream-key":
        return public_key
    return None

# Create metadata
metadata = {
    "model": "gpt-4",
    "provider": "openai",
    "timestamp": time.time(),
    "key_id": "litellm-stream-key"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key # Use the private key
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
    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content

        # Process the chunk
        processed_chunk = handler.process_chunk(chunk=content)

        # Print and accumulate the processed chunk if available
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")

# Extract and verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    full_response,
    public_key_resolver=resolve_public_key
)

print("\nExtracted metadata:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## Advanced Integration

### Using Different LLM Providers

LiteLLM makes it easy to switch between different providers:

```python
import litellm
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json
import os

# Set up your API keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Generate key pair and resolver (replace with your actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # Use different keys per provider or a central key
    if key_id == "litellm-openai-key":
        return public_key # Same key for demo
    elif key_id == "litellm-anthropic-key":
        return public_key # Same key for demo
    return None

# Function to generate text with metadata using any LLM provider
def generate_with_metadata(model, prompt, system_prompt=None):
    # Determine provider based on model prefix
    if model.startswith("gpt"):
        provider = "openai"
        key_id = "litellm-openai-key"
    elif model.startswith("claude"):
        provider = "anthropic"
        key_id = "litellm-anthropic-key"
    else:
        provider = "unknown"
        key_id = "litellm-unknown-key" # Might need a default or error

    # Create messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Create a completion
    response = litellm.completion(
        model=model,
        messages=messages
    )

    # Get the response text
    text = response.choices[0].message.content

    # Create metadata
    metadata = {
        "model": response.model,
        "provider": provider,
        "timestamp": time.time(),
        "key_id": key_id
    }

    # Add usage info if available
    if hasattr(response, "usage"):
        metadata.update({
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        })

    # Embed metadata
    encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)

    return encoded_text, metadata

# Example usage with different models
openai_response, openai_meta = generate_with_metadata(
    model="gpt-4",
    prompt="Write a short paragraph about AI ethics.",
    system_prompt="You are a helpful assistant."
)

anthropic_response, anthropic_meta = generate_with_metadata(
    model="claude-3-opus-20240229",
    prompt="Write a short paragraph about AI ethics."
)

print("OpenAI Response:")
print(openai_response)
print("\nMetadata:", openai_meta)

print("\nAnthropic Response:")
print(anthropic_response)
print("\nMetadata:", anthropic_meta)

# Verify the responses
print("\nVerifying responses...")
for i, (encoded, original_meta) in enumerate([openai_response, anthropic_response]):
    is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
        encoded,
        public_key_resolver=resolve_public_key
    )
    print(f"\nResponse {i+1} (Model: {original_meta['model']}):")
    print(f"  Verified Metadata: {json.dumps(verified_metadata, indent=2)}")
    print(f"  Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

### Function Calling with LiteLLM

Using function calling with LiteLLM and EncypherAI:

```python
import litellm
import json
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time

# Assume LiteLLM Proxy is running at http://localhost:8000
litellm.api_base = "http://localhost:8000"

# Set a virtual key (used by the proxy to route to the actual key)
litellm.api_key = "sk-1234" # Example virtual key

# Generate key pair and resolver for proxy interaction
private_key, public_key = generate_key_pair()
def resolve_public_key_proxy(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "litellm-proxy-key":
        return public_key
    return None

# Create a completion via the proxy
response = litellm.completion(
    model="gpt-4",  # The model requested via proxy
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ],
    functions=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    ],
    function_call="auto"
)

# Get the response
message = response.choices[0].message

# Check if the model wants to call a function
if hasattr(message, "function_call") and message.function_call:
    # Get the function call
    function_call = message.function_call
    function_name = function_call.name
    function_args = json.loads(function_call.arguments)

    print(f"Function call: {function_name}")
    print(f"Arguments: {function_args}")

    # Simulate function response
    function_response = {
        "location": function_args["location"],
        "temperature": 72,
        "unit": function_args.get("unit", "fahrenheit"),
        "condition": "sunny"
    }

    # Continue the conversation with the function result
    response = litellm.completion(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the weather like in San Francisco?"},
            message,
            {
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_response)
            }
        ]
    )

    # Get the final response text
    text = response.choices[0].message.content
else:
    # Get the response text
    text = message.content

# Create metadata
metadata = {
    "model": response.model,
    "provider": "openai", # Provider info might come from proxy response
    "timestamp": time.time(),
    "key_id": "litellm-proxy-key",
    "function_call": message.function_call.name if hasattr(message, "function_call") and message.function_call else None
}

# Add usage information if available
if hasattr(response, "usage"):
    metadata.update({
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    })

# Embed metadata
encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)

print("Response via LiteLLM Proxy with embedded metadata:")
print(encoded_text)

# Verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    encoded_text,
    public_key_resolver=resolve_public_key_proxy
)

print("\nExtracted metadata from proxy response:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## LiteLLM Proxy Integration

If you're using LiteLLM as a proxy server, you can integrate EncypherAI on the server side:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from litellm.proxy.proxy_server import router as litellm_router
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import json

app = FastAPI()
security = HTTPBearer()
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "litellm-proxy-key":
        return public_key
    return None

# Add LiteLLM router
app.include_router(litellm_router)

# Middleware to process responses
@app.middleware("http")
async def add_metadata_middleware(request, call_next):
    # Process the request normally
    response = await call_next(request)

    # Check if this is a completion response
    if request.url.path == "/v1/chat/completions" and response.status_code == 200:
        # Get the response body
        body = await response.body()
        data = json.loads(body)

        # Check if this is a streaming response
        if "choices" in data and len(data["choices"]) > 0:
            # Get the response text
            if "message" in data["choices"][0] and "content" in data["choices"][0]["message"]:
                text = data["choices"][0]["message"]["content"]

                # Create metadata
                metadata = {
                    "model": data.get("model", "unknown"),
                    "organization": "YourOrganization",
                    "timestamp": time.time(),
                    "key_id": "litellm-proxy-key"
                }

                # Add usage information if available
                if "usage" in data:
                    metadata.update({
                        "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                        "completion_tokens": data["usage"].get("completion_tokens", 0),
                        "total_tokens": data["usage"].get("total_tokens", 0)
                    })

                # Embed metadata
                encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)

                # Update the response
                data["choices"][0]["message"]["content"] = encoded_text

                # Return the modified response
                return JSONResponse(
                    content=data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

    return response

# Authentication endpoint
@app.post("/auth")
async def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validate the token
    token = credentials.credentials
    if token != "your-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {"authenticated": True}

# Verification endpoint
@app.post("/verify")
async def verify(request: Request):
    data = await request.json()
    text = data.get("text", "")

    # Extract and verify metadata
    try:
        is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
            text,
            public_key_resolver=resolve_public_key
        )

        return {
            "has_metadata": True,
            "metadata": verified_metadata,
            "verified": is_valid
        }
    except Exception as e:
        return {
            "has_metadata": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Client-Side Integration

When using LiteLLM as a client to a proxy server:

```python
import litellm
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import os

# Configure LiteLLM to use a proxy
litellm.api_base = "http://localhost:8000"
litellm.api_key = "sk-1234" # Example virtual key

# Generate key pair and resolver for proxy streaming
private_key, public_key = generate_key_pair()
def resolve_public_key_proxy_stream(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "litellm-proxy-stream-key":
        return public_key
    return None

# Create metadata
metadata = {
    "model": "gpt-4", # The model requested via proxy
    "provider": "openai", # Or determined by proxy
    "timestamp": time.time(),
    "key_id": "litellm-proxy-stream-key"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key # Use the private key
)

# Create a streaming completion via the proxy
response = litellm.completion(
    model="gpt-4",  # This will be routed through the proxy
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short paragraph about AI ethics."}
    ],
    stream=True
)

# Process each chunk
full_response = ""
for chunk in response:
    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content

        # Process the chunk
        processed_chunk = handler.process_chunk(chunk=content)

        # Print and accumulate the processed chunk if available
        if processed_chunk:
            print(processed_chunk, end="", flush=True)
            full_response += processed_chunk

# Finalize the stream
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming via LiteLLM Proxy completed!")

# Extract and verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    full_response,
    public_key_resolver=resolve_public_key_proxy_stream
)

print("\nExtracted metadata from proxy stream:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## Best Practices

1. **Provider-Agnostic Code**: Use LiteLLM to write provider-agnostic code that works with multiple LLM providers.

2. **Include Provider Information**: Always include the provider name in the metadata to track which service generated the content.

3. **Fallback Mechanisms**: Implement fallback mechanisms to switch between providers if one fails.

4. **Consistent Metadata**: Maintain a consistent metadata schema across different providers to simplify downstream processing.

5. **API Key Management**: Use environment variables or a secure key management system to store API keys for different providers.

6. **Error Handling**: Implement proper error handling for both LiteLLM and EncypherAI operations.

7. **Model Selection**: Use LiteLLM's model selection capabilities to choose the most appropriate model for each task.

## Troubleshooting

### API Key Issues

If you encounter authentication errors with LiteLLM:

```python
import os

# Set API keys as environment variables
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Or configure LiteLLM directly
litellm.set_api_key(api_key="your-api-key", key_type="openai")
litellm.set_api_key(api_key="your-api-key", key_type="anthropic")
```

### Provider-Specific Issues

If you encounter issues with a specific provider:

```python
# Configure provider-specific settings
litellm.set_provider_config(provider="openai", config={
    "timeout": 30,
    "max_retries": 3
})

# Or use a different provider
try:
    response = litellm.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
except Exception as e:
    print(f"OpenAI failed: {str(e)}")
    # Fallback to Anthropic
    response = litellm.completion(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": "Hello"}]
    )
```

### Metadata Extraction Failures

If metadata extraction fails:

1. Ensure the text hasn't been modified after embedding.
2. Check if the text has enough suitable targets for embedding.
3. Verify you're using the same secret key for embedding and extraction.

## Related Documentation

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [EncypherAI Streaming Support](../user-guide/streaming.md)
- [Metadata Encoding Guide](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
