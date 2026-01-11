# Metadata Encoding Formats

Encypher supports different formats for encoding metadata, allowing you to choose the best fit for your application's needs. The format determines the structure and content of the payload that gets digitally signed and embedded in the text.

The SDK selects the appropriate format based on the parameters you provide to the `embed_metadata` or `StreamingHandler` methods. The two primary formats are the simple `basic` format and the C2PA-compliant `c2pa` format. Legacy formats (including `manifest` and `cbor_manifest`) remain available for backward compatibility.

> Note: The `timestamp` parameter is optional across all formats (basic, manifest, cbor_manifest, c2pa). If omitted, verification still works. For C2PA, action assertions (e.g., `c2pa.created`, `c2pa.watermarked`) omit the `when` field when no timestamp is supplied.

## The `basic` Format

The `basic` format is a simple, straightforward key-value structure. It is easy to use and human-readable, making it an excellent choice for getting started or for applications that don't require a standardized, extensible schema.

### Example: Using the `basic` Format

When you provide key-value data in the `custom_metadata` parameter, the SDK uses the `basic` format by default.

```python
import time
from typing import Dict, Optional, Any

from encypher import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair

# --- Key Management ---
private_key, public_key = generate_ed25519_key_pair()
signer_id = "basic-format-signer-001"
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_resolver(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- Embed with 'basic' format ---
encoded_text = UnicodeMetadata.embed_metadata(
    text="This text uses the basic metadata format.",
    private_key=private_key,
    signer_id=signer_id,
    custom_metadata={"source": "basic-format-example"},
    omit_keys=["user_id"]  # Optionally remove sensitive fields before signing
)

# --- Verification ---
is_valid, _, payload = UnicodeMetadata.verify_metadata(
    text=encoded_text, public_key_resolver=public_key_resolver
)

if is_valid and payload:
    print(f"Successfully verified 'basic' payload:")
    print(f"- Timestamp present: {bool(getattr(payload, 'timestamp', None))}")
    print(f"- Custom Data: {payload.custom_metadata}")
```

## The `c2pa` (C2PA) Format

The `c2pa` format is compliant with the [C2PA (Coalition for Content Provenance and Authenticity)](https://c2pa.org/) standard and follows the published C2PA v2.3 rules for embedding manifests into unstructured text.

Use this format when you need to:
- Adhere to an industry standard for content provenance.
- Represent complex relationships between different pieces of metadata.
- Ensure your metadata can be understood by other C2PA-compatible tools.

### Example: Using the `c2pa` Format

When you set `metadata_format="c2pa"`, the SDK builds a standards-aligned C2PA manifest, signs it as COSE `Sign1`, and appends it as a FEFF-prefixed `C2PATextManifestWrapper` at the end of the text.

```python
from datetime import datetime
from typing import Dict, Optional

from encypher import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair

# --- Key Management (same as before) ---
private_key, public_key = generate_ed25519_key_pair()
signer_id = "c2pa-format-signer-001"
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_resolver(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- Embed with 'c2pa' format ---
encoded_text_c2pa = UnicodeMetadata.embed_metadata(
    text="This text contains a C2PA-compliant manifest.",
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    claim_generator="Encypher-Example/1.0",
    actions=[{"label": "c2pa.created", "when": datetime.now().isoformat()}],
)

# --- Verification ---
is_valid_c2pa, _, payload_c2pa = UnicodeMetadata.verify_metadata(
    text=encoded_text_c2pa, public_key_resolver=public_key_resolver
)

if is_valid_c2pa and payload_c2pa:
    print(f"\nSuccessfully verified 'c2pa' payload:")
    print(f"- Claim Generator: {payload_c2pa.get('claim_generator')}")
    print(f"- Assertions Count: {len(payload_c2pa.get('assertions', []))}")
```
