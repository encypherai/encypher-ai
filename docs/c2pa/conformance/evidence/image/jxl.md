# C2PA Evidence: image/jxl (JPEG XL)

**Format**: JPEG XL (ISO 18181)
**MIME Type**: image/jxl
**Category**: Image
**Pipeline**: Custom JUMBF/COSE (ISOBMFF container embedder)
**Status**: PASS (structural verification)

## Embedding Approach

JPEG XL has two container variants:
- **Bare codestream**: starts with `ff 0a` -- no box structure, cannot embed C2PA
- **ISOBMFF container**: starts with `00 00 00 0c 4a 58 4c 20 0d 0a 87 0a` -- standard ISOBMFF box structure

Encypher signs the ISOBMFF container variant using a custom embedder that:
1. Parses top-level ISOBMFF boxes (JXL signature, ftyp, jxlc/jxlp)
2. Appends a `c2pa` box at the end with a zero-filled placeholder
3. Computes SHA-256 hash with byte-range exclusion for the manifest data
4. Builds JUMBF manifest store (assertions + CBOR claim + COSE_Sign1 signature)
5. Replaces placeholder with actual signed manifest via in-place byte patching

The `c2pa` box is a standard ISOBMFF box (4CC type `c2pa`) per the C2PA spec's
BMFF embedding convention.

### Why c2pa.hash.data (not c2pa.hash.bmff.v3)?

The custom embedder uses `c2pa.hash.data` with explicit byte-range exclusion rather
than `c2pa.hash.bmff.v3`. This is spec-compliant (c2pa.hash.data is allowed for any
format) and simpler to implement correctly. The c2pa.hash.bmff.v3 assertion requires
deep understanding of all ISOBMFF box types for selective hashing, which is unnecessary
for the integrity guarantee provided by a full-file hash with exclusion.

### Why not c2pa-rs?

c2pa-rs 0.78.4 (embedded in c2pa-python 0.29.0) does not implement JPEG XL manifest
embedding. c2pa-rs support for JXL is tracked upstream but not yet available. Encypher
built a custom embedder to provide JXL support ahead of c2pa-rs.

## Implementation

- Embedder: `enterprise_api/app/utils/jxl_c2pa_embedder.py`
- Signing: `enterprise_api/app/services/document_signing_service.py` (`sign_jxl()`)
- JUMBF builder: `enterprise_api/app/utils/jumbf.py`
- COSE signer: `enterprise_api/app/utils/cose_signer.py`
- Claim builder: `enterprise_api/app/utils/c2pa_claim_builder.py`

## Manifest Structure

```
JUMBF Manifest Store (c2pa)
  Manifest (urn:c2pa:<uuid>)
    Assertion Store (c2pa.assertions)
      c2pa.actions.v2 [CBOR]
      c2pa.hash.data [CBOR] -- byte-range exclusion hash
      com.encypher.provenance [CBOR]
    Claim (c2pa.claim.v2) [CBOR]
      dc:format = "image/jxl"
      claim_generator = "Encypher Enterprise API/2.0"
      assertions = [hashed references]
    Signature (c2pa.signature) [COSE_Sign1_Tagged]
      Algorithm: ES256 (ECC P-256)
      Certificate chain: x5chain
      Padding: 0x43504164 ("CPAd")
```

## Verification

Structural verification confirms:
1. ISOBMFF box structure valid (JXL signature + ftyp + jxlc + c2pa boxes)
2. c2pa box contains valid JUMBF manifest store
3. Manifest store parses correctly (assertions, claim, signature)
4. Claim dc:format matches "image/jxl"
5. COSE_Sign1 signature verifiable with certificate chain
6. Data hash re-computation matches stored hash (exclusion range integrity)

## Evidence Artifacts

- Fixture: `tests/c2pa_conformance/fixtures/test.jxl` (ISOBMFF container, 106 bytes)
- Signed: `tests/c2pa_conformance/signed/signed_test.jxl`
- Manifest JSON: `tests/c2pa_conformance/manifests/signed_test_jxl.json`

## Test Coverage

- `TestJxlEmbedder::test_parse_jxl_boxes` -- ISOBMFF box parsing
- `TestJxlEmbedder::test_parse_rejects_bare_codestream` -- bare codestream rejection
- `TestJxlEmbedder::test_create_placeholder` -- placeholder insertion
- `TestJxlEmbedder::test_replace_manifest` -- manifest replacement
- `TestJxlEmbedder::test_replace_manifest_too_large` -- overflow protection
- `TestJxlEmbedder::test_hash_excludes_manifest_range` -- exclusion hash integrity
- `TestJxlEmbedder::test_existing_c2pa_box_removed` -- idempotent embedding
- `TestJxlSigning::test_sign_jxl_roundtrip` -- full E2E signing + structural verification
- `TestJxlSigning::test_sign_jxl_via_dispatcher` -- MIME type routing

All 9 tests PASS.
