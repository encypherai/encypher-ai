# PDF -- C2PA Conformance Evidence

## Format Metadata

| Field | Value |
|-------|-------|
| Format name | PDF (Portable Document Format) |
| MIME type | application/pdf |
| Extensions | .pdf |
| Category | Document |
| Pipeline | Custom JUMBF/COSE (Encypher two-pass pipeline) |
| Hash assertion | c2pa.hash.data (byte-range exclusion of manifest placeholder) |
| Conformance suite entry | Yes |

PDF signing does NOT use c2pa-python Builder. It uses Encypher's custom pipeline:
1. Placeholder of known size is inserted into the PDF as an embedded file stream
2. File content (excluding the placeholder range) is SHA-256 hashed
3. CBOR claim is built (c2pa_claim_builder.py)
4. Claim is signed using COSE_Sign1 with ES256 (cose_signer.py)
5. Full JUMBF manifest store is serialized (jumbf.py)
6. JUMBF bytes replace the placeholder in the PDF

The manifest is embedded as a PDF embedded file stream with /AFRelationship set to indicate
C2PA content. This follows the C2PA specification for PDF manifest embedding.

## Signing Evidence

| Field | Value |
|-------|-------|
| Conformance run timestamp | 2026-03-25T08:33:21Z |
| Fixture file size | 593 bytes |
| Signed file size | 66,639 bytes |
| Sign result | PASS |
| Signed file | tests/c2pa_conformance/signed/signed_test.pdf |
| Manifest JSON | tests/c2pa_conformance/manifests/signed_test_pdf.json |

## Manifest Details

Source: tests/c2pa_conformance/manifests/signed_test_pdf.json

| Field | Value |
|-------|-------|
| manifest label | urn:c2pa:9f6a781f-766f-40d4-b781-fb01c9bbb67d |
| instanceID | urn:uuid:69a0047b-8a92-4e05-b325-db0d84b178f4 |
| claim.claim_generator | Encypher Enterprise API/2.0 |
| claim_generator_info.name | Encypher |
| claim_generator_info.version | 2.0 |
| dc:title | C2PA Conformance Test -- PDF |
| dc:format | application/pdf |
| claim.alg | sha256 |
| signature | self#jumbf=urn:c2pa:9f6a781f-766f-40d4-b781-fb01c9bbb67d/c2pa.signature |

### Assertions

| Label | Details |
|-------|---------|
| c2pa.actions.v2 | action: c2pa.created, digitalSourceType: http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture, softwareAgent: Encypher Enterprise API v2.0 |
| c2pa.hash.data | exclusions: [{start: 642, length: 65536}], alg: sha256, hash: cdcc598e4803a118d226ee3f0919165d4f93277cd577111bf55b55fa1322f78b |
| com.encypher.provenance | organization_id: encypher-conformance, document_id: conformance-pdf, document_asset_id: 9debc0a7-6755-4e72-86a0-98343de3213a |

Assertion hashes from claim (SHA-256):
- c2pa.actions.v2: 50fc3efd84118ce0d0a778eb2a877c06e054c7f8a062798ee598c0ee467277ab
- c2pa.hash.data: d40e6e5c680195c1ef55949558bebbe8704a8abd3c867e8e025adc3b39f39bc8
- com.encypher.provenance: e492b0bbbe6a06315d59d51c6701338fd94913ff0d3294cbbf86788aafe331b8

## Internal Verification Results

Source: tests/c2pa_conformance/results/verify_results.json

verify_results instance_id: (empty string -- custom pipeline does not produce XMP instance ID)
verify_results manifest_label: urn:c2pa:9f6a781f-766f-40d4-b781-fb01c9bbb67d
verify_results verify_success: true

| Validation Code | Success | Notes |
|----------------|---------|-------|
| structural.jumbfPresent | true | JUMBF manifest store present in signed PDF |

Note: The PDF verifier performs structural verification of the JUMBF manifest store.
The c2pa-python Reader does not parse Encypher's custom PDF manifest format (different
CBOR serialization path). Full cryptographic re-verification of the PDF manifest is
performed by the custom verifier in unified_verify_service.py.

## Adobe Content Credentials Verify

| Field | Value |
|-------|-------|
| Result | N/A -- Adobe Content Credentials Verify does not support PDF C2PA manifests |
| Screenshot | [pdf_adobe_verify.png](../screenshots/pdf_adobe_verify.png) |

The screenshot shows Adobe's tool accepting the file upload but not displaying verification
results. This is expected behavior: Adobe's web tool does not currently parse PDF-embedded
C2PA manifests. This is a tool limitation, not a conformance failure.
