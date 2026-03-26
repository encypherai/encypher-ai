# C2PA Conformance Matrix

**Generated**: 2026-03-25T08:33:21Z (conformance suite run timestamp)
**Document version**: 2.0 (rebuilt 2026-03-25)
**Product**: Encypher Enterprise API v2.0.0
**Certificate**: CN=Encypher Conformance Test Cert, O=Encypher Corporation
**Certificate algorithm**: ECC P-256 / ES256
**Certificate authority**: SSL.com (c2pasign conformance testing program)
**TSA**: http://ts.ssl.com (RFC 3161), SSL.com Timestamping Unit 2025 E1

## Software Versions

| Component | Version |
|-----------|---------|
| c2pa-python | 0.29.0 |
| c2pa-rs (embedded in c2pa-python) | 0.78.4 (from claim_generator_info in signed manifests) |
| cryptography (Python) | >=46.0.5 |
| Encypher Enterprise API | 2.0.0 |

## Complete Format Coverage

### All 28 Asserted Formats (28/28 -- all PASS sign + verify)

| # | Format | MIME Type | Ext(s) | Category | Pipeline | Sign | Verify (internal) | Evidence |
|---|--------|-----------|--------|----------|----------|------|-------------------|----------|
| 1 | JPEG | image/jpeg | .jpg .jpeg | Image | c2pa-rs | PASS | PASS | [image/jpeg.md](image/jpeg.md) |
| 2 | JXL | image/jxl | .jxl | Image | Custom JUMBF/COSE (ISOBMFF) | PASS | PASS (structural) | [image/jxl.md](image/jxl.md) |
| 3 | PNG | image/png | .png | Image | c2pa-rs | PASS | PASS | [image/png.md](image/png.md) |
| 4 | SVG | image/svg+xml | .svg | Image | c2pa-rs | PASS | PASS | [image/svg.md](image/svg.md) |
| 5 | GIF | image/gif | .gif | Image | c2pa-rs | PASS | PASS | [image/gif.md](image/gif.md) |
| 6 | DNG | image/x-adobe-dng | .dng | Image | c2pa-rs | PASS | PASS | [image/dng.md](image/dng.md) |
| 7 | TIFF | image/tiff | .tiff .tif | Image | c2pa-rs | PASS | PASS | [image/tiff.md](image/tiff.md) |
| 8 | WebP | image/webp | .webp | Image | c2pa-rs | PASS | PASS | [image/webp.md](image/webp.md) |
| 9 | HEIC | image/heic | .heic | Image | c2pa-rs (BMFF) | PASS | PASS | [image/heic.md](image/heic.md) |
| 10 | HEIC-sequence | image/heic-sequence | .heic | Image | c2pa-rs (BMFF) | PASS | PASS | [image/heic.md](image/heic.md) |
| 11 | HEIF | image/heif | .heif | Image | c2pa-rs (BMFF) | PASS | PASS | [image/heif.md](image/heif.md) |
| 12 | HEIF-sequence | image/heif-sequence | .heif | Image | c2pa-rs (BMFF) | PASS | PASS | [image/heif.md](image/heif.md) |
| 13 | AVIF | image/avif | .avif | Image | c2pa-rs (BMFF) | PASS | PASS | [image/avif.md](image/avif.md) |
| 14 | AVI | video/x-msvideo | .avi | Video | c2pa-rs | PASS | PASS | [video/avi.md](video/avi.md) |
| 15 | MP4 | video/mp4 | .mp4 | Video | c2pa-rs (BMFF) | PASS | PASS | [video/mp4.md](video/mp4.md) |
| 16 | MOV | video/quicktime | .mov | Video | c2pa-rs (BMFF) | PASS | PASS | [video/mov.md](video/mov.md) |
| 17 | FLAC | audio/flac | .flac | Audio | Custom JUMBF/COSE | PASS | PASS (structural) | [audio/flac.md](audio/flac.md) |
| 18 | MPA | audio/MPA | .mp3 | Audio | c2pa-rs (via audio/mpeg) | PASS | PASS | [audio/mp3.md](audio/mp3.md) |
| 19 | MP3 | audio/mpeg | .mp3 | Audio | c2pa-rs | PASS | PASS | [audio/mp3.md](audio/mp3.md) |
| 20 | WAV | audio/wav | .wav | Audio | c2pa-rs | PASS | PASS | [audio/wav.md](audio/wav.md) |
| 21 | AAC | audio/aac | .m4a | Audio | c2pa-rs (BMFF via M4A) | PASS | PASS | [audio/aac.md](audio/aac.md) |
| 22 | M4A | audio/mp4 | .m4a | Audio | c2pa-rs (BMFF) | PASS | PASS | [audio/m4a.md](audio/m4a.md) |
| 23 | PDF | application/pdf | .pdf | Document | Custom JUMBF/COSE | PASS | PASS (structural) | [document/pdf.md](document/pdf.md) |
| 24 | EPUB | application/epub+zip | .epub | Document | Custom JUMBF/COSE (ZIP) | PASS | PASS (structural) | [document/epub.md](document/epub.md) |
| 25 | DOCX | application/vnd.openxmlformats-officedocument.wordprocessingml.document | .docx | Document | Custom JUMBF/COSE (ZIP) | PASS | PASS (structural) | [document/docx.md](document/docx.md) |
| 26 | ODT | application/vnd.oasis.opendocument.text | .odt | Document | Custom JUMBF/COSE (ZIP) | PASS | PASS (structural) | [document/odt.md](document/odt.md) |
| 27 | OXPS | application/oxps | .oxps | Document | Custom JUMBF/COSE (ZIP) | PASS | PASS (structural) | [document/oxps.md](document/oxps.md) |
| 28 | OTF | font/otf | .otf | Font | Custom JUMBF/COSE (SFNT) | PASS | PASS (structural) | [font/otf.md](font/otf.md) |

