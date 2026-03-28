# JPEG -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | JPEG |
| MIME type | image/jpeg |
| Aliases accepted | image/jpg |
| Extensions | .jpg, .jpeg |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Thumbnail in manifest | Yes (image/jpeg) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:16Z |
| Fixture file size | 1,306 bytes |
| Signed file size | 45,435 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.jpg |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_jpg.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:b75cdef3-1173-4946-ae17-66d74997a358 |
| title | C2PA Conformance Test -- JPEG |
| instance_id (manifest) | xmp:iid:b562f4be-10b8-4938-ae74-f9b69e89c03a |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.78.4 |
| signature_info.alg | Es256 |
| signature_info.issuer | Encypher Corporation |
| signature_info.common_name | Encypher Conformance Test Cert |
| signature_info.cert_serial_number | 8149767912641611982350984011013689761321125 |
| signature_info.time | 2026-03-25T08:33:16+00:00 |
| validation_state | Valid |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture |
| c2pa.thumbnail.claim | JPEG thumbnail embedded in JUMBF manifest store |
| c2pa.hash.data | SHA-256 byte-range hash |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-jpeg, image_id: 7149f719-ac8c-4dca-81cd-0f43bfac3297 |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:672e4347-85a7-4e06-ad0a-2926e26f8830
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
| Screenshot | [jpeg_adobe_verify.png](../screenshots/jpeg_adobe_verify.png) |

JPEG was one of four formats tested in the interoperability round (INTEROP_TEST_REPORT.md).
Adobe displayed: signer "Encypher Conformance Test Cert", issuer "Encypher Corporation",
action "Created", RFC 3161 timestamp from SSL.com.
