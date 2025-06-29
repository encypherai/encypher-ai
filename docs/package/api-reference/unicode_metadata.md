# Unicode Metadata Module

The `UnicodeMetadata` module provides utilities for embedding and extracting metadata in text using Unicode variation selectors. This approach enables C2PA-compliant provenance information to be embedded directly within text content while maintaining visual integrity.

## Overview

The Unicode variation selector embedding technique is a form of hard binding that embeds metadata directly into text content. This approach:

- Uses zero-width, non-printing characters (Unicode variation selectors)
- Preserves the visual appearance of the text
- Enables robust verification and tamper detection
- Follows C2PA principles for content provenance

## Embedding Mechanism

### Unicode Variation Selectors

Unicode variation selectors (ranges U+FE00-FE0F and U+E0100-E01EF) are special characters designed to specify a specific variant of a preceding character without changing its appearance. Our implementation repurposes these selectors to encode binary data:

- Each byte of metadata is encoded as a Unicode variation selector
- These selectors are invisible when rendered in text
- The encoded data travels with the content as part of the text itself

### Embedding Targets

The module supports several embedding targets:

| Target | Description | Use Case |
|--------|-------------|----------|
| `WHITESPACE` | Embeds after whitespace characters | Default; works well for most text |
| `PUNCTUATION` | Embeds after punctuation marks | Alternative for texts with limited whitespace |
| `FIRST_LETTER` | Embeds after the first letter of words | Higher capacity but may affect some text processing |
| `LAST_LETTER` | Embeds after the last letter of words | Alternative to FIRST_LETTER |
| `ALL_CHARACTERS` | Embeds after any character | Highest capacity but most intrusive |

### Embedding Approaches

The module supports two embedding approaches:

1. **Single-Point Embedding** (default): All metadata is embedded after a single target character (typically the first whitespace)
2. **Distributed Embedding**: Metadata is distributed across multiple target characters throughout the text

Single-point embedding is generally recommended as it minimizes the impact on text processing and is easier to manage.

## Content Hash Coverage

When using the C2PA manifest format, a content hash assertion is included in the manifest:

- The hash covers the plain text content only (not HTML markup or other formatting)
- SHA-256 is used as the hashing algorithm
- The hash is computed before embedding the metadata
- This creates a cryptographic fingerprint of the original content

This content hash enables tamper detection - if the text is modified after embedding, the current hash will no longer match the stored hash.

## API Reference

### `UnicodeMetadata.embed_metadata`

```python
@classmethod
def embed_metadata(
    cls,
    text: str,
    private_key: PrivateKeyTypes,
    signer_id: str,
    metadata_format: Literal["basic", "manifest", "cbor_manifest", "c2pa_v2_2"] = "basic",
    c2pa_manifest: Optional[Dict[str, Any]] = None,
    model_id: Optional[str] = None,
    timestamp: Optional[Union[str, datetime, date, int, float]] = None,
    target: Optional[Union[str, MetadataTarget]] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    claim_generator: Optional[str] = None,
    actions: Optional[List[Dict[str, Any]]] = None,
    ai_info: Optional[Dict[str, Any]] = None,
    custom_claims: Optional[Dict[str, Any]] = None,
    distribute_across_targets: bool = False,
) -> str:
```

Embeds metadata into text using Unicode variation selectors, signing with a private key.

**Parameters:**
- `text`: The text to embed metadata into.
- `private_key`: The Ed25519 private key object for signing.
- `signer_id`: A string identifying the signer/key pair.
- `metadata_format`: Format for the metadata payload.
  - `basic`: A simple key-value payload.
  - `manifest`: A legacy C2PA-like manifest.
  - `cbor_manifest`: A CBOR-encoded version of the legacy manifest.
  - `c2pa_v2_2`: The latest C2PA-compliant format using COSE Sign1.
- `c2pa_manifest`: A dictionary representing the full C2PA v2.2 manifest. Required when `metadata_format` is `c2pa_v2_2`.
- `model_id`: Model identifier (used in 'basic' payload).
- `timestamp`: Timestamp (datetime, ISO string, int/float epoch).
- `target`: Where to embed metadata ('whitespace', 'punctuation', etc.).
- `custom_metadata`: Dictionary for custom fields (used in 'basic' payload).
- `claim_generator`, `actions`, `ai_info`, `custom_claims`: Used for legacy 'manifest' formats.
- `distribute_across_targets`: If True, distribute bits across multiple targets.

**Returns:**
- The text with embedded metadata and digital signature.

### `UnicodeMetadata.verify_metadata`

```python
@classmethod
def verify_metadata(
    cls,
    text: str,
    public_key_resolver: Callable[[str], Optional[Union[PublicKeyTypes, bytes]]],
    trust_anchors: Optional[List[bytes]] = None,
    allow_fallback_extraction: bool = True,
) -> Tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, C2PAPayload, None]]:
```

