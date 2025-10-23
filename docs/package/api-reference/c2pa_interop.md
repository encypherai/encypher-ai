# C2PA Interoperability Module

The ``encypher.interop.c2pa`` package groups the helpers that make EncypherAI's
text pipeline interoperable with the Coalition for Content Provenance and
Authenticity (C2PA) specification. These utilities are shared between the core
``UnicodeMetadata`` implementation, integration tests, and third-party
integrations that want to reason about manifests at a lower level.

The module focuses on three areas:

1. Building and decoding the FEFF-prefixed ``C2PATextManifestWrapper`` that
   carries a complete C2PA manifest store inside a Unicode text asset.
2. Normalising text and calculating the SHA-256 content hash with the exact same
   procedure during embedding and verification.
3. Converting manifests between EncypherAI's convenience shape and the canonical
   C2PA structure when interoperability with external tooling is required.

## Text Wrapper Helpers

```python
from encypher.interop.c2pa import encode_wrapper, find_and_decode
```

### ``encode_wrapper(manifest_bytes: bytes) -> str``

- Packs the ``magic | version | manifestLength`` header defined by the
  ``C2PATextManifestWrapper`` proposal.
- Converts every byte of the header and manifest store into a Unicode variation
  selector (0–15 → ``U+FE00``–``U+FE0F``; 16–255 → ``U+E0100``–``U+E01EF``).
- Prefixes the selector block with ``U+FEFF`` and returns the resulting string so
  it can be appended to the visible text content.

### ``find_and_decode(text: str) -> Tuple[Optional[bytes], str, Optional[Tuple[int, int]]]``

- Scans ``text`` for a ``U+FEFF`` marker followed by a contiguous run of
  variation selectors.
- Verifies the ``C2PATXT\0`` magic value, version number, and manifest length
  before returning the decoded JUMBF bytes.
- Normalises the remaining text to NFC and returns both the clean string and the
  wrapper span (start/end indices) so callers can exclude the wrapper bytes when
  recomputing hashes.

These helpers are used internally by ``UnicodeMetadata`` to append the wrapper at
embedding time and to detect tampering during verification.

## Normalisation and Hashing Helpers

```python
from encypher.interop.c2pa import compute_normalized_hash, normalize_text
```

### ``normalize_text(text: str) -> str``

Returns the NFC-normalised form of ``text``. Normalisation occurs before any
byte offsets are calculated to guarantee that exclusion ranges match the C2PA
specification.

### ``compute_normalized_hash(text: str, exclusions: Sequence[Tuple[int, int]] | None = None, *, algorithm: str = "sha256")``

- Normalises ``text`` to NFC and encodes it as UTF-8 bytes.
- Removes the byte ranges specified by ``exclusions`` (each expressed as
  ``(start, length)`` offsets into the normalised byte array).
- Computes a SHA-256 digest of the filtered bytes and returns a
  ``NormalizedHashResult`` object containing the normalised text, raw bytes, and
  digest.

Embedding and verification both call this helper so that the hash recorded in
``c2pa.hash.data.v1`` matches the value recomputed by validators.

## Manifest Conversion Helpers

```python
from encypher.interop.c2pa import (
    c2pa_like_dict_to_encypher_manifest,
    encypher_manifest_to_c2pa_like_dict,
    get_c2pa_manifest_schema,
)
```

These functions convert between the convenience dictionaries exposed by the
EncypherAI SDK and schema-compliant C2PA manifests. They are useful when you need
full control over the actions and assertions that will be embedded inside the
text manifest store.

## End-to-End Example

The snippet below demonstrates how the helpers combine with
``UnicodeMetadata`` to embed a manifest and verify it later.

```python
from datetime import datetime
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import compute_normalized_hash

# Prepare signer credentials
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-signer"

text = "Breaking news: invisible provenance ships today."

# Embed a C2PA manifest – the wrapper is appended as FEFF + variation selectors.
embedded = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    actions=[{"label": "c2pa.created", "when": datetime.now().isoformat()}],
)
assert embedded.startswith(text)
assert embedded != text  # invisible wrapper appended

# Copy/paste operations preserve the wrapper, so validators can recover it.
def resolver(requested_signer_id: str):
    return public_key if requested_signer_id == signer_id else None

verified, recovered_signer, manifest = UnicodeMetadata.verify_metadata(
    text=embedded,
    public_key_resolver=resolver,
)
assert verified and recovered_signer == signer_id

# The manifest records a hard-binding hash computed with the shared helper.
content_hash_assertion = next(
    assertion
    for assertion in manifest["assertions"]
    if assertion["label"] == "c2pa.hash.data.v1"
)
exclusions = [
    (item["start"], item["length"])
    for item in content_hash_assertion["data"].get("exclusions", [])
]
hash_result = compute_normalized_hash(embedded, exclusions)
print(hash_result.hexdigest)
```

During verification the library:

1. Calls ``find_and_decode`` to locate the FEFF-prefixed wrapper and recover the
   JUMBF manifest store.
2. Verifies the COSE ``Sign1`` signature and actions.
3. Uses ``compute_normalized_hash`` with the recorded exclusions to recompute the
   hard-binding digest.

Any mismatch in the wrapper structure, manifest signature, or content hash causes
verification to fail, surfacing provenance tampering to downstream consumers.
