# Google Gemini Integration

This guide demonstrates how to integrate EncypherAI with Google's Gemini API to embed and verify metadata in both standard and streaming AI-generated content.

## Prerequisites

First, ensure you have an API key for Google Gemini. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey). Set it as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Next, install the necessary packages:

```bash
uv pip install encypher-ai google-generativeai
```

## Non-Streaming Example

This example demonstrates how to sign and verify a standard, non-streaming response from the Gemini API.

```python
import os
import google.generativeai as genai
from encypher.core.encypher import Encypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
# In a real application, use a secure key management solution.
# Make sure your GEMINI_API_KEY is set as an environment variable.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

private_key, public_key = generate_ed25519_key_pair()
signer_id = "gemini-guide-signer-001"
public_keys_store = {signer_id: public_key}

encypher = Encypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get
)

# --- 2. Call the Gemini API ---
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain the significance of the C2PA standard.")
original_text = response.text

# --- 3. Embed Metadata ---
custom_metadata = {
    "model_name": "gemini-1.5-flash",
    "safety_ratings": str(response.prompt_feedback.safety_ratings),
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

For streaming responses, use the `StreamingEncypher` class.

```python
import os
import google.generativeai as genai
from encypher.streaming.encypher import StreamingEncypher
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Setup ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

private_key, public_key = generate_ed25519_key_pair()
signer_id = "gemini-streaming-signer-001"
public_keys_store = {signer_id: public_key}

# --- 2. Initialize the StreamingEncypher ---
streaming_encypher = StreamingEncypher(
    private_key=private_key,
    signer_id=signer_id,
    public_key_provider=public_keys_store.get,
    custom_metadata={"model_name": "gemini-1.5-flash-stream"},
)

# --- 3. Process the Stream ---
model = genai.GenerativeModel("gemini-1.5-flash")
stream = model.generate_content(
    "Write a short story about a friendly robot.", stream=True
)

full_encoded_response = ""
print("--- Streaming Response with Embedded Metadata ---")
for chunk in stream:
    encoded_chunk = streaming_encypher.process_chunk(chunk=chunk.text)
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
from encypher.core.encypher import Encypher
verifier = Encypher(public_key_provider=public_keys_store.get)
verification_result = verifier.verify(text=full_encoded_response)

print(f"\nSignature valid: {verification_result.is_valid}")
if verification_result.is_valid:
    print(f"Verified Payload: {verification_result.payload.custom_metadata}")
```





## Best Practices

1.  **Include Model Information**: Always include the model name and other relevant details in the metadata.
2.  **Add Timestamps**: Include a UTC timestamp to track when the content was generated.
3.  **Use Secure Keys**: Store your Gemini API key and EncypherAI private keys securely, using environment variables or a dedicated key management system.

## Troubleshooting

### API Key Issues

If you encounter authentication errors, ensure your `GEMINI_API_KEY` is set correctly as an environment variable.

### Metadata Verification Failures

If metadata verification fails:

1.  Ensure the text has not been modified after the metadata was embedded.
2.  Confirm that the correct `public_key_provider` is being used and can resolve the `signer_id` found in the payload.
3.  Check that the text contains enough suitable characters for the metadata to have been embedded successfully.