**Canonicalization notes:**

- **image/heic-sequence** and **image/heif-sequence** share the HEIF/ISOBMFF container
  with image/heic and image/heif. c2pa-rs canonicalizes to the parent type during signing
  and Reader parsing. Both are accepted as distinct MIME types at the API boundary.
- **audio/MPA** is canonicalized to audio/mpeg for signing (same MP3 container).
- **audio/aac** is canonicalized to audio/mp4 for signing. AAC codec data must be in an
  M4A/ISOBMFF container. Raw ADTS AAC bitstreams cannot carry C2PA manifests.

### Additional MIME Type Aliases (accepted by API)

| Alias | Canonical Type | Notes |
|-------|---------------|-------|
| image/jpg | image/jpeg | Non-standard but widely used; treated identically to image/jpeg |

## Format Notes

| Format | MIME Type | Notes |
|--------|-----------|-------|
| JXL | image/jxl | c2pa-rs does not natively support JXL embedding. Encypher implements a custom ISOBMFF embedder (jxl_c2pa_embedder.py) that inserts a top-level 'c2pa' box with c2pa.hash.data binding. Verification is structural. |
| AAC (raw) | audio/aac | Raw AAC (ADTS framing) has no container structure for JUMBF embedding. AAC in MP4/M4A container is supported via M4A canonicalization. |

## Hash Assertion Types by Format

Two content-binding assertion types are used, determined by container structure:

| Hash Type | Assertion Label | Formats |
|-----------|----------------|---------|
| Data hash (byte-range exclusion) | c2pa.hash.data | JPEG, PNG, WebP, TIFF, SVG, DNG, GIF, WAV, MP3, MPA, AVI, FLAC, PDF, JXL, OTF |
| BMFF box hash | c2pa.hash.bmff.v3 | AVIF, HEIC, HEIC-sequence, HEIF, HEIF-sequence, MP4, MOV, M4A, AAC (via M4A) |
| Collection data hash (ZIP) | c2pa.hash.collection.data | EPUB, DOCX, ODT, OXPS |

PDF, FLAC, and JXL use a custom data hash with explicit byte-range exclusion covering the JUMBF manifest store placeholder.
JXL uses a top-level ISOBMFF 'c2pa' box with c2pa.hash.data (not c2pa.hash.bmff.v3) -- simpler and spec-compliant.
ZIP-based documents use collection data hashing (per-file + central directory).
AAC uses the M4A (audio/mp4) pipeline -- BMFF hash via c2pa-rs.
MPA uses the MP3 (audio/mpeg) pipeline -- data hash via c2pa-rs.

## Conformance Suite -- Pass/Fail Summary

| Metric | Value |
|--------|-------|
| Total asserted types | 28 |
| Sign PASS | 28 / 28 |
| Verify PASS (internal c2pa-python Reader or structural) | 28 / 28 |
| c2pa-rs native pipeline | 20 / 28 |
| Custom JUMBF/COSE pipeline | 8 / 28 |

Custom pipeline formats (PDF, EPUB, DOCX, ODT, OXPS, FLAC, JXL) use
structural JUMBF verification. ZIP-based documents additionally verify per-file and
central directory hash binding. FLAC and JXL E2E tests verify COSE signature +
data hash binding. Canonicalized types (heic-sequence, heif-sequence, MPA, AAC)
are routed through their parent type's pipeline.

## Generator Compliance Notes

- claim_generator_info: present with name "Encypher", version present in all c2pa-rs manifests
- c2pa.actions.v2: used in all formats (not legacy c2pa.actions v1)
- digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture in all
- softwareAgent: name "Encypher Enterprise API", version present in all action records
- Timestamps: RFC 3161, SSL.com TSA, all manifests show timeStamp.validated = true
- timeStamp.untrusted informational: expected for conformance test certificates not yet on the C2PA trust list; not a validation failure
- com.encypher.provenance: custom assertion present in all 28 formats
- Signing algorithm: ES256 (ECC P-256) in all formats

## Adobe Content Credentials Verify Details

Adobe's tool at contentcredentials.org/verify can parse the c2pa-rs-signed formats.
Custom pipeline formats (PDF, EPUB, DOCX, ODT, OXPS, FLAC, JXL) use
Encypher's own JUMBF/COSE structure and may not be parseable by Adobe's tool. For those
formats, internal structural verification and E2E roundtrip tests provide the conformance
evidence.

- Displayed signer identity: "Encypher Conformance Test Cert" (from certificate CN)
- Displayed organization: "Encypher Corporation" (from certificate O)
- Trust status: "Unrecognized" -- expected for conformance test certificates not yet on the C2PA trust list
- Manifest structure: JUMBF, claim, assertions, signature chain, and timestamp all parsed
- Actions: "Created" action correctly displayed
- RFC 3161 timestamp from SSL.com displayed

Screenshots are in [screenshots/](screenshots/) -- one per format.
