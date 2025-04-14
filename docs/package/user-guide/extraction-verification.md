# Metadata Extraction and Verification

This guide explains how to extract embedded metadata from text and verify its authenticity using EncypherAI's digital signature verification system.

## Basic Extraction

Extracting metadata from text that has been encoded with EncypherAI is straightforward:

```python
from encypher.core.unicode_metadata import UnicodeMetadata

# Text with embedded metadata
encoded_text = "This text contains embedded metadata that is invisible to human readers."

# Extract the metadata
try:
    metadata = UnicodeMetadata.extract_metadata(encoded_text)
    if metadata:
        print("Extracted metadata (unverified):", metadata)
    else:
        print("No metadata found or extraction failed")
except Exception as e:
    print("No metadata found or extraction failed:", str(e))
```

The `extract_metadata` method scans the text for metadata markers (zero-width characters), extracts the embedded data, decompresses it, and returns the metadata as a Python dictionary. This method does not verify the digital signature of the metadata.

## Understanding the Extraction Process

When extracting metadata, EncypherAI's `UnicodeMetadata` performs the following steps:

1. **Locates Data Block**: Identifies a special sequence of zero-width characters at the beginning of the text that marks the start of the embedded data.
2. **Extracts Content**: Reads the bytes encoded as variation selectors between the start and end markers.
3. **Decodes Base64**: Decodes the extracted bytes from Base64.
4. **Decompresses**: Decompresses the decoded data using zlib.
5. **Deserializes JSON**: Converts the decompressed data into a Python dictionary.

![Metadata Extraction Process](../../assets/metadata-extraction-diagram.png)

## Digital Signature Verification

EncypherAI uses Ed25519 digital signatures to ensure data integrity, authenticity, and detect tampering. The verification process requires a public key resolver function that can look up the public key corresponding to the `key_id` in the metadata:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional

# Define a public key resolver function
# In a real application, this would look up keys from a secure database
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # Example: Return the public key for the given key_id
    # This is just a placeholder - implement your actual key lookup logic
    return public_keys_store.get(key_id)

# Text with embedded metadata
encoded_text = "This text contains embedded metadata that is invisible to human readers."

# Verify the text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")

# Use metadata only if verification succeeds
if is_valid:
    print("Verified metadata:", verified_metadata)
else:
    print("Verification failed, metadata may be compromised")
```

## Key Management

For digital signature verification to work, you need to manage your key pairs properly:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict

# Generate a key pair
private_key, public_key = generate_key_pair()
key_id = "example-key-1"

# Store public keys (in a real application, use a secure database)
public_keys_store: Dict[str, PublicKeyTypes] = {key_id: public_key}

# Create a resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)

# When embedding metadata, include the key_id
metadata = {
    "model": "gpt-4",
    "timestamp": int(time.time()),
    "key_id": key_id,  # Required for verification
    "custom_field": "example value"
}

# Embed metadata with digital signature
encoded_text = UnicodeMetadata.embed_metadata(
    text="Original text",
    metadata=metadata,
    private_key=private_key
)

# Later, verify using the resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
```

The `key_id` in the metadata is used to look up the corresponding public key through the resolver function. If the key cannot be found or is incorrect, verification will fail.

## Extraction Without Verification

In some cases, you might want to extract metadata without verifying the signature:

```python
from encypher.core.unicode_metadata import UnicodeMetadata

# Extract metadata without verification
try:
    metadata = UnicodeMetadata.extract_metadata(encoded_text)
    if metadata:
        print("Extracted metadata (unverified):", metadata)
        print("⚠️ Note: This metadata has not been verified!")
    else:
        print("No metadata found")
except Exception as e:
    print("No metadata found or extraction failed:", str(e))
```

This approach is useful for debugging or when you don't need to verify the authenticity of the metadata.

## Understanding Verification Failures

Verification can fail for several reasons:

1. **Content Modification**: The text has been modified after metadata was embedded
2. **Missing or Invalid Public Key**: The public key corresponding to the key_id cannot be found
3. **Invalid Signature**: The signature doesn't match the content (tampering detected)
4. **Missing key_id**: The metadata doesn't contain a key_id field
5. **Resolver Function Error**: The public key resolver function fails or returns an invalid key
6. **Data Block Alteration**: The block containing metadata and signature has been altered or removed

