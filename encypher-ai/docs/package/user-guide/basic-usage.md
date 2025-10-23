# Basic Usage Guide

This guide provides a detailed walkthrough of the fundamental concepts in EncypherAI, expanding on the examples from the [Quick Start Guide](../getting-started/quickstart.md). Here, we'll dive deeper into key management, the embedding process, and verification.

> Note: The `timestamp` parameter is optional across all formats (basic, manifest, cbor_manifest, c2pa). If omitted, verification still works. For C2PA, action assertions (e.g., `c2pa.created`, `c2pa.watermarked`) omit the `when` field when no timestamp is supplied.

## The Core Workflow

The basic workflow in EncypherAI follows three main steps:
1.  **Key Management**: Securely manage the cryptographic keys used for signing and verification.
2.  **Embedding**: Create a metadata payload, sign it with a private key, and embed it invisibly into the text.
3.  **Verification**: Extract the metadata payload from the text and verify its integrity and authenticity using a public key.

The following example demonstrates this entire process.

```python
import time
from typing import Dict, Optional, Any

from encypher import UnicodeMetadata
from encypher.keys import generate_ed25519_key_pair

# --- 1. Key Management ---
# In a real application, you would load a securely stored private key and have a robust
# system for providing public keys for verification. For this example, we generate a new
# key pair and use a simple dictionary as a public key store.
private_key, public_key = generate_ed25519_key_pair()
signer_id = "user-guide-signer-001"

# The public_key_provider is a function that takes a key identifier (signer_id) and
# returns the corresponding public key. This allows the verification function to find
# the correct key to use.
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_provider(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- 2. Embedding Metadata ---
# With keys ready, you can now embed metadata. The `embed_metadata` method handles
# payload creation, signing, and invisible encoding in one step.

# Original AI-generated text
text = "This is AI-generated content that will contain invisible metadata."

# The `embed_metadata` method requires a private key and a signer_id to create the
# digital signature.
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    custom_metadata={
        "model_id": "gpt-4o",
        "source": "basic-usage-guide"
    }
)

print(f"Original text:  '{text}'")
print(f"Encoded text:   '{encoded_text}'")
print(f"Text appears identical: {text == encoded_text}") # Will be False due to invisible chars

# --- 3. Verification ---
# Verification is the most critical step. It confirms that the text has not been
# tampered with and that the signature is valid for the given payload.

is_valid: bool
extracted_signer_id: Optional[str]
verified_payload: Optional[Any]
is_valid, extracted_signer_id, verified_payload = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_provider=public_key_provider
)

print(f"\nSignature valid: {is_valid}")
if is_valid and verified_payload:
    # The payload object gives you access to the verified data
    print(f"Verified Signer ID: {extracted_signer_id}")
    print(f"Verified Timestamp: {verified_payload.timestamp}")
    print(f"Verified Custom Metadata: {verified_payload.custom_metadata}")
else:
    print("Metadata validation failed. The content may have been tampered with.")

```

### Embedding without a timestamp

```python
encoded_text_no_ts = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    custom_metadata={"model_id": "gpt-4o", "source": "basic-usage-guide"},
)

is_valid2, _, payload2 = UnicodeMetadata.verify_metadata(
    text=encoded_text_no_ts,
    public_key_provider=public_key_provider
)
print(f"Valid: {is_valid2}; Timestamp present: {bool(getattr(payload2, 'timestamp', None))}")
```

## What's Next?

Now that you understand the basic usage, you can explore more advanced topics:
- **[Metadata Encoding](./metadata-encoding.md)**: Learn about the different payload formats (`basic` vs. `cbor_manifest`).
- **[Tamper Detection](./tamper-detection.md)**: See how verification fails when content is modified.
- **[Streaming Support](./streaming.md)**: Integrate EncypherAI with streaming LLM responses.
