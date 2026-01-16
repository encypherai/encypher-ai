# Google Gemini Integration

This guide demonstrates how to integrate Encypher with Google's Gemini API to embed and verify metadata in both standard and streaming AI-generated content.

## Prerequisites

First, ensure you have an API key for Google Gemini. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey). Set it as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Next, install the necessary packages:

```bash
uv add encypher-ai google-generativeai
```

## Non-Streaming Example

This example demonstrates how to sign and verify a standard, non-streaming response from the Gemini API.

```python
import os
import google.generativeai as genai
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata

# --- 1. Setup ---
# In a real application, use a secure key management solution.
# Make sure your GEMINI_API_KEY is set as an environment variable.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

private_key, public_key = generate_ed25519_key_pair()
signer_id = "gemini-guide-signer-001"
public_keys_store = {signer_id: public_key}

# --- 2. Call the Gemini API ---
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain the significance of the C2PA standard.")
original_text = response.text

# --- 3. Embed Metadata ---
custom_metadata = {
    "model_name": "gemini-1.5-flash",
    "safety_ratings": str(response.prompt_feedback.safety_ratings),
}

encoded_text = UnicodeMetadata.embed_metadata(
    text=original_text,
    private_key=private_key,
    signer_id=signer_id,
    custom_metadata=custom_metadata,
    metadata_format="basic",
)

print("--- Response with Embedded Metadata ---")
print(encoded_text)

# --- 4. Verify Metadata ---
is_valid, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=public_keys_store.get,
)

print(f"\nSignature valid: {is_valid}")
if is_valid and payload:
    print(f"Verified Signer ID: {extracted_signer_id}")
    print(f"Verified Payload: {payload}")
```
## Streaming Example

For streaming responses, use the `StreamingHandler` class.

```python
import os
import google.generativeai as genai

from encypher.streaming.handlers import StreamingHandler
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata

# --- 1. Setup ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

private_key, public_key = generate_ed25519_key_pair()
signer_id = "gemini-streaming-signer-001"
public_keys_store = {signer_id: public_key}

# --- 2. Initialize the StreamingHandler ---
streaming_handler = StreamingHandler(
    private_key=private_key,
    signer_id=signer_id,
    custom_metadata={"model_name": "gemini-1.5-flash-stream"},
    metadata_format="basic",
)

# --- 3. Process the Stream ---
model = genai.GenerativeModel("gemini-1.5-flash")
stream = model.generate_content(
    "Write a short story about a friendly robot.", stream=True
)

full_encoded_response = ""
print("--- Streaming Response with Embedded Metadata ---")
for chunk in stream:
    encoded_chunk = streaming_handler.process_chunk(chunk=chunk.text)
    if encoded_chunk:
        print(encoded_chunk, end="")
        full_encoded_response += encoded_chunk

# --- 4. Finalize the Stream ---
final_chunk = streaming_handler.finalize()
if final_chunk:
    print(final_chunk, end="")
    full_encoded_response += final_chunk
print("\n--- End of Stream ---")

# --- 5. Verify the Complete Streamed Text ---
is_valid, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(
    text=full_encoded_response,
    public_key_resolver=public_keys_store.get,
)

print(f"\nSignature valid: {is_valid}")
if is_valid and payload:
    print(f"Verified Signer ID: {extracted_signer_id}")
    print(f"Verified Payload: {payload}")
```





## Best Practices

1.  **Include Model Information**: Always include the model name and other relevant details in the metadata.
2.  **Timestamps (optional)**: It's recommended to include a UTC timestamp, but timestamps are optional across all formats (including C2PA). When omitted, C2PA assertions that normally include `when` will simply omit that field.
3.  **Use Secure Keys**: Store your Gemini API key and Encypher private keys securely, using environment variables or a dedicated key management system.

## Troubleshooting

### API Key Issues

If you encounter authentication errors, ensure your `GEMINI_API_KEY` is set correctly as an environment variable.

### Metadata Verification Failures

If metadata verification fails:

1.  Ensure the text has not been modified after the metadata was embedded.
2.  Confirm that the correct `public_key_resolver` is being used and can resolve the `signer_id` found in the payload.
3.  Check that the text contains enough suitable characters for the metadata to have been embedded successfully.
