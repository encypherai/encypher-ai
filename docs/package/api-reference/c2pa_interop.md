# C2PA Interoperability Module

The `c2pa` module provides utilities for interoperability between EncypherAI's metadata formats and the C2PA (Coalition for Content Provenance and Authenticity) standard. This enables text content to benefit from the same provenance and verification capabilities that C2PA provides for images and videos.

## Overview

C2PA is an open technical standard for providing provenance and verifiability for digital content. While C2PA was initially designed for media files like images and videos, EncypherAI extends these principles to text content through our Unicode variation selector embedding technique.

Our implementation:
- Creates C2PA-compliant manifests for text content
- Embeds these manifests directly into the text using Unicode variation selectors
- Provides verification and tamper detection capabilities
- Maintains compatibility with C2PA concepts and structures

## Hard Binding Implementation

Our approach to C2PA for text is classified as a **hard binding** technique:

- The manifest is embedded directly within the text content itself
- The embedding uses invisible Unicode variation selectors
- The binding is inseparable from the content

This differs from soft binding approaches where the manifest exists separately from the content with only a reference included in the content.

## Content Hash Coverage

A critical component of our C2PA implementation is the content hash assertion:

- The hash covers the plain text content only (not HTML markup or other formatting)
- SHA-256 is used as the hashing algorithm
- The hash is computed before embedding the metadata
- This creates a cryptographic fingerprint of the original content

This content hash enables tamper detection - if the text is modified after embedding, the current hash will no longer match the stored hash.

## API Reference

### `c2pa_like_dict_to_encypher_manifest`

```python
def c2pa_like_dict_to_encypher_manifest(
    c2pa_like_dict: Dict[str, Any]
) -> Dict[str, Any]:
```

Converts a C2PA-like dictionary to EncypherAI's internal manifest format for embedding.

**Parameters:**
- `c2pa_like_dict`: A dictionary following the C2PA manifest structure

**Returns:**
- A dictionary in EncypherAI's internal manifest format ready for embedding

### `encypher_manifest_to_c2pa_like_dict`

```python
def encypher_manifest_to_c2pa_like_dict(
    encypher_manifest: Dict[str, Any]
) -> Dict[str, Any]:
```

Converts an EncypherAI internal manifest back to a C2PA-like dictionary structure.

**Parameters:**
- `encypher_manifest`: A dictionary in EncypherAI's internal manifest format

**Returns:**
- A dictionary following the C2PA manifest structure

## C2PA Manifest Structure

A C2PA-like manifest for text content typically includes:

```json
{
  "claim_generator": "EncypherAI/2.3.0",
  "timestamp": "2025-06-16T15:00:00Z",
  "assertions": [
    {
      "label": "stds.schema-org.CreativeWork",
      "data": {
        "@context": "https://schema.org/",
        "@type": "CreativeWork",
        "headline": "Article Title",
        "author": {"@type": "Person", "name": "Author Name"},
        "publisher": {"@type": "Organization", "name": "Publisher Name"},
        "datePublished": "2025-06-15",
        "description": "Article description"
      }
    },
    {
      "label": "stds.c2pa.content.hash",
      "data": {
        "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "alg": "sha256"
      },
      "kind": "ContentHash"
    }
  ]
}
```

## Example Usage

### Creating and Embedding a C2PA Manifest

```python
import hashlib
from datetime import datetime
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest

# Generate keys
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-001"

# Article text
article_text = """This is the full article text.
It contains multiple paragraphs.
All of this text will be hashed for the content hash assertion."""

# Calculate content hash
content_hash = hashlib.sha256(article_text.encode('utf-8')).hexdigest()

# Create C2PA manifest
c2pa_manifest = {
    "claim_generator": "EncypherAI/2.3.0",
    "timestamp": datetime.now().isoformat(),
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org/",
                "@type": "CreativeWork",
                "headline": "Example Article",
                "author": {"@type": "Person", "name": "John Doe"},
                "publisher": {"@type": "Organization", "name": "Example Publisher"},
                "datePublished": "2025-06-15",
                "description": "An example article for C2PA demonstration"
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

# Extract first paragraph for embedding
first_paragraph = article_text.split('\n')[0]

# Embed into first paragraph
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

# Replace first paragraph in article
embedded_article = article_text.replace(first_paragraph, embedded_paragraph)
```

### Verifying and Extracting a C2PA Manifest

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import encypher_manifest_to_c2pa_like_dict
import hashlib

# Define key provider function
def key_provider(kid):
    if kid == signer_id:
        return public_key
    return None

# Extract first paragraph (which contains the embedded metadata)
first_paragraph = embedded_article.split('\n')[0]

# Verify and extract metadata
is_verified, extracted_signer_id, extracted_manifest = UnicodeMetadata.verify_and_extract_metadata(
    text=first_paragraph,
    public_key_provider=key_provider,
    return_payload_on_failure=True
)

if is_verified:
    # Convert back to C2PA format
    c2pa_extracted = encypher_manifest_to_c2pa_like_dict(extracted_manifest)
    
    # Verify content hash
    current_content_hash = hashlib.sha256(article_text.encode('utf-8')).hexdigest()
    
    # Find content hash assertion
    stored_hash = None
    for assertion in c2pa_extracted.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break
    
    if stored_hash == current_content_hash:
        print("Content hash verification successful!")
    else:
        print("Content hash verification failed - content may have been tampered with.")
else:
    print("Signature verification failed!")
```

## Tamper Detection

Our C2PA implementation enables two types of tamper detection:

1. **Content Tampering**: If the text content is modified after embedding, the current hash will no longer match the stored hash in the manifest.

2. **Metadata Tampering**: If the embedded manifest itself is modified, the digital signature verification will fail.

These mechanisms ensure the integrity and authenticity of both the content and its provenance information.
