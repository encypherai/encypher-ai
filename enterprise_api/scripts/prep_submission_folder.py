#!/usr/bin/env python3
"""Assemble the C2PA conformance submission folder for Scott Perry's review.

Run from the enterprise_api directory:
    uv run python scripts/prep_submission_folder.py

Output: ../docs/c2pa/conformance/submission/
"""

import json
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths (all relative to enterprise_api/)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
ENTERPRISE_API_DIR = SCRIPT_DIR.parent  # enterprise_api/
REPO_ROOT = ENTERPRISE_API_DIR.parent  # encypherai-commercial/

SIGNED_DIR = ENTERPRISE_API_DIR / "tests/c2pa_conformance/signed"
MANIFESTS_DIR = ENTERPRISE_API_DIR / "tests/c2pa_conformance/manifests"
EXTENDED_EVIDENCE_DIR = ENTERPRISE_API_DIR / "tests/c2pa_conformance/extended_evidence"
INGESTION_RESULTS = ENTERPRISE_API_DIR / "tests/c2pa_conformance/ingestion_evidence/ingestion_results.json"
EXTERNAL_RESULTS = ENTERPRISE_API_DIR / "tests/c2pa_conformance/external_ingestion_evidence/external_ingestion_results.json"
CONFORMANCE_MATRIX_SRC = REPO_ROOT / "docs/c2pa/conformance/evidence/CONFORMANCE_MATRIX.md"
MIME_TYPES_SRC = REPO_ROOT / "docs/c2pa/conformance/SUBMISSION_MIME_TYPES.md"

OUTPUT_DIR = REPO_ROOT / "docs/c2pa/conformance/submission"


# ---------------------------------------------------------------------------
# Generator sample map
# Each entry: (category, subfolder, signed_filename, manifest_filename)
# ---------------------------------------------------------------------------

GENERATOR_SAMPLES = [
    # Image
    ("image", "jpeg", "signed_test.jpg", "signed_test_jpg.json"),
    ("image", "jxl", "signed_test.jxl", "signed_test_jxl.json"),
    ("image", "png", "signed_test.png", "signed_test_png.json"),
    ("image", "svg", "signed_test.svg", "signed_test_svg.json"),
    ("image", "gif", "signed_test.gif", "signed_test_gif.json"),
    ("image", "dng", "signed_test.dng", "signed_test_dng.json"),
    ("image", "tiff", "signed_test.tiff", "signed_test_tiff.json"),
    ("image", "webp", "signed_test.webp", "signed_test_webp.json"),
    ("image", "heic", "signed_test.heic", "signed_test_heic.json"),
    ("image", "heic-sequence", "signed_test_heic-sequence.heic", "signed_test_heic-sequence.json"),
    ("image", "heif", "signed_test.heif", "signed_test_heif.json"),
    ("image", "heif-sequence", "signed_test_heif-sequence.heif", "signed_test_heif-sequence.json"),
    ("image", "avif", "signed_test.avif", "signed_test_avif.json"),
    # Video
    ("video", "mp4", "signed_test.mp4", "signed_test_mp4.json"),
    ("video", "quicktime", "signed_test.mov", "signed_test_mov.json"),
    ("video", "avi", "signed_test.avi", "signed_test_avi.json"),
    # Audio
    ("audio", "flac", "signed_test.flac", "signed_test_flac.json"),
    ("audio", "mpa", "signed_test_mpa.mp3", "signed_test_mpa.json"),
    ("audio", "mpeg", "signed_test.mp3", "signed_test_mp3.json"),
    ("audio", "wav", "signed_test.wav", "signed_test_wav.json"),
    ("audio", "aac", "signed_test_aac.m4a", "signed_test_aac.json"),
    ("audio", "mp4", "signed_test.m4a", "signed_test_m4a.json"),
    # Document
    ("document", "pdf", "signed_test.pdf", "signed_test_pdf.json"),
    ("document", "epub", "signed_test.epub", "signed_test_epub.json"),
    ("document", "docx", "signed_test.docx", "signed_test_docx.json"),
    ("document", "odt", "signed_test.odt", "signed_test_odt.json"),
    ("document", "oxps", "signed_test.oxps", "signed_test_oxps.json"),
    # Font
    ("font", "otf", "signed_test.otf", "signed_test_otf.json"),
]


# ---------------------------------------------------------------------------
# README.md content (submission root)
# ---------------------------------------------------------------------------

README_CONTENT = """\
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
"""


