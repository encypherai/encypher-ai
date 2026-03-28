# HEIF -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | HEIF |
| MIME type | image/heif |
| Aliases accepted | image/heif-sequence (animated; signed as image/heif) |
| Extensions | .heif |
| Category | Image |
| Pipeline | c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media) |
| Hash assertion | c2pa.hash.bmff.v3 (BMFF box-level hash) |
| Thumbnail in manifest | No (BMFF-container images do not embed a thumbnail) |
| Conformance suite entry | Yes |

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:18Z |
| Fixture file size | 459 bytes |
| Signed file size | 15,301 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.heif |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_heif.json |

Note: HEIF and HEIC share the same container format (ISO Base Media File Format).
The fixture and signed file sizes are identical because the same minimal HEIF/HEIC container
fixture was used for both. Each has a distinct manifest UUID and instance_id.

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:66db777e-62b5-43aa-bbf9-716833598249 |
| title | C2PA Conformance Test -- HEIF |
| instance_id (manifest) | xmp:iid:dbe4cdaa-bb5c-418b-9a1b-f8b17677fdbf |
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
| c2pa.hash.bmff.v3 | SHA-256 BMFF box hash, alg: sha256, hash: 7ICHWuAmRgYbrItKIQIeQ/Z7+NasN6MnLk45BGvxvAk= |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-heif, image_id: 261a3b07-276c-47d4-a8da-d19da43d207f |

BMFF exclusions: /uuid (manifest box, with c2pa UUID offset), /ftyp, /mfra

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:cf03c4b0-6db0-47fe-bde1-bc7444eec56a
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
| Screenshot | [heif_adobe_verify.png](../screenshots/heif_adobe_verify.png) |
