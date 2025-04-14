# Metadata Encoding

This guide explains how EncypherAI embeds metadata into text using Unicode variation selectors, providing a detailed overview of the encoding process, available options, and best practices.

## How Metadata Encoding Works

EncypherAI embeds metadata into text using Unicode variation selectors (VS), which are special characters designed to modify the appearance of the preceding character. These selectors are typically invisible or have minimal visual impact, making them ideal for embedding metadata without changing the visible appearance of the text.

### The Encoding Process

1. **Metadata Preparation**: The metadata (a JSON-serializable dictionary) is converted to a binary format
2. **Digital Signature Generation**: A cryptographic signature is created using Ed25519 to ensure data integrity and authenticity
3. **Target Selection**: Suitable characters in the text are identified as targets for embedding
4. **Embedding**: Variation selectors representing the metadata and digital signature are inserted after target characters

![Metadata Encoding Process](../../assets/metadata-encoding-diagram.png)

## Metadata Targets

EncypherAI provides several options for where to embed metadata in text:

| Target Type | Description | Example |
|-------------|-------------|---------|
| `whitespace` | After spaces, tabs, and newlines | "Hello world" → "Hello␣world" (VS after space) |
| `punctuation` | After punctuation marks | "Hello, world!" → "Hello,␣world!" (VS after comma) |
| `first_letter` | After the first letter of each word | "Hello world" → "H␣ello w␣orld" (VS after H and w) |
| `last_letter` | After the last letter of each word | "Hello world" → "Hello␣ world␣" (VS after o and d) |
| `all_characters` | After any character | "Hello" → "H␣e␣l␣l␣o␣" (VS after each letter) |

The default target is `whitespace`, which provides a good balance between robustness and minimal impact on the text.

## Basic Usage

```python
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import time

# Sample text
text = "This is a sample text that will have metadata embedded within it."

# Generate a key pair for digital signatures
private_key, public_key = generate_key_pair()
key_id = "example-key-1"

# Store public key (in a real application, use a secure database)
public_keys_store: Dict[str, PublicKeyTypes] = {key_id: public_key}

# Create a resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)

# Create metadata dictionary
metadata = {
    "model_id": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "2.0.0",
    "key_id": key_id  # Required for verification
}

# Embed metadata
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key,
    target=MetadataTarget.WHITESPACE  # Default target
)

print("Original text:")
print(text)
print("\nEncoded text (looks identical but contains embedded metadata):")
print(encoded_text)

# Extract metadata
extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)
print("\nExtracted metadata (unverified):")
print(extracted_metadata)

# Verify the text hasn't been tampered with
is_verified, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
print(f"\nVerification result: {'✅ Verified' if is_verified else '❌ Failed'}")
if verified_metadata:
    print("Verified metadata:", verified_metadata)
```

## Digital Signature Verification

EncypherAI uses Ed25519 digital signatures to ensure data integrity, authenticity, and detect tampering. When metadata is embedded, a digital signature is created using:

1. The metadata content (serialized as JSON)
2. A private key (Ed25519PrivateKey)

This signature is embedded alongside the metadata. When extracting metadata, the signature is verified using the corresponding public key to ensure the content hasn't been modified and comes from a trusted source.

### Key Management

```python
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
from encypher.core.keys import generate_key_pair, load_private_key, load_public_key
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import os

# Generate and save keys (do this once)
def generate_and_save_keys(private_key_path, public_key_path):
    private_key, public_key = generate_key_pair()

    # Save private key (keep this secure!)
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes_raw())

    # Save public key
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes_raw())

    return private_key, public_key

# Example paths
private_key_path = "private_key.pem"
public_key_path = "public_key.pem"

# Generate keys if they don't exist
if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
    private_key, public_key = generate_and_save_keys(private_key_path, public_key_path)
else:
    # Load existing keys
    with open(private_key_path, "rb") as f:
        private_key = load_private_key(f.read())

    with open(public_key_path, "rb") as f:
        public_key = load_public_key(f.read())

# Create a key store and resolver
key_id = "production-key-1"
public_keys_store = {key_id: public_key}

def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)

# Create metadata with key_id
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "organization": "EncypherAI",
    "version": "2.0.0",
    "key_id": key_id  # Required for verification
}

# Embed metadata
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key,
    target=MetadataTarget.WHITESPACE,
)

# Verify using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
if verified_metadata:
    print("Verified metadata:", verified_metadata)
```

### Verification Process

The verification process involves:

1. Extracting the embedded metadata and digital signature
2. Looking up the public key using the `key_id` in the metadata
3. Verifying the signature using the public key

If the signature is valid, the verification succeeds, indicating the content hasn't been tampered with and comes from a trusted source.

## Advanced Configuration

### Custom Target Selection

You can specify where to embed metadata using either a string or the `MetadataTarget` enum:

```python
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
# Assume text, metadata, and private_key are defined

# Using a string
encoded_text1 = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key,
    target="punctuation"
)

# Using the enum
encoded_text2 = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key,
    target=MetadataTarget.FIRST_LETTER
)
```

### Metadata Size Considerations

The amount of metadata you can embed depends on:

1. The length of the text
2. The number of suitable targets in the text
3. The chosen target type

Each byte of metadata requires one suitable target character. If there aren't enough targets, an error will be raised.

```python
# Check if text has enough targets for metadata
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
import json

# Estimate metadata size (in bytes)
metadata_json = json.dumps(metadata).encode('utf-8')
metadata_size = len(metadata_json)

# Find available targets
targets = UnicodeMetadata.find_targets(text, MetadataTarget.WHITESPACE)
available_targets = len(targets)

print(f"Metadata size: {metadata_size} bytes")
print(f"Available targets: {available_targets}")
print(f"Sufficient targets: {'Yes' if available_targets >= metadata_size else 'No'}")
```

