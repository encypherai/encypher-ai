# DNG -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | DNG (Digital Negative) |
| MIME type | image/x-adobe-dng |
| Extensions | .dng |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder; c2pa-rs treats DNG as TIFF variant) |
| Hash assertion | c2pa.hash.data (byte-range exclusion) |
| Thumbnail in manifest | No (DNG is a TIFF extension; no thumbnail for this test fixture) |
| Conformance suite entry | Yes |

DNG is an extension of the TIFF specification. c2pa-rs uses the same manifest embedding
path as TIFF for DNG files. The MIME type image/x-adobe-dng is accepted by c2pa-python
and routed to the TIFF codec within c2pa-rs.

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:19Z |
| Fixture file size | 4,230 bytes |
| Signed file size | 18,858 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.dng |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_dng.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:dadad5c1-ed48-49f2-8655-ae210a461ba1 |
| title | C2PA Conformance Test -- DNG |
| instance_id (manifest) | xmp:iid:677395d3-0213-43a6-88d5-f84e38fbccf7 |
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
| c2pa.hash.data | SHA-256 byte-range hash |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-dng, image_id: c47ea911-60cb-473e-a9c7-e3f0434dffef |

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:2f3c7c17-bb97-4a67-af2d-5c6c79595f94
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
| Screenshot | [dng_adobe_verify.png](../screenshots/dng_adobe_verify.png) |
