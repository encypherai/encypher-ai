# HEIC -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | HEIC |
| MIME type | image/heic |
| Aliases accepted | image/heic-sequence (animated; signed as image/heic) |
| Extensions | .heic |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media) |
| Hash assertion | c2pa.hash.bmff.v3 (BMFF box-level hash) |
| Thumbnail in manifest | No (BMFF-container images do not embed a thumbnail) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:18Z |
| Fixture file size | 459 bytes |
| Signed file size | 15,301 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.heic |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_heic.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:c090a181-f52f-4457-90c8-6b6b17e22adb |
| title | C2PA Conformance Test -- HEIC |
| instance_id (manifest) | xmp:iid:a1991d68-c4d2-4477-b052-1138e5483451 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.67.1 |
| signature_info.alg | Es256 |
| signature_info.issuer | Encypher Corporation |
| signature_info.common_name | Encypher Conformance Test Cert |
| signature_info.cert_serial_number | 8149767912641611982350984011013689761321125 |
| signature_info.time | 2026-03-25T08:33:18+00:00 |
| validation_state | Valid |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture |
| c2pa.hash.bmff.v3 | SHA-256 BMFF box hash, alg: sha256, hash: 3BDDvsXj9tg+zx2Z9RWOzzLyWDfWbapZ2T5PT0ONDBQ= |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-heic, image_id: 927ed891-45d7-45ce-a6ad-837d4c994e86 |

BMFF exclusions: /uuid (manifest box, with c2pa UUID offset), /ftyp, /mfra

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:90b14b0b-6952-45bd-b87f-4554b8e83a2e
verify_results verify_success: true

| Validation Code | Success | Explanation |
|----------------|---------|-------------|
| timeStamp.validated | true | timestamp message digest matched: SSL.com Timestamping Unit 2025 E1 |
| claimSignature.insideValidity | true | claim signature valid |
| claimSignature.validated | true | claim signature valid |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.actions.v2 |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.hash.bmff.v3 |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/com.encypher.provenance |
| assertion.bmffHash.match | true | data hash valid |

Informational (not a failure): timeStamp.untrusted -- conformance test TSA certificate not yet on trust list.
Failure codes: none.

## Adobe Content Credentials Verify

| Field | Value |
|-------|-------|
| Result | PASS -- manifest parsed and signer identity displayed |
| Trust status | Unrecognized (expected for conformance test certificate) |
| Screenshot | [heic_adobe_verify.png](../screenshots/heic_adobe_verify.png) |
