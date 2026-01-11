> **Note:** Legacy embedding targets (``whitespace``, ``punctuation`` and similar)
> remain available for the ``basic``, ``manifest``, and ``cbor_manifest`` formats.
> When ``metadata_format="c2pa"`` the library automatically appends a
> FEFF-prefixed ``C2PATextManifestWrapper`` to the end of the visible text so the
> manifest stays contiguous, satisfying the latest specification.

# Advanced C2PA Text Demo

This guide provides a walkthrough of a C2PA text demo workflow using the example scripts that ship with `encypher-ai`.

Related links:

- Wrapper reference implementation (MIT): https://github.com/encypherai/c2pa-text
- Encypher Enterprise API: https://encypherai.com

## Demo Overview

The C2PA text demo demonstrates:

1. Embedding C2PA manifests into text
2. Verifying embedded metadata and content integrity
3. Simulating and detecting tampering scenarios

## Setup Instructions

Before running the demo, install the project and its development extras:

```bash
uv sync --all-extras
```

Then, generate a keypair using the included helper:

```bash
uv run python -m encypher.examples.generate_keys
```

## Demo Components

### Key Files

The repository includes runnable examples under `encypher/examples/`:

- `encypher/examples/c2pa_text_embedding_demo.py`: C2PA-like manifest conversion + embedding + verification.
- `encypher/examples/generate_keys.py`: Helper script for generating Ed25519 keys.

### Embedding Process

Embedding with `metadata_format="c2pa"` always appends a FEFF-prefixed C2PA text wrapper at the end of the visible text.

```python
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from encypher import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair

private_key, public_key = generate_ed25519_key_pair()
signer_id = "c2pa-demo-signer-001"

def public_key_resolver(kid: str) -> Optional[Ed25519PublicKey]:
    if kid == signer_id:
        return public_key
    return None

text = "This text will receive a C2PA-compliant wrapper."
encoded_text = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    claim_generator="encypher-ai/demo",
    actions=[{"label": "c2pa.created", "when": datetime.now(timezone.utc).isoformat()}],
)

is_valid, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=public_key_resolver,
)
print(is_valid, extracted_signer_id)
print(payload)
```

### Content Hash Calculation

``UnicodeMetadata`` normalises the paragraph, appends the wrapper, and records the
wrapper's byte span in the ``c2pa.hash.data.v1`` assertion automatically. If you
need to pre-compute the digest for auditing or logging, use the shared helper:

```python
from encypher.interop.c2pa import compute_normalized_hash

hash_result = compute_normalized_hash(text)
print("Pre-embed NFC hash:", hash_result.hexdigest)
```

After embedding you can reproduce the recorded digest by removing the wrapper
bytes from the normalised text and re-running ``compute_normalized_hash`` (see
the basic tutorial for a standalone example).

### UI Integration

If you want a UI for verification, build it as a thin wrapper around:

- `UnicodeMetadata.verify_metadata(text=..., public_key_resolver=..., require_hard_binding=...)`

and render the returned `payload` and `signer_id`.

### Tamper Detection

To test tamper detection, modify either:

1. The visible text content (content tampering). With `metadata_format="c2pa"`, signature verification can still pass, but the hard binding assertion (`c2pa.hash.data.v1`) will fail.
2. The embedded wrapper bytes / manifest (metadata tampering). This causes signature verification to fail.

## Running the Demo

Run the included C2PA embedding demo:

```bash
uv run python -m encypher.examples.c2pa_text_embedding_demo
```

## Customization Options

### Embedding Location

C2PA manifests always append a FEFF-prefixed wrapper to the end of the text.
The ``target`` parameter is ignored for ``metadata_format="c2pa"`` because the
specification requires the wrapper to remain contiguous.

### Manifest Content

Customise the manifest by adjusting the ``claim_generator`` string, providing
pre-existing action entries, or toggling ``add_hard_binding``. The library
constructs the remaining assertions automatically.

```python
custom_actions = [
    {
        "label": "c2pa.created",
        "softwareAgent": "YourApp/1.0.0",
        "when": datetime.now().isoformat(),
    },
    {
        "label": "c2pa.captured",
        "softwareAgent": "YourApp/1.0.0",
        "description": "Article prepared with Encypher",
    },
]

embedded_text = UnicodeMetadata.embed_metadata(
    text=first_p.get_text(),
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    claim_generator="YourApp/1.0.0",
    actions=custom_actions,
    add_hard_binding=True,
)
```

### UI Customization

To customize a verification UI, render the decoded manifest assertions and verification status.

## Conclusion

The C2PA text demo showcases a complete implementation of text provenance using Encypher's Unicode variation selector approach. It demonstrates:

1. How to embed C2PA manifests into HTML articles
2. How to verify embedded metadata and detect tampering
3. How to create a user-friendly verification UI

This implementation provides a robust foundation for adding provenance to text content in real-world applications.
