# DOCX -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | DOCX (Office Open XML Word Document) |
| MIME type | application/vnd.openxmlformats-officedocument.wordprocessingml.document |
| Extensions | .docx |
| Category | Document |
| Pipeline | Custom JUMBF/COSE (Encypher ZIP-based pipeline) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Conformance suite entry | No -- unit tested only |

## Coverage Status

Signing for DOCX has been tested via unit tests in:
tests/unit/test_document_signing.py

DOCX has NOT been included in the conformance suite run (verify_results.json).
No conformance-suite-generated manifest JSON or verify_results entry exists for DOCX.
A full conformance suite run including DOCX is planned for a future release.

## Pipeline Architecture

DOCX is a ZIP-based container (Office Open XML). The Encypher signing pipeline for DOCX:
1. Opens the DOCX ZIP archive
2. Inserts a placeholder file entry of known size
3. Computes SHA-256 hash over the archive content excluding the placeholder byte range
4. Builds CBOR claim and signs with COSE_Sign1 (ES256)
5. Serializes full JUMBF manifest store
6. Replaces placeholder bytes in the ZIP archive with the signed JUMBF manifest

Implementation: enterprise_api/app/utils/zip_c2pa_embedder.py

## Unit Test Reference

Test file: enterprise_api/tests/unit/test_document_signing.py
Tests cover: signing pipeline, CBOR claim structure, COSE signature, JUMBF serialization,
ZIP structural integrity of output (verifies output is a valid ZIP with intact DOCX structure).

## Adobe Content Credentials Verify

Not applicable -- no conformance suite run performed. No signed artifact available
for Adobe verification testing.
