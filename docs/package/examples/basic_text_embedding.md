# Basic Text Embedding Tutorial

This tutorial provides a step-by-step guide for embedding C2PA-compliant provenance metadata into text content using EncypherAI's Unicode variation selector approach.

## Prerequisites

Before starting, ensure you have:

- EncypherAI Python package installed (`uv add encypher-ai`)
- Basic understanding of Python programming
- Familiarity with content provenance concepts

## Step 1: Set Up Your Environment

First, import the necessary modules:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair, load_ed25519_key_pair
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest
import hashlib
import json
from datetime import datetime
import os
```

### Embedding without a timestamp (optional)

If you prefer not to include a timestamp, remove it from the manifest and do not pass it to `embed_metadata()`:

```python
# Create a C2PA manifest WITHOUT a timestamp
c2pa_manifest_no_time = {
    "claim_generator": "EncypherAI/2.3.0",
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org/",
                "@type": "CreativeWork",
                "headline": "Sample Article Title",
                "author": {"@type": "Person", "name": "John Doe"},
                "publisher": {"@type": "Organization", "name": "Example Publisher"},
                "description": "A sample article demonstrating text embedding without a timestamp"
            }
        }
    ]
}

# Convert to EncypherAI format
encypher_manifest_no_time = c2pa_like_dict_to_encypher_manifest(c2pa_manifest_no_time)

# Embed without passing a timestamp (it will be omitted in the payload)
embedded_paragraph_no_time = UnicodeMetadata.embed_metadata(
    text=first_paragraph,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format='cbor_manifest',
    claim_generator=encypher_manifest_no_time.get("claim_generator"),
    actions=encypher_manifest_no_time.get("assertions")
)
```

## Step 2: Generate or Load Keys

You'll need a key pair for signing the metadata. You can either generate a new pair or load an existing one:

```python
# Option 1: Generate a new key pair
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-001"

# Save keys for future use
keys_dict = {
    "private_key": private_key.hex(),
    "public_key": public_key.hex(),
    "signer_id": signer_id
}

with open("keys.json", "w") as f:
    json.dump(keys_dict, f)

# Option 2: Load existing keys
if os.path.exists("keys.json"):
    with open("keys.json", "r") as f:
        keys_dict = json.load(f)

    private_key = bytes.fromhex(keys_dict["private_key"])
    public_key = bytes.fromhex(keys_dict["public_key"])
    signer_id = keys_dict["signer_id"]
```

## Step 3: Prepare Your Text Content

Define the text content you want to embed metadata into:

```python
# Full article text
article_text = """# Sample Article Title

This is the first paragraph of the sample article. This paragraph will contain
the embedded metadata using Unicode variation selectors.

This is the second paragraph with additional content. The content hash will
cover all paragraphs in the article, ensuring the integrity of the entire text.

## Subsection

This is a subsection with more content. The embedding process will not affect
the visual appearance of the text, even though the metadata is embedded directly
within it.
"""

# For demonstration, we'll embed metadata into the first paragraph
first_paragraph = article_text.split("\n\n")[1]
```

## Step 4: Calculate Content Hash

Calculate a hash of the full content to enable tamper detection:

```python
# Calculate content hash (using plain text without formatting)
plain_text = "\n".join([line.strip() for line in article_text.split("\n")])
content_hash = hashlib.sha256(plain_text.encode("utf-8")).hexdigest()
```

## Step 5: Create C2PA Manifest

Create a C2PA-compliant manifest with relevant assertions:

```python
# Current timestamp
timestamp = datetime.now().isoformat()

