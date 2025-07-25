# OpenAI Integration

This guide explains how to integrate EncypherAI with the OpenAI API to embed and verify metadata in content generated by models like GPT-4.

## Prerequisites

Before you begin, ensure you have an OpenAI API key and have installed the required packages:

```bash
uv pip install encypher-ai openai
```

## Non-Streaming Example

This example demonstrates how to sign and verify a standard, non-streaming response from the OpenAI API.

```python
import os
import openai
from encypher.core.encypher import Encypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
# In a real application, use a secure key management solution.
# Make sure your OPENAI_API_KEY is set as an environment variable.

private_key, public_key = generate_ed25519_key_pair()
signer_id = "openai-guide-signer-001"
public_keys_store = {signer_id: public_key}

encypher = Encypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get
)

client = openai.OpenAI()

# --- 2. Call the OpenAI API ---
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the significance of the C2PA standard."}
    ]
)
original_text = response.choices[0].message.content

# --- 3. Embed Metadata ---
custom_metadata = {
    "openai_model": response.model,
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

For streaming responses, use the `StreamingEncypher` class to buffer chunks and embed the payload efficiently.

```python
import os
import openai
from encypher.streaming.encypher import StreamingEncypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
private_key, public_key = generate_ed25519_key_pair()
signer_id = "openai-streaming-signer-001"
public_keys_store = {signer_id: public_key}

client = openai.OpenAI()

# --- 2. Initialize the StreamingEncypher ---
streaming_encypher = StreamingEncypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get,
    custom_metadata={"openai_model": "gpt-4o-stream"},
)

# --- 3. Process the Stream ---
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
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
