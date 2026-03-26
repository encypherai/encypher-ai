# MP3 -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | MP3 |
| MIME type | audio/mpeg |
| Extensions | .mp3 |
| Category | Audio |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:20Z |
| Fixture file size | 5,977 bytes |
| Signed file size | 20,651 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.mp3 |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_mp3.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:61154e0b-86df-4349-ac83-9f5ddca17d8f |
| title | C2PA Conformance Test -- MP3 |
| instance_id (manifest) | xmp:iid:5ff37f0b-7942-449a-a23e-22e79be65d4e |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.67.1 |
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
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-mp3, audio_id: 4d82602c-1805-4b30-81f6-b299d173d6e1 |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:4b140d24-6123-4258-b24e-935ee8db00d8
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
| Screenshot | [mp3_adobe_verify.png](../screenshots/mp3_adobe_verify.png) |
