# Encypher Corporation -- C2PA Conformance Submission

**Organization**: Encypher Corporation
**Record ID**: 019d2241-eb97-7728-9ec0-cdaafba300c2
**Product**: Encypher Enterprise API v2.0.0
**Submission Date**: 2026-03-25
**Contact**: conformance@encypher.com

---

## Summary

This submission covers 28 MIME types across image, video, audio, document, and
font categories matching the C2PA conformance program submission list.  All 28
types have been exercised end-to-end: signed with our API, verified internally
with c2pa-python/c2pa-rs, and where available verified externally with
third-party C2PA implementations.

---

## MIME Type Coverage

### Image (13 types)

- image/jpeg
- image/jxl
- image/png
- image/svg+xml
- image/gif
- image/x-adobe-dng
- image/tiff
- image/webp
- image/heic
- image/heic-sequence
- image/heif
- image/heif-sequence
- image/avif

Note: image/heic-sequence and image/heif-sequence share the HEIF/ISOBMFF
container with image/heic and image/heif respectively. c2pa-rs collapses
these to their parent type during Reader parsing; both are accepted and
signed as distinct MIME types at the API boundary.

### Video (3 types)

- video/x-msvideo
- video/mp4
- video/quicktime

### Audio (6 types)

- audio/flac
- audio/MPA
- audio/mpeg
- audio/wav
- audio/aac
- audio/mp4

Note: audio/MPA is an alias for audio/mpeg (MP3 container). audio/aac
is accepted as M4A/ISOBMFF-wrapped AAC (c2pa-rs reports audio/mp4 during
Reader parsing). Both are signed and verified as distinct MIME types.

### Document (5 types)

- application/pdf
- application/epub+zip
- application/vnd.openxmlformats-officedocument.wordprocessingml.document
- application/vnd.oasis.opendocument.text
- application/oxps

### Font (1 type)

- font/otf

Total types in submission: 28

---

## Signing Pipelines

**Pipeline A -- c2pa-rs native (c2pa-python 0.29.0 / c2pa-rs 0.78.4)**

Used for: JPEG, PNG, WebP, TIFF, GIF, HEIC, HEIF, AVIF, SVG, DNG, MP4, MOV,
AVI, WAV, MP3, M4A.

**Pipeline B -- Custom JUMBF/COSE**

Used for: JXL (custom ISOBMFF c2pa box), FLAC (APPLICATION metadata block),
PDF (byte-range insertion), EPUB/DOCX/ODT/OXPS (ZIP-based manifest at
META-INF/content_credential.c2pa), AAC (routed to audio/mp4 M4A container).

**Certificate**: SSL.com c2pasign test certificate
**Algorithm**: ECC P-256 / ES256
**TSA**: http://ts.ssl.com (RFC 3161)

---

## Folder Structure

```
submission/
  README.md                              This file
  Encypher_Security_Architecture_Document.docx  (generated separately)

  generator_samples/
    image/
      jpeg/        signed_test.jpg + signed_test_jpg.json
      jxl/         signed_test.jxl + signed_test_jxl.json
      png/         signed_test.png + signed_test_png.json
      svg/         signed_test.svg + signed_test_svg.json
      gif/         signed_test.gif + signed_test_gif.json
      dng/         signed_test.dng + signed_test_dng.json
      tiff/        signed_test.tiff + signed_test_tiff.json
      webp/        signed_test.webp + signed_test_webp.json
      heic/        signed_test.heic + signed_test_heic.json
      heic-sequence/  signed_test_heic-sequence.heic + signed_test_heic-sequence.json
      heif/        signed_test.heif + signed_test_heif.json
      heif-sequence/  signed_test_heif-sequence.heif + signed_test_heif-sequence.json
      avif/        signed_test.avif + signed_test_avif.json
    video/
      mp4/         signed_test.mp4 + signed_test_mp4.json
      quicktime/   signed_test.mov + signed_test_mov.json
      avi/         signed_test.avi + signed_test_avi.json
    audio/
      flac/        signed_test.flac + signed_test_flac.json
      mpa/         signed_test_mpa.mp3 + signed_test_mpa.json
      mpeg/        signed_test.mp3 + signed_test_mp3.json
      wav/         signed_test.wav + signed_test_wav.json
      aac/         signed_test_aac.m4a + signed_test_aac.json
      mp4/         signed_test.m4a + signed_test_m4a.json
    document/
      pdf/         signed_test.pdf + signed_test_pdf.json
      epub/        signed_test.epub + signed_test_epub.json
      docx/        signed_test.docx + signed_test_docx.json
      odt/         signed_test.odt + signed_test_odt.json
      oxps/        signed_test.oxps + signed_test_oxps.json
    font/
      otf/         signed_test.otf + signed_test_otf.json

  validation_evidence/
    self_verification/
      ingestion_results.json    Consolidated self-verification results
    external_interoperability/
      external_ingestion_results.json  Consolidated external verification results
      README.md                 Explains what files were tested

  test_methodology/
    TEST_METHODOLOGY.md         How to reproduce all tests
    CONFORMANCE_MATRIX.md       28/28 format pass/fail matrix
    MIME_TYPE_INVENTORY.md      Full MIME type list with pipeline notes

  extended_capabilities/
    README.md                   Live video streaming + text C2PA evidence
    live_video_streaming_evidence.json  3 signed segments, verification, Merkle root
    signed_stream_segment_0.mp4        Signed MP4 segment sample (17 KB)
    text_c2pa_evidence.json            Sign, verify, tamper detection results
    signed_text_sample.txt             Signed text with embedded C2PA manifest
```

---

## Extended Capabilities

In addition to the 28 submitted MIME types, Encypher supports two production
capabilities defined in C2PA v2.3 but not yet covered by the conformance
program:

1. **Live Video Streaming** -- per-segment C2PA signing (Section 19) for
   RTMP/HLS pipelines with backward manifest chaining and Merkle finalization.
2. **Unstructured Text** -- C2PA text manifests (Manifests_Text.adoc) embedded
   via Unicode Variation Selectors with Ed25519 COSE_Sign1 signing.

See extended_capabilities/README.md for evidence files and details.  We are
happy to help strengthen the conformance program with these capabilities.

---

## Note on Security Architecture Document

The Security Architecture Document (Encypher_Security_Architecture_Document.docx)
is provided as a separate file in this folder.  It was generated from the
Markdown source at docs/c2pa/conformance/SECURITY_ARCHITECTURE_DOCUMENT.md and
converted to DOCX for review convenience.
