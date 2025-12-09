# MetadataEncoder

> **DEPRECATED**: The `MetadataEncoder` class is deprecated as of version 1.1.0. Please use the [`UnicodeMetadata`](unicode-metadata.md) class with digital signatures instead, which provides stronger security through Ed25519 signatures rather than HMAC. See the [Tamper Detection](../user-guide/tamper-detection.md) guide for details on the new approach.

The `MetadataEncoder` class is the primary interface for embedding and extracting metadata in text.

## Class Definition

```python
class MetadataEncoder:
    def __init__(self, hmac_secret_key: Optional[str] = None):
        """
        Initialize a MetadataEncoder instance.

        Args:
            hmac_secret_key: Optional secret key for HMAC verification. If None, HMAC verification is disabled.
        """
```

## Methods

### encode_metadata

```python
def encode_metadata(self, text: str, metadata: Dict[str, Any]) -> str:
    """
    Embed metadata into the provided text using zero-width characters.

    Args:
        text: The text to embed metadata into
        metadata: Dictionary containing metadata to embed

    Returns:
        Text with embedded metadata as zero-width characters
    """
```

This method encodes the provided metadata and embeds it into the text using zero-width characters. If a secret key was provided when initializing the encoder, an HMAC signature is also generated and embedded to enable tamper detection.

### decode_metadata

```python
def decode_metadata(self, text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Extract metadata from text and return the metadata along with the clean text.

    Args:
        text: Text potentially containing embedded metadata

    Returns:
        Tuple of (metadata, clean_text), where metadata is None if no metadata was found
    """
```

Extracts any embedded metadata from the provided text. Returns both the extracted metadata (or None if not found) and the clean text with zero-width characters removed.

### verify_text

```python
def verify_text(self, text: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Verify the integrity of text with embedded metadata using HMAC.

    Args:
        text: Text with potentially embedded metadata

    Returns:
        Tuple of (is_valid, metadata, clean_text), where:
          - is_valid: True if metadata was found and HMAC verification passed
          - metadata: The extracted metadata, or None if not found
          - clean_text: The text with zero-width characters removed
    """
```

This method extracts metadata from the text and verifies its integrity using the HMAC signature. It returns a tuple containing:

1. A boolean indicating whether the verification was successful
2. The extracted metadata (or None if not found)
3. The clean text with zero-width characters removed

Verification will fail if:
- No metadata was found
- The encoder was initialized without a secret key
- The HMAC signature doesn't match (indicating tampering)

## Usage Examples

### Basic Metadata Embedding

```python
from encypher.core.metadata_encoder import MetadataEncoder
import time

# Initialize with a secret key for HMAC verification
encoder = MetadataEncoder(hmac_secret_key="your-secret-key")

# Define metadata
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "1.1.0"
}

# Original text
text = "This is AI-generated content."

# Embed metadata
encoded_text = encoder.encode_metadata(text, metadata)
print(encoded_text)  # Visually identical to original text
```

### Extracting and Verifying Metadata

```python
# Later, verify and extract metadata
is_valid, extracted_metadata, clean_text = encoder.verify_text(encoded_text)

if is_valid:
    print("Verification successful!")
    print(f"Metadata: {extracted_metadata}")
    print(f"Clean text: {clean_text}")
else:
    print("Verification failed - content may have been tampered with.")
```

> **Note**: For target-based embedding (whitespace, punctuation, etc.), use the `UnicodeMetadata.verify_metadata()` method instead. See [UnicodeMetadata](unicode-metadata.md) for details.

### Handling Tampered Content

```python
# Simulate tampering by modifying the encoded text
tampered_text = encoded_text.replace("AI-generated", "human-written")

# Attempt to verify
is_valid, extracted_metadata, clean_text = encoder.verify_text(tampered_text)

if not is_valid:
    print("Tampering detected - content has been modified!")
```

## Advanced Usage

### Disable HMAC Verification

If you only need to embed and extract metadata without tamper detection:

```python
from encypher.core.metadata_encoder import MetadataEncoder
import time

# Initialize without a secret key
encoder = MetadataEncoder()  # No HMAC verification

# Define metadata
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time())  # Unix/Epoch timestamp
}

# Original text
text = "This is AI-generated content."

# Encode metadata (no HMAC signature will be generated)
encoded_text = encoder.encode_metadata(text, metadata)

# Extract metadata (no verification will be performed)
metadata, clean_text = encoder.decode_metadata(encoded_text)
```

### Custom HMAC Implementation

By default, Encypher uses SHA-256 for HMAC generation. If you need to customize this:

```python
from encypher.core.metadata_encoder import MetadataEncoder
import hmac
import hashlib

# Subclass MetadataEncoder to customize HMAC implementation
class CustomEncoder(MetadataEncoder):
    def _create_hmac(self, data_bytes: bytes) -> str:
        return hmac.new(
            self.hmac_secret_key.encode('utf-8'),
            data_bytes,
            hashlib.sha512  # Use SHA-512 instead of SHA-256
        ).hexdigest()
```

## Related Classes

- [StreamingMetadataEncoder](streaming-metadata-encoder.md): For handling streaming text from LLM providers
- [UnicodeMetadata](unicode-metadata.md): Low-level interface for encoding and decoding metadata using zero-width characters
