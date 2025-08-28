# Anthropic Integration

This guide explains how to integrate EncypherAI with Anthropic's Claude models to embed and verify metadata in AI-generated content.

## Prerequisites

Before you begin, ensure you have an Anthropic API key and have installed the required packages:

```bash
uv pip install encypher-ai anthropic
```

## Non-Streaming Example

This example demonstrates how to sign and verify a standard, non-streaming response from the Anthropic API.

```python
import os
import anthropic
from encypher.core.encypher import Encypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
# In a real application, use a secure key management solution.
# Make sure your ANTHROPIC_API_KEY is set as an environment variable.

private_key, public_key = generate_ed25519_key_pair()
signer_id = "anthropic-guide-signer-001"
public_keys_store = {signer_id: public_key}

encypher = Encypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get
)

client = anthropic.Anthropic()

# --- 2. Call the Anthropic API ---
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Explain the significance of the C2PA standard."}
    ]
)
original_text = response.content[0].text

# --- 3. Embed Metadata ---
custom_metadata = {
    "anthropic_model": response.model,
    "usage_tokens": {
        "input": response.usage.input_tokens,
        "output": response.usage.output_tokens,
    },
}

encoded_text = encypher.embed(
    text=original_text,
    custom_metadata=custom_metadata
)

print("--- Response with Embedded Metadata ---")
print(encoded_text)

# --- 4. Verify Metadata ---
verification_result = encypher.verify(text=encoded_text)

print(f"\nSignature valid: {verification_result.is_valid}")
if verification_result.is_valid:
    print(f"Verified Payload: {verification_result.payload.custom_metadata}")
```

## Streaming Example

For streaming responses, use the `StreamingEncypher` class to buffer chunks and embed the payload efficiently.

```python
import os
import anthropic
from encypher.streaming.encypher import StreamingEncypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
private_key, public_key = generate_ed25519_key_pair()
signer_id = "anthropic-streaming-signer-001"
public_keys_store = {signer_id: public_key}

client = anthropic.Anthropic()

# --- 2. Initialize the StreamingEncypher ---
streaming_encypher = StreamingEncypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get,
    custom_metadata={"anthropic_model": "claude-3-opus-stream"},
)

# --- 3. Process the Stream ---
full_encoded_response = ""
print("--- Streaming Response with Embedded Metadata ---")
with client.messages.stream(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Write a short story about a friendly robot."}
    ]
) as stream:
    for text_chunk in stream.text_stream:
        encoded_chunk = streaming_encypher.process_chunk(chunk=text_chunk)
        if encoded_chunk:
            print(encoded_chunk, end="")
            full_encoded_response += encoded_chunk

# --- 4. Finalize the Stream ---
final_chunk = streaming_encypher.finalize()
if final_chunk:
    print(final_chunk, end="")
    full_encoded_response += final_chunk
print("\n--- End of Stream ---")

# --- 5. Verify the Complete Streamed Text ---
# For verification, we use the standard Encypher class.
# Since hard binding is not added to streamed content, we must disable it during verification.
from encypher.core.encypher import Encypher
verifier = Encypher(public_key_provider=public_keys_store.get)
verification_result = verifier.verify(
    text=full_encoded_response,
    require_hard_binding=False  # Disable for streaming
)

print(f"\nSignature valid: {verification_result.is_valid}")
if verification_result.is_valid:
    print(f"Verified Payload: {verification_result.payload.custom_metadata}")
```



## Best Practices

1.  **Include Model Information**: Always include the model name and version in the metadata.
2.  **Timestamps (optional)**: It's recommended to include a UTC timestamp, but timestamps are optional across all formats (including C2PA). When omitted, C2PA assertions that normally include `when` will simply omit that field.
3.  **Track Token Usage**: Include token counts to monitor API usage and costs.
4.  **Use Secure Keys**: Store your Anthropic API key and EncypherAI private keys securely, using environment variables or a dedicated key management system.
5.  **Handle Errors Gracefully**: Implement proper error handling for both Anthropic API calls and EncypherAI operations.

## Troubleshooting

### API Key Issues

If you encounter authentication errors, ensure your Anthropic API key is set correctly as an environment variable:

```python
import os
import anthropic

# Set API key as an environment variable (recommended)
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# The client automatically reads the environment variable
client = anthropic.Anthropic()
```

### Rate Limiting

If you hit rate limits, the `anthropic` library can handle retries automatically. You can configure this during client initialization:

```python
import anthropic

# Configure the client with automatic retries
client = anthropic.Anthropic(max_retries=5)
```

### Metadata Verification Failures

If metadata verification fails:

1.  Ensure the text has not been modified after the metadata was embedded.
2.  Confirm that the correct `public_key_provider` is being used and can resolve the `signer_id` found in the payload.
3.  Check that the text contains enough suitable characters for the metadata to have been embedded successfully.
