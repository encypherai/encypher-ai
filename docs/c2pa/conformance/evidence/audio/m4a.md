# M4A -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | M4A (MPEG-4 Audio) |
| MIME type | audio/mp4 |
| Extensions | .m4a |
| Category | Audio |
| Pipeline | c2pa-rs (c2pa-python Builder, BMFF/ISO Base Media) |
| Hash assertion | c2pa.hash.bmff.v3 (BMFF box-level hash) |
| Conformance suite entry | Yes |

M4A uses the ISO Base Media File Format (BMFF) container, the same as MP4 and MOV.
c2pa-rs embeds the manifest in a UUID box and uses BMFF box-level hashing (c2pa.hash.bmff.v3).
This is a different hash binding than WAV and MP3 (which use c2pa.hash.data).

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:21Z |
| Fixture file size | 16,161 bytes |
| Signed file size | 31,001 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.m4a |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_m4a.json |

## Manifest Details

| Field | Value |
|-------|-------|
| active_manifest | urn:c2pa:051615cb-8640-45af-a470-fc8426cf7bdd |
| title | C2PA Conformance Test -- M4A |
| instance_id (manifest) | xmp:iid:3ea7bf80-bb06-48c0-a3c5-74ee187a87a5 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 1.0 |
| claim_generator_info.org.contentauth.c2pa_rs | 0.78.4 |
| signature_info.alg | Es256 |
| signature_info.issuer | Encypher Corporation |
| signature_info.common_name | Encypher Conformance Test Cert |
| signature_info.cert_serial_number | 8149767912641611982350984011013689761321125 |
| signature_info.time | 2026-03-25T08:33:21+00:00 |
| validation_state | Valid |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture |
| c2pa.hash.bmff.v3 | SHA-256 BMFF box hash, alg: sha256, hash: hU0SRr5Az/gO9Jwc+fafu4one6KwfyjaEevPnnJK6XM= |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-m4a, audio_id: 1daaa249-6687-4ae0-ba1b-4a8f31da2b15 |

BMFF exclusions: /uuid (manifest box, with c2pa UUID offset), /ftyp, /mfra

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: urn:uuid:b069b2ba-5eea-497a-813a-acf3a4a06542
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
| Screenshot | [m4a_adobe_verify.png](../screenshots/m4a_adobe_verify.png) |
