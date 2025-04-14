# UnicodeMetadata

The `UnicodeMetadata` class provides utilities for embedding and extracting metadata using Unicode variation selectors. This class is the primary interface for embedding and verifying metadata with digital signatures.

## Overview

Unicode variation selectors are special characters that modify the appearance of the preceding character. EncypherAI uses a specific range of these selectors (VS1-VS256) to encode binary data within text without changing its visible appearance.

The `UnicodeMetadata` class provides methods to:

1. Convert binary data to and from variation selectors
2. Find suitable targets in text for embedding metadata
3. Embed and extract metadata at the character level
4. Sign and verify metadata using Ed25519 digital signatures

## Class Definition

```python
class UnicodeMetadata:
    """
    Utilities for embedding and extracting metadata using Unicode variation selectors.
    """

    # Unicode variation selector range (VS1-VS256)
    VARIATION_SELECTOR_START = 0xFE00  # VS1
    VARIATION_SELECTOR_END = 0xFE0F    # VS16 (first range)
    VARIATION_SELECTOR_START_2 = 0xE0100  # VS17
    VARIATION_SELECTOR_END_2 = 0xE01EF    # VS256 (second range)
```

## Class Methods

### to_variation_selector

```python
@classmethod
def to_variation_selector(cls, byte: int) -> Optional[str]:
    """
    Convert a byte value (0-255) to a Unicode variation selector.

    Args:
        byte: Integer value between 0-255

    Returns:
        Unicode variation selector character or None if the byte is out of range
    """
```

### from_variation_selector

```python
@classmethod
def from_variation_selector(cls, char: str) -> Optional[int]:
    """
    Convert a Unicode variation selector to its byte value.

    Args:
        char: Unicode variation selector character

    Returns:
        Integer value between 0-255 or None if the character is not a variation selector
    """
```

### is_variation_selector

```python
@classmethod
def is_variation_selector(cls, char: str) -> bool:
    """
    Check if a character is a Unicode variation selector.

    Args:
        char: Character to check

    Returns:
        True if the character is a variation selector, False otherwise
    """
```

### find_targets

```python
@classmethod
def find_targets(
    cls,
    text: str,
    target: Union[str, MetadataTarget] = "whitespace"
) -> List[int]:
    """
    Find suitable target positions in text for embedding metadata.

    Args:
        text: The text to analyze
        target: Where to embed metadata. Can be a string ("whitespace", "punctuation",
               "first_letter", "last_letter", "all_characters") or a MetadataTarget enum.

    Returns:
        List of character indices that are suitable for embedding metadata
    """
```

### embed_bytes

```python
@classmethod
def embed_bytes(
    cls,
    text: str,
    data: bytes,
    target: Union[str, MetadataTarget] = "whitespace"
) -> str:
    """
    Embed binary data into text using Unicode variation selectors.

    Args:
        text: The text to embed data into
        data: Binary data to embed
        target: Where to embed data. Can be a string ("whitespace", "punctuation",
               "first_letter", "last_letter", "all_characters") or a MetadataTarget enum.

    Returns:
        Text with embedded data

    Raises:
        ValueError: If there are not enough targets to embed all data
    """
```

### extract_bytes

```python
@classmethod
def extract_bytes(cls, text: str) -> bytes:
    """
    Extract binary data embedded in text using Unicode variation selectors.

    Args:
        text: Text with embedded data

    Returns:
        Extracted binary data
    """
```

### embed_metadata

```python
@classmethod
def embed_metadata(
    cls,
    text: str,
    metadata: Dict[str, Any],
    private_key: PrivateKeyTypes,
    target: str = "whitespace"
) -> str:
    """
    Embed metadata into text using Unicode variation selectors.

    Args:
        text: The text to embed metadata into
        metadata: Dictionary containing metadata to embed. Must include a 'key_id' field
                 that identifies the private key used for signing and a 'timestamp' field.
        private_key: Ed25519 private key used to sign the metadata
        target: Where to embed metadata. Can be "whitespace", "punctuation",
               "first_letter", "last_letter", or "all_characters"

    Returns:
        Text with embedded metadata and digital signature

    Raises:
        ValueError: If there are not enough targets to embed all data, if metadata
                   doesn't contain a 'key_id' field, or if metadata doesn't contain a 'timestamp' field
    """
```

### extract_metadata

```python
@classmethod
def extract_metadata(cls, text: str) -> Optional[Dict[str, Any]]:
    """
    Extract metadata embedded in text using Unicode variation selectors.
    This method does NOT verify the digital signature.

    Args:
        text: Text with embedded metadata

    Returns:
        Extracted metadata dictionary or None if no metadata could be extracted
    """
```

