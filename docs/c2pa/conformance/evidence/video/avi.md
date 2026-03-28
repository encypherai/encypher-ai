# AVI -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | AVI (Audio Video Interleave) |
| MIME type | video/x-msvideo |
| Extensions | .avi |
| Category | Video |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Conformance suite entry | Yes |

AVI uses RIFF container framing, not BMFF. c2pa-rs uses c2pa.hash.data (byte-range exclusion)
rather than BMFF box hashing. This is the same hash binding type as WAV, MP3, JPEG, and PNG.

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:20Z |
| Fixture file size | 7,436 bytes |
| Signed file size | 22,060 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.avi |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_avi.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:9b57b1fb-a06d-4807-a571-04bf70ad24ec |
| title | C2PA Conformance Test -- AVI |
| instance_id (manifest) | xmp:iid:a59eb6e9-a7d6-46e9-aa90-a161028e980b |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.78.4 |
| signature_info.alg | Es256 |
| signature_info.issuer | Encypher Corporation |
| signature_info.common_name | Encypher Conformance Test Cert |
| signature_info.cert_serial_number | 8149767912641611982350984011013689761321125 |
| signature_info.time | 2026-03-25T08:33:20+00:00 |
| validation_state | Valid |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture |
| c2pa.hash.data | SHA-256 byte-range hash |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-avi, video_id: 00a160c6-55ba-4ac8-9beb-d2430c440e7c |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:7b5dd219-7785-41f6-9966-20ac36efa30f
verify_results verify_success: true

| Validation Code | Success | Explanation |
|----------------|---------|-------------|
| timeStamp.validated | true | timestamp message digest matched: SSL.com Timestamping Unit 2025 E1 |
| claimSignature.insideValidity | true | claim signature valid |
| claimSignature.validated | true | claim signature valid |
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
| Screenshot | [avi_adobe_verify.png](../screenshots/avi_adobe_verify.png) |
