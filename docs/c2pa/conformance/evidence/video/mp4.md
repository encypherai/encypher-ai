# MP4 -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | MP4 |
| MIME type | video/mp4 |
| Extensions | .mp4 |
| Category | Video |
| Pipeline | c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media) |
| Hash assertion | c2pa.hash.bmff.v3 (BMFF box-level hash) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:19Z |
| Fixture file size | 8,448 bytes |
| Signed file size | 23,288 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.mp4 |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_mp4.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:5870d2b4-2efa-4223-850d-4074ac5dde1a |
| title | C2PA Conformance Test -- MP4 |
| instance_id (manifest) | xmp:iid:9c4d5b88-43f0-4012-8a75-619396c6966d |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.78.4 |
| signature_info.alg | Es256 |
| signature_info.issuer | Encypher Corporation |
| signature_info.common_name | Encypher Conformance Test Cert |
| signature_info.cert_serial_number | 8149767912641611982350984011013689761321125 |
| signature_info.time | 2026-03-25T08:33:19+00:00 |
| validation_state | Valid |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture |
| c2pa.hash.bmff.v3 | SHA-256 BMFF box hash, alg: sha256, hash: ho6eZZ39R91QE9VlG3MyKtLmqG0QK52OA5jj7Q9RUCA= |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-mp4, video_id: cd9f127f-aeed-400f-a284-0e1ff9e7c7fe |

BMFF exclusions: /uuid (manifest box, with c2pa UUID offset), /ftyp, /mfra

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:4a95efce-f6e4-43e5-ab7e-2b18c23742ee
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
| Screenshot | [mp4_adobe_verify.png](../screenshots/mp4_adobe_verify.png) |

MP4 was one of four formats tested in the interoperability round (INTEROP_TEST_REPORT.md).
Adobe displayed: signer "Encypher Conformance Test Cert", issuer "Encypher Corporation",
action "Created", RFC 3161 timestamp from SSL.com.
