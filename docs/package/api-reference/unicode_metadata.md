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
    metadata_format: Literal["basic", "manifest", "cbor_manifest"] = "basic",
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
- `text`: The text to embed metadata into
- `private_key`: The Ed25519 private key object for signing
- `signer_id`: A string identifying the signer/key pair
- `metadata_format`: Format for the metadata payload ('basic', 'manifest', or 'cbor_manifest')
- `model_id`: Model identifier (used in 'basic' and optionally in 'manifest' ai_info)
- `timestamp`: Timestamp (datetime, ISO string, int/float epoch)
- `target`: Where to embed metadata ('whitespace', 'punctuation', etc.)
- `custom_metadata`: Dictionary for custom fields (used in 'basic' payload)
- `claim_generator`: Claim generator string (used in 'manifest' format)
- `actions`: List of action dictionaries (used in 'manifest' format)
- `ai_info`: Dictionary with AI-specific info (used in 'manifest' format)
- `custom_claims`: Dictionary for custom C2PA-like claims (used in 'manifest' format)
- `distribute_across_targets`: If True, distribute bits across multiple targets

**Returns:**
- The text with embedded metadata and digital signature

### `UnicodeMetadata.verify_and_extract_metadata`

```python
@classmethod
def verify_and_extract_metadata(
    cls,
    text: str,
    public_key_provider: Callable[[str], Optional[PublicKeyTypes]],
    return_payload_on_failure: bool = False,
) -> Tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, None]]:
```

Extracts embedded metadata, verifies its signature using a public key, and returns the payload, verification status, and signer ID.

**Parameters:**
- `text`: Text potentially containing embedded metadata
- `public_key_provider`: A callable function that takes a signer_id and returns the corresponding public key
- `return_payload_on_failure`: If True, return the payload even when verification fails

**Returns:**
- A tuple containing:
  - Verification status (bool): True if the signature is valid
  - The signer_id (str) found in the metadata, or None if extraction fails
  - The extracted inner payload or None if extraction/verification fails

### `UnicodeMetadata.extract_metadata`

```python
@classmethod
def extract_metadata(cls, text: str) -> Optional[Dict[str, Any]]:
```

Extracts embedded metadata from text without verifying its signature.

**Parameters:**
- `text`: The text containing potentially embedded metadata

**Returns:**
- The extracted inner metadata dictionary if found, otherwise None

## Example Usage

### Basic Embedding

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
from datetime import datetime

# Generate keys
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-001"

# Embed metadata
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

# Define a key provider function
def key_provider(kid):
    if kid == signer_id:
        return public_key
    return None

# Verify and extract metadata
is_verified, extracted_signer_id, payload = UnicodeMetadata.verify_and_extract_metadata(
    text=embedded_text,
    public_key_provider=key_provider
)

print(f"Verification: {is_verified}")
print(f"Signer ID: {extracted_signer_id}")
print(f"Payload: {payload}")
```

### C2PA Manifest Embedding

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest
import hashlib

# Generate content hash
content = "This is the full content that will be hashed."
content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

# Create C2PA manifest
c2pa_manifest = {
    "claim_generator": "EncypherAI/2.3.0",
    "timestamp": "2025-06-16T15:00:00Z",
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org/",
                "@type": "CreativeWork",
                "headline": "Example Article",
                "author": {"@type": "Person", "name": "John Doe"}
            }
        },
        {
            "label": "stds.c2pa.content.hash",
            "data": {
                "hash": content_hash,
                "alg": "sha256"
            },
            "kind": "ContentHash"
        }
    ]
}

# Convert to EncypherAI format
encypher_manifest = c2pa_like_dict_to_encypher_manifest(c2pa_manifest)

# Embed into text (first paragraph)
first_paragraph = "This is the first paragraph of the article."
embedded_paragraph = UnicodeMetadata.embed_metadata(
    text=first_paragraph,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format='cbor_manifest',
    claim_generator=encypher_manifest.get("claim_generator"),
    actions=encypher_manifest.get("assertions"),
    ai_info=encypher_manifest.get("ai_assertion", {}),
    custom_claims=encypher_manifest.get("custom_claims", {}),
    timestamp=encypher_manifest.get("timestamp")
)
```

## Hard Binding vs. Soft Binding

Our Unicode variation selector approach is classified as a **hard binding** technique because:

1. The metadata is embedded directly within the content itself
2. The metadata travels with the content as part of the same file/text
3. The binding is inseparable from the content

This differs from **soft binding** approaches where:
- The manifest exists separately from the content
- Only a reference or link to the manifest is included with the content

Hard binding provides stronger provenance guarantees as the metadata cannot be separated from the content, but may have limitations in terms of capacity and processing impact.
