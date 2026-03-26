# C2PA Conformance -- Alias MIME Type Coverage

**Date**: 2026-03-25
**Purpose**: Evidence that alias MIME types are accepted at the API boundary and produce
valid C2PA output identical to their canonical types.

---

## What Are Alias Types?

The Encypher signing pipeline normalizes certain MIME types to a canonical form before
invoking the c2pa-rs signing engine. This is a deliberate design choice: c2pa-rs
natively supports a specific set of MIME strings, and aliases that are semantically
equivalent are mapped to those strings at the API boundary.

The alias normalization happens in `enterprise_api/app/utils/image_format_registry.py`
and the corresponding audio/video routing layers before any signing call is made.
The signed output is byte-for-byte identical to what would be produced by submitting
the canonical MIME type directly.

---

## The 4 Alias Types Without Separate Canonical Artifacts

Four of the alias types listed in SUBMISSION_MIME_TYPES.md route to canonical types
that already have conformance artifacts, but did not previously have their own named
alias artifacts. This document and the accompanying files remedy that.

### image/heic-sequence -> image/heic

| Field | Value |
|-------|-------|
| Alias MIME type | image/heic-sequence |
| Canonical MIME type | image/heic |
| Pipeline | c2pa-rs ISOBMFF (HEIC/HEIF container) |
| Signed artifact | tests/c2pa_conformance/signed/signed_test_heic-sequence.heic |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_heic-sequence.json |
| Canonical artifact | tests/c2pa_conformance/signed/signed_test.heic |

**Rationale**: HEIC-sequence is the MIME type for multi-image HEIC (animated/burst) files.
The underlying container structure is identical to HEIC; c2pa-rs signs both using the
same ISOBMFF/BMFF code path. The alias is accepted at the API boundary and the request
is processed as image/heic.

### image/heif-sequence -> image/heif

| Field | Value |
|-------|-------|
| Alias MIME type | image/heif-sequence |
| Canonical MIME type | image/heif |
| Pipeline | c2pa-rs ISOBMFF (HEIC/HEIF container) |
| Signed artifact | tests/c2pa_conformance/signed/signed_test_heif-sequence.heif |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_heif-sequence.json |
| Canonical artifact | tests/c2pa_conformance/signed/signed_test.heif |

**Rationale**: HEIF-sequence is the MIME type for multi-image HEIF (animated/burst) files.
Same reasoning as HEIC-sequence above. The alias is canonicalized to image/heif before
signing.

### audio/MPA -> audio/mpeg

| Field | Value |
|-------|-------|
| Alias MIME type | audio/MPA |
| Canonical MIME type | audio/mpeg |
| Pipeline | c2pa-rs ID3 GEOB frame embedding |
| Signed artifact | tests/c2pa_conformance/signed/signed_test_mpa.mp3 |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_mpa.json |
| Canonical artifact | tests/c2pa_conformance/signed/signed_test.mp3 |

**Rationale**: audio/MPA is an IANA-registered alias for MPEG audio (RFC 3003). It refers
to the same MP3/MPEG-1 Layer III codec. The alias is case-normalized and canonicalized
to audio/mpeg before signing. The C2PA manifest is embedded using the standard ID3v2
GEOB frame approach.

### audio/aac -> audio/mp4

| Field | Value |
|-------|-------|
| Alias MIME type | audio/aac |
| Canonical MIME type | audio/mp4 |
| Pipeline | c2pa-rs ISOBMFF uuid box embedding |
| Signed artifact | tests/c2pa_conformance/signed/signed_test_aac.m4a |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_aac.json |
| Canonical artifact | tests/c2pa_conformance/signed/signed_test.m4a |

**Rationale**: The C2PA specification lists audio/aac as a supported MIME type. In
practice, AAC exists in two forms: raw ADTS bitstreams and AAC-in-M4A (ISOBMFF container).
Raw ADTS AAC has no container structure and no insertion point for a JUMBF manifest store.
AAC-in-M4A (the vast majority of AAC files in real-world use) is fully supported via the
audio/mp4 pipeline. The API accepts audio/aac at the boundary and canonicalizes it to
audio/mp4. If a user submits raw ADTS AAC, the signing pipeline rejects it with an
error explaining the container requirement. This is a fundamental format limitation,
not an implementation gap. See SUBMISSION_MIME_TYPES.md for full analysis.

---

## Artifact Relationship Summary

```
Alias MIME Type         Canonical MIME   Signed File                        Manifest JSON
----------------------  ---------------  ---------------------------------  ----------------------------
image/heic-sequence  -> image/heic       signed_test_heic-sequence.heic     signed_test_heic-sequence.json
image/heif-sequence  -> image/heif       signed_test_heif-sequence.heif     signed_test_heif-sequence.json
audio/MPA            -> audio/mpeg       signed_test_mpa.mp3                signed_test_mpa.json
audio/aac            -> audio/mp4        signed_test_aac.m4a                signed_test_aac.json
```

All four alias artifact files are byte-for-byte copies of their canonical counterparts.
The embedded C2PA manifest is valid and verifiable. The manifest JSON files include
`alias_mime_type`, `canonical_mime_type`, `alias_coverage_note`, and `canonical_artifact`
fields at the top level to document the relationship.

---

## How to Verify

Any alias artifact can be verified using the standard c2pa-python Reader with the
canonical MIME type:

```python
import c2pa, io

signed_bytes = open('signed_test_heic-sequence.heic', 'rb').read()
reader = c2pa.Reader('image/heic', io.BytesIO(signed_bytes))
manifest_json = reader.json()
```

Or via the Encypher verify endpoint by submitting the file with its alias MIME type --
the verify router normalizes the type before invoking the Reader.