### Example: Detecting Modified Text

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair

# Generate a key pair
private_key, public_key = generate_key_pair()
key_id = "tamper-detection-key"

# Store public key
public_keys_store = {key_id: public_key}

# Create a resolver function
def resolve_public_key(key_id):
    return public_keys_store.get(key_id)

# Create metadata with key_id
metadata = {
    "model": "gpt-4",
    "timestamp": int(time.time()),
    "key_id": key_id
}

# Embed metadata with digital signature
original_encoded_text = UnicodeMetadata.embed_metadata(
    text="This text contains embedded metadata.",
    metadata=metadata,
    private_key=private_key
)

# Simulate tampering by modifying the text
tampered_text = original_encoded_text.replace("contains", "has")

# Try to verify the tampered text
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=tampered_text,
    public_key_resolver=resolve_public_key
)
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## Handling Extraction Errors

When working with text that may or may not contain metadata, it's essential to handle potential extraction errors:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict

# Define a public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # Your key lookup logic here
    return public_keys_store.get(key_id)

# Function to safely extract metadata
def safe_extract_metadata(text):
    try:
        # First, try to extract metadata without verification
        metadata = UnicodeMetadata.extract_metadata(text)

        if not metadata:
            return {
                "has_metadata": False,
                "metadata": None,
                "verified": False,
                "error": "No metadata found"
            }

        # Then try to verify the metadata
        is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
            text=text,
            public_key_resolver=resolve_public_key
        )

        return {
            "has_metadata": True,
            "metadata": verified_metadata if is_valid else metadata,
            "verified": is_valid,
            "verification_attempted": True
        }
    except Exception as e:
        # No metadata found or extraction failed
        return {
            "has_metadata": False,
            "metadata": None,
            "verified": False,
            "verification_attempted": False,
            "error": str(e)
        }

# Example usage
result = safe_extract_metadata(encoded_text)
if result["has_metadata"]:
    if result["verified"]:
        print("✅ Verified metadata:", result["metadata"])
    else:
        print("❌ Metadata found but verification failed:", result["metadata"])
else:
    print("No metadata found:", result.get("error", "Unknown error"))
```

## Batch Processing

For processing multiple texts, you can use a batch approach:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import pandas as pd

# Define a public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # Your key lookup logic here
    return public_keys_store.get(key_id)

# Sample texts
texts = [
    "This text contains embedded metadata.",
    "This text also contains embedded metadata, but different.",
    "This text doesn't contain any metadata."
]

# Process all texts
results = []
for i, text in enumerate(texts):
    result = {
        "text_id": i,
        "text": text[:50] + "..." if len(text) > 50 else text,
        "has_metadata": False,
        "verified": False,
        "metadata": None,
        "error": None
    }

    try:
        # First, try to extract metadata without verification
        metadata = UnicodeMetadata.extract_metadata(text)

        if not metadata:
            result["error"] = "No metadata found"
        else:
            # Then try to verify the metadata
            is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
                text=text,
                public_key_resolver=resolve_public_key
            )

            result["has_metadata"] = True
            result["verified"] = is_valid
            result["metadata"] = verified_metadata if is_valid else metadata
    except Exception as e:
        # No metadata found or extraction failed
        result["error"] = str(e)

    results.append(result)

# Convert to DataFrame for easier analysis
df = pd.DataFrame(results)
print(df[["text_id", "has_metadata", "verified"]].to_string(index=False))
```

## Advanced: Verification with External Keys

In some scenarios, you might want to verify text using a key that's stored externally:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
import os
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional

# Function to get or create a secret key
def get_secret_key(key_file="secret_key.key"):
    if os.path.exists(key_file):
        # Load existing key
        with open(key_file, "rb") as f:
            return f.read()
    else:
        # Generate new key
        key = generate_key_pair()
        with open(key_file, "wb") as f:
            f.write(key)
        return key

# Get the secret key
secret_key = get_secret_key()

# Create a metadata encoder with the secret key
encoder = UnicodeMetadata(private_key=secret_key)

