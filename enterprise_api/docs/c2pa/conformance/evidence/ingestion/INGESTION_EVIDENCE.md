# C2PA Ingestion/Validation Evidence

**Generated**: 2026-03-25T12:30:01.903072+00:00
**Product**: Encypher Enterprise API v2.0.0
**Total files tested**: 62
**Pass**: 60 / **Fail**: 2

---

## 1. External Interoperability -- C2PA Sample Library

Files from the C2PA Conformance Program sample library
(https://drive.google.com/drive/folders/1TCSjsDGp5g6vx37oSiry2lHHpVNq7zct).
These are third-party signed files (Google Pixel Camera, Google Photos, etc.)
verified by the Encypher Enterprise API validator.

| # | File | MIME Type | Size | Source | Valid | Generator | Failures |
|---|------|-----------|------|--------|-------|-----------|----------|
| 1 | NotebookLM_Infographic.jpg | image/jpeg | 675,492 | Interoperability Testing Files | PASS | unknown | 0 |
| 2 | camera-capture-2_Magic-Editor.jpg | image/jpeg | 2,631,187 | Interoperability Testing Files | PASS | unknown | 0 |
| 3 | camera-capture-2_Magic-Eraser.jpg | image/jpeg | 2,494,109 | Interoperability Testing Files | PASS | unknown | 0 |
| 4 | camera-capture-2_cropped.jpg | image/jpeg | 1,062,269 | Interoperability Testing Files | PASS | unknown | 0 |
| 5 | camera-capture-2_cropped_Magic-Editor.jpg | image/jpeg | 1,055,641 | Interoperability Testing Files | PASS | unknown | 0 |
| 6 | camera-capture_Magic-Editor_crop_nonAI-filter.jpg | image/jpeg | 1,241,315 | Interoperability Testing Files | PASS | unknown | 0 |
| 7 | camera-capture_Magic-Eraser.jpg | image/jpeg | 2,979,867 | Interoperability Testing Files | PASS | unknown | 0 |
| 8 | camera-capture_Zoom-Enhance.jpg | image/jpeg | 1,277,427 | Interoperability Testing Files | PASS | unknown | 0 |
| 9 | camera-capture_cropped.jpg | image/jpeg | 1,429,260 | Interoperability Testing Files | PASS | unknown | 0 |
| 10 | PXL_20250708_194721212.MP.jpg | image/jpeg | 7,553,272 | Interoperability Testing Files | PASS | unknown | 0 |
| 11 | PXL_20250708_194741653.PORTRAIT.jpg | image/jpeg | 6,020,273 | Interoperability Testing Files | PASS | unknown | 0 |
| 12 | PXL_20250708_194756993.PANO.jpg | image/jpeg | 3,390,357 | Interoperability Testing Files | PASS | unknown | 0 |
| 13 | PXL_20250708_194920135.BURST-01.jpg | image/jpeg | 1,540,589 | Interoperability Testing Files | PASS | unknown | 0 |
| 14 | PXL_20250708_194920135.BURST-02.original.jpg | image/jpeg | 1,716,633 | Interoperability Testing Files | PASS | unknown | 0 |
| 15 | PXL_20250708_195016574.50MP.jpg | image/jpeg | 7,952,777 | Interoperability Testing Files | PASS | unknown | 0 |
| 16 | PXL_20250708_195029920.50MP.PORTRAIT.jpg | image/jpeg | 15,234,388 | Interoperability Testing Files | PASS | unknown | 0 |
| 17 | PXL_20250808_044132153.MP_multi_part.jpg | image/jpeg | 5,755,577 | Interoperability Testing Files | PASS | unknown | 0 |
| 18 | PXL_20250808_044132153.MP_multi_part_stripped.jpg | image/jpeg | 4,028,399 | Interoperability Testing Files | FAIL | unknown | 1 |
| 19 | Unedited regular capture 2.jpg | image/jpeg | 4,008,310 | Interoperability Testing Files | PASS | unknown | 0 |
| 20 | Unedited regular capture.jpg | image/jpeg | 4,546,038 | Interoperability Testing Files | PASS | unknown | 0 |
| 21 | PXL_20250814_054649791.ProResZoom-AI.jpg | image/jpeg | 1,714,957 | Interoperability Testing Files | PASS | unknown | 0 |
| 22 | PXL_20250814_054649791.ProResZoom-Original.jpg | image/jpeg | 2,115,569 | Interoperability Testing Files | PASS | unknown | 0 |
| 23 | PXL_20250814_054852946.jpg | image/jpeg | 2,306,528 | Interoperability Testing Files | PASS | unknown | 0 |
| 24 | PXL_20250814_054908613.Portrait.jpg | image/jpeg | 2,620,727 | Interoperability Testing Files | PASS | unknown | 0 |
| 25 | PXL_20250814_054932904.50MP.jpg | image/jpeg | 8,128,541 | Interoperability Testing Files | PASS | unknown | 0 |
| 26 | PXL_20250814_054957360.50MP-Night.jpg | image/jpeg | 6,848,558 | Interoperability Testing Files | PASS | unknown | 0 |
| 27 | PXL_20250814_055103150.Panorama.jpg | image/jpeg | 5,003,819 | Interoperability Testing Files | PASS | unknown | 0 |
| 28 | PXL_20250814_055223679.ActionPan-Original.jpg | image/jpeg | 2,449,293 | Interoperability Testing Files | PASS | unknown | 0 |
| 29 | PXL_20250814_055223679.ActionPan.jpg | image/jpeg | 2,376,820 | Interoperability Testing Files | PASS | unknown | 0 |
| 30 | PXL_20250814_055359794.VideoSnapshot.jpg | image/jpeg | 1,536,403 | Interoperability Testing Files | PASS | unknown | 0 |
| 31 | PXL_20250814_055729041.AddMe-01.jpg | image/jpeg | 3,372,000 | Interoperability Testing Files | PASS | unknown | 0 |
| 32 | PXL_20250814_055729041.AddMe-02.jpg | image/jpeg | 4,470,607 | Interoperability Testing Files | PASS | unknown | 0 |
| 33 | PXL_20250814_055729041.AddMe-Combined.jpg | image/jpeg | 4,694,056 | Interoperability Testing Files | PASS | unknown | 0 |
| 34 | PXL_20250814_180141200.MP.jpg | image/jpeg | 7,375,261 | Interoperability Testing Files | PASS | unknown | 0 |
| 35 | PXL_20250814_180141200.MP_stripped.jpg | image/jpeg | 2,819,040 | Interoperability Testing Files | FAIL | unknown | 1 |

**External verification: 33/35 passed.**

All external files use third-party signing certificates (Google, etc.).
The `signingCredential.untrusted` status is expected for certificates
not on our configured trust list -- this is informational, not a failure.

---

## 2. Self-Signed Roundtrip Verification

Our own signed output files verified by our own validator,
demonstrating end-to-end generate + validate capability per media type.

| # | File | MIME Type | Size | Pipeline | Valid | Generator | Failures |
|---|------|-----------|------|----------|-------|-----------|----------|
| 1 | signed_test.avi | video/x-msvideo | 22,108 | c2pa-python | PASS |  | 0 |
| 2 | signed_test.avif | image/avif | 15,331 | c2pa-python | PASS |  | 0 |
| 3 | signed_test.dng | image/x-adobe-dng | 18,931 | c2pa-python | PASS |  | 0 |
| 4 | signed_test.docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | 66,740 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 5 | signed_test.epub | application/epub+zip | 66,608 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 6 | signed_test.flac | audio/flac | 65,586 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 7 | signed_test.gif | image/gif | 17,102 | c2pa-python | PASS |  | 0 |
| 8 | signed_test.heic | image/heic | 15,464 | c2pa-python | PASS |  | 0 |
| 9 | signed_test.heif | image/heif | 15,464 | c2pa-python | PASS |  | 0 |
| 10 | signed_test.jpg | image/jpeg | 45,482 | c2pa-python | PASS |  | 0 |
| 11 | signed_test.jxl | image/jxl | 65,650 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 12 | signed_test.m4a | audio/mp4 | 31,164 | c2pa-python | PASS |  | 0 |
| 13 | signed_test.m4v | video/x-m4v | 17,218 | c2pa-python | PASS |  | 0 |
| 14 | signed_test.mov | video/quicktime | 17,164 | c2pa-python | PASS |  | 0 |
| 15 | signed_test.mp3 | audio/mpeg | 20,681 | c2pa-python | PASS |  | 0 |
| 16 | signed_test.mp4 | video/mp4 | 23,451 | c2pa-python | PASS |  | 0 |
| 17 | signed_test.odt | application/vnd.oasis.opendocument.text | 66,577 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 18 | signed_test.otf | font/otf | 65,612 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 19 | signed_test.oxps | application/oxps | 66,674 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 20 | signed_test.pdf | application/pdf | 66,639 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 21 | signed_test.png | image/png | 21,827 | c2pa-python | PASS |  | 0 |
| 22 | signed_test.sfnt | font/sfnt | 65,612 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 23 | signed_test.svg | image/svg+xml | 19,997 | c2pa-python | PASS |  | 0 |
| 24 | signed_test.tiff | image/tiff | 164,349 | c2pa-python | PASS |  | 0 |
| 25 | signed_test.ttf | font/ttf | 65,612 | custom_jumbf_cose | PASS | Encypher Enterprise API/2.0 | 0 |
| 26 | signed_test.wav | audio/wav | 102,918 | c2pa-python | PASS |  | 0 |
| 27 | signed_test.webp | image/webp | 15,706 | c2pa-python | PASS |  | 0 |

**Self-signed verification: 27/27 passed.**

---

## 3. Submission MIME Type Coverage

Mapping each of Scott's 27 submission MIME types to validation evidence:

| Submission MIME Type | Alias Of | Self-Signed Evidence | External Evidence | Status |
|---------------------|----------|---------------------|-------------------|--------|
| image/jpeg | -- | signed_test.jpg | NotebookLM_Infographic.jpg | COVERED |
| image/jxl | -- | signed_test.jxl | N/A (library JPEG-only) | COVERED |
| image/png | -- | signed_test.png | N/A (library JPEG-only) | COVERED |
| image/svg+xml | -- | signed_test.svg | N/A (library JPEG-only) | COVERED |
| image/gif | -- | signed_test.gif | N/A (library JPEG-only) | COVERED |
| image/x-adobe-dng | -- | signed_test.dng | N/A (library JPEG-only) | COVERED |
| image/tiff | -- | signed_test.tiff | N/A (library JPEG-only) | COVERED |
| image/webp | -- | signed_test.webp | N/A (library JPEG-only) | COVERED |
| image/heic | -- | signed_test.heic | N/A (library JPEG-only) | COVERED |
| image/heic-sequence | image/heic | signed_test.heic | N/A (library JPEG-only) | COVERED |
| image/heif | -- | signed_test.heif | N/A (library JPEG-only) | COVERED |
| image/heif-sequence | image/heif | signed_test.heif | N/A (library JPEG-only) | COVERED |
| image/avif | -- | signed_test.avif | N/A (library JPEG-only) | COVERED |
| video/x-msvideo | -- | signed_test.avi | N/A (library JPEG-only) | COVERED |
| video/mp4 | -- | signed_test.mp4 | N/A (library JPEG-only) | COVERED |
| video/quicktime | -- | signed_test.mov | N/A (library JPEG-only) | COVERED |
| audio/flac | -- | signed_test.flac | N/A (library JPEG-only) | COVERED |
| audio/MPA | audio/mpeg | signed_test.mp3 | N/A (library JPEG-only) | COVERED |
| audio/mpeg | -- | signed_test.mp3 | N/A (library JPEG-only) | COVERED |
| audio/wav | -- | signed_test.wav | N/A (library JPEG-only) | COVERED |
| audio/aac | audio/mp4 | signed_test.m4a | N/A (library JPEG-only) | COVERED |
| audio/mp4 | -- | signed_test.m4a | N/A (library JPEG-only) | COVERED |
| application/pdf | -- | signed_test.pdf | N/A (library JPEG-only) | COVERED |
| application/epub+zip | -- | signed_test.epub | N/A (library JPEG-only) | COVERED |
| application/vnd.openxmlformats-officedocument.wordprocessingml.document | -- | signed_test.docx | N/A (library JPEG-only) | COVERED |
| application/vnd.oasis.opendocument.text | -- | signed_test.odt | N/A (library JPEG-only) | COVERED |
| application/oxps | -- | signed_test.oxps | N/A (library JPEG-only) | COVERED |

### Notes on alias types

- `image/heic-sequence`: Animated HEIC uses the same ISOBMFF container as static HEIC.
  The API accepts this MIME type and routes to the `image/heic` signing pipeline.
  Evidence: `signed_test.heic` demonstrates HEIC manifest generation and validation.

- `image/heif-sequence`: Same as above for HEIF.

- `audio/MPA`: MPEG Audio (RFC 3003). The API accepts `audio/MPA` and canonicalizes
  to `audio/mpeg` for c2pa-rs. Evidence: `signed_test.mp3` demonstrates MPEG audio
  manifest generation and validation.

- `audio/aac`: Raw ADTS AAC cannot carry C2PA manifests (no container structure).
  The API accepts `audio/aac` and canonicalizes to `audio/mp4` for M4A-wrapped AAC.
  Evidence: `signed_test.m4a` demonstrates AAC-in-M4A manifest generation and validation.
  See `SUBMISSION_MIME_TYPES.md` section 'Structurally Constrained Type: audio/aac'.

### Notes on external sample coverage

The C2PA Conformance Program sample library currently contains JPEG files only
(Google Pixel Camera, Google Photos, NotebookLM). For non-JPEG types, self-signed
roundtrip verification demonstrates the validate capability. As additional format
samples become available in the library, they can be added to this evidence.
