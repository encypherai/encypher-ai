# Tamper Detection Examples

This guide provides detailed examples of how to implement tamper detection for text content with embedded C2PA manifests. It covers both content tampering (modifying the text after embedding) and metadata tampering (modifying the embedded manifest itself).

## Overview

EncypherAI's text embedding approach enables two types of tamper detection:

1. **Content Tampering**: If the text content is modified after embedding, the current hash will no longer match the stored hash in the manifest.

2. **Metadata Tampering**: If the embedded manifest itself is modified, the digital signature verification will fail.

These mechanisms ensure the integrity and authenticity of both the content and its provenance information.

## Prerequisites

Before implementing tamper detection, ensure you have:

- EncypherAI Python package installed (`uv add encypher-ai`)
- A text with embedded C2PA metadata
- Access to the public key corresponding to the private key used for signing

## Content Tampering Detection

Content tampering occurs when someone modifies the text after the metadata has been embedded. This is detected by comparing the stored content hash in the manifest with a freshly calculated hash of the current content.

### Step-by-Step Implementation

```python
import hashlib
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import encypher_manifest_to_c2pa_like_dict

def detect_content_tampering(text, public_key_provider):
    """
    Detect if the content has been tampered with after embedding.
    
    Args:
        text (str): The text with embedded metadata
        public_key_provider (callable): Function that returns the public key for a given signer_id
        
    Returns:
        dict: Results of tampering detection
    """
    # Extract the first paragraph (assuming metadata is in first paragraph)
    first_paragraph = text.split('\n')[0]
    
    # Verify and extract metadata
    is_verified, signer_id, manifest = UnicodeMetadata.verify_and_extract_metadata(
        text=first_paragraph,
        public_key_provider=public_key_provider
    )
    
    if not is_verified:
        return {
            "signature_verified": False,
            "content_hash_verified": False,
            "error": "Signature verification failed"
        }
    
    # Convert to C2PA format if using cbor_manifest format
    if isinstance(manifest, dict) and "assertions" in manifest:
        c2pa_manifest = manifest
    else:
        c2pa_manifest = encypher_manifest_to_c2pa_like_dict(manifest)
    
    # Find content hash assertion
    stored_hash = None
    
    # Look in assertions list
    for assertion in c2pa_manifest.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break
    
    # Also look in actions list (alternative location)
    if not stored_hash:
        for action in c2pa_manifest.get("actions", []):
            if action.get("label") == "stds.c2pa.content.hash":
                stored_hash = action["data"]["hash"]
                break
    
    if not stored_hash:
        return {
            "signature_verified": True,
            "content_hash_verified": False,
            "error": "Content hash assertion not found in manifest"
        }
    
    # Calculate current content hash
    # Note: This should match exactly how the hash was calculated during embedding
    current_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    # Compare hashes
    content_hash_verified = (stored_hash == current_hash)
    
    return {
        "signature_verified": True,
        "content_hash_verified": content_hash_verified,
        "stored_hash": stored_hash,
        "current_hash": current_hash
    }
```

### Example Usage

```python
from encypher.core.keys import load_ed25519_key_pair
import json

# Load keys
with open("keys.json", "r") as f:
    keys_dict = json.load(f)

public_key = bytes.fromhex(keys_dict["public_key"])
signer_id = keys_dict["signer_id"]

# Define key provider
def key_provider(kid):
    if kid == signer_id:
        return public_key
    return None

# Original text with embedded metadata
with open("embedded_article.txt", "r", encoding="utf-8") as f:
    original_text = f.read()

# Check if original is tampered
original_result = detect_content_tampering(original_text, key_provider)
print("Original Article Verification:")
print(f"Signature verified: {'Yes' if original_result['signature_verified'] else 'No'}")
print(f"Content hash verified: {'Yes' if original_result['content_hash_verified'] else 'No'}")

# Create tampered version (modify some text)
tampered_text = original_text.replace("artificial intelligence", "TAMPERED TEXT")

# Save tampered version
with open("tampered_article.txt", "w", encoding="utf-8") as f:
    f.write(tampered_text)

# Check if tampered version is detected
tampered_result = detect_content_tampering(tampered_text, key_provider)
print("\nTampered Article Verification:")
print(f"Signature verified: {'Yes' if tampered_result['signature_verified'] else 'No'}")
print(f"Content hash verified: {'Yes' if tampered_result['content_hash_verified'] else 'No'}")

if tampered_result['signature_verified'] and not tampered_result['content_hash_verified']:
    print("\nTampering detected!")
    print(f"Stored hash: {tampered_result['stored_hash'][:10]}...{tampered_result['stored_hash'][-10:]}")
    print(f"Current hash: {tampered_result['current_hash'][:10]}...{tampered_result['current_hash'][-10:]}")
```

