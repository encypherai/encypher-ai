# EPUB -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | EPUB (Electronic Publication) |
| MIME type | application/epub+zip |
| Extensions | .epub |
| Category | Document |
| Pipeline | Custom JUMBF/COSE (Encypher ZIP-based pipeline) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Conformance suite entry | No -- unit tested only |

## Coverage Status

Signing for EPUB has been tested via unit tests in:
tests/unit/test_document_signing.py

EPUB has NOT been included in the conformance suite run (verify_results.json).
No conformance-suite-generated manifest JSON or verify_results entry exists for EPUB.
A full conformance suite run including EPUB is planned for a future release.

## Pipeline Architecture

EPUB is a ZIP-based container format. The Encypher signing pipeline for EPUB:
1. Opens the EPUB ZIP archive
2. Inserts a placeholder file entry of known size (or appends to an existing manifest store entry)
3. Computes SHA-256 hash over the archive content excluding the placeholder byte range
4. Builds CBOR claim and signs with COSE_Sign1 (ES256)
5. Serializes full JUMBF manifest store
6. Replaces placeholder bytes in the ZIP archive with the signed JUMBF manifest

This follows the same general approach as PDF but adapted for ZIP container structure.
Implementation: enterprise_api/app/utils/zip_c2pa_embedder.py

## Unit Test Reference

Test file: enterprise_api/tests/unit/test_document_signing.py
Tests cover: signing pipeline, CBOR claim structure, COSE signature, JUMBF serialization,
ZIP structural integrity of output.

## Adobe Content Credentials Verify

Not applicable -- no conformance suite run performed. No signed artifact available
for Adobe verification testing.