### verify_metadata

```python
@classmethod
def verify_metadata(
    cls,
    text: str,
    public_key_resolver: Callable[[str], Optional[PublicKeyTypes]]
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify the metadata embedded in text using digital signature verification.

    Args:
        text: Text with embedded metadata and digital signature
        public_key_resolver: A function that takes a key_id and returns the corresponding
                            public key, or None if the key_id is not recognized

    Returns:
        Tuple containing:
        - A boolean indicating whether the verification was successful
        - The verified metadata if successful, otherwise None

    Notes:
        The verification process:
        1. Extracts the metadata and signature from the text
        2. Gets the key_id from the metadata
        3. Resolves the public key using the provided resolver function
        4. Verifies the signature using the public key
        5. Returns (True, metadata) if verification succeeds, (False, None) otherwise
    """
```

## MetadataTarget Enum

The `MetadataTarget` enum defines the possible targets for embedding metadata:

```python
class MetadataTarget(Enum):
    """Enum for specifying where to embed metadata in text"""

    WHITESPACE = "whitespace"  # Default - embed in whitespace
    PUNCTUATION = "punctuation"  # Embed in punctuation marks
    FIRST_LETTER = "first_letter"  # Embed in first letter of each word
    LAST_LETTER = "last_letter"  # Embed in last letter of each word
    ALL_CHARACTERS = "all_characters"  # Embed in all characters (not recommended)
    NONE = "none"  # Don't embed metadata (for testing/debugging)
```

## Usage Example

```python
from encypher.core.unicode_metadata import UnicodeMetadata
import time

# Sample text
text = "This is a sample text for embedding metadata."

# Find suitable targets for embedding
whitespace_targets = UnicodeMetadata.find_targets(text, MetadataTarget.WHITESPACE)
punctuation_targets = UnicodeMetadata.find_targets(text, MetadataTarget.PUNCTUATION)

print(f"Whitespace targets: {len(whitespace_targets)} positions")
print(f"Punctuation targets: {len(punctuation_targets)} positions")

# Embed metadata
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "1.0.0",
    "key_id": "your-key-id"  # Required for verification
}
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key="your-private-key"  # Use your private key here
)

print("\nOriginal text:")
print(text)
print("\nEncoded text (looks identical but contains embedded data):")
print(encoded_text)

# Extract the metadata
extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)
print(f"\nExtracted metadata: {extracted_metadata}")

# Verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=lambda key_id: "your-public-key"  # Use your public key resolver here
)
print(f"\nVerification result: {'✅ Verified' if is_valid else '❌ Failed'}")
print(f"Verified metadata: {verified_metadata}")

# Demonstrate variation selector conversion
byte_value = 65  # ASCII 'A'
vs_char = UnicodeMetadata.to_variation_selector(byte_value)
print(f"\nByte value {byte_value} converted to variation selector: U+{ord(vs_char):04X}")
back_to_byte = UnicodeMetadata.from_variation_selector(vs_char)
print(f"Variation selector converted back to byte: {back_to_byte}")
```

## Advanced: Key Management

The `UnicodeMetadata` class requires proper key management for secure operation:

```python
from encypher.core.keys import generate_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import time

# Generate key pair
private_key, public_key = generate_key_pair()
key_id = "example-key-1"

# Store public key (in a real application, this would be a database or secure storage)
public_keys_store = {key_id: public_key}

# Create a resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)

# Create metadata with key_id
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "version": "2.0.0",
    "key_id": key_id  # Required for verification
}

# Embed metadata with digital signature
encoded_text = UnicodeMetadata.embed_metadata(
    text="This is a sample text.",
    metadata=metadata,
    private_key=private_key
)

# Later, verify the metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
```

## Advanced: Handling Timestamps

The `UnicodeMetadata` class works with timestamps as part of the metadata:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
import time

# Sample text
text = "This is a sample text for embedding metadata with timestamps."

# Create metadata with a timestamp
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Unix/Epoch timestamp
    "version": "1.0.0",
    "key_id": "your-key-id"  # Required for verification
}

# Embed metadata
is_valid, encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key="your-private-key"  # Use your private key here
)

print(f"Embedding successful: {is_valid}")
print(f"Encoded text: {encoded_text}")

# Extract metadata
is_valid, extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)

print(f"Extraction successful: {is_valid}")
print(f"Extracted metadata: {extracted_metadata}")
```

## Related Classes

- [`MetadataEncoder`](./metadata-encoder.md): Higher-level interface for embedding and extracting metadata
- [`StreamingMetadataEncoder`](./streaming-metadata-encoder.md): For handling streaming content
