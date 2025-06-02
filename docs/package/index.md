# EncypherAI

<div align="center">
  <img src="../../assets/horizontal-logo.png" alt="EncypherAI Logo" width="600"/>
  <h2>Invisible Metadata for AI-Generated Text</h2>
</div>

## Overview

EncypherAI is an open-source Python package that enables invisible metadata embedding in AI-generated text using zero-width characters.

With EncypherAI, you can:

- **Embed invisible metadata** in AI-generated text without altering its visible appearance
- **Verify content authenticity** using digital signatures
- **Detect tampering** of AI-generated content
- **Support streaming** responses from LLM providers
- **Track provenance** of AI-generated content

## Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Invisible Embedding** | Add metadata without changing visible content |
| 🔐 **Digital Signature Verification** | Ensure data integrity, authenticity, and detect tampering |
| 🌊 **Streaming Support** | Compatible with chunk-by-chunk streaming |
| 🔄 **Extensible API** | Easily integrate with any LLM provider |

## Quick Links

- [Installation](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [Examples Overview](examples/index.md)
- [V2.0 Demo Notebook](examples/encypher_v2_demo.ipynb)
- [Migration Guide](user-guide/migration-guide.md)
- [GitHub Repository](https://github.com/encypherai/encypher-ai)

## Why EncypherAI?

As AI-generated content becomes more prevalent, establishing provenance and ensuring integrity becomes critical. EncypherAI addresses these needs by providing a simple way to invisibly embed metadata that can later be verified.

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional, Dict
import time

# Generate key pair for digital signature
private_key, public_key = generate_key_pair()
key_id = "example-key-1"

# Store public keys (in a real system, this would be a secure database)
public_keys_store = {key_id: public_key}

# Create a resolver function to look up public keys by ID
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)

# Embed metadata in AI-generated text
metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "organization": "EncypherAI",
    "key_id": key_id  # Required for verification
}
text = "This is AI-generated content with invisible metadata."
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    metadata=metadata,
    private_key=private_key
)

# Later, verify and extract metadata
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"Verified metadata: {verified_metadata}")
```

## License

EncypherAI is released under the GNU Affero General Public License v3.0 (AGPL-3.0).
