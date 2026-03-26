# C2PA Conformance Evidence Index

**Product**: Encypher Enterprise API v2.0.0
**Conformance suite run**: 2026-03-25T08:33:21Z
**Document version**: 1.0 (created 2026-03-25)
**Total formats**: 28 (all 28 asserted MIME types covered)
**Conformance suite result**: 28/28 sign PASS, 28/28 verify PASS

---

## How to Read This Package

All evidence files are traceable to primary sources:

| Primary Source | Path |
|---------------|------|
| Conformance suite run results | enterprise_api/tests/c2pa_conformance/results/verify_results.json |
| Signed manifest JSON (per format) | enterprise_api/tests/c2pa_conformance/manifests/signed_test_*.json |
| Adobe verify screenshots | docs/c2pa/conformance/evidence/screenshots/ |
| Summary table | docs/c2pa/conformance/evidence/CONFORMANCE_MATRIX.md |
| Interoperability report | docs/c2pa/conformance/evidence/INTEROP_TEST_REPORT.md |

Claims in evidence files must be verified against those sources. No values were fabricated.

---

## Image Formats (11 formats)

10 image formats use c2pa-python Builder (c2pa-rs). JXL uses a custom ISOBMFF embedder
(c2pa-rs does not support JXL yet).

| Format | MIME Type | Hash Type | Pipeline | Evidence File |
|--------|-----------|-----------|----------|---------------|
| JPEG | image/jpeg | c2pa.hash.data | c2pa-rs | [image/jpeg.md](image/jpeg.md) |
| PNG | image/png | c2pa.hash.data | c2pa-rs | [image/png.md](image/png.md) |
| WebP | image/webp | c2pa.hash.data | c2pa-rs | [image/webp.md](image/webp.md) |
| TIFF | image/tiff | c2pa.hash.data | c2pa-rs | [image/tiff.md](image/tiff.md) |
| AVIF | image/avif | c2pa.hash.bmff.v3 | c2pa-rs | [image/avif.md](image/avif.md) |
| HEIC | image/heic | c2pa.hash.bmff.v3 | c2pa-rs | [image/heic.md](image/heic.md) |
| HEIF | image/heif | c2pa.hash.bmff.v3 | c2pa-rs | [image/heif.md](image/heif.md) |
| SVG | image/svg+xml | c2pa.hash.data | c2pa-rs | [image/svg.md](image/svg.md) |
| DNG | image/x-adobe-dng | c2pa.hash.data | c2pa-rs | [image/dng.md](image/dng.md) |
| GIF | image/gif | c2pa.hash.data | c2pa-rs | [image/gif.md](image/gif.md) |
| JXL | image/jxl | c2pa.hash.data | Custom ISOBMFF | [image/jxl.md](image/jxl.md) |

### Image MIME Type Aliases

| Alias | Routes To | Notes |
|-------|-----------|-------|
| image/jpg | image/jpeg | Non-standard alias, widely used |
| image/heic-sequence | image/heic | Animated HEIC; canonicalized per image_format_registry.py |
| image/heif-sequence | image/heif | Animated HEIF; canonicalized per image_format_registry.py |

---

## Audio Formats (5 formats)

WAV, MP3, and M4A use c2pa-rs. FLAC uses a custom JUMBF/COSE pipeline.
AAC is canonicalized to M4A (audio/mp4) -- raw ADTS AAC cannot carry manifests.

| Format | MIME Type | Hash Type | Pipeline | Evidence File |
|--------|-----------|-----------|----------|---------------|
| WAV | audio/wav | c2pa.hash.data | c2pa-rs | [audio/wav.md](audio/wav.md) |
| MP3 | audio/mpeg | c2pa.hash.data | c2pa-rs | [audio/mp3.md](audio/mp3.md) |
| M4A | audio/mp4 | c2pa.hash.bmff.v3 | c2pa-rs | [audio/m4a.md](audio/m4a.md) |
| FLAC | audio/flac | c2pa.hash.data | Custom JUMBF/COSE | [audio/flac.md](audio/flac.md) |
| AAC | audio/aac | c2pa.hash.bmff.v3 | c2pa-rs (via M4A) | [audio/aac.md](audio/aac.md) |

---

## Video Formats (4 formats)

All 4 video formats use c2pa-rs. M4V is an ISOBMFF variant of MP4.