Extracts embedded metadata, verifies its signature, and returns the payload. This method automatically detects the metadata format (legacy vs. C2PA v2.2).

For C2PA v2.2 manifests, it performs full cryptographic verification, including:
- COSE signature validation.
- Soft-binding hash comparison.
- Hard-binding (content hash) comparison.
- X.509 certificate chain validation against provided `trust_anchors`.

**Parameters:**
- `text`: Text potentially containing embedded metadata.
- `public_key_resolver`: A callable that takes a `signer_id` and returns the corresponding public key (as a `PublicKeyTypes` object) or a certificate (as `bytes`).
- `trust_anchors`: A list of trusted root CA certificates (in PEM format as bytes) for validating certificate chains in C2PA v2.2 manifests.
- `allow_fallback_extraction`: If True, attempts to extract data from the end of the string if standard extraction fails.

**Returns:**
A tuple of `(is_verified, signer_id, payload)`:
- `is_verified` (`bool`): `True` if the signature and all binding checks (content hash, manifest hash) are valid.
- `signer_id` (`Optional[str]`): The identifier of the key used for signing.
- `payload` (`Union[BasicPayload, ManifestPayload, C2PAPayload, None]`): The extracted and verified inner payload, or `None` on failure.

### `UnicodeMetadata.extract_metadata`

```python
@classmethod
def extract_metadata(cls, text: str) -> Optional[Dict[str, Any]]:
```

Extracts embedded metadata from text without verifying its signature.

**Parameters:**
- `text`: The text containing potentially embedded metadata.

**Returns:**
- The extracted outer payload dictionary if found, otherwise `None`. Note: For C2PA v2.2, this will be a COSE structure.

## Example Usage

### Basic Embedding and Verification

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
from datetime import datetime

# 1. Generate keys
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-001"

# 2. Embed metadata
text = "This is a sample text for embedding metadata."
embedded_text = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="basic",
    model_id="example-model",
    timestamp=datetime.now(),
    target="whitespace"
)

# 3. Define a key resolver
def key_resolver(kid):
    if kid == signer_id:
        return public_key
    return None

# 4. Verify and extract metadata
is_verified, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(
    text=embedded_text,
    public_key_resolver=key_resolver
)

print(f"Verification: {is_verified}")
print(f"Signer ID: {extracted_signer_id}")
print(f"Payload: {payload}")
```

### C2PA v2.2 Manifest Embedding

This example demonstrates embedding a full C2PA v2.2 manifest.

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
import hashlib

# 1. Generate keys
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-c2pa-key-001"

# 2. Define the text content and create its hash
clean_text = "This is the article content that we want to protect."
clean_text_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

# 3. Create the C2PA manifest
c2pa_manifest = {
    "claim_generator": "EncypherAI/2.3.0",
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org/",
                "@type": "CreativeWork",
                "headline": "Example Article",
                "author": {"@type": "Person", "name": "Jane Doe"}
            }
        },
        {
            "label": "c2pa.hash.data.v1",
            "data": {
                "hash": clean_text_hash,
                "alg": "sha256"
            },
            "kind": "ContentHash"
        }
    ]
}

# 4. Embed the manifest into the text
embedded_text = UnicodeMetadata.embed_metadata(
    text=clean_text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format='c2pa_v2_2',
    c2pa_manifest=c2pa_manifest,
)

# 5. Verify the embedded manifest
is_verified, _, payload = UnicodeMetadata.verify_metadata(
    text=embedded_text,
    public_key_resolver=lambda kid: public_key if kid == signer_id else None
)

print(f"C2PA Verification: {is_verified}")
```
```

## C2PA Binding Mechanisms

The EncypherAI SDK leverages C2PA's multi-layered approach to ensure content integrity and authenticity. This involves two primary types of cryptographic bindings within the manifest itself, which is then embedded in the text using our Unicode variation selector technique.

### Hard Binding (Content Integrity)

A **hard binding** creates a direct, unbreakable link between the C2PA manifest and the content it describes.

- **How it works**: We calculate a SHA-256 hash of the clean, original text content.
- **Assertion**: This hash is stored in a `c2pa.hash.data.v1` assertion within the manifest.
- **Purpose**: This proves that the visible text content has not been altered since the manifest was created. Any modification to the text will cause the hash check to fail during verification.

### Soft Binding (Manifest Integrity)

A **soft binding** protects the integrity of the manifest itself, ensuring that the claims within it have not been tampered with.

- **How it works**: We calculate a hash of the manifest's assertions *before* the final COSE signature is applied.
- **Assertion**: This hash is stored in a `c2pa.soft_binding.v1` assertion.
- **Purpose**: This prevents an attacker from modifying, adding, or removing assertions in the manifest without invalidating the soft binding. For example, it prevents someone from changing the author's name or the creation date.

The `verify_metadata` method automatically validates both the hard and soft bindings, providing robust, two-layered tamper detection.
