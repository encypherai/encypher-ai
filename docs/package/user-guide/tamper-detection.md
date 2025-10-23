# Tamper Detection

A core feature of EncypherAI is its ability to detect when a piece of text has been modified after its metadata was embedded. This is achieved through cryptographic signatures and content hashing, providing a robust guarantee of authenticity and integrity.

## How It Works: The Digital Signature

When you embed metadata, EncypherAI performs several key steps:

1.  **Payload Creation**: It assembles the metadata you provide (e.g., timestamp, custom data, or a C2PA manifest) into a structured payload.
2.  **Content Hashing (Hard Binding)**: It calculates a cryptographic hash (SHA-256) of the original, unmodified text. This hash is added to the metadata payload. This is the **hard binding**—it directly links the payload to the specific text content.
3.  **Signing**: The entire payload, including the content hash, is then digitally signed using your private key.
4.  **Embedding**: The signature and the payload are encoded into invisible Unicode characters and embedded into the text.

When you later call `UnicodeMetadata.verify_metadata()`, the process is reversed:

1.  **Extraction**: The metadata payload and signature are extracted from the text.
2.  **Re-Hashing**: The verifier calculates a new SHA-256 hash of the text as it currently exists.
3.  **Comparison**: It compares the newly calculated hash with the hash stored inside the extracted payload. **If they do not match, verification fails immediately.**
4.  **Signature Verification**: If the hashes match, the verifier uses the public key to check if the digital signature is valid for the extracted payload. If the signature is invalid, verification fails.

A successful verification is a guarantee that the text has not been altered in any way since it was signed.

## Tamper Detection Example

This example shows how verification succeeds for original content and fails for tampered content.

```python
import time
from typing import Dict, Optional

from encypher import UnicodeMetadata
from encypher.keys import generate_ed25519_key_pair

# --- 1. Setup ---
# Generate keys and define a public key provider.
private_key, public_key = generate_ed25519_key_pair()
signer_id = "tamper-demo-signer-001"
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_provider(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- 2. Embed Metadata in Original Text ---
original_text = "This is the original, authentic content."

encoded_text = UnicodeMetadata.embed_metadata(
    text=original_text,
    private_key=private_key,
    signer_id=signer_id,
    timestamp=int(time.time()),
    custom_metadata={"source": "tamper-detection-guide"}
)

# --- 3. Verify the Original Text (Success) ---
# Verification on the untouched text should always pass.
is_valid_original, _, _ = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_provider=public_key_provider
)

print(f"Verification of original text: {'✅ Passed' if is_valid_original else '🚨 Failed'}")

# --- 4. Tamper with the Text and Verify Again (Failure) ---
# An attacker modifies the text slightly. Even changing a single character will be detected.
tampered_text = encoded_text.replace("authentic", "tampered")

print(f"\nOriginal text: '{original_text}'")
print(f"Tampered text: '{tampered_text.strip()}'")

# Verification on the tampered text will fail because the content hash no longer matches.
is_valid_tampered, _, _ = UnicodeMetadata.verify_metadata(
    text=tampered_text,
    public_key_provider=public_key_provider
)

print(f"Verification of tampered text: {'✅ Passed' if is_valid_tampered else '🚨 Failed'}")
```

### C2PA and Tamper Detection

This mechanism is fundamental to C2PA compliance. When you use the `cbor_manifest` format, the content hash is stored in a standardized `c2pa.hash.data` assertion, making the tamper-detection mechanism interoperable with other C2PA-compliant tools.