# Verify text
is_valid, verified_metadata = encoder.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
print(f"Verification result: {'✅ Verified' if is_valid else '❌ Failed'}")
```

## Implementation Details

### Digital Signature Verification Process

The verification process involves:

1. Extracting the embedded metadata and signature
2. Looking up the public key corresponding to the key_id in the metadata
3. Verifying the signature using the public key

If the signature is valid, the verification succeeds, indicating the content hasn't been tampered with.

### Metadata Format

The embedded metadata follows this structure:

1. **Header**: Identifies the metadata format and version
2. **Metadata Length**: The size of the metadata in bytes
3. **Metadata Content**: The JSON-serialized metadata
4. **Signature**: The digital signature for verification

### Handling Unicode and Encoding Issues

When working with text from various sources, you might encounter encoding issues:

```python
from encypher.core.unicode_metadata import UnicodeMetadata

# Function to safely handle text with potential encoding issues
def safe_process_text(text):
    # Ensure text is properly encoded as UTF-8
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')

    # Replace any problematic characters
    text = ''.join(c if ord(c) < 65536 else ' ' for c in text)

    # Try to extract and verify metadata
    try:
        is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
            text=text,
            public_key_resolver=resolve_public_key
        )
        return verified_metadata, is_valid
    except Exception as e:
        return None, False

# Example usage
metadata, is_valid = safe_process_text(encoded_text)
```

## Best Practices

1. **Always verify before trusting**: Use `verify_metadata` before relying on extracted metadata
2. **Handle extraction errors**: Implement proper error handling for cases where metadata is missing or corrupted
3. **Use consistent key management**: Store and reuse secret keys for verification across systems
4. **Combine extraction and verification**: Use `verify_metadata` for a streamlined approach
5. **Consider key management**: Implement secure storage for secret keys
6. **Process in batches**: Use batch processing for efficiency when handling multiple texts

## Common Use Cases

### Content Authentication

```python
from encypher.core.unicode_metadata import UnicodeMetadata

def authenticate_content(text, expected_source):
    """Authenticate content based on embedded metadata."""
    # Define a public key resolver function
    def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
        # Your key lookup logic here
        return public_keys_store.get(key_id)

    try:
        # Extract and verify metadata
        is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
            text=text,
            public_key_resolver=resolve_public_key
        )

        if not is_valid:
            return False, "Verification failed, content may be tampered"

        # Check source in metadata
        if verified_metadata.get("organization") != expected_source:
            return False, f"Content source mismatch: expected {expected_source}, got {verified_metadata.get('organization')}"

        return True, verified_metadata
    except Exception as e:
        return False, f"Authentication failed: {str(e)}"

# Example usage
is_authentic, result = authenticate_content(encoded_text, "EncypherAI")
if is_authentic:
    print("✅ Content authenticated:", result)
else:
    print("❌ Authentication failed:", result)
```

### Timestamp Verification

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from datetime import datetime, timezone
import dateutil.parser

def verify_content_age(text, max_age_hours=24):
    """Verify content is not older than specified age."""
    # Define a public key resolver function
    def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
        # Your key lookup logic here
        return public_keys_store.get(key_id)

    try:
        # Extract and verify metadata
        is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
            text=text,
            public_key_resolver=resolve_public_key
        )

        if not is_valid:
            return False, "Verification failed, content may be tampered"

        # Check timestamp in metadata
        if "timestamp" not in verified_metadata:
            return False, "No timestamp in metadata"

        # Parse timestamp
        timestamp = dateutil.parser.parse(verified_metadata["timestamp"])

        # Calculate age
        now = datetime.now(timezone.utc)
        age_hours = (now - timestamp).total_seconds() / 3600

        if age_hours > max_age_hours:
            return False, f"Content too old: {age_hours:.1f} hours (max {max_age_hours})"

        return True, f"Content age: {age_hours:.1f} hours"
    except Exception as e:
        return False, f"Verification failed: {str(e)}"

# Example usage
is_recent, result = verify_content_age(encoded_text, max_age_hours=48)
if is_recent:
    print("✅ Content is recent:", result)
else:
    print("❌ Content is too old:", result)
```

## Related Documentation

- [UnicodeMetadata API Reference](../api-reference/unicode-metadata.md)
- [Metadata Encoding Guide](./metadata-encoding.md)
- [Streaming Support Guide](./streaming.md)
- [Jupyter Notebook Examples](../examples/jupyter.md)
- [Streamlit Demo App](../examples/streamlit.md)
