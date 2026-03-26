# OTF (font/otf) -- C2PA Conformance Evidence

**Pipeline**: Custom JUMBF/COSE (SFNT C2PA table embedder)
**Hash assertion**: c2pa.hash.data (byte-range exclusion)
**Verification method**: JUMBF structural verification

## Signing Result

| Field | Value |
|-------|-------|
| Format | OTF (font/otf) |
| Fixture size | 60 bytes |
| Signed size | 65,612 bytes |
| Sign result | PASS |
| Embedding method | SFNT C2PA table |

## Manifest Details

| Field | Value |
|-------|-------|
| Active manifest | urn:c2pa:1eefbb88-824b-45c1-9d8f-b494a205aff4 |
| Instance ID | urn:uuid:4f599bb3-4657-4d8c-8248-9eaa277e2e8a |
| Claim generator | Encypher Enterprise API/2.0 |
| JUMBF present | Yes |
| C2PA marker present | Yes |
| Signature present | Yes |
| Claim CBOR size | 621 bytes |
| COSE signature size | 27,255 bytes |

## Assertions

- `c2pa.actions.v2`: c2pa.created
- `c2pa.hash.data`: SHA-256, byte-range exclusion covering JUMBF manifest store
- `com.encypher.provenance`: conformance test metadata

## Structural Verification

| Check | Result |
|-------|--------|
| JUMBF present | PASS |
| C2PA marker present | PASS |
| COSE signature present | PASS |
| Manifest parseable | PASS |
| Assertion count | 3 (expected) |

## Notes

OTF uses the same SFNT C2PA table embedding as TTF and SFNT. The custom
JUMBF/COSE pipeline inserts a C2PA SFNT table containing the JUMBF manifest
store. c2pa-python Reader cannot natively read SFNT-embedded manifests, so
verification is structural (JUMBF parse + COSE signature presence).

## Primary Sources

- Signed file: `tests/c2pa_conformance/signed/signed_test.otf`
- Manifest JSON: `tests/c2pa_conformance/manifests/signed_test_otf.json`
- Verify results: `tests/c2pa_conformance/results/verify_results.json`
- Ingestion evidence: `tests/c2pa_conformance/ingestion_evidence/signed_test_otf_evidence.json`
