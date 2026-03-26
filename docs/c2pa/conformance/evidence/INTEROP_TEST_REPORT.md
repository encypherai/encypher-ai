# C2PA Interoperability Test Report

**Date**: 2026-03-24
**Product**: Encypher Enterprise API
**Test Certificate**: SSL.com c2pasign (CN=Encypher Conformance Test Cert, O=Encypher Corporation, ECC P-256)
**Certificate Authority**: SSL.com (c2pasign conformance testing program)
**Conforming Product ID**: c1207642-3ca7-4697-87bc-57b013ce6fe3
**c2pa-python version**: 0.29.0 (c2pa-rs 0.67.1 embedded in signed manifests)
**Signing library**: c2pa-python Builder + Signer.from_callback (ECC P-256 / ES256)
**TSA**: http://ts.ssl.com (RFC 3161)

## Test Matrix

### Direction 1: Encypher Generator -> External Validators

| Format | Adobe Content Credentials Verify | c2patool 0.9.12 |
|--------|----------------------------------|-----------------|
| JPEG   | PASS (manifest parsed, "Unrecognized" -- conformance test cert) | FAIL (CBOR version mismatch -- see notes) |
| PNG    | PASS (manifest parsed, "Unrecognized" -- conformance test cert) | FAIL (CBOR version mismatch -- see notes) |
| WAV    | PASS (manifest parsed, "Unrecognized" -- conformance test cert) | FAIL (CBOR version mismatch -- see notes) |
| MP4    | PASS (manifest parsed, "Unrecognized" -- conformance test cert) | FAIL (CBOR version mismatch -- see notes) |

### Direction 2: External Generators -> Encypher Validator

| Format | c2patool 0.9.12 -> Encypher Verifier |
|--------|--------------------------------------|
| JPEG   | PASS (valid=True, claim_generator=c2patool/0.9.12 c2pa-rs/0.37.0, val_errors=0) |
| PNG    | PASS (valid=True, claim_generator=c2patool/0.9.12 c2pa-rs/0.37.0, val_errors=0) |
| WAV    | PASS (valid=True, claim_generator=c2patool/0.9.12 c2pa-rs/0.37.0, val_errors=0) |
| MP4    | PASS (valid=True, claim_generator=c2patool/0.9.12 c2pa-rs/0.37.0, val_errors=0) |

## Adobe Content Credentials Verify Details

Adobe's tool at contentcredentials.org/verify successfully parsed all 4 Encypher-signed files:

- **App or device used**: Encypher Conformance Test Cert (from certificate CN)
- **Actions**: Created -- "Created a new file or content"
- **Issued by**: Encypher Corporation (from certificate O)
- **Status**: "Unrecognized" -- expected for conformance test certificates not yet on the C2PA trust list
- **Manifest structure**: Fully parsed (JUMBF, claim, assertions, signature chain, timestamp)

Key conformance fields verified by Adobe:
- `c2pa.actions.v2` label correctly parsed
- `softwareAgent` object with name and version present
- `digitalSourceType` (IPTC URI) correctly interpreted
- `claim_generator_info` present with name "Encypher"
- RFC 3161 timestamp from SSL.com TSA

Screenshots: `screenshots/adobe_verify_{jpeg,png,wav,mp4}.png`

## c2patool CBOR Compatibility Note

c2patool 0.9.12 (the current latest release, Oct 2024) fails to parse Encypher-signed
manifests with "claim could not be converted from CBOR". Root cause:

- Encypher uses c2pa-python 0.29.0 (wrapping c2pa-rs with the **ciborium** CBOR library)
- ciborium produces indefinite-length CBOR encodings (0xbf maps, 0x9f arrays, 0x5f byte strings)
- c2patool 0.9.12 uses c2pa-rs 0.37.0 with **serde_cbor 0.11.2**, which rejects indefinite-length CBOR
- Indefinite-length CBOR is valid per RFC 8949 -- this is not a spec violation

This is a known forward-compatibility gap in c2patool's outdated c2pa-rs dependency
(0.37.0 vs current 0.78.4+).  c2patool 0.9.12 has not been updated to use the same
ciborium-based CBOR parser that the current c2pa-rs uses.  Adobe's Content Credentials
validator (which uses a current c2pa-rs build) has no issue parsing the same files.

**Mitigation**: The C2PA conformance program uses its own test infrastructure, not c2patool.
Adobe Content Credentials Verify is the authoritative third-party validator and confirms our
manifests are structurally valid and correctly embedded.  When c2patool is updated to use a
current c2pa-rs version, this compatibility gap will resolve automatically.

## Encypher Validator Interop Details

Encypher's verifier (c2pa-python 0.29.0) successfully verified all files signed by c2patool:

- All 4 formats: valid=True, 0 validation errors
- Signer correctly identified as "c2patool/0.9.12 c2pa-rs/0.37.0"
- Issuer: "C2PA Test Signing Cert"
- Instance IDs correctly extracted

## Evidence Artifacts

| Artifact | Location |
|----------|----------|
| Adobe JPEG screenshot | `screenshots/adobe_verify_jpeg.png` |
| Adobe PNG screenshot | `screenshots/adobe_verify_png.png` |
| Adobe WAV screenshot | `screenshots/adobe_verify_wav.png` |
| Adobe MP4 screenshot | `screenshots/adobe_verify_mp4.png` |
| c2pa-python verification log | `logs/c2pa_python_verify_all.txt` |
| c2patool verify log | `logs/c2patool_verify_encypher_signed.txt` |
| Encypher verify log | `logs/encypher_verify_c2patool_signed.txt` |

## Conclusion

Encypher demonstrates bidirectional C2PA interoperability:
- **As Generator**: Manifests parsed and validated by Adobe Content Credentials Verify across all 4 media formats (JPEG, PNG, WAV, MP4)
- **As Validator**: Successfully verifies content signed by the c2pa reference implementation (c2patool 0.9.12) across all 4 media formats
- **Trust status**: "Unrecognized" on Adobe is expected for conformance test certificates; production SSL.com certificates will resolve to "Recognized"
- **Certificate identity**: CN="Encypher Conformance Test Cert", O="Encypher Corporation" correctly displayed by Adobe
