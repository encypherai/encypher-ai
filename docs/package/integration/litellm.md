# LiteLLM Integration

This guide explains how to integrate Encypher with LiteLLM to embed and verify metadata in content generated from over 100 LLM providers through a unified interface.

## Prerequisites

Before you begin, ensure you have the necessary API keys for your chosen LLM providers and have installed the required packages:

```bash
uv pip install encypher-ai litellm
```

## Non-Streaming Example

This example demonstrates signing and verifying a standard response from a provider (e.g., OpenAI) via LiteLLM.

```python
import os
import litellm
from encypher.core.encypher import Encypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
# Set the API key for your chosen provider (e.g., OpenAI)
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

private_key, public_key = generate_ed25519_key_pair()
signer_id = "litellm-guide-signer-001"
public_keys_store = {signer_id: public_key}

encypher = Encypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get
)

# --- 2. Call the Provider via LiteLLM ---
response = litellm.completion(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Explain the significance of the C2PA standard."}
    ]
)
original_text = response.choices[0].message.content

# --- 3. Embed Metadata ---
custom_metadata = {
    "litellm_model": response.model,
    "provider": response.metadata.get("litellm_provider"),
    "usage_tokens": dict(response.usage),
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

For streaming responses, use the `StreamingEncypher` class with LiteLLM's streaming interface.

```python
import os
import litellm
from encypher.streaming.encypher import StreamingEncypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

private_key, public_key = generate_ed25519_key_pair()
signer_id = "litellm-streaming-signer-001"
public_keys_store = {signer_id: public_key}

# --- 2. Initialize the StreamingEncypher ---
streaming_encypher = StreamingEncypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get,
    custom_metadata={"litellm_model": "gpt-4o-stream"},
)

# --- 3. Process the Stream ---
stream = litellm.completion(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Write a short story about a friendly robot."}
    ],
    stream=True,
)

full_encoded_response = ""
print("--- Streaming Response with Embedded Metadata ---")
for chunk in stream:
    content = chunk.choices[0].delta.content or ""
    encoded_chunk = streaming_encypher.process_chunk(chunk=content)
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

1.  **Provider-Agnostic Code**: Use LiteLLM to write provider-agnostic code that works with multiple LLM providers.
2.  **Timestamps (optional)**: Timestamps are recommended but optional across all formats (including C2PA). When omitted, C2PA assertions that normally include a `when` field will simply omit it.
3.  **Include Provider Information**: Always include the provider name in the metadata to track which service generated the content.
4.  **Consistent Metadata**: Maintain a consistent metadata schema across different providers to simplify downstream processing.
5.  **API Key Management**: Use environment variables or a secure key management system like HashiCorp Vault to store API keys for different providers.
6.  **Error Handling**: Implement proper error handling for both LiteLLM and Encypher operations.

## Troubleshooting

### API Key Issues

If you encounter authentication errors, ensure your API keys are set correctly as environment variables or configured directly in LiteLLM:

```python
import os
import litellm

# Set API keys as environment variables (recommended)
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Or configure LiteLLM directly (less secure)
# litellm.api_key = "your-openai-api-key"
```

### Provider-Specific Issues

If you encounter issues with a specific provider, you can configure provider-specific settings in LiteLLM:

```python
import litellm

# Example: Configure settings for OpenAI
litellm.set_provider_config(
    provider="openai",
    config={
        "timeout": 30,
        "max_retries": 3
    }
)
```
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
- [Encypher Streaming Support](../user-guide/streaming.md)
- [Metadata Encoding Guide](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
