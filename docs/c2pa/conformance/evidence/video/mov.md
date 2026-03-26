# MOV -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | MOV (QuickTime) |
| MIME type | video/quicktime |
| Extensions | .mov |
| Category | Video |
| Pipeline | c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media) |
| Hash assertion | c2pa.hash.bmff.v3 (BMFF box-level hash) |
| Conformance suite entry | Yes |

MOV uses the QuickTime File Format, which is the precursor to the ISO Base Media File Format.
c2pa-rs handles MOV with the same BMFF pipeline as MP4, embedding the manifest in a UUID box.

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:19Z |
| Fixture file size | 2,161 bytes |
| Signed file size | 17,001 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.mov |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_mov.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:630bb86f-930a-44e7-8ccb-0fddc8358a4a |
| title | C2PA Conformance Test -- MOV |
| instance_id (manifest) | xmp:iid:0d7814b3-88d1-49df-8980-3b90d316d5b0 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.67.1 |
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
| c2pa.hash.bmff.v3 | SHA-256 BMFF box hash, alg: sha256, hash: sc/dgYuKMkVpPh6dhn60xzSvMlsIcThUln3u13YTUg8= |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-mov, video_id: 5fd04906-63ba-4870-86fb-fa3b6117e85b |

BMFF exclusions: /uuid (manifest box, with c2pa UUID offset), /ftyp, /mfra

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:59678f6c-9483-4d93-acd7-521e1ef4f584
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
| Screenshot | [mov_adobe_verify.png](../screenshots/mov_adobe_verify.png) |
