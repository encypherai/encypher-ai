# OXPS -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | OXPS (Open XML Paper Specification) |
| MIME type | application/oxps |
| Extensions | .oxps |
| Category | Document |
| Pipeline | Custom JUMBF/COSE (Encypher ZIP-based pipeline) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Conformance suite entry | No -- unit tested only |

## Coverage Status

Signing for OXPS has been tested via unit tests in:
tests/unit/test_document_signing.py

OXPS has NOT been included in the conformance suite run (verify_results.json).
No conformance-suite-generated manifest JSON or verify_results entry exists for OXPS.
A full conformance suite run including OXPS is planned for a future release.

## Pipeline Architecture

OXPS is a ZIP-based container (Open XML Paper Specification, ECMA-388). The Encypher
signing pipeline for OXPS:
1. Opens the OXPS ZIP archive
2. Inserts a placeholder file entry of known size
3. Computes SHA-256 hash over the archive content excluding the placeholder byte range
4. Builds CBOR claim and signs with COSE_Sign1 (ES256)
5. Serializes full JUMBF manifest store
6. Replaces placeholder bytes in the ZIP archive with the signed JUMBF manifest

Implementation: enterprise_api/app/utils/zip_c2pa_embedder.py

## Unit Test Reference

Test file: enterprise_api/tests/unit/test_document_signing.py
Tests cover: signing pipeline, CBOR claim structure, COSE signature, JUMBF serialization,
ZIP structural integrity of output.

## Adobe Content Credentials Verify

Not applicable -- no conformance suite run performed. No signed artifact available
for Adobe verification testing. OXPS is a relatively uncommon format and Adobe's tool
is unlikely to support it regardless.