| Format | MIME Type | Hash Type | Pipeline | Evidence File |
|--------|-----------|-----------|----------|---------------|
| MP4 | video/mp4 | c2pa.hash.bmff.v3 | c2pa-rs | [video/mp4.md](video/mp4.md) |
| MOV | video/quicktime | c2pa.hash.bmff.v3 | c2pa-rs | [video/mov.md](video/mov.md) |
| AVI | video/x-msvideo | c2pa.hash.data | c2pa-rs | [video/avi.md](video/avi.md) |
| M4V | video/x-m4v | c2pa.hash.bmff.v3 | c2pa-rs | [video/m4v.md](video/m4v.md) |

---

## Document Formats (5 formats)

All use Encypher's custom JUMBF/COSE pipeline. PDF uses byte-range insertion.
ZIP-based formats (EPUB, DOCX, ODT, OXPS) use collection data hashing.

| Format | MIME Type | Pipeline | Evidence File |
|--------|-----------|----------|---------------|
| PDF | application/pdf | Custom JUMBF/COSE | [document/pdf.md](document/pdf.md) |
| EPUB | application/epub+zip | Custom JUMBF/COSE (ZIP) | [document/epub.md](document/epub.md) |
| DOCX | application/vnd.openxmlformats-officedocument.wordprocessingml.document | Custom JUMBF/COSE (ZIP) | [document/docx.md](document/docx.md) |
| ODT | application/vnd.oasis.opendocument.text | Custom JUMBF/COSE (ZIP) | [document/odt.md](document/odt.md) |
| OXPS | application/oxps | Custom JUMBF/COSE (ZIP) | [document/oxps.md](document/oxps.md) |

---

## Font Formats (3 formats)

All use the same SFNT C2PA table embedder. font/sfnt is the generic SFNT container type.

| Format | MIME Type | Pipeline | Evidence File |
|--------|-----------|----------|---------------|
| OTF | font/otf | Custom JUMBF/COSE (SFNT) | [font/otf.md](font/otf.md) |

---

## Screenshots Index

All screenshots are in [screenshots/](screenshots/). Adobe Content Credentials Verify
was used as the external validator (contentcredentials.org/verify).

| Screenshot File | Format | Source |
|----------------|--------|--------|
| jpeg_adobe_verify.png | JPEG | Conformance suite + interop test |
| png_adobe_verify.png | PNG | Conformance suite + interop test |
| webp_adobe_verify.png | WebP | Conformance suite |
| tiff_adobe_verify.png | TIFF | Conformance suite |
| avif_adobe_verify.png | AVIF | Conformance suite |
| heic_adobe_verify.png | HEIC | Conformance suite |
| heif_adobe_verify.png | HEIF | Conformance suite |
| svg_adobe_verify.png | SVG | Conformance suite |
| dng_adobe_verify.png | DNG | Conformance suite |
| mp4_adobe_verify.png | MP4 | Conformance suite + interop test |
| mov_adobe_verify.png | MOV | Conformance suite |
| avi_adobe_verify.png | AVI | Conformance suite |
| wav_adobe_verify.png | WAV | Conformance suite + interop test |
| mp3_adobe_verify.png | MP3 | Conformance suite |
| m4a_adobe_verify.png | M4A | Conformance suite |
| pdf_adobe_verify.png | PDF | Conformance suite (shows tool cannot parse) |
| adobe_verify_jpeg.png | JPEG | Interop test (alternative screenshot) |
| adobe_verify_png.png | PNG | Interop test (alternative screenshot) |
| adobe_verify_wav.png | WAV | Interop test (alternative screenshot) |
| adobe_verify_mp4.png | MP4 | Interop test (alternative screenshot) |

---

## API and Web Tool Verification

Independent verification evidence using curl and the drag-and-drop File Inspector.

| Evidence | Path |
|----------|------|
| API curl + Web File Inspector results | [API_VERIFICATION_EVIDENCE.md](API_VERIFICATION_EVIDENCE.md) |

---

## Related Documents

| Document | Path |
|----------|------|
| Conformance matrix (summary table) | [CONFORMANCE_MATRIX.md](CONFORMANCE_MATRIX.md) |
| Interoperability test report | [INTEROP_TEST_REPORT.md](INTEROP_TEST_REPORT.md) |
| Conformance suite runner | enterprise_api/tests/c2pa_conformance/ |
| Image format registry | enterprise_api/app/utils/image_format_registry.py |
| Document signing service | enterprise_api/app/services/document_signing_service.py |
| JUMBF implementation | enterprise_api/app/utils/jumbf.py |
| COSE signer | enterprise_api/app/utils/cose_signer.py |
| Unified verify service | enterprise_api/app/services/unified_verify_service.py |
