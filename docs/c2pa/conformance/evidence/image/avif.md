# AVIF -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | AVIF |
| MIME type | image/avif |
| Extensions | .avif |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media) |
| Hash assertion | c2pa.hash.bmff.v3 (BMFF box-level hash) |
| Thumbnail in manifest | No (BMFF-container images do not embed a thumbnail) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:17Z |
| Fixture file size | 326 bytes |
| Signed file size | 15,168 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.avif |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_avif.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:06aea5d5-f92d-4831-8cf9-e3acd7c90f0f |
| title | C2PA Conformance Test -- AVIF |
| instance_id (manifest) | xmp:iid:0d2872bf-eec6-47d1-a6e4-0978edb65f47 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.78.4 |
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
| c2pa.hash.bmff.v3 | SHA-256 BMFF box hash, alg: sha256, hash: b+63KllXi7Rs/UthxbicCPaIftma+MtpO4N/o9mXziE= |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-avif, image_id: 3f29f304-a6f7-4fae-b4ac-d5e760d52250 |

BMFF exclusions: /uuid (manifest box, with c2pa UUID offset), /ftyp, /mfra

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:56d05853-914a-4d2f-a079-5eb34c94ca00
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
| Screenshot | [avif_adobe_verify.png](../screenshots/avif_adobe_verify.png) |