## Metadata Tampering Detection

Metadata tampering occurs when someone modifies the embedded manifest itself. This is detected by the digital signature verification process, which will fail if the manifest has been altered.

### Step-by-Step Implementation

```python
from encypher.core.unicode_metadata import UnicodeMetadata

def detect_metadata_tampering(text, public_key_provider):
    """
    Detect if the embedded metadata has been tampered with.
    
    Args:
        text (str): The text with embedded metadata
        public_key_provider (callable): Function that returns the public key for a given signer_id
        
    Returns:
        dict: Results of tampering detection
    """
    # Extract the first paragraph (assuming metadata is in first paragraph)
    first_paragraph = text.split('\n')[0]
    
    # First, just extract metadata without verification
    raw_metadata = UnicodeMetadata.extract_metadata(first_paragraph)
    
    if not raw_metadata:
        return {
            "metadata_present": False,
            "signature_verified": False,
            "error": "No metadata found"
        }
    
    # Now verify the signature
    is_verified, signer_id, manifest = UnicodeMetadata.verify_and_extract_metadata(
        text=first_paragraph,
        public_key_provider=public_key_provider,
        return_payload_on_failure=True
    )
    
    return {
        "metadata_present": True,
        "signature_verified": is_verified,
        "signer_id": signer_id
    }
```

### Simulating Metadata Tampering

To demonstrate metadata tampering detection, we can simulate tampering by modifying the embedded metadata:

```python
def simulate_metadata_tampering(text):
    """
    Simulate tampering with the embedded metadata by modifying a byte.
    
    Args:
        text (str): The text with embedded metadata
        
    Returns:
        str: Text with tampered metadata
    """
    # Find the first variation selector character (typically after first character)
    for i, char in enumerate(text):
        if 0xFE00 <= ord(char) <= 0xFE0F or 0xE0100 <= ord(char) <= 0xE01EF:
            # Found a variation selector, modify it
            char_code = ord(char)
            # Flip a bit in the character code
            tampered_char_code = char_code ^ 0x1  # XOR with 1 to flip the least significant bit
            tampered_char = chr(tampered_char_code)
            
            # Replace the character in the text
            tampered_text = text[:i] + tampered_char + text[i+1:]
            return tampered_text, i
    
    return text, -1  # No variation selector found
```

### Example Usage

```python
# Simulate metadata tampering
tampered_metadata_text, tamper_position = simulate_metadata_tampering(original_text)

if tamper_position >= 0:
    print(f"\nMetadata tampered at position {tamper_position}")
    
    # Save tampered version
    with open("tampered_metadata.txt", "w", encoding="utf-8") as f:
        f.write(tampered_metadata_text)
    
    # Check if metadata tampering is detected
    metadata_result = detect_metadata_tampering(tampered_metadata_text, key_provider)
    print("\nTampered Metadata Verification:")
    print(f"Metadata present: {'Yes' if metadata_result['metadata_present'] else 'No'}")
    print(f"Signature verified: {'Yes' if metadata_result['signature_verified'] else 'No'}")
    
    if metadata_result['metadata_present'] and not metadata_result['signature_verified']:
        print("\nMetadata tampering detected!")
else:
    print("\nNo metadata found to tamper with")
```

## Comprehensive Tamper Detection

For a complete tamper detection solution, combine both approaches:

