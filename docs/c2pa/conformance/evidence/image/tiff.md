# TIFF -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | TIFF |
| MIME type | image/tiff |
| Extensions | .tiff, .tif |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Thumbnail in manifest | Yes (image/jpeg cross-format thumbnail) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:17Z |
| Fixture file size | 120,140 bytes |
| Signed file size | 164,274 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.tiff |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_tiff.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:c1de5751-f3d0-4b0b-848b-6cf7399c8af3 |
| title | C2PA Conformance Test -- TIFF |
| instance_id (manifest) | xmp:iid:e4543312-d0ab-4b5c-ab1d-94db155d88c1 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.78.4 |
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
| c2pa.thumbnail.claim | JPEG thumbnail (cross-format) embedded in JUMBF manifest store |
| c2pa.hash.data | SHA-256 byte-range hash |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-tiff, image_id: 0ce52fda-10d2-4164-82b1-6b832127ec7c |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:8c4931e3-e082-48ee-b454-616f392a6d94
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
| Screenshot | [tiff_adobe_verify.png](../screenshots/tiff_adobe_verify.png) |

Note: DNG is treated as a TIFF variant by c2pa-rs (DNG is an extension of TIFF).
Both TIFF and DNG use c2pa.hash.data and TIFF-compatible manifest embedding.