# ---------------------------------------------------------------------------
# TEST_METHODOLOGY.md content
# ---------------------------------------------------------------------------

TEST_METHODOLOGY_CONTENT = """\
# C2PA Conformance Test Methodology

**Product**: Encypher Enterprise API v2.0.0
**Date**: 2026-03-25

This document describes how to reproduce all conformance tests from source.

---

## Prerequisites

- Python 3.11 or later
- uv (https://docs.astral.sh/uv/)
- Git clone of the encypherai-commercial repository
- All Python dependencies installed: `uv sync` from enterprise_api/

Optional for external ingestion verification:
- Node.js 20+ (for adobe_verify.mjs)

---

## Step 1 -- Run the Signing Suite

The signing suite generates minimal test fixtures for all target MIME types,
signs each file using the appropriate pipeline, and verifies each signed file
internally.

```
cd enterprise_api
uv run python tests/c2pa_conformance/run_conformance.py
```

**Output directories**:
- `tests/c2pa_conformance/fixtures/`  -- unsigned test files generated from scratch
- `tests/c2pa_conformance/signed/`    -- signed output files
- `tests/c2pa_conformance/manifests/` -- extracted manifest JSON for each file
- `tests/c2pa_conformance/results/`   -- verify_results.json + verify_all.log

**Pipeline A (c2pa-rs native)**: Used for JPEG, PNG, WebP, TIFF, GIF, HEIC,
HEIF, AVIF, SVG, DNG, MP4, MOV, AVI, WAV, MP3, M4A.  The c2pa-python 0.29.0
library (wrapping c2pa-rs 0.78.4) is used to build and sign manifests.

**Pipeline B (custom JUMBF/COSE)**: Used for JXL, FLAC, PDF, EPUB, DOCX, ODT,
OXPS.  A two-pass approach is used: pass 1 inserts a placeholder manifest,
pass 2 replaces it with the signed COSE structure.  The COSE signing uses the
same SSL.com ECC P-256 / ES256 test certificate as Pipeline A.

**Certificate**: SSL.com c2pasign test certificate
**Algorithm**: ECC P-256 / ES256
**TSA**: http://ts.ssl.com (RFC 3161), SSL.com Timestamping Unit 2025 E1

---

## Step 2 -- Run Self-Verification (Ingestion Evidence)

Self-verification uses c2pa-python Reader to re-read each signed file and
confirm that the embedded manifest is well-formed and the signature is valid.

```
cd enterprise_api
uv run python tests/c2pa_conformance/run_ingestion_evidence.py
```

**Output**:
- `tests/c2pa_conformance/ingestion_evidence/ingestion_results.json`  -- consolidated results
- `tests/c2pa_conformance/ingestion_evidence/*_evidence.json`         -- per-file evidence

The consolidated `ingestion_results.json` included in validation_evidence/self_verification/
of this submission was produced by this command.

---

## Step 3 -- Run External Verification (Interoperability)

External verification tests C2PA manifests generated by third-party
implementations against our verifier, and vice versa.

```
cd enterprise_api
uv run python tests/c2pa_conformance/run_external_ingestion.py
```

**Output**:
- `tests/c2pa_conformance/external_ingestion_evidence/external_ingestion_results.json`
- `tests/c2pa_conformance/external_ingestion_evidence/*_evidence.json`

The Google Pixel Camera, NotebookLM, Veo/Imagen, YouTube, and Pixel Recorder
sample files from the C2PA sample library were used for cross-vendor ingestion
testing.  Results are included in validation_evidence/external_interoperability/.

---

## Step 4 -- Run Unit Tests

The unit test suite covers individual utilities, signing services, and the
verify pipeline.

```
cd enterprise_api
uv run pytest tests/
```

All tests should pass.  The test suite includes:

- `tests/unit/test_c2pa_shared.py`        -- shared signing utilities
- `tests/unit/test_document_signing.py`   -- PDF, EPUB, DOCX, ODT, OXPS
- `tests/unit/test_flac_embedder.py`      -- FLAC JUMBF/COSE pipeline
- `tests/unit/test_image_format_registry.py` -- image format routing
- `tests/test_leaf_hash_verification.py`  -- Merkle leaf hash verification
- `tests/test_unified_verify.py`          -- unified verify endpoint

---

## Signing Pipeline Details

### Pipeline A -- c2pa-rs native

Source files:
- `app/services/image_signing_service.py`
- `app/services/video_signing_service.py`
- `app/services/audio_signing_service.py`
- `app/utils/c2pa_manifest.py`
- `app/utils/c2pa_signer.py`
- `app/utils/c2pa_trust_list.py`

The c2pa.Builder API is used to construct a manifest with:
- `c2pa.actions` assertion (recording the signing action)
- Soft binding via `c2pa.hash.data` (file hash, excluding manifest bytes)
- Claim generator set to `Encypher Enterprise API/2.0.0`

The builder is then signed using the SSL.com test certificate (PEM chain +
private key).  The RFC 3161 TSA at http://ts.ssl.com is used for timestamping.

### Pipeline B -- Custom JUMBF/COSE

Source files:
- `app/utils/jumbf.py`              -- JUMBF box serialization
- `app/utils/cose_signer.py`        -- COSE Sign1 structure
- `app/utils/c2pa_claim_builder.py` -- C2PA Claim CBOR construction
- `app/utils/pdf_c2pa_embedder.py`  -- PDF byte-range insertion
- `app/utils/flac_c2pa_embedder.py` -- FLAC APPLICATION block
- `app/utils/jxl_c2pa_embedder.py`  -- JXL ISOBMFF c2pa box
- `app/utils/zip_c2pa_embedder.py`  -- ZIP manifest (EPUB, DOCX, ODT, OXPS)

The custom pipeline implements the C2PA 2.1 JUMBF manifest store structure
directly.  The COSE Sign1 payload is a CBOR-encoded C2PA Claim.  The same
SSL.com ECC P-256 / ES256 test certificate is used.

---

## Certificate Details

The test certificate chain is stored in `tests/c2pa_test_certs/`.

- **Leaf certificate**: CN=Encypher Conformance Test Cert, O=Encypher Corporation
- **Issuer**: SSL.com (c2pasign OID in EKU)
- **Algorithm**: ECC P-256 / ES256
- **TSA**: http://ts.ssl.com (RFC 3161), SSL.com Timestamping Unit 2025 E1

The certificate includes the C2PA required Extended Key Usage OID
(1.3.6.1.4.1.57264.1.x) issued via SSL.com staging.
"""


