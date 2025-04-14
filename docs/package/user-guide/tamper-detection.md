# Tamper Detection

One of EncypherAI's key security features is its ability to detect when AI-generated content has been tampered with. This is achieved through Ed25519 digital signature verification.

## How Digital Signature Verification Works

When metadata is embedded in text, EncypherAI creates a digital signature using:

1. The metadata content (serialized as JSON)
2. A private key (Ed25519PrivateKey)

This signature is embedded alongside the metadata. When the content is later verified, the following conditions must be met:

- The public key corresponding to the private key must be available through the resolver
- The metadata must not have been altered
- The text content must not have been modified
- The `key_id` in the metadata must be valid

If any of these conditions are not met, verification will fail, indicating that tampering has occurred or the content comes from an untrusted source.

## Implementation Details

The digital signature generation and verification process uses the following approach:

```python
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import json

# Generate key pair
def generate_key_pair():
    """Generate an Ed25519 key pair for signing and verification."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

# When embedding metadata with signature
metadata_bytes = json.dumps(metadata).encode('utf-8')
signature = private_key.sign(metadata_bytes)  # Sign the metadata

# When verifying (resolver function to get public key by key_id)
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # Look up the public key for the given key_id
    return public_keys_store.get(key_id)

# Verification
extracted_signature = # (from embedded data)
extracted_metadata = # (from embedded data)
key_id = extracted_metadata.get("key_id")
public_key = resolve_public_key(key_id)

try:
    # Verify the signature
    public_key.verify(extracted_signature, metadata_bytes)
    is_valid = True
except Exception:
    is_valid = False
```

## Preventing Tampering Attacks

EncypherAI protects against several types of attacks:

### 1. Content Modification

If someone modifies the visible text content while preserving the invisible metadata:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
import time

# Generate key pair
private_key, public_key = generate_key_pair()
key_id = "example-key-1"

# Store public key
public_keys_store = {key_id: public_key}

# Create a resolver function
def resolve_public_key(key_id):
    return public_keys_store.get(key_id)

# Create metadata with key_id
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "key_id": key_id  # Required for verification
}

# Embed metadata with digital signature
encoded_text = UnicodeMetadata.embed_metadata(
    text="This is the original AI-generated content.",
    metadata=metadata,
    private_key=private_key
)

# Modified text (with preserved metadata)
tampered_text = "This has been changed but still has the metadata."

# Verification will fail
is_valid, _ = UnicodeMetadata.verify_metadata(
    text=tampered_text,
    public_key_resolver=resolve_public_key
)  # is_valid will be False
```

### 2. Signature Forgery

If an attacker tries to create their own metadata without the private key:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
import time

# Original key pair
original_private_key, original_public_key = generate_key_pair()
original_key_id = "original-key-1"

# Attacker's key pair
attacker_private_key, attacker_public_key = generate_key_pair()
attacker_key_id = "attacker-key-1"

# Store only the original public key
public_keys_store = {original_key_id: original_public_key}

# Create a resolver function that only knows the original key
def resolve_public_key(key_id):
    return public_keys_store.get(key_id)

# Attacker creates their own metadata with their own key
fake_metadata = {
    "model_id": "fake-model",
    "timestamp": int(time.time()),
    "key_id": attacker_key_id  # This key_id is not in the trusted store
}

# Attacker embeds metadata with their own private key
fake_encoded_text = UnicodeMetadata.embed_metadata(
    text="This is fake content.",
    metadata=fake_metadata,
    private_key=attacker_private_key
)

# Verification will fail because the key_id is not recognized
is_valid, _ = UnicodeMetadata.verify_metadata(
    text=fake_encoded_text,
    public_key_resolver=resolve_public_key
)  # is_valid will be False
```

## Example Usage

Here's how to implement tamper detection in your application:

> **Tip:** You can use the provided helper script `encypher/examples/generate_keys.py` to generate your first key pair and get detailed setup instructions.

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import time

# Generate key pair
private_key, public_key = generate_key_pair()
key_id = "tamper-detection-example"

# Store public key
public_keys_store = {key_id: public_key}

# Create a resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)

# Original text
original_text = "Content authenticity is crucial in the age of AI-generated media."

# Create metadata with key_id
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "version": "2.0.0",
    "key_id": key_id  # Required for verification
}

# Embed metadata with digital signature
encoded_text = UnicodeMetadata.embed_metadata(
    text=original_text,
    metadata=metadata,
    private_key=private_key
)

# Verify untampered text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
if is_valid:
    print("✅ Verification successful!")
    print(f"Metadata: {verified_metadata}")
else:
    print("🚨 Tampering detected!")

# Simulating tampering by modifying text
tampered_text = encoded_text.replace("authenticity", "integrity")
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=tampered_text,
    public_key_resolver=resolve_public_key
)
if not is_valid:
    print("🚨 Tampering detected! The content has been modified.")
```

## Best Practices

To ensure effective tamper detection:

1. **Secure your private keys**:
   - Store them in environment variables or a secure vault
   - Rotate keys periodically
   - Never expose private keys in client-side code
   - Maintain a secure registry of public keys

2. **Implement additional verification**:
   - Check timestamps are recent
   - Verify model IDs match expected values
   - Validate organization fields
   - Ensure key_ids come from trusted sources

3. **Handle verification failures gracefully**:
   - Log verification failures with relevant context
   - Consider implementing rate limiting for verification attempts
   - Provide clear user feedback when tampering is detected

## Reference Implementation

For a complete demonstration of tamper detection, see the [YouTube Demo Script](../examples/youtube-demo.md) which provides an interactive example of how tampering is detected in EncypherAI.
