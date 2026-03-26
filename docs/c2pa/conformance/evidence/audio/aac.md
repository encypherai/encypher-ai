# C2PA Evidence: audio/aac (AAC)

**Format**: Advanced Audio Coding (AAC)
**MIME Type**: audio/aac
**Category**: Audio
**Pipeline**: c2pa-rs via M4A (audio/mp4) canonicalization
**Status**: PASS (with container constraint)

## Embedding Approach

AAC audio is supported through MIME type canonicalization:

1. `audio/aac` is accepted at the API boundary
2. Canonicalized to `audio/mp4` (M4A container) before signing
3. Signed via c2pa-rs BMFF pipeline (same as M4A)
4. Manifest embedded in ISOBMFF `uuid` box

The signed output is an M4A file (ISOBMFF container with AAC codec data).

## Container Constraint

Raw AAC (ADTS-framed bitstream) cannot carry a C2PA manifest:

- ADTS is a bare codec bitstream with no metadata container
- No box structure, no metadata blocks, no insertion point for JUMBF
- This is a fundamental format limitation, not an implementation gap

AAC content MUST be in an M4A/ISOBMFF container for C2PA signing.
The vast majority of AAC content in production is M4A-wrapped.

## Verification

Verification uses the same c2pa-python Reader as M4A:

```
reader = c2pa.Reader("audio/mp4", stream)
```

The reader validates:
- COSE_Sign1 signature (ES256)
- c2pa.hash.bmff.v3 content binding
- RFC 3161 timestamp from SSL.com
- Certificate chain

## Evidence Artifacts

- Signed M4A fixture: `tests/c2pa_conformance/signed/signed_test.m4a`
- Manifest JSON: `tests/c2pa_conformance/manifests/signed_test_m4a.json`
- The M4A evidence applies directly to AAC since AAC is routed to the M4A pipeline

## Test Coverage

- Unit test: MIME canonicalization `audio/aac` -> `audio/mp4` in audio_utils.py
- E2E test: M4A signing roundtrip (covers AAC codec path)
- Conformance suite: `run_conformance.py` M4A entry covers the shared BMFF pipeline