# Create C2PA manifest
c2pa_manifest = {
    "claim_generator": "EncypherAI/2.3.0",
    "timestamp": timestamp,
    "assertions": [
        {
            "label": "stds.schema-org.CreativeWork",
            "data": {
                "@context": "https://schema.org/",
                "@type": "CreativeWork",
                "headline": "Sample Article Title",
                "author": {"@type": "Person", "name": "John Doe"},
                "publisher": {"@type": "Organization", "name": "Example Publisher"},
                "datePublished": timestamp.split("T")[0],
                "description": "A sample article demonstrating text embedding"
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
```

> Note: Timestamp optional
>
> - The `timestamp` is optional across all metadata formats, including C2PA.
> - When omitted, C2PA action assertions (e.g., `c2pa.created`, `c2pa.watermarked`) will simply omit their `when` fields.
> - You can provide a timestamp (recommended) or skip it depending on your needs.

## Step 6: Embed Metadata into Text

Embed the manifest into the first paragraph of your text:

```python
# Embed metadata into the first paragraph
embedded_paragraph = UnicodeMetadata.embed_metadata(
    text=first_paragraph,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format='cbor_manifest',
    claim_generator=encypher_manifest.get("claim_generator"),
    actions=encypher_manifest.get("assertions"),
    timestamp=encypher_manifest.get("timestamp")
)

# Replace the first paragraph in the article
embedded_article = article_text.replace(first_paragraph, embedded_paragraph)

# Save the embedded article
with open("embedded_article.txt", "w", encoding="utf-8") as f:
    f.write(embedded_article)
```

## Step 7: Verify and Extract Metadata

To verify the embedded metadata and check for tampering:

```python
# Define a key provider function
def key_provider(kid):
    if kid == signer_id:
        return public_key
    return None

# Extract the first paragraph (which contains the embedded metadata)
embedded_first_paragraph = embedded_article.split("\n\n")[1]

# Verify and extract metadata
is_verified, extracted_signer_id, extracted_manifest = UnicodeMetadata.verify_and_extract_metadata(
    text=embedded_first_paragraph,
    public_key_provider=key_provider
)

if is_verified:
    print(f"✓ Signature verification successful!")
    print(f"✓ Signer ID: {extracted_signer_id}")

    # Check for content tampering
    current_content_hash = hashlib.sha256(plain_text.encode("utf-8")).hexdigest()

    # Find content hash assertion
    stored_hash = None
    for assertion in extracted_manifest.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break

    if stored_hash == current_content_hash:
        print("✓ Content hash verification successful!")
    else:
        print("✗ Content hash verification failed - content may have been tampered with.")
        print(f"  Stored hash: {stored_hash}")
        print(f"  Current hash: {current_content_hash}")
else:
    print("✗ Signature verification failed!")
```

## Step 8: Simulate Tampering (Optional)

To demonstrate tamper detection, you can modify the content and verify again:

```python
# Simulate content tampering
tampered_article = embedded_article.replace("sample article", "modified article")

# Calculate new content hash
tampered_plain_text = "\n".join([line.strip() for line in tampered_article.split("\n")])
tampered_content_hash = hashlib.sha256(tampered_plain_text.encode("utf-8")).hexdigest()

# Extract the first paragraph (which contains the embedded metadata)
tampered_first_paragraph = tampered_article.split("\n\n")[1]

# Verify and extract metadata
is_verified, extracted_signer_id, extracted_manifest = UnicodeMetadata.verify_and_extract_metadata(
    text=tampered_first_paragraph,
    public_key_provider=key_provider
)

if is_verified:
    print("\nTampered Content Test:")
    print(f"✓ Signature verification successful!")

    # Find content hash assertion
    stored_hash = None
    for assertion in extracted_manifest.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break

    if stored_hash == tampered_content_hash:
        print("✓ Content hash verification successful (unexpected!)")
    else:
        print("✓ Content hash verification failed - tampering detected!")
        print(f"  Stored hash: {stored_hash}")
        print(f"  Current hash: {tampered_content_hash}")
else:
    print("\nTampered Content Test:")
    print("✗ Signature verification failed!")
```

## Complete Example

Here's the complete code for the basic text embedding workflow:

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest
import hashlib
from datetime import datetime

# 1. Generate keys
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-001"

# 2. Prepare article text
article_text = """# Sample Article Title

This is the first paragraph of the sample article. This paragraph will contain
the embedded metadata using Unicode variation selectors.

This is the second paragraph with additional content. The content hash will
cover all paragraphs in the article, ensuring the integrity of the entire text.

## Subsection

This is a subsection with more content. The embedding process will not affect
the visual appearance of the text, even though the metadata is embedded directly
within it.
"""

# Extract first paragraph for embedding
first_paragraph = article_text.split("\n\n")[1]

# 3. Calculate content hash
plain_text = "\n".join([line.strip() for line in article_text.split("\n")])
content_hash = hashlib.sha256(plain_text.encode("utf-8")).hexdigest()

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
                "headline": "Sample Article Title",
                "author": {"@type": "Person", "name": "John Doe"},
                "publisher": {"@type": "Organization", "name": "Example Publisher"},
                "datePublished": datetime.now().date().isoformat(),
                "description": "A sample article demonstrating text embedding"
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

# 6. Embed into first paragraph
embedded_paragraph = UnicodeMetadata.embed_metadata(
    text=first_paragraph,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format='cbor_manifest',
    claim_generator=encypher_manifest.get("claim_generator"),
    actions=encypher_manifest.get("assertions"),
    timestamp=encypher_manifest.get("timestamp")
)

# 7. Replace first paragraph in article
embedded_article = article_text.replace(first_paragraph, embedded_paragraph)

# 8. Save the embedded article
with open("embedded_article.txt", "w", encoding="utf-8") as f:
    f.write(embedded_article)

# 9. Define key provider function
def key_provider(kid):
    if kid == signer_id:
        return public_key
    return None

# 10. Extract first paragraph (which contains the embedded metadata)
embedded_first_paragraph = embedded_article.split("\n\n")[1]

# 11. Verify and extract metadata
is_verified, extracted_signer_id, extracted_manifest = UnicodeMetadata.verify_and_extract_metadata(
    text=embedded_first_paragraph,
    public_key_provider=key_provider
)

# 12. Check verification results
if is_verified:
    print(f"✓ Signature verification successful!")
    print(f"✓ Signer ID: {extracted_signer_id}")

    # Check for content tampering
    current_content_hash = hashlib.sha256(plain_text.encode("utf-8")).hexdigest()

    # Find content hash assertion
    stored_hash = None
    for assertion in extracted_manifest.get("assertions", []):
        if assertion.get("label") == "stds.c2pa.content.hash":
            stored_hash = assertion["data"]["hash"]
            break

    if stored_hash == current_content_hash:
        print("✓ Content hash verification successful!")
    else:
        print("✗ Content hash verification failed - content may have been tampered with.")
else:
    print("✗ Signature verification failed!")
```

## Output Example

When running the verification code on an untampered article, you should see:

```
✓ Signature verification successful!
✓ Signer ID: example-key-001
✓ Content hash verification successful!
```

If the content has been tampered with, you'll see:

```
✓ Signature verification successful!
✓ Signer ID: example-key-001
✗ Content hash verification failed - content may have been tampered with.
  Stored hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  Current hash: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0
```

## Next Steps

Now that you've learned the basics of text embedding with EncypherAI, you can:

1. Integrate this workflow into your content management system
2. Explore more complex C2PA assertions for richer provenance information
3. Implement a user-friendly verification interface
4. Check out the advanced C2PA text demo for HTML integration examples
