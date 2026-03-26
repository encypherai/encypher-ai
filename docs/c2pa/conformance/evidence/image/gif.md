# GIF - C2PA Conformance Evidence

## Format Details
- MIME Type: image/gif
- Extension: .gif
- Category: Image
- Pipeline: c2pa-python (c2pa-rs)

## Signing Evidence
- Method: c2pa-python Builder.sign()
- Content binding: Standard c2pa-rs GIF embedding
- Signature algorithm: ECC P-256 / ES256
- Test file: tests/c2pa_conformance/fixtures/test.gif (365 bytes)
- Signed file: tests/c2pa_conformance/signed/signed_test.gif (17,102 bytes)
- Sign: PASS
- Verify: PASS (9 validation status codes)

## Verification Evidence
- c2pa-python Reader successfully parses signed GIF
- All validation status codes pass

## Notes
- GIF support is native in c2pa-rs; no custom embedding needed