```python
def verify_text_integrity(text, public_key_provider):
    """
    Comprehensive verification of text integrity, checking both
    signature and content hash.
    
    Args:
        text (str): The text with embedded metadata
        public_key_provider (callable): Function that returns the public key for a given signer_id
        
    Returns:
        dict: Comprehensive verification results
    """
    # Extract the first paragraph (assuming metadata is in first paragraph)
    paragraphs = text.split('\n\n')
    first_paragraph = paragraphs[0]
    
    # Verify and extract metadata
    is_verified, signer_id, manifest = UnicodeMetadata.verify_and_extract_metadata(
        text=first_paragraph,
        public_key_provider=public_key_provider,
        return_payload_on_failure=True
    )
    
    result = {
        "metadata_present": manifest is not None,
        "signature_verified": is_verified,
        "signer_id": signer_id,
        "content_hash_verified": False
    }
    
    # If signature verification failed, we're done
    if not is_verified:
        result["error"] = "Signature verification failed"
        return result
    
    # Convert to C2PA format if using cbor_manifest format
    if isinstance(manifest, dict) and "assertions" in manifest:
        c2pa_manifest = manifest
    else:
        c2pa_manifest = encypher_manifest_to_c2pa_like_dict(manifest)
    
    # Find content hash assertion
    stored_hash = None
    
    # Look in assertions list
    for assertion in c2pa_manifest.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break
    
    # Also look in actions list (alternative location)
    if not stored_hash:
        for action in c2pa_manifest.get("actions", []):
            if action.get("label") == "stds.c2pa.content.hash":
                stored_hash = action["data"]["hash"]
                break
    
    if not stored_hash:
        result["error"] = "Content hash assertion not found in manifest"
        return result
    
    # Calculate current content hash
    # Note: This should match exactly how the hash was calculated during embedding
    current_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    # Compare hashes
    result["content_hash_verified"] = (stored_hash == current_hash)
    result["stored_hash"] = stored_hash
    result["current_hash"] = current_hash
    
    if not result["content_hash_verified"]:
        result["error"] = "Content hash verification failed - content may have been tampered with"
    
    return result
```

## Real-World Example: HTML Article Verification

For HTML content, the verification process needs to extract the plain text for hashing:

```python
from bs4 import BeautifulSoup

def verify_html_article(html_content, public_key_provider):
    """
    Verify the integrity of an HTML article with embedded metadata.
    
    Args:
        html_content (str): The HTML content with embedded metadata
        public_key_provider (callable): Function that returns the public key for a given signer_id
        
    Returns:
        dict: Verification results
    """
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find first paragraph (which contains embedded metadata)
    first_p = soup.select_one('p')
    if not first_p:
        return {"error": "No paragraphs found in HTML"}
    
    # Extract all paragraphs for content hash
    paragraphs = soup.find_all('p')
    article_text = '\n'.join([p.get_text() for p in paragraphs])
    
    # Verify and extract metadata
    is_verified, signer_id, manifest = UnicodeMetadata.verify_and_extract_metadata(
        text=first_p.get_text(),
        public_key_provider=public_key_provider,
        return_payload_on_failure=True
    )
    
    result = {
        "metadata_present": manifest is not None,
        "signature_verified": is_verified,
        "signer_id": signer_id,
        "content_hash_verified": False
    }
    
    # If signature verification failed, we're done
    if not is_verified:
        result["error"] = "Signature verification failed"
        return result
    
    # Convert to C2PA format if using cbor_manifest format
    if isinstance(manifest, dict) and "assertions" in manifest:
        c2pa_manifest = manifest
    else:
        c2pa_manifest = encypher_manifest_to_c2pa_like_dict(manifest)
    
    # Find content hash assertion
    stored_hash = None
    
    # Look in assertions list
    for assertion in c2pa_manifest.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break
    
    # Also look in actions list (alternative location)
    if not stored_hash:
        for action in c2pa_manifest.get("actions", []):
            if action.get("label") == "stds.c2pa.content.hash":
                stored_hash = action["data"]["hash"]
                break
    
    if not stored_hash:
        result["error"] = "Content hash assertion not found in manifest"
        return result
    
    # Calculate current content hash
    current_hash = hashlib.sha256(article_text.encode('utf-8')).hexdigest()
    
    # Compare hashes
    result["content_hash_verified"] = (stored_hash == current_hash)
    result["stored_hash"] = stored_hash
    result["current_hash"] = current_hash
    
    if not result["content_hash_verified"]:
        result["error"] = "Content hash verification failed - content may have been tampered with"
    
    return result
```

## Best Practices for Tamper Detection

1. **Consistent Hashing**: Ensure the content hash calculation is identical during embedding and verification
2. **Handle Both Tampering Types**: Check both signature verification and content hash
3. **Detailed Error Reporting**: Provide specific information about what verification step failed
4. **User-Friendly Messaging**: Translate technical verification results into clear user messages
5. **Graceful Degradation**: Handle cases where metadata is missing or malformed

## Conclusion

EncypherAI's approach to text provenance provides robust tamper detection through two complementary mechanisms:

1. Digital signatures verify the integrity of the embedded metadata
2. Content hashes verify the integrity of the text content

By implementing both checks, you can provide comprehensive tamper detection for text content, ensuring that both the content and its provenance information remain authentic and unmodified.
