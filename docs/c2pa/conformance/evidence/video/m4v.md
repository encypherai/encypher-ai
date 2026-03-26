# M4V (video/x-m4v) -- C2PA Conformance Evidence

**Pipeline**: c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media)
**Hash assertion**: c2pa.hash.bmff.v3

## Signing Result

| Field | Value |
|-------|-------|
| Format | M4V (video/x-m4v) |
| Fixture size | 2,215 bytes |
| Signed size | 17,218 bytes |
| Sign result | PASS |

## Manifest Details

| Field | Value |
|-------|-------|
| Active manifest | urn:c2pa:1628dc7f-fb46-4ed7-b288-cd8f995659cf |
| Title | C2PA Conformance Test -- M4V |
| Instance ID | xmp:iid:074d642f-d4d0-46f0-b800-e49e1c73764f |
| Claim generator | Encypher 1.0 |
| Algorithm | Es256 (ECC P-256) |
| Issuer | Encypher Corporation |
| Common name | Encypher Conformance Test Cert |
| Signed at | 2026-03-25T09:09:35Z |
| Timestamp | 2026-03-25T09:09:36+00:00 (SSL.com TSA) |
| Validation state | Valid |

## Assertions

- `c2pa.actions.v2`: c2pa.created, digitalSourceType: digitalCapture
- `c2pa.hash.bmff.v3`: SHA-256, BMFF box exclusions (/uuid, /ftyp, /mfra, /free, /skip)
- `com.encypher.provenance`: document_id: conformance-m4v, organization_id: encypher-conformance

## Verification Validation Codes (7 success)

| Code | Result | Detail |
|------|--------|--------|
| timeStamp.validated | SUCCESS | timestamp message digest matched: SSL.com Timestamping Unit 2025 E1 |
| claimSignature.insideValidity | SUCCESS | claim signature valid |
| claimSignature.validated | SUCCESS | claim signature valid |
| assertion.hashedURI.match | SUCCESS | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.hash.bmff.v3 |
| assertion.hashedURI.match | SUCCESS | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.actions.v2 |
| assertion.hashedURI.match | SUCCESS | hashed uri matched: self#jumbf=c2pa.assertions/com.encypher.provenance |
| assertion.bmffHash.match | SUCCESS | BMFF hash valid |

## Adobe Content Credentials Verify

Not tested (M4V not commonly uploaded to Adobe's tool).

## Primary Sources

- Signed file: `tests/c2pa_conformance/signed/signed_test.m4v`
- Manifest JSON: `tests/c2pa_conformance/manifests/signed_test_m4v.json`
- Verify results: `tests/c2pa_conformance/results/verify_results.json`
- Ingestion evidence: `tests/c2pa_conformance/ingestion_evidence/signed_test_m4v_evidence.json`