# ---------------------------------------------------------------------------
# external_ingestion evidence README
# ---------------------------------------------------------------------------

EXTERNAL_EVIDENCE_README_CONTENT = """\
# External Interoperability Evidence

This directory contains the results of testing C2PA manifests from third-party
implementations against Encypher's verifier.

## Files

- `external_ingestion_results.json` -- consolidated verification results for
  all third-party sample files

## Sources Tested

The following third-party C2PA implementations were tested:

**Google Pixel Camera (Prod)**
Real device captures including standard photos, 50MP mode, Portrait, Panorama,
Burst, Action Pan, Video Snapshot, and Add Me composite captures.

**Google Photos (Prod)**
Magic Editor, Magic Eraser, Crop, Zoom Enhance, and other AI edit operations.

**NotebookLM (Prod)**
Infographic generation output.

**Veo, Imagen, and Nano Banana (Prod)**
Text-to-image, text-to-video, image-to-video, and NanoBananaPro outputs.

**YouTube (Prod)**
Inspiration thumbnail content.

**Pixel Recorder (Prod)**
Audio recordings with C2PA provenance.

## Verification Method

Each file was passed to the Encypher verify endpoint and the raw c2pa-python
Reader.  The per-file evidence JSON files record:
- Whether a manifest was detected
- Whether the signature was valid
- The claim generator string (identifies the signing implementation)
- Any validation errors or trust list results

## Scope

External verification tests that our verifier correctly ingests and validates
manifests produced by other C2PA implementations.  It does not test that those
implementations can ingest our manifests -- that cross-direction test would
require uploading our signed files to each vendor's verification tool.
"""


# ---------------------------------------------------------------------------
# extended_capabilities README
# ---------------------------------------------------------------------------

