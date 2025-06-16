# Text Provenance Guide

## Introduction

As digital content becomes increasingly sophisticated, establishing the provenance and authenticity of text content is becoming as critical as it is for images and videos. Text provenance presents unique challenges due to the fluid nature of text, its ease of modification, and the lack of established standards specifically designed for text content.

EncypherAI's text provenance solution extends C2PA principles to text content, providing a robust framework for verifying the origin and integrity of textual information.

## The Challenge of Text Provenance

Text content faces several unique challenges when it comes to establishing provenance:

1. **Fluidity**: Text is easily modified, copied, and redistributed without visible traces
2. **Format Independence**: Text can be transferred across multiple formats (HTML, PDF, plain text)
3. **Partial Copying**: Quotes and excerpts are common and legitimate uses of text
4. **Invisible Metadata**: Traditional metadata approaches often rely on container formats

These challenges require innovative approaches that can maintain provenance information within the text itself, regardless of how it's formatted or where it appears.

## C2PA and Text Content

The Coalition for Content Provenance and Authenticity (C2PA) has established standards for tracking the origin and history of digital content, primarily focusing on images and videos. EncypherAI extends these principles to text content by:

1. Creating C2PA-compliant manifests for text
2. Embedding these manifests directly into the text using Unicode variation selectors
3. Including content hashes for tamper detection
4. Providing verification mechanisms to validate authenticity

## Our Embedding Approach

### Unicode Variation Selectors

Our approach uses Unicode variation selectors (ranges U+FE00-FE0F and U+E0100-E01EF) to embed metadata directly into text:

- These are zero-width, non-printing characters designed to specify variants of characters
- When repurposed for metadata, they become invisible carriers of binary data
- The embedded data travels with the text as part of the content itself
- The visual appearance of the text remains unchanged

### Single-Point Embedding

The default embedding strategy places all metadata after a single target character (typically the first whitespace or the first letter):

```
Original: This is example text.
Embedded: This⁠︀︁︂︃︄︅︆︇︈︉︊︋︌︍︎️ is example text.
```

The variation selectors (represented by ⁠︀︁︂︃︄︅︆︇︈︉︊︋︌︍︎️ above, though invisible in actual use) are attached to the first character, encoding the entire manifest.

### Content Hash Coverage

A critical component of our implementation is the content hash assertion:

- The hash covers the plain text content (all paragraphs concatenated)
- It does not include HTML markup or the variation selectors themselves
- SHA-256 is used as the hashing algorithm
- The hash is computed before embedding the metadata

This content hash enables tamper detection - if the text is modified after embedding, the current hash will no longer match the stored hash.

## Comparison with Other Approaches

### Hard Binding vs. Soft Binding

Our Unicode variation selector approach is classified as a **hard binding** technique:

| Approach | Description | Advantages | Disadvantages |
|----------|-------------|------------|---------------|
| **Hard Binding** (Our Approach) | Metadata embedded directly within content | - Inseparable from content<br>- Works across format conversions<br>- No external dependencies | - Limited capacity<br>- Potential processing impact |
| **Soft Binding** | Metadata stored separately with reference in content | - Unlimited metadata size<br>- No impact on content processing | - Can be separated from content<br>- Requires infrastructure |
| **Hybrid Binding** | Combination of both approaches | - Redundancy<br>- Flexibility | - Complexity<br>- Implementation overhead |

### Watermarking vs. Provenance Metadata

While both aim to establish content authenticity, they serve different purposes:

| Technique | Primary Purpose | Visibility | Content Coverage |
|-----------|----------------|------------|------------------|
| **Watermarking** | Ownership/copyright | Often visible or detectable | Typically covers entire content |
| **Provenance Metadata** | Origin verification | Invisible | Can include partial content hashes |

Our approach focuses on provenance metadata while maintaining the invisibility of watermarks.

## Best Practices for Implementation

### When to Apply Text Provenance

Text provenance is most valuable for:

- News articles and journalistic content
- Official statements and press releases
- Research papers and academic publications
- Legal documents and contracts
- AI-generated content

### Embedding Considerations

For optimal results:

1. **Embed Early**: Apply provenance at the point of content creation
2. **Target Selection**: Choose appropriate embedding targets based on content type
3. **Content Hashing**: Include all relevant content in the hash calculation
4. **Metadata Selection**: Include relevant provenance information (author, publisher, timestamp)
5. **Key Management**: Maintain secure and verifiable key infrastructure

### Verification Workflow

A robust verification process should:

1. Extract embedded metadata from the text
2. Verify the digital signature using the public key
3. Calculate the current content hash
4. Compare with the stored hash in the manifest
5. Present verification results to the user

## Example Implementation

### Basic Workflow

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest
import hashlib
from datetime import datetime

# 1. Generate keys (or load existing keys)
private_key, public_key = generate_ed25519_key_pair()
signer_id = "publisher-key-001"

# 2. Prepare article text
article_text = """This is the full article text.
It contains multiple paragraphs.
All of this text will be hashed for the content hash assertion."""

# 3. Calculate content hash
content_hash = hashlib.sha256(article_text.encode('utf-8')).hexdigest()

# 4. Create C2PA manifest
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
                "datePublished": "2025-06-15"
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

# 5. Convert to EncypherAI format
encypher_manifest = c2pa_like_dict_to_encypher_manifest(c2pa_manifest)

# 6. Extract first paragraph for embedding
first_paragraph = article_text.split('\n')[0]

# 7. Embed into first paragraph
embedded_paragraph = UnicodeMetadata.embed_metadata(
    text=first_paragraph,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format='cbor_manifest',
    claim_generator=encypher_manifest.get("claim_generator"),
    actions=encypher_manifest.get("assertions"),
    timestamp=encypher_manifest.get("timestamp")
)

# 8. Replace first paragraph in article
embedded_article = article_text.replace(first_paragraph, embedded_paragraph)
```

### Verification Example

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
    public_key_provider=key_provider
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

## Future Directions

As text provenance technology evolves, several promising directions are emerging:

1. **Standardization**: Working with C2PA to establish formal standards for text content
2. **Partial Content Verification**: Enabling verification of excerpts and quotes
3. **Cross-Format Persistence**: Ensuring provenance survives format conversions
4. **Integration with Publishing Platforms**: Automatic embedding in content management systems
5. **User-Friendly Verification**: Simplified tools for readers to verify content

EncypherAI is actively contributing to these developments, pushing the boundaries of what's possible in text provenance while maintaining compatibility with emerging standards.
