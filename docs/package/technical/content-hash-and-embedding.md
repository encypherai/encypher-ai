# Content Hash Coverage and Embedding Technical Details

This document explains how Encypher embeds Coalition for Content Provenance and Authenticity (C2PA) manifests inside plain
text while respecting the updated `C2PATextManifestWrapper` specification. It focuses on two critical implementation details:

Specification reference:
https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text

Reference implementation (MIT):
https://github.com/encypherai/c2pa-text

1. **How we compute and record the hard-binding content hash**
2. **How the manifest store is wrapped, encoded as Unicode variation selectors, and appended to the text**

The goal is to make the manifest portable with the text itself—copy and paste operations keep the provenance intact—while
remaining fully compatible with the C2PA validation model.

## Content Hash Normalisation and Exclusions

C2PA requires producers and consumers to normalise text to Unicode Normalisation Form C (NFC) before hashing. To guarantee that
every code path performs the exact same sequence of operations we rely on the shared helper `compute_normalized_hash()` from
`encypher.interop.c2pa.text_hashing`.

Our embedding pipeline follows these rules:

1. **Normalise and hash via the helper**: `compute_normalized_hash(original_text)` returns the NFC-normalised string,
   its UTF-8 bytes, and the SHA-256 digest used for the `c2pa.hash.data.v1` assertion.
2. **Append the wrapper** (described later) to the end of the original text. The wrapper occupies a contiguous range of bytes
   that do not belong to the visible content.
3. **Record exclusion offsets** for the wrapper. Offsets are expressed as byte positions within the NFC-normalised text, using
   the structure `{"start": <byte_offset>, "length": <byte_count>}`. This exclusion list is stored in the `c2pa.hash.data.v1`
   assertion so that validators know which bytes to ignore before hashing.

During verification we repeat the same procedure:

- Detect the wrapper span and pass the full text plus the exclusion tuple to `compute_normalized_hash()`.
- Apply the exclusion offsets from the manifest and ensure they match the detected wrapper span.
- Compare the calculated hash against the manifest assertion. Any mismatch triggers tamper detection.

This guarantees that copy/paste operations (which keep the wrapper) and validators (which must remove it before hashing) remain
synchronised.

## `C2PATextManifestWrapper` Layout

All manifests embedded in unstructured text conform to the binary layout mandated by the specification:

```text
aligned(8) class C2PATextManifestWrapper {
    unsigned int(64) magic = 0x4332504154585400;  // "C2PATXT\0"
    unsigned int(8)  version = 1;
    unsigned int(32) manifestLength;
    unsigned int(8)  jumbfContainer[manifestLength];
}
```

Key points:

- The wrapper is **prefixed with a single U+FEFF** (Zero-Width No-Break Space). This marker makes it easy for validators to
  locate the wrapper even if other variation selectors appear in the text for unrelated reasons.
- `manifestLength` records the size of the embedded C2PA manifest store.
- `jumbfContainer` carries the manifest store encoded as a JUMBF box. We serialise the store with canonical JSON ordering to
  obtain deterministic bytes before signing.

## Variation Selector Encoding

Every byte of the header and manifest store is converted to an invisible Unicode variation selector so that the wrapper travels
with the text:

- Bytes 0–15 map to `U+FE00`–`U+FE0F`.
- Bytes 16–255 map to `U+E0100`–`U+E01EF`.

Decoding performs the inverse mapping and rejects any code points outside these ranges, ensuring corrupted wrappers are detected.

## Embedding Workflow

The high-level embedding steps executed by `UnicodeMetadata._embed_c2pa` are:

1. **Build the manifest**: Construct the C2PA manifest with mandatory assertions (actions, optional AI metadata, etc.). If a
   hard binding is requested we insert a `c2pa.hash.data.v1` assertion whose `exclusions` list initially matches the last
   computed offsets.
2. **Sign the manifest**: Serialise the manifest to CBOR, produce a COSE `Sign1` structure with the Ed25519 private key, and
   package the result inside a minimal JUMBF box.
3. **Encode the wrapper**: Pack the `magic`, `version`, and `manifestLength` fields with the JUMBF bytes, convert them to
   variation selectors, and prefix the block with U+FEFF.
4. **Append the block**: Place the wrapper after the visible text as a single contiguous run. The plain text itself is not
   otherwise modified; the wrapper is the only addition.
5. **Stabilise exclusion offsets**: Because the wrapper length depends on the manifest, we recompute the exclusion list until it
   stabilises (usually immediately). The final manifest is re-signed once the offsets are correct.

The resulting string looks like `visible_text + "\uFEFF" + <variation selectors>`. When rendered, the wrapper is invisible but it
remains part of the Unicode stream.

### Example

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair

text = "Provenance-enabled article"
private_key, _ = generate_ed25519_key_pair()
wrapper_ready_text = UnicodeMetadata.embed_metadata(
    text=text,
    private_key=private_key,
    signer_id="demo-signer",
    metadata_format="c2pa",
)
assert wrapper_ready_text.endswith("\ufeff") is False  # The FEFF is followed by variation selectors
```

## Extraction and Verification Workflow

Validators follow the inverse process:

1. **Locate the wrapper** by scanning for U+FEFF followed by a contiguous run of variation selectors.
2. **Decode the header**, verify the `C2PATXT\0` magic value, check the version, and ensure the manifest length matches the
   decoded byte count.
3. **Recover the JUMBF manifest store** and feed it into the COSE verification flow.
4. **Normalise and hash the visible text**, excluding the byte range recorded in the manifest, and compare the digest against the
   stored `c2pa.hash.data.v1` assertion.

If multiple wrappers appear the verifier rejects the content with the `manifest.text.multipleWrappers` failure code. If decoding
fails part-way through the block we emit `manifest.text.corruptedWrapper`.

## Advantages of the Updated Flow

- **Specification alignment**: The wrapper structure, FEFF prefix, and exclusion handling match the C2PA v2.3 text
  embedding specification (Appendix A.7).
- **Copy/paste resilience**: The wrapper stays attached to the text while remaining invisible to readers.
- **Deterministic hashing**: NFC normalisation and explicit exclusion offsets guarantee that hard-binding hashes are stable
  across producers and consumers.
- **Interoperability**: By serialising a complete manifest store in JUMBF we are compatible with the broader C2PA ecosystem.