EXTENDED_CAPABILITIES_README_CONTENT = """\
# Extended Capabilities

This section documents two production Encypher capabilities that go beyond the
current C2PA conformance program submission categories. Both are defined in the
C2PA v2.3 specification but are not yet covered by conformance testing.

Evidence files, signed samples, and verification results are included below.
We are happy to help strengthen the conformance program with these capabilities
-- for example, by providing test vectors, verification tooling, or
specification contributions.

---

## 1. Live Video Streaming (Per-Segment C2PA Signing)

**Spec reference**: C2PA v2.3, Section 19 (Live Streaming)

**Description**

Encypher's video stream signing service applies C2PA provenance to live video
at the segment level:

    RTMP ingest -> per-segment C2PA signing -> HLS delivery with manifests

Each segment is signed independently with a `c2pa.livevideo.segment` assertion
containing `sequenceNumber`, `streamId`, and backward `previousManifestId`
chaining via `continuityMethod: "c2pa.manifestId"`. A SHA-256 Merkle tree over
segment manifest hashes provides a finalization root for the complete stream.

**Implementation**

Source: `enterprise_api/app/services/video_stream_signing_service.py`

Pipeline: c2pa-rs (c2pa-python 0.29.0 / c2pa-rs 0.78.4), ECC P-256 / ES256,
SSL.com TSA (RFC 3161).

**Evidence files**

| File | Description |
|------|-------------|
| live_video_streaming_evidence.json | Full session: 3 segments signed, verified, Merkle root finalized |
| signed_stream_segment_0.mp4 | Signed MP4 segment (17,385 bytes) with c2pa.livevideo.segment assertion |

**Results summary**

- 3 segments signed (segment 0: 17,385 bytes, segments 1-2: 17,451 bytes)
- All 3 segments verified valid (c2pa-python Reader)
- Merkle root: sha256:d500354c92eccbc900d95909190ea97448dcd1d0e31fd13ef11f6512b6c7bef2
- Backward manifest chaining verified across all segments
- Certificate: CN=Encypher Conformance Test Cert, O=Encypher Corporation

---

## 2. Unstructured Text Provenance (C2PA Text Manifests)

**Spec reference**: C2PA v2.3, Manifests_Text.adoc

**Description**

Encypher embeds C2PA-compatible manifests in plain text using Unicode Variation
Selectors (U+FE00-FE0F, U+E0100-E01EF) as defined in Manifests_Text.adoc.
This allows content provenance for text that has no binary file container --
web pages, messaging platforms, social media posts, and AI-generated text output.

**Implementation**

Source: `encypher` Python SDK (`UnicodeMetadata.embed_metadata()`)

Pipeline: Ed25519 COSE_Sign1 signing, Unicode Variation Selector embedding,
hard binding via content hash.

**Evidence files**

| File | Description |
|------|-------------|
| text_c2pa_evidence.json | Sign, verify, and tamper detection results |
| signed_text_sample.txt | Signed text file with embedded C2PA manifest (1,656 chars, 1,410 embedded) |

**Results summary**

- Original text: 246 characters
- Signed text: 1,656 characters (1,410 invisible variation selector characters embedded)
- Verification: PASS (signature valid, signer_id recovered, hard binding verified)
- Tamper detection: PASS (modified text correctly rejected with hash mismatch)
- Claim generator: Encypher Enterprise API/2.0
- Actions: c2pa.created
- Custom assertions: com.encypher.provenance
- Hard binding: enabled (content hash integrity)

---

## Contact

If the C2PA working group is interested in test vectors, specification drafts,
or implementation contributions for either capability, please contact
conformance@encypher.com.

We can also provide access to our File Inspector verification tool
(https://encypher.com/tools/file-inspector) for testing manifests produced
by any implementation against our verifier.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path, label: str) -> bool:
    """Copy src to dst.  Returns True on success, prints warning on missing src."""
    if not src.exists():
        print(f"  WARNING: source not found, skipping: {src}")
        return False
    shutil.copy2(src, dst)
    print(f"  copied  {label}")
    return True


def write_text(path: Path, content: str, label: str) -> None:
    path.write_text(content, encoding="ascii", errors="replace")
    print(f"  wrote   {label}")


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------


def build_submission() -> None:
    print(f"\nBuilding submission folder at: {OUTPUT_DIR}\n")

    # Wipe and recreate output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    ensure_dir(OUTPUT_DIR)

    # ------------------------------------------------------------------
    # 1. Root README.md
    # ------------------------------------------------------------------
    print("[1/6] Writing root README.md ...")
    write_text(OUTPUT_DIR / "README.md", README_CONTENT, "README.md")

    # ------------------------------------------------------------------
    # 2. generator_samples/
    # ------------------------------------------------------------------
    print("[2/6] Copying generator samples ...")
    missing_files: list[str] = []

    for category, subfolder, signed_fname, manifest_fname in GENERATOR_SAMPLES:
        dest_dir = OUTPUT_DIR / "generator_samples" / category / subfolder
        ensure_dir(dest_dir)

        signed_src = SIGNED_DIR / signed_fname
        manifest_src = MANIFESTS_DIR / manifest_fname

        ok1 = copy_file(signed_src, dest_dir / signed_fname, f"generator_samples/{category}/{subfolder}/{signed_fname}")
        ok2 = copy_file(manifest_src, dest_dir / manifest_fname, f"generator_samples/{category}/{subfolder}/{manifest_fname}")

        if not ok1:
            missing_files.append(str(signed_src))
        if not ok2:
            missing_files.append(str(manifest_src))

    # ------------------------------------------------------------------
    # 3. validation_evidence/
    # ------------------------------------------------------------------
    print("[3/6] Copying validation evidence ...")

    # self_verification/
    self_ver_dir = OUTPUT_DIR / "validation_evidence/self_verification"
    ensure_dir(self_ver_dir)
    copy_file(
        INGESTION_RESULTS,
        self_ver_dir / "ingestion_results.json",
        "validation_evidence/self_verification/ingestion_results.json",
    )

    # external_interoperability/
    ext_dir = OUTPUT_DIR / "validation_evidence/external_interoperability"
    ensure_dir(ext_dir)
    copy_file(
        EXTERNAL_RESULTS,
        ext_dir / "external_ingestion_results.json",
        "validation_evidence/external_interoperability/external_ingestion_results.json",
    )
    write_text(
        ext_dir / "README.md",
        EXTERNAL_EVIDENCE_README_CONTENT,
        "validation_evidence/external_interoperability/README.md",
    )

    # ------------------------------------------------------------------
    # 4. test_methodology/
    # ------------------------------------------------------------------
    print("[4/6] Building test_methodology/ ...")
    methodology_dir = OUTPUT_DIR / "test_methodology"
    ensure_dir(methodology_dir)

    write_text(methodology_dir / "TEST_METHODOLOGY.md", TEST_METHODOLOGY_CONTENT, "test_methodology/TEST_METHODOLOGY.md")

    copy_file(
        CONFORMANCE_MATRIX_SRC,
        methodology_dir / "CONFORMANCE_MATRIX.md",
        "test_methodology/CONFORMANCE_MATRIX.md",
    )
    copy_file(
        MIME_TYPES_SRC,
        methodology_dir / "MIME_TYPE_INVENTORY.md",
        "test_methodology/MIME_TYPE_INVENTORY.md",
    )

    # ------------------------------------------------------------------
    # 5. extended_capabilities/
    # ------------------------------------------------------------------
    print("[5/6] Writing extended_capabilities/ ...")
    ext_cap_dir = OUTPUT_DIR / "extended_capabilities"
    ensure_dir(ext_cap_dir)
    write_text(
        ext_cap_dir / "README.md",
        EXTENDED_CAPABILITIES_README_CONTENT,
        "extended_capabilities/README.md",
    )

    # Copy evidence files from extended_evidence directory
    ext_evidence_files = [
        "live_video_streaming_evidence.json",
        "signed_stream_segment_0.mp4",
        "text_c2pa_evidence.json",
        "signed_text_sample.txt",
    ]
    for fname in ext_evidence_files:
        copy_file(
            EXTENDED_EVIDENCE_DIR / fname,
            ext_cap_dir / fname,
            f"extended_capabilities/{fname}",
        )

    # ------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------
    print("[6/6] Generating summary ...")
    all_files = sorted(OUTPUT_DIR.rglob("*"))
    file_list = [str(f.relative_to(OUTPUT_DIR)) for f in all_files if f.is_file()]

    summary = {
        "output_dir": str(OUTPUT_DIR),
        "total_files": len(file_list),
        "missing_source_files": missing_files,
        "files": file_list,
    }
    summary_path = OUTPUT_DIR / "_assembly_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nDone.  {len(file_list)} files written to {OUTPUT_DIR}")

    if missing_files:
        print(f"\nWARNING: {len(missing_files)} source file(s) were missing:")
        for mf in missing_files:
            print(f"  - {mf}")
        print("\nRun the conformance suite first:")
        print("  cd enterprise_api")
        print("  uv run python tests/c2pa_conformance/run_conformance.py")
        print("  uv run python tests/c2pa_conformance/run_ingestion_evidence.py")
        print("  uv run python tests/c2pa_conformance/run_external_ingestion.py")
        sys.exit(1)


if __name__ == "__main__":
    build_submission()
