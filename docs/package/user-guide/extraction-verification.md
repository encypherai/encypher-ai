# Extraction and Verification

Verifying embedded metadata is a critical step to ensure the authenticity and integrity of text content. The EncypherAI SDK provides a robust verification process that handles both legacy formats and the latest C2PA v2.2 standard.

## The Verification Workflow

The primary method for verification is `UnicodeMetadata.verify_metadata()`. This method performs a series of checks to validate the embedded data:

1.  **Extraction**: It first extracts the raw byte sequence from the Unicode variation selectors in the text.
2.  **Format Detection**: It automatically detects the payload format (legacy `basic`/`manifest` or `c2pa_v2_2`).
3.  **Signature Validation**: It verifies the cryptographic signature using the key provided by the `public_key_provider`.
4.  **Deep Manifest Validation (for C2PA v2.2)**: If a C2PA v2.2 manifest is detected, it performs additional, deeper validation:
    *   **COSE Signature**: Verifies the COSE_Sign1 structure.
    *   **Certificate Chain**: If a certificate chain is present, it validates it against the provided `trust_anchors`.
    *   **Soft Binding**: It re-calculates the hash of the manifest to ensure the manifest itself hasn't been altered post-signing.
    *   **Hard Binding**: It re-calculates the hash of the clean text content to ensure the underlying text has not been tampered with.

## `verify_metadata` vs. `extract_metadata`

It's important to choose the right method for your needs:

-   **`UnicodeMetadata.verify_metadata()`**: Use this when you need to confirm authenticity. It performs a full cryptographic verification and returns a boolean status, the signer's ID, and the verified payload. This is the recommended method for most use cases.
-   **`UnicodeMetadata.extract_metadata()`**: Use this only when you need to retrieve the raw, unverified metadata payload. It performs no signature or integrity checks. This might be useful for debugging or in specific scenarios where verification is handled separately.

## The Public Key Provider

The `verify_metadata` method requires a `public_key_provider`. This is a callable function that you provide, which is responsible for supplying the correct public key for a given `signer_id`.

This design gives you full control over key management. You can fetch keys from a database, a local file, or a secure key management service.

### Example Provider

```python
from typing import Dict, Optional
from encypher.core.keys import generate_ed25519_key_pair

# 1. Generate a key pair and store the public key
private_key, public_key = generate_ed25519_key_pair()
signer_id = "user-001-key"

public_key_store = {signer_id: public_key}

# 2. Create the public key provider function
def public_key_provider(key_id: str):
    """A simple function to retrieve a public key from our store."""
    return public_key_store.get(key_id)

# 3. Use the provider during verification
# is_valid, _, payload = UnicodeMetadata.verify_metadata(
#     text=encoded_text,
#     public_key_provider=public_key_provider
# )
```

## Verifying a C2PA v2.2 Manifest

When verifying a C2PA v2.2 manifest that was signed with a certificate, you must provide a list of trusted root CA certificates (`trust_anchors`). The `public_key_provider` in this case should return the certificate in bytes.

```python
# Assume 'encoded_text' contains a C2PA v2.2 manifest
# and 'public_key_provider' is defined to return certificates.

# Load your trusted root certificates (as bytes)
with open("trusted_root_ca.pem", "rb") as f:
    trusted_cert = f.read()

trust_anchors = [trusted_cert]

# Verify the manifest
is_verified, signer_id, payload = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_provider=public_key_provider,
    trust_anchors=trust_anchors
)

if is_verified:
    print(f"Successfully verified content signed by {signer_id}.")
    # You can now inspect the payload, which will be a C2PAPayload object
    print(f"Claim Generator: {payload.claim_generator}")
else:
    print("Verification failed. The content may have been tampered with.")
```

This setup ensures that not only is the signature valid, but the certificate used for signing is also trusted within your ecosystem.
