# Advanced Usage Examples

This guide provides advanced examples for using the EncypherAI package in various scenarios.

> Note: Timestamp optional
>
> - The `timestamp` field is optional across all metadata formats (including C2PA).
> - If omitted, C2PA assertions that normally include `when` will simply omit that field.
> - Provide a timestamp when you need time-bound auditing; otherwise you can skip it.

## Custom Metadata Handling

### Creating a Custom Metadata Handler

You can create custom handlers that build upon the `UnicodeMetadata` class to add specialized functionality:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, Any, Tuple
from encypher.interop.c2pa import compute_normalized_hash
import time
import json

class EnhancedMetadataHandler:
    """Custom metadata handler with enhanced features."""

    def __init__(self, private_key=None, include_hash=True):
        """
        Initialize the enhanced metadata handler.

        Args:
            private_key: The private key for signing metadata. If None, a new key pair is generated.
            include_hash: Whether to include a content hash in the metadata.
        """
        # Generate a key pair if not provided
        if private_key is None:
            self.private_key, self.public_key = generate_key_pair()
        else:
            self.private_key = private_key

        self.include_hash = include_hash
        self.key_id = "enhanced-handler-key"

        # In a real application, you would store this more securely
        self.public_keys = {self.key_id: self.public_key}

    def resolve_public_key(self, key_id: str) -> Optional[PublicKeyTypes]:
        """Resolve a public key by its ID."""
        return self.public_keys.get(key_id)

    def embed_metadata(self, text: str, metadata: Dict[str, Any], target: str = "whitespace") -> str:
        """Embed metadata with additional content hash."""
        # Add content hash if enabled
        if self.include_hash:
            content_hash = compute_normalized_hash(text).hexdigest
            metadata["content_hash"] = content_hash

        # Use UnicodeMetadata to perform the embedding
        return UnicodeMetadata.embed_metadata(
            text=text,
            custom_metadata=metadata,
            private_key=self.private_key,
            signer_id=self.key_id,
            # timestamp is optional; passing None will omit it
            timestamp=metadata.get("timestamp"),
            target=target
        )

    def verify_metadata(self, text: str, verify_hash: bool = True) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Enhanced verification that also checks content hash."""
        # Standard verification with digital signature
        is_valid, signer_id, verified_payload_dict = UnicodeMetadata.verify_metadata(
            text=text,
            public_key_provider=self.resolve_public_key
        )

        if not is_valid or not verified_payload_dict:
            return False, signer_id, None

        # Optionally verify content hash
        if verify_hash and self.include_hash and verified_payload_dict.get("content_hash"):
            # Extract the original text (without metadata)
            # This is a simplified approach - in practice you'd need to strip the metadata
            original_text_for_hash_check = UnicodeMetadata.extract_original_text(text)

            # Calculate hash of original text
            current_hash = compute_normalized_hash(original_text_for_hash_check).hexdigest

            # Compare with stored hash
            hash_verification = current_hash == verified_payload_dict.get("content_hash")

            # Both verifications must pass
            return hash_verification, signer_id, verified_payload_dict if hash_verification else None

        return is_valid, signer_id, verified_payload_dict

# Target options
# Supported targets include: "whitespace", "punctuation", "first_letter", "last_letter",
# "all_characters", "file_end", and "file_end_zwnbsp". End-of-file targets append selectors at
# the end of the text; "file_end_zwnbsp" prefixes a zero-width no-break space (U+FEFF) before the
# selectors for improved robustness in some pipelines.

# Example usage
handler = EnhancedMetadataHandler()
text = "This is a sample text for advanced encoding."
metadata = {
    "model": "gpt-4",
    "organization": "EncypherAI",
    "version": "2.3.0"
}

# Encode with enhanced metadata
encoded_text = handler.embed_metadata(text, metadata)
print(f"Encoded text: {encoded_text}")

# Verify with enhanced verification
is_valid, signer_id, verified_payload = handler.verify_metadata(encoded_text)
print(f"Verification result: {is_valid}")
if is_valid and verified_payload:
    print(f"Signer ID: {signer_id}")
    print(f"Verified metadata: {verified_payload}")

## Batch Processing

For processing large volumes of text, you can implement batch processing:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, List
import time
import concurrent.futures
import json

def process_batch(texts, metadata_template, private_key=None, key_id="batch-key", max_workers=4):
    """Process a batch of texts with metadata embedding."""
    # Generate a key pair if not provided
    if private_key is None:
        private_key, public_key = generate_key_pair()
    else:
        # In a real application, you would have a way to get the public key
        # corresponding to the private key
        _, public_key = generate_key_pair()  # This is just a placeholder

    # Store the public key (in a real app, this would be in a secure database)
    public_keys = {key_id: public_key}

    def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
        return public_keys.get(key_id)

    results = []

    # Define processing function
    def process_item(item):
        text = item["text"]
        # Create a copy of the template and add item-specific fields
        metadata = metadata_template.copy()
        metadata["item_id"] = item.get("id", f"item_{len(results)}")
        metadata["key_id"] = key_id  # Required for verification

        try:
            # Encode metadata
            encoded_text = UnicodeMetadata.embed_metadata(
                text=text,
                custom_metadata=metadata,
                private_key=private_key,
                signer_id=key_id,
                # timestamp optional; omit to skip
                timestamp=metadata.get("timestamp")
            )
            return {
                "success": True,
                "original_text": text,
                "encoded_text": encoded_text,
                "metadata": metadata
            }
        except Exception as e:
            return {
                "success": False,
                "original_text": text,
                "error": str(e)
            }

    # Process items in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_item, item) for item in texts]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Add the resolver function to the results for later verification
    results_with_resolver = {
        "results": results,
        "public_key_resolver": resolve_public_key
    }

    return results_with_resolver

# Example usage
texts = [
    {"id": "item1", "text": "This is the first text item."},
    {"id": "item2", "text": "This is the second text item."},
    {"id": "item3", "text": "This is the third text item."}
]

metadata_template = {
    "model": "gpt-4",
    "organization": "EncypherAI",
    "version": "2.3.0"
}

# Process batch
batch_result = process_batch(texts, metadata_template)
results = batch_result["results"]
resolver = batch_result["public_key_resolver"]

# Print results
for result in results:
    if result["success"]:
        print(f"Successfully processed item: {result['metadata']['item_id']}")

        # Verify the encoded text
        is_valid, signer_id, verified_payload_dict = UnicodeMetadata.verify_metadata(
            text=result["encoded_text"],
            public_key_provider=resolver
        )

        if is_valid and verified_payload_dict:
            print(f"  Verification successful for signer {signer_id}: {verified_payload_dict.get('item_id')}")
        else:
            print(f"  Verification failed")
    else:
        print(f"Failed to process item: {result.get('error', 'Unknown error')}")

## Advanced Streaming Techniques

### Custom Streaming Handler

You can create a custom streaming handler with specialized behavior:

```python
from encypher.streaming.handlers import StreamingHandler
from encypher.core.unicode_metadata import MetadataTarget
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, Any
import time
import json

class EnhancedStreamingHandler(StreamingHandler):
    """Enhanced streaming handler with additional features."""

    def __init__(self, metadata=None, private_key=None, target=MetadataTarget.WHITESPACE,
                 chunk_threshold=100, log_chunks=False):
        # Generate a key pair if not provided
        if private_key is None:
            private_key, public_key = generate_key_pair()

        # Ensure metadata has a key_id
        if metadata is None:
            metadata = {}

        if "key_id" not in metadata:
            metadata["key_id"] = "enhanced-stream-key"

        super().__init__(metadata=metadata, private_key=private_key, target=target)
        self.chunk_threshold = chunk_threshold
        self.log_chunks = log_chunks
        self.chunks_processed = 0
        self.total_length = 0

        # Store public key for verification (in a real app, use a secure store)
        self.public_key = public_key
        self.public_keys = {metadata["key_id"]: self.public_key}

    def resolve_public_key(self, key_id: str) -> Optional[PublicKeyTypes]:
        """Resolve a public key by its ID."""
        return self.public_keys.get(key_id)

    def process_chunk(self, chunk):
        """Process a chunk with enhanced logging and analytics."""
        self.chunks_processed += 1
        self.total_length += len(chunk)

        if self.log_chunks:
            print(f"Processing chunk {self.chunks_processed}: {len(chunk)} chars")

        # Add dynamic metadata if needed
        if self.metadata and "chunks_processed" not in self.metadata:
            self.metadata["chunks_processed"] = 0

        if self.metadata:
            self.metadata["chunks_processed"] = self.chunks_processed

        # Use standard processing
        processed_chunk = super().process_chunk(chunk)

        # Apply special handling for large chunks
        if len(chunk) > self.chunk_threshold and self.chunks_processed > 1:
            # For large chunks after the first, we might want special handling
            # This is just an example - you could implement custom logic here
            pass

        return processed_chunk

    def finalize(self):
        """Finalize the stream with enhanced metadata."""
        if self.metadata:
            self.metadata["total_chunks"] = self.chunks_processed
            self.metadata["total_length"] = self.total_length
            self.metadata["finalized_at"] = int(time.time())

        return super().finalize()

# Example usage
metadata = {
    "model": "streaming-demo",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),
    "version": "2.3.0",
    "key_id": "enhanced-stream-example"  # Required for verification
}

# Generate a key pair for this example
private_key, public_key = generate_key_pair()

handler = EnhancedStreamingHandler(
    metadata=metadata,
    private_key=private_key,
    log_chunks=True,
    chunk_threshold=50
)

# Simulate streaming
chunks = [
    "The quick ",
    "brown fox jumps ",
    "over the lazy dog. ",
    "This is an example of streaming text with embedded metadata."
]

full_text = ""
for chunk in chunks:
    processed = handler.process_chunk(chunk)
    if processed:  # May be None if buffering
        full_text += processed
        print(f"Accumulated text: {full_text}")

# Finalize
final_chunk = handler.finalize()
if final_chunk:
    full_text += final_chunk

print(f"Final text: {full_text}")

# Extract metadata without verification
from encypher.core.unicode_metadata import UnicodeMetadata
extracted = UnicodeMetadata.extract_metadata(full_text)
print(f"Extracted metadata (unverified): {json.dumps(extracted, indent=2)}")

# Verify the metadata
is_valid, signer_id, verified_payload_dict = UnicodeMetadata.verify_metadata(
    text=full_text,
    public_key_provider=handler.resolve_public_key
)

if is_valid and verified_payload_dict:
    print(f"Signer ID: {signer_id}")
    print(f"Verified metadata: {json.dumps(verified_payload_dict, indent=2)}")

## Custom Verification Logic

You can implement custom verification logic for specific use cases:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict, Any
import time

def verify_content_with_custom_logic(text, resolver, expected_organization=None, max_age_hours=24):
    """
    Verify content with custom logic beyond the standard verification.

    Args:
        text: Text with embedded metadata to verify
        resolver: Function to resolve public keys by key_id
        expected_organization: If set, verify the organization matches
        max_age_hours: Maximum age of content in hours

    Returns:
        dict: Verification results with detailed information
    """
    # Standard digital signature verification
    is_valid, signer_id, verified_payload_dict = UnicodeMetadata.verify_metadata(
        text=text,
        public_key_provider=resolver
    )

    # Initialize results
    results = {
        "signature_verified": is_valid,
        "signer_id": signer_id,
        "metadata_present": bool(verified_payload_dict),
        "custom_checks": {},
        "payload": verified_payload_dict
    }

    # If metadata is present and verified, perform custom checks
    if is_valid and verified_payload_dict:
        # Check organization if specified
        if expected_organization:
            org_match = verified_payload_dict.get("organization") == expected_organization
            results["custom_checks"]["organization_match"] = org_match

        # Check age if timestamp is present
        if "timestamp" in verified_payload_dict:
            try:
                # Get timestamp as int
                timestamp_data = verified_payload_dict.get("timestamp")
                timestamp = timestamp_data
                if isinstance(timestamp_data, str) and timestamp_data.isdigit():
                    timestamp = int(timestamp_data)
                elif not isinstance(timestamp_data, (int, float)):
                    # Attempt to parse if it's an ISO string, etc.
                    # For this example, we'll assume it's already a Unix timestamp or parsable int string
                    raise ValueError("Timestamp format not directly usable as int/float.")
                content_age_seconds = time.time() - timestamp
                age_match = content_age_seconds <= (max_age_hours * 3600)
                results["custom_checks"]["age_match"] = age_match
            except (ValueError, TypeError) as e:
                results["custom_checks"]["age_match"] = False
                results["custom_checks"]["age_error"] = str(e)

    # Overall verification result
    results["verified"] = (
        is_valid and
        bool(verified_payload_dict) and
        all(val for key, val in results["custom_checks"].items() if not key.endswith('_error')) # Check only boolean custom checks
    )

    return results

# Example usage
# Generate a key pair
private_key, public_key = generate_key_pair()
key_id = "verification-example-key"

# Create a resolver function
public_keys = {key_id: public_key}
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys.get(key_id)

text = "This is a sample text for verification."
metadata = {
    "model": "gpt-4",
    "organization": "EncypherAI",
    "timestamp": int(time.time()),
    "version": "2.3.0",
    "key_id": key_id  # Required for verification
}

# Embed metadata with digital signature
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    custom_metadata=metadata,
    private_key=private_key,
    signer_id=key_id,
    timestamp=metadata.get("timestamp")
)

# Verify with custom logic
verification_results = verify_content_with_custom_logic(
    encoded_text,
    resolver=resolve_public_key,
    expected_organization="EncypherAI",
    max_age_hours=48
)

print(f"Verification results: {json.dumps(verification_results, indent=2)}")

These advanced examples demonstrate how to extend and customize EncypherAI's functionality for various use cases using digital signatures for enhanced security and verification.
