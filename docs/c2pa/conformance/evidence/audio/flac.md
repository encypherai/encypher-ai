# FLAC - C2PA Conformance Evidence

## Format Details
- MIME Type: audio/flac
- Extension: .flac
- Category: Audio
- Pipeline: Custom JUMBF/COSE (Encypher document signing pipeline)

## Signing Evidence
- Method: FLAC APPLICATION metadata block embedding (block type 2, app ID "c2pa")
- Content binding: c2pa.hash.data with exclusion range for manifest data
- Two-pass approach: placeholder insertion -> hash -> sign -> replace
- Signature algorithm: ECC P-256 / ES256 (COSE_Sign1_Tagged)
- Test file: tests/c2pa_conformance/fixtures/test.flac (42 bytes, minimal STREAMINFO-only)
- Signed file: tests/c2pa_conformance/signed/signed_test.flac (65,586 bytes)
- Sign: PASS
- Verify: PASS (structural - JUMBF markers present)

## Verification Evidence
- Internal structural verification confirms JUMBF/C2PA markers embedded
- c2pa-python Reader does not support FLAC (c2pa-rs 0.78.4 lacks FLAC support)
- Custom embedder implements same two-pass pattern as PDF/font pipeline

## Notes
- c2pa-rs added FLAC support in 0.78.6 but not yet available in c2pa-python wrapper
- Encypher implements custom FLAC embedding using FLAC APPLICATION metadata blocks
- Same COSE/JUMBF infrastructure used for PDF, ZIP-based documents, and fonts
