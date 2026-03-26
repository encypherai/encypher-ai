# WAV -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | WAV |
| MIME type | audio/wav |
| Extensions | .wav |
| Category | Audio |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:20Z |
| Fixture file size | 88,244 bytes |
| Signed file size | 102,870 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.wav |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_wav.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:a849e755-acc8-4002-9c88-a499fccb7bde |
| title | C2PA Conformance Test -- WAV |
| instance_id (manifest) | xmp:iid:ccc9f45d-78f2-4fe4-8745-826a043b2cc8 |
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
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-wav, audio_id: 2e8eb5bd-9f81-41b6-9e48-6628cf543a24 |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:d0eca172-1493-4242-8935-d8a3da301fdb
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
| Screenshot | [wav_adobe_verify.png](../screenshots/wav_adobe_verify.png) |

WAV was one of four formats tested in the interoperability round (INTEROP_TEST_REPORT.md).
Adobe displayed: signer "Encypher Conformance Test Cert", issuer "Encypher Corporation",
action "Created", RFC 3161 timestamp from SSL.com.
