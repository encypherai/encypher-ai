# Content Hash Coverage and Embedding Technical Details

This document provides a detailed technical explanation of how EncypherAI's C2PA text embedding approach works, specifically focusing on content hash coverage and the embedding mechanism.

## What the Content Hash Covers

The content hash in our implementation covers the plain text content of the article - specifically:

### Text Extraction Process

1. The code extracts all paragraph text from the article
   - It looks for paragraphs in content columns first, then falls back to direct paragraph search
   - All paragraph texts are joined with double newlines (`"\n\n"`)
   - This extracted plain text is saved to `clean_text_for_hashing.txt` as a reference

### Hash Generation

1. A SHA-256 hash is calculated on this extracted text
2. The hash is computed on the UTF-8 encoded version of the text
3. This happens before any metadata embedding occurs

### Hash Usage

1. The hash is included in the manifest as a `stds.c2pa.content.hash` assertion
2. This assertion includes both the hash value and the algorithm used (sha256)

### Important Distinction

- The hash covers only the plain text content, not the HTML markup
- The hash does not include the embedded metadata itself (the Unicode variation selectors)
- This creates a "snapshot" of the original content at the time of signing

This approach allows for tamper detection - if the text content is modified after embedding, the hash of the current content will no longer match the hash stored in the embedded manifest.

## How Our C2PA-like Embedding Actually Works

### Single-Point Embedding with Zero-Width Characters

1. The metadata (manifest) is embedded as a sequence of Unicode variation selectors
2. These are zero-width, non-printing characters (code points in ranges U+FE00-FE0F and U+E0100-E01EF)
3. All metadata is attached to a single character in the text (by default, the first whitespace)
4. The original character is preserved, and the variation selectors are inserted immediately after it

### This is Still Hard Binding Because

- The manifest is directly embedded within the content itself
- The manifest travels with the content as part of the same file
- The binding is inseparable from the content

### Not a Hybrid Approach Because

In a true hybrid approach, you would have:
1. A manifest stored separately from the content (soft binding component)
2. A small reference embedded in the content pointing to the external manifest (hard binding component)

Our implementation embeds the entire manifest directly in the content. The content hash we include is just an assertion within the hard-bound manifest.

## Implementation Details

### Embedding Process

```python
def embed_metadata(text, metadata, metadata_format="json"):
    """
    Embeds metadata into text using Unicode variation selectors.
    
    Args:
        text (str): The text to embed metadata into
        metadata (dict or bytes): The metadata to embed
        metadata_format (str): Format of the metadata ("json" or "cbor_manifest")
        
    Returns:
        str: Text with embedded metadata
    """
    # Serialize metadata based on format
    if metadata_format == "json":
        serialized = json.dumps(metadata).encode("utf-8")
    elif metadata_format == "cbor_manifest":
        if isinstance(metadata, dict):
            serialized = cbor2.dumps(metadata)
        else:
            serialized = metadata  # Already serialized
    else:
        raise ValueError(f"Unsupported metadata format: {metadata_format}")
    
    # Convert to binary and encode using variation selectors
    binary_data = base64.b64encode(serialized).decode("ascii")
    encoded_metadata = _encode_to_variation_selectors(binary_data)
    
    # Find position to insert (typically after first character)
    if len(text) > 0:
        return text[0] + encoded_metadata + text[1:]
    else:
        return encoded_metadata
```

### Extraction Process

```python
def extract_metadata(text, metadata_format="json"):
    """
    Extracts metadata from text with embedded Unicode variation selectors.
    
    Args:
        text (str): Text with embedded metadata
        metadata_format (str): Format of the metadata ("json" or "cbor_manifest")
        
    Returns:
        dict or bytes: Extracted metadata
    """
    # Extract variation selectors
    encoded_data = ""
    for char in text:
        if 0xFE00 <= ord(char) <= 0xFE0F or 0xE0100 <= ord(char) <= 0xE01EF:
            encoded_data += char
    
    if not encoded_data:
        return None
    
    # Decode from variation selectors to binary
    binary_data = _decode_from_variation_selectors(encoded_data)
    serialized = base64.b64decode(binary_data)
    
    # Deserialize based on format
    if metadata_format == "json":
        return json.loads(serialized.decode("utf-8"))
    elif metadata_format == "cbor_manifest":
        return cbor2.loads(serialized)
    else:
        raise ValueError(f"Unsupported metadata format: {metadata_format}")
```

## Verification Process

The verification process involves two key steps:

1. **Signature Verification**: Ensures the manifest itself hasn't been tampered with
   - Extracts the embedded metadata using Unicode variation selectors
   - Verifies the digital signature using the provided public key
   - If the signature is invalid, verification fails immediately

2. **Content Hash Verification**: Ensures the text content hasn't been modified
   - Extracts the stored content hash from the manifest
   - Calculates a fresh hash of the current content using the same algorithm
   - Compares the stored hash with the freshly calculated hash
   - If they don't match, the content has been tampered with

This two-step verification process provides comprehensive tamper detection for both the manifest and the content it describes.

## Advantages of This Approach

1. **Invisibility**: The embedding doesn't visibly alter the text appearance
2. **Portability**: The metadata travels with the content
3. **Robustness**: Works across different text formats and platforms
4. **Standards Alignment**: Compatible with C2PA concepts and structures
5. **Tamper Detection**: Provides comprehensive verification of both metadata and content integrity
