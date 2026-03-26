# WebP -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | WebP |
| MIME type | image/webp |
| Extensions | .webp |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Thumbnail in manifest | Yes (image/webp) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:17Z |
| Fixture file size | 164 bytes |
| Signed file size | 15,658 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.webp |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_webp.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:e6fdbff4-312a-47bf-a292-7ee525ed15a6 |
| title | C2PA Conformance Test -- WebP |
| instance_id (manifest) | xmp:iid:01d3d160-c374-4ed1-9431-f60feef41a10 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.67.1 |
| signature_info.alg | Es256 |
| signature_info.issuer | Encypher Corporation |
| signature_info.common_name | Encypher Conformance Test Cert |
| signature_info.cert_serial_number | 8149767912641611982350984011013689761321125 |
| signature_info.time | 2026-03-25T08:33:17+00:00 |
| validation_state | Valid |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture |
| c2pa.thumbnail.claim | WebP thumbnail embedded in JUMBF manifest store |
| c2pa.hash.data | SHA-256 byte-range hash |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-webp, image_id: 22f04885-4276-4675-ba38-bb795031ebe9 |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:81db17dd-3bab-45cc-91dc-e9375d95c256
verify_results verify_success: true

| Validation Code | Success | Explanation |
|----------------|---------|-------------|
| timeStamp.validated | true | timestamp message digest matched: SSL.com Timestamping Unit 2025 E1 |
| claimSignature.insideValidity | true | claim signature valid |
| claimSignature.validated | true | claim signature valid |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.thumbnail.claim |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.actions.v2 |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/c2pa.hash.data |
| assertion.hashedURI.match | true | hashed uri matched: self#jumbf=c2pa.assertions/com.encypher.provenance |
| assertion.dataHash.match | true | data hash valid |

Informational (not a failure): timeStamp.untrusted -- conformance test TSA certificate not yet on trust list.
Failure codes: none.

## Adobe Content Credentials Verify

| Field | Value |
|-------|-------|
| Result | PASS -- manifest parsed and signer identity displayed |
| Trust status | Unrecognized (expected for conformance test certificate) |
| Screenshot | [webp_adobe_verify.png](../screenshots/webp_adobe_verify.png) |
