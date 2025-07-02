# Metadata Encoding Formats

EncypherAI supports different formats for encoding metadata, allowing you to choose the best fit for your application's needs. The format determines the structure and content of the payload that gets digitally signed and embedded in the text.

The SDK automatically selects the appropriate format based on the parameters you provide to the `embed_metadata` or `StreamingHandler` methods. The two primary formats are the simple `basic` format and the C2PA-compliant `cbor_manifest`.

## The `basic` Format

The `basic` format is a simple, straightforward key-value structure. It is easy to use and human-readable, making it an excellent choice for getting started or for applications that don't require a standardized, extensible schema.

### Example: Using the `basic` Format

When you provide key-value data in the `custom_metadata` parameter, the SDK uses the `basic` format by default.

```python
import time
from typing import Dict, Optional, Any

from encypher import UnicodeMetadata
from encypher.keys import generate_ed25519_key_pair

# --- Key Management ---
private_key, public_key = generate_ed25519_key_pair()
signer_id = "basic-format-signer-001"
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_provider(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- Embed with 'basic' format ---
encoded_text = UnicodeMetadata.embed_metadata(
    text="This text uses the basic metadata format.",
    private_key=private_key,
    signer_id=signer_id,
    timestamp=int(time.time()),
    custom_metadata={"source": "basic-format-example"},
    omit_keys=["user_id"]  # Optionally remove sensitive fields before signing
)

# --- Verification ---
is_valid, _, payload = UnicodeMetadata.verify_metadata(
    text=encoded_text, public_key_provider=public_key_provider
)

if is_valid and payload:
    print(f"Successfully verified 'basic' payload:")
    print(f"- Timestamp: {payload.timestamp}")
    print(f"- Custom Data: {payload.custom_metadata}")
```

## The `cbor_manifest` (C2PA) Format

The `cbor_manifest` format is compliant with the [C2PA (Coalition for Content Provenance and Authenticity)](https://c2pa.org/) standard. It uses a structured manifest containing one or more **assertions**. This format is highly extensible and designed for interoperability across different systems that support C2PA.

Use this format when you need to:
- Adhere to an industry standard for content provenance.
- Represent complex relationships between different pieces of metadata.
- Ensure your metadata can be understood by other C2PA-compatible tools.

### Example: Using the `cbor_manifest` Format

When you provide a dictionary to the `c2pa_manifest` parameter, the SDK automatically uses the `cbor_manifest` format.

```python
import time
from typing import Dict, Optional, Any

from encypher import UnicodeMetadata
from encypher.keys import generate_ed25519_key_pair

# --- Key Management (same as before) ---
private_key, public_key = generate_ed25519_key_pair()
signer_id = "c2pa-format-signer-001"
public_keys_store: Dict[str, object] = {signer_id: public_key}

def public_key_provider(kid: str) -> Optional[object]:
    """A simple function to retrieve a public key by its ID."""
    return public_keys_store.get(kid)

# --- Define a C2PA-style Manifest ---
# A manifest is a dictionary containing a list of assertions.
# Each assertion is a dictionary with a 'label' and a 'data' payload.
my_c2pa_manifest = {
    "claim_generator": "EncypherAI-Example/1.0",
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org",
                "@type": "CreativeWork",
                "author": [
                    {
                        "@type": "Person",
                        "name": "Jane Doe"
                    }
                ]
            }
        },
        {
            "label": "org.encypherai.custom.training-data",
            "data": {
                "dataset_id": "d-12345",
                "snapshot_date": "2023-10-27"
            }
        }
    ]
}

# --- Embed with 'cbor_manifest' format ---
encoded_text_c2pa = UnicodeMetadata.embed_metadata(
    text="This text contains a C2PA-compliant CBOR manifest.",
    private_key=private_key,
    signer_id=signer_id,
    c2pa_manifest=my_c2pa_manifest  # Provide the manifest here
)

# --- Verification ---
is_valid_c2pa, _, payload_c2pa = UnicodeMetadata.verify_metadata(
    text=encoded_text_c2pa, public_key_provider=public_key_provider
)

if is_valid_c2pa and payload_c2pa:
    print(f"\nSuccessfully verified 'cbor_manifest' payload:")
    # For C2PA manifests, the payload object gives you direct access to the manifest data
    print(f"- Claim Generator: {payload_c2pa.claim_generator}")
    print(f"- Assertions Count: {len(payload_c2pa.assertions)}")
    print(f"- First Assertion Label: {payload_c2pa.assertions[0].label}")
```