## Handling Target Limitations

If you have limited targets but need to embed larger metadata:

1. **Use a more inclusive target type**: `all_characters` provides the most targets
2. **Reduce metadata size**: Include only essential information
3. **Increase text length**: Add more content to provide more targets
4. **Compress metadata**: Use shorter field names or compress values

## Comparing Target Types

Different target types offer different trade-offs between capacity and robustness:

| Target Type | Capacity | Robustness | Visual Impact | Use Case |
|-------------|----------|------------|---------------|----------|
| `whitespace` | Medium | High | Minimal | General purpose |
| `punctuation` | Low-Medium | High | Minimal | Short texts with punctuation |
| `first_letter` | Medium | Medium | Minimal | Texts with many words |
| `last_letter` | Medium | Medium | Minimal | Texts with many words |
| `all_characters` | High | Low | Minimal | Maximum capacity needed |

```python
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
from encypher.core.keys import generate_key_pair
import pandas as pd
import time

# Sample text
text = "This is a sample text that will have metadata embedded within it."

# Generate a key pair
private_key, public_key = generate_key_pair()
key_id = "target-comparison-key"

# Create metadata
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "organization": "EncypherAI",
    "version": "2.0.0",
    "key_id": key_id
}

# Test different targets
results = []
for target in [t for t in MetadataTarget if t != MetadataTarget.NONE]:
    # Count available targets
    targets = UnicodeMetadata.find_targets(text, target)

    # Try to embed metadata
    try:
        encoded = UnicodeMetadata.embed_metadata(
            text=text,
            metadata=metadata,
            private_key=private_key,
            target=target
        )
        success = True
    except ValueError:
        success = False

    results.append({
        "Target": target.value,
        "Available Targets": len(targets),
        "Embedding Successful": "Yes" if success else "No",
        "Encoded Length": len(encoded) if success else None,
        "Added Characters": len(encoded) - len(text) if success else None
    })

# Display results
pd.DataFrame(results)
```

## Tamper Detection

EncypherAI's digital signature verification can detect various types of tampering:

### Example: Detecting Modified Text

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair

# Generate a key pair
private_key, public_key = generate_key_pair()
key_id = "tamper-detection-key"

# Store public key
public_keys_store = {key_id: public_key}
def resolve_public_key(key_id):
    return public_keys_store.get(key_id)

# Create metadata with key_id
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "organization": "EncypherAI",
    "version": "2.0.0",
    "key_id": key_id
}

# Embed metadata with digital signature
encoded_text = UnicodeMetadata.embed_metadata(
    text="This is a sample text that will have metadata embedded within it.",
    metadata=metadata,
    private_key=private_key
)

# Simulate tampering by modifying the text
tampered_text = encoded_text.replace("sample", "modified")

# Try to verify the tampered text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=tampered_text,
    public_key_resolver=resolve_public_key
)
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

### Example: Detecting Removed Metadata

```python
import re
from encypher.core.unicode_metadata import UnicodeMetadata
# Assume encoded_text and resolve_public_key are from the previous example

# Simulate tampering by removing variation selectors
tampered_text_removed_vs = re.sub(r'[\uFE00-\uFE0F\U000E0100-\U000E01EF]', '', encoded_text)

# Try to extract metadata
try:
    # Verification should fail because the signature is gone
    is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
        text=tampered_text_removed_vs,
        public_key_resolver=resolve_public_key
    )
    print(f"Verification after removing VS: {'✅ Verified' if is_valid else '❌ Failed'}")

    # Extraction might still return something if parsing is lenient
    extracted = UnicodeMetadata.extract_metadata(tampered_text_removed_vs)
    print("Attempted extraction after removing VS:", extracted)
except Exception as e:  # Catch potential errors during processing badly tampered data
    print("Metadata extraction failed:", str(e))
```

## Best Practices

1. **Choose appropriate targets**: Use `whitespace` for general purposes, `all_characters` for maximum capacity
2. **Limit metadata size**: Include only necessary information to minimize embedding overhead
3. **Implement secure key management**: Store private keys securely and distribute public keys appropriately
4. **Handle extraction errors**: Implement proper error handling for cases where metadata is missing or corrupted
5. **Verify before trusting**: Always verify the digital signature before trusting extracted metadata
6. **Test with your content**: Different content types may require different target strategies

## Implementation Details

### Unicode Variation Selectors

Unicode defines two ranges of variation selectors:

1. VS1-VS16: U+FE00 to U+FE0F (16 selectors)
2. VS17-VS256: U+E0100 to U+E01EF (240 selectors)

EncypherAI uses both ranges to encode a full byte (0-255).

### Metadata Format

The embedded metadata follows this structure:

1. **Header**: Identifies the metadata format and version
2. **Metadata Length**: The size of the metadata in bytes
3. **Metadata Content**: The JSON-serialized metadata
4. **Digital Signature**: The cryptographic signature for verification

### Encoding Algorithm

1. Convert metadata to JSON
2. Calculate digital signature using the metadata and private key
3. Find suitable targets in the text
4. Convert each byte of the header, metadata, and signature to variation selectors
5. Insert variation selectors after target characters

### Decoding Algorithm

1. Scan the text for variation selectors
2. Convert variation selectors back to bytes
3. Parse the header to identify the format and version
4. Extract the metadata content and signature
5. Verify the signature using the public key corresponding to the key_id in the metadata

## Related Documentation

- [UnicodeMetadata API Reference](../api-reference/unicode-metadata.md)
- [Streaming Support Guide](./streaming.md)
- [Jupyter Notebook Examples](../examples/jupyter.md)
- [Streamlit Demo App](../examples/streamlit.md)
