# PNG -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | PNG |
| MIME type | image/png |
| Extensions | .png |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Thumbnail in manifest | Yes (image/png) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:16Z |
| Fixture file size | 594 bytes |
| Signed file size | 21,779 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.png |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_png.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:68ce75ff-8494-4ddc-a513-28b4b2c1d6fc |
| title | C2PA Conformance Test -- PNG |
| instance_id (manifest) | xmp:iid:3e4a0455-42d8-4c3f-a219-09010f55258d |
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
| c2pa.thumbnail.claim | PNG thumbnail embedded in JUMBF manifest store |
| c2pa.hash.data | SHA-256 byte-range hash |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-png, image_id: 95137dc9-0507-4a4d-a258-90f4914f616f |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:3f9d7317-5be6-41a3-b9e7-f32d37384595
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
| Screenshot | [png_adobe_verify.png](../screenshots/png_adobe_verify.png) |

PNG was one of four formats tested in the interoperability round (INTEROP_TEST_REPORT.md).
Adobe displayed: signer "Encypher Conformance Test Cert", issuer "Encypher Corporation",
action "Created", RFC 3161 timestamp from SSL.com.
