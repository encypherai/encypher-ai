# OpenAI Integration

This guide explains how to integrate EncypherAI with OpenAI's API to embed metadata in AI-generated content from models like GPT-3.5 and GPT-4.

## Prerequisites

Before you begin, make sure you have:

1. An OpenAI API key
2. The OpenAI Python package installed
3. EncypherAI installed

```bash
uv pip install encypher-ai openai
```

## Basic Integration

### Non-Streaming Response

For standard (non-streaming) responses from OpenAI:

```python
import openai
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key")

# Generate key pair (replace with your actual key management)
private_key, public_key = generate_key_pair()

# Example public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "openai-nonstream-key":
        return public_key
    return None

# Create a completion
response = client.chat.completions.create(
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
    "organization": "YourOrganization",
    "timestamp": time.time(),
    "prompt_tokens": response.usage.prompt_tokens,
    "completion_tokens": response.usage.completion_tokens,
    "total_tokens": response.usage.total_tokens,
    "key_id": "openai-nonstream-key" # Identifier for the key
}

# Embed metadata using UnicodeMetadata
encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)

print("Original response:")
print(text)
print("\nResponse with embedded metadata:")
print(encoded_text)

# Later, extract and verify the metadata
# Extract metadata (optional)
# extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)

# Verify the metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    encoded_text,
    public_key_resolver=resolve_public_key # Pass the resolver function
)

print("\nExtracted metadata:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

### Streaming Response

For streaming responses, use the `StreamingHandler`:

```python
import openai
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "openai-stream-key":
        return public_key
    return None

# Create metadata
metadata = {
    "model": "gpt-4",
    "organization": "YourOrganization",
    "timestamp": time.time(),
    "key_id": "openai-stream-key"
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key # Use the private key
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

# Extract and verify the metadata
# Extract metadata (optional)
# extracted_metadata = UnicodeMetadata.extract_metadata(full_response)

# Verify the metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    full_response,
    public_key_resolver=resolve_public_key # Pass the resolver function
)

print("\nExtracted metadata:")
print(json.dumps(verified_metadata, indent=2))
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## Advanced Integration

### Function Calling

When using OpenAI's function calling feature:

```python
import openai
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time
import json

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "openai-func-key":
        return public_key
    return None

# Define functions
functions = [
    {
        "type": "function",
        "function": {
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
    }
]

# Create a completion with function calling
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ],
    tools=functions,
    tool_choice="auto"
)

# Get the response
message = response.choices[0].message

# Check if the model wants to call a function
if message.tool_calls:
    # Get the function call
    function_call = message.tool_calls[0].function
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
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the weather like in San Francisco?"},
            message,
            {
                "role": "tool",
                "tool_call_id": message.tool_calls[0].id,
                "name": function_name,
                "content": json.dumps(function_response)
            }
        ]
    )

    # Get the final response text
    final_text = response.choices[0].message.content

    # Create metadata
    metadata = {
        "model": response.model,
        "initial_function_call": function_name,
        "timestamp": time.time(),
        "key_id": "openai-func-key"
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
    # No function call, process as a regular response
    text = message.content
    metadata = {
        "model": response.model,
        "timestamp": time.time(),
        "key_id": "openai-func-key" # Use the same key_id for consistency
    }
    encoded_text = UnicodeMetadata.embed_metadata(text, metadata, private_key)
    print("Response with embedded metadata:")
    print(encoded_text)
    # Verification would be the same as above
```

### Custom Metadata Extraction

You can create a helper function to extract metadata from OpenAI responses:

```python
def extract_openai_metadata(response):
    """Extract metadata from an OpenAI API response."""
    metadata = {
        "model": response.model,
        "organization": "YourOrganization",
        "timestamp": time.time(),
    }

    # Add usage information if available
    if hasattr(response, "usage"):
        metadata.update({
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        })

    # Add function call information if available
    message = response.choices[0].message
    if hasattr(message, "tool_calls") and message.tool_calls:
        function_call = message.tool_calls[0].function
        metadata.update({
            "function_call": function_call.name,
            "function_args": json.loads(function_call.arguments)
        })

    return metadata
```

## Web Application Integration

Here's an example of integrating OpenAI and EncypherAI in a Flask web application:

```python
from flask import Flask, request, jsonify
import openai
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time

app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key")

# Generate key pair and resolver (replace with actual key management)
private_key, public_key = generate_key_pair()
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    if key_id == "fastapi-openai-key":
        return public_key
    return None

# Create a metadata encoder
encoder = UnicodeMetadata(private_key=private_key)

@app.route('/generate', methods=['POST'])
def generate():
    # Get request data
    data = request.json
    prompt = data.get('prompt', '')

    # Create a completion
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Get the response text
    text = response.choices[0].message.content

    # Create metadata
    metadata = {
        "model": response.model,
        "organization": "YourOrganization",
        "timestamp": time.time(),
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "user_id": data.get('user_id', 'anonymous')
    }

    # Embed metadata
    encoded_text = encoder.embed_metadata(text, metadata)

    # Return the response
    return jsonify({
        "text": encoded_text,
        "metadata": metadata
    })

@app.route('/verify', methods=['POST'])
def verify():
    # Get request data
    data = request.json
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

if __name__ == '__main__':
    app.run(debug=True)
```

## Streaming in Web Applications

For streaming responses in a web application:

```python
from flask import Flask, Response, request, stream_with_context
import openai
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
import time

app = Flask(__name__)

@app.post("/generate-stream")
def generate_stream(request: Request):
    # Get request data
    data = request.json
    prompt = data.get('prompt', '')

    # Create metadata
    metadata = {
        "model": "gpt-4",
        "timestamp": time.time(),
        "user_id": data.get('user_id', 'anonymous'), # Example extra field
        "key_id": "fastapi-openai-key"
    }

    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key
    )

    async def generate():
        # Create a streaming completion
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        # Process each chunk
        for chunk in completion:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content

                # Process the chunk
                processed_chunk = handler.process_chunk(chunk=content)

                # Yield the processed chunk if available
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

## Best Practices

1. **Include Model Information**: Always include the model name, version, and other relevant information in the metadata.

2. **Add Timestamps**: Include a UTC timestamp to track when the content was generated.

3. **Track Token Usage**: Include token counts to monitor API usage and costs.

4. **Use Secure Keys**: Store your OpenAI API key and EncypherAI secret key securely, using environment variables or a secure key management system.

5. **Handle Errors Gracefully**: Implement proper error handling for both OpenAI API calls and EncypherAI operations.

6. **Verify Before Trusting**: Always verify the metadata before relying on it, especially for security-sensitive applications.

7. **Choose Appropriate Targets**: For longer responses, using `whitespace` as the embedding target is usually sufficient. For shorter responses, consider using `all_characters` to ensure enough targets are available.

## Troubleshooting

### API Key Issues

If you encounter authentication errors with the OpenAI API:

```python
import os

# Set API key as environment variable
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Or configure the client with the key
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
        except openai.RateLimitError:
            retries += 1
            if retries == max_retries:
                raise
            # Exponential backoff with jitter
            sleep_time = (2 ** retries) + random.random()
            print(f"Rate limited, retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

# Example usage
def make_openai_call():
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short paragraph about AI ethics."}
        ]
    )

response = call_with_retry(make_openai_call)
```

### Metadata Extraction Failures

If metadata extraction fails:

1. Ensure the text hasn't been modified after embedding
2. Check if the text has enough suitable targets for embedding
3. Verify you're using the same secret key for embedding and extraction

## Related Documentation

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [EncypherAI Streaming Support](../user-guide/streaming.md)
- [Metadata Encoding Guide](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
