# Basic Text Embedding Tutorial

This tutorial walks through the minimal steps required to embed a C2PA manifest
into plain text with Encypher. The workflow follows the C2PA v2.3
``C2PATextManifestWrapper`` specification: the manifest is encoded as a JUMBF
container, converted to Unicode variation selectors, and appended to the end of
the text after a ``U+FEFF`` marker. The visible content never changes, but copy
and paste operations retain the provenance wrapper.

## Prerequisites

Before starting, ensure you have:

- The Encypher Python package installed (``uv add encypher-ai``)
- An understanding of Python basics and Ed25519 keys

```python
from datetime import datetime
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import compute_normalized_hash
```

## Step 1: Generate a Signing Key

```python
private_key, public_key = generate_ed25519_key_pair()
signer_id = "example-key-001"
```

The private key signs the manifest. The public key is used later to verify the
embedded metadata.

## Step 2: Prepare the Text Content

```python
text = "Encypher now emits FEFF-prefixed text manifests."
```

## Step 3: Embed the C2PA Manifest

```python
embedded_text = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    add_hard_binding=True,
    actions=[{"label": "c2pa.created", "when": datetime.now().isoformat()}],
)
```

What happens under the hood:

1. ``UnicodeMetadata`` constructs a C2PA manifest with ``c2pa.actions.v1``,
   ``c2pa.soft_binding.v1``, and ``c2pa.hash.data.v1`` assertions.
2. The manifest is serialised to CBOR, wrapped in a COSE ``Sign1`` signature, and
   packaged as a compact JUMBF container.
3. ``encode_wrapper`` converts the header + manifest bytes into variation selectors
   and returns ``"\ufeff" + <selectors>``.
4. The wrapper is appended to the original text so the output renders identically
   to the input.

You can confirm that the wrapper exists without being visible:

```python
assert embedded_text.startswith(text)
assert embedded_text[len(text)] == "\ufeff"
print(len(embedded_text) - len(text), "additional code points appended")
```

## Step 4: Inspect the Hard-Binding Hash

The ``c2pa.hash.data.v1`` assertion records an SHA-256 digest of the NFC
normalised text with the wrapper bytes excluded. You can reproduce it with the
shared helper:

```python
from encypher.interop.c2pa import find_and_decode, normalize_text

manifest_bytes, _, span = find_and_decode(embedded_text)
assert manifest_bytes and span is not None

wrapper_segment = embedded_text[span[0] : span[1]]
normalized_full = normalize_text(embedded_text)
normalized_index = normalized_full.rfind(wrapper_segment)
assert normalized_index >= 0

# Remove the wrapper span from the normalised text when hashing
exclusion_start = len(normalized_full[:normalized_index].encode("utf-8"))
exclusion_length = len(wrapper_segment.encode("utf-8"))

hash_result = compute_normalized_hash(
    embedded_text,
    exclusions=[(exclusion_start, exclusion_length)],
)
print("NFC hash:", hash_result.hexdigest)
```

## Step 5: Verify the Embedded Manifest

```python
def resolver(requested_signer_id: str):
    return public_key if requested_signer_id == signer_id else None

verified, recovered_signer, manifest = UnicodeMetadata.verify_metadata(
    text=embedded_text,
    public_key_resolver=resolver,
)
assert verified and recovered_signer == signer_id
```

Verification automatically:

1. Locates the FEFF-prefixed wrapper via ``find_and_decode``.
2. Validates the COSE ``Sign1`` signature and actions.
3. Recomputes the hard-binding hash with ``compute_normalized_hash`` and the
   recorded exclusion offsets.

## Step 6: Share the Provenance-Enabled Text

The string in ``embedded_text`` can be copied into documents, chat systems, or
CMS platforms. The invisible wrapper survives round-trips, allowing downstream
consumers to authenticate the text without requiring sidecar files.
