# Streaming Support

EncypherAI provides robust support for embedding metadata in streaming content, such as text generated chunk-by-chunk from Large Language Models (LLMs). This is essential for real-time applications where you cannot wait for the full response to be generated before sending it to the user.

## The `StreamingHandler`

The `encypher.streaming.handlers.StreamingHandler` class is the core component for managing streaming data. It intelligently buffers incoming text chunks, embeds the signed metadata payload at the first suitable opportunity, and then passes the content through.

By default, the handler embeds the entire payload into the first chunk of text that has a suitable embedding target (like whitespace). This is the most efficient method for most use cases.

### Streaming Example

This example demonstrates the end-to-end streaming workflow.

```python
import time
from typing import Dict, Optional, Any

from encypher import UnicodeMetadata
from encypher.keys import generate_ed25519_key_pair
from encypher.streaming import StreamingHandler

# --- 1. Key Management ---
# Use the same key setup as in the basic examples.
private_key, public_key = generate_ed25519_key_pair()
signer_id = "streaming-guide-signer-001"
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_provider(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- 2. Initialize the StreamingHandler ---
# The handler is initialized with the metadata payload and signing credentials.
streaming_handler = StreamingHandler(
    private_key=private_key,
    signer_id=signer_id,
    timestamp=int(time.time()),
    custom_metadata={
        "model_id": "gpt-4o-stream",
        "source": "streaming-usage-guide"
    },
    # encode_first_chunk_only=True is the default and most common strategy.
)

# --- 3. Process Chunks from a Simulated Stream ---
# In a real application, these chunks would come from an LLM API.
streaming_response_chunks = [
    "This is the first chunk ",
    "of a streamed response, ",
    "and this is the final part."
]

full_encoded_response = ""
print("Simulating stream output:")
for chunk in streaming_response_chunks:
    # Pass each chunk to the handler
    encoded_chunk = streaming_handler.process_chunk(chunk=chunk)
    if encoded_chunk:
        print(encoded_chunk, end="")
        full_encoded_response += encoded_chunk

# --- 4. Finalize the Stream ---
# The finalize() method processes any remaining text in the buffer.
# It's crucial to call this at the end of the stream.
final_chunk = streaming_handler.finalize()
if final_chunk:
    print(final_chunk, end="")
    full_encoded_response += final_chunk
print("\n--- End of Stream ---")

# --- 5. Verify the Complete Text ---
# The final, complete text can be verified just like any other content.
# Since hard binding is not added to streamed content, we must disable it during verification.
is_valid, _, payload = UnicodeMetadata.verify_metadata(
    text=full_encoded_response,
    public_key_provider=public_key_provider,
    require_hard_binding=False  # Disable for streaming
)

print(f"\nStreamed text signature valid: {is_valid}")
if is_valid and payload:
    print(f"Verified Stream Payload: {payload.custom_metadata}")
```

## Provider-Specific Integrations

For detailed examples of how to integrate the `StreamingHandler` with specific LLM providers like **OpenAI**, **Anthropic**, and **LiteLLM**, please see the guides in the **[Integrations](../integrations)** section.
