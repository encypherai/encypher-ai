# API and Web Tool Verification Evidence

**Product**: Encypher Enterprise API v2.0.0
**Date**: 2026-03-26
**Verification methods**: REST API (curl), Web File Inspector (Puppeteer)
**Certificate**: CN=Encypher Conformance Test Cert, O=Encypher Corporation (SSL.com c2pasign)

---

## 1. API Verification -- Tested curl Output

All requests were executed against a live instance of Encypher Enterprise API v2.0.0.
Test files were signed with the SSL.com c2pasign conformance certificate
(CN="Encypher Conformance Test Cert", O="Encypher Corporation", ECC P-256 / ES256).

**Note on trust status**: `signingCredential.untrusted` and `timeStamp.untrusted` are
expected informational statuses for conformance test certificates not yet enrolled on
the C2PA trust list. They do not indicate a validation failure -- `validation_state`
is "Valid" for all test files.

### 1.1 Image Verification (JPEG)

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/verify/image \
  -H "Content-Type: application/json" \
  -d '{"image_data": "<base64 of signed_test.jpg>", "mime_type": "image/jpeg"}'
```

**Response (tested 2026-03-26T13:05:06Z):**

```json
{
    "success": true,
    "valid": true,
    "verified_at": "2026-03-26T13:05:06.072394+00:00",
    "c2pa_manifest": {
        "active_manifest": "urn:c2pa:74754344-f6d9-4d40-a32f-65b436f4de14",
        "manifests": {
            "urn:c2pa:74754344-f6d9-4d40-a32f-65b436f4de14": {
                "claim_generator_info": [
                    {"name": "Encypher", "version": "1.0", "org.contentauth.c2pa_rs": "0.78.4"}
                ],
                "title": "Encypher Signed Content",
                "instance_id": "xmp:iid:00113f21-421e-40c1-a797-9f858bb4d072",
                "thumbnail": {
                    "format": "image/jpeg",
                    "identifier": "self#jumbf=/c2pa/urn:c2pa:74754344-f6d9-4d40-a32f-65b436f4de14/c2pa.assertions/c2pa.thumbnail.claim"
                },
                "assertions": [
                    {
                        "label": "c2pa.actions.v2",
                        "data": {
                            "actions": [{
                                "action": "c2pa.created",
                                "when": "2026-03-26T13:02:15Z",
                                "softwareAgent": {"name": "Encypher Enterprise API", "version": "1.0"},
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
                            }]
                        }
                    },
                    {
                        "label": "com.encypher.provenance",
                        "data": {
                            "document_id": "doc_interop_test",
                            "image_id": "asset_interop_test",
                            "organization_id": "org_test",
                            "signed_at": "2026-03-26T13:02:15Z"
                        }
                    }
                ],
                "signature_info": {
                    "alg": "Es256",
                    "issuer": "Encypher Corporation",
                    "common_name": "Encypher Conformance Test Cert",
                    "cert_serial_number": "8149767912641611982350984011013689761321125",
                    "time": "2026-03-26T13:02:15+00:00"
                },
                "claim_version": 2
            }
        },
        "validation_results": {
            "activeManifest": {
                "success": [
                    {"code": "timeStamp.validated", "explanation": "timestamp message digest matched: SSL.com Timestamping Unit 2025 E1"},
                    {"code": "claimSignature.insideValidity", "explanation": "claim signature valid"},
                    {"code": "claimSignature.validated", "explanation": "claim signature valid"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.hash.data"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.thumbnail.claim"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.actions.v2"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/com.encypher.provenance"},
                    {"code": "assertion.dataHash.match", "explanation": "data hash valid"}
                ],
                "informational": [
                    {"code": "timeStamp.untrusted", "explanation": "timestamp cert untrusted: SSL.com Timestamping Unit 2025 E1"}
                ]
            }
        },
        "validation_state": "Valid"
    },
    "cryptographically_verified": true
}
```

**Key findings**: 8 success validation codes, claim signature valid, data hash valid, RFC 3161 timestamp validated via SSL.com TSA. Signer: CN=Encypher Conformance Test Cert, O=Encypher Corporation.

---

### 1.2 Audio Verification (WAV)

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/verify/audio \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "<base64 of signed_test.wav>", "mime_type": "audio/wav"}'
```

**Response (tested 2026-03-26T13:05:08Z):**

```json
{
    "success": true,
    "valid": true,
    "c2pa_manifest_valid": true,
    "hash_matches": true,
    "c2pa_instance_id": "xmp:iid:87e64d1b-5535-4fd5-9b0d-9fb3b9cd0c1a",
    "signed_at": "2026-03-26T13:02:15Z",
    "manifest_data": {
        "active_manifest": "urn:c2pa:0e67e58e-17f6-4850-9192-b3c4c4c73bc6",
        "manifests": {
            "urn:c2pa:0e67e58e-17f6-4850-9192-b3c4c4c73bc6": {
                "claim_generator_info": [
                    {"name": "Encypher", "version": "1.0", "org.contentauth.c2pa_rs": "0.78.4"}
                ],
                "title": "Encypher Signed Content",
                "instance_id": "xmp:iid:87e64d1b-5535-4fd5-9b0d-9fb3b9cd0c1a",
                "assertions": [
                    {
                        "label": "c2pa.actions.v2",
                        "data": {
                            "actions": [{
                                "action": "c2pa.created",
                                "when": "2026-03-26T13:02:15Z",
                                "softwareAgent": {"name": "Encypher Enterprise API", "version": "1.0"},
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
                            }]
                        }
                    },
                    {
                        "label": "com.encypher.provenance",
                        "data": {
                            "audio_id": "asset_interop_test",
                            "document_id": "doc_interop_test",
                            "organization_id": "org_test",
                            "signed_at": "2026-03-26T13:02:15Z"
                        }
                    }
                ],
                "signature_info": {
                    "alg": "Es256",
                    "issuer": "Encypher Corporation",
                    "common_name": "Encypher Conformance Test Cert",
                    "cert_serial_number": "8149767912641611982350984011013689761321125",
                    "time": "2026-03-26T13:02:16+00:00"
                },
                "claim_version": 2
            }
        },
        "validation_results": {
            "activeManifest": {
                "success": [
                    {"code": "timeStamp.validated", "explanation": "timestamp message digest matched: SSL.com Timestamping Unit 2025 E1"},
                    {"code": "claimSignature.insideValidity", "explanation": "claim signature valid"},
                    {"code": "claimSignature.validated", "explanation": "claim signature valid"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.hash.data"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.actions.v2"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/com.encypher.provenance"},
                    {"code": "assertion.dataHash.match", "explanation": "data hash valid"}
                ],
                "informational": [
                    {"code": "timeStamp.untrusted", "explanation": "timestamp cert untrusted: SSL.com Timestamping Unit 2025 E1"}
                ]
            }
        },
        "validation_state": "Valid"
    }
}
```

**Key findings**: 7 success validation codes, c2pa_manifest_valid: true, hash_matches: true, c2pa.hash.data binding confirmed. Signer: CN=Encypher Conformance Test Cert, O=Encypher Corporation.

---

### 1.3 Video Verification (MP4)

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/verify/video \
  -F "file=@signed_test.mp4" \
  -F "mime_type=video/mp4"
```

**Response (tested 2026-03-26T13:05:10Z):**

```json
{
    "success": true,
    "valid": true,
    "c2pa_manifest_valid": true,
    "hash_matches": true,
    "c2pa_instance_id": "xmp:iid:d8819696-c460-4306-8f6b-3c88c8ebaf99",
    "signed_at": "2026-03-26T13:02:16Z",
    "manifest_data": {
        "active_manifest": "urn:c2pa:feb9aceb-6b74-4d1f-b663-b2c530d745a9",
        "manifests": {
            "urn:c2pa:feb9aceb-6b74-4d1f-b663-b2c530d745a9": {
                "claim_generator_info": [
                    {"name": "Encypher", "version": "1.0", "org.contentauth.c2pa_rs": "0.78.4"}
                ],
                "title": "Encypher Signed Content",
                "instance_id": "xmp:iid:d8819696-c460-4306-8f6b-3c88c8ebaf99",
                "assertions": [
                    {
                        "label": "c2pa.hash.bmff.v3",
                        "data": {
                            "exclusions": [
                                {"xpath": "/uuid", "data": [{"offset": 8, "value": "2P7D1hsOSDySl1goh37EgQ=="}]},
                                {"xpath": "/ftyp"},
                                {"xpath": "/mfra"},
                                {"xpath": "/free"},
                                {"xpath": "/skip"}
                            ],
                            "alg": "sha256",
                            "hash": "5U7K+NAxI+yq0UEn2iEFk4fXlrrvzSIl1dGe+DC86IM=",
                            "name": "jumbf manifest"
                        }
                    },
                    {
                        "label": "c2pa.actions.v2",
                        "data": {
                            "actions": [{
                                "action": "c2pa.created",
                                "when": "2026-03-26T13:02:16Z",
                                "softwareAgent": {"name": "Encypher Enterprise API", "version": "1.0"},
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
                            }]
                        }
                    },
                    {
                        "label": "com.encypher.provenance",
                        "data": {
                            "document_id": "doc_interop_test",
                            "organization_id": "org_test",
                            "signed_at": "2026-03-26T13:02:16Z",
                            "video_id": "asset_interop_test"
                        }
                    }
                ],
                "signature_info": {
                    "alg": "Es256",
                    "issuer": "Encypher Corporation",
                    "common_name": "Encypher Conformance Test Cert",
                    "cert_serial_number": "8149767912641611982350984011013689761321125",
                    "time": "2026-03-26T13:02:16+00:00"
                },
                "claim_version": 2
            }
        },
        "validation_results": {
            "activeManifest": {
                "success": [
                    {"code": "timeStamp.validated", "explanation": "timestamp message digest matched: SSL.com Timestamping Unit 2025 E1"},
                    {"code": "claimSignature.insideValidity", "explanation": "claim signature valid"},
                    {"code": "claimSignature.validated", "explanation": "claim signature valid"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.hash.bmff.v3"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/c2pa.actions.v2"},
                    {"code": "assertion.hashedURI.match", "explanation": "hashed uri matched: self#jumbf=c2pa.assertions/com.encypher.provenance"},
                    {"code": "assertion.bmffHash.match", "explanation": "BMFF hash valid"}
                ],
                "informational": [
                    {"code": "timeStamp.untrusted", "explanation": "timestamp cert untrusted: SSL.com Timestamping Unit 2025 E1"}
                ]
            }
        },
        "validation_state": "Valid"
    }
}
```

**Key findings**: 7 success validation codes, c2pa.hash.bmff.v3 ISOBMFF hashing with box exclusions (/uuid, /ftyp, /mfra, /free, /skip), BMFF hash valid. Signer: CN=Encypher Conformance Test Cert, O=Encypher Corporation.

---

### 1.4 Text Verification

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/public/verify-text \
  -H "Content-Type: application/json" \
  -d '{"text": "paste signed text here"}'
```

**Note**: The text verify endpoint is documented in the Extended Capabilities section.
Text C2PA manifest embedding per Manifests_Text.adoc is a production capability
not yet covered by the conformance program's submission categories.

---

## 2. Web File Inspector Tool -- Puppeteer Verification

The File Inspector tool at https://encypher.com/tools/inspect provides drag-and-drop
verification for all C2PA media formats. Testing was performed via Puppeteer headless
browser automation against a live Next.js dev server.

### Test Configuration

- Browser: Chromium (headless, Puppeteer)
- Frontend: Next.js marketing-site (localhost:3000)
- Backend: Encypher Enterprise API v2.0.0 (localhost:9000)
- Test files: Same signed files from generator_samples/ + Google interop sample

### Test Results (5/5 PASS)

| # | File | Format | Result | Details |
|---|------|--------|--------|---------|
| 1 | signed_test.jpg | JPEG | PASS -- Provenance Verified | C2PA manifest expandable, validation_state: Valid |
| 2 | signed_test.wav | WAV | PASS -- Audio Provenance Verified | C2PA Manifest Valid, Hash Matches, Instance ID, timestamps |
| 3 | signed_test.mp4 | MP4 | PASS -- Video Provenance Verified | C2PA Manifest Valid, Hash Matches, BMFF hash binding |
| 4 | signed_test.png | PNG | PASS -- Provenance Verified | C2PA manifest expandable, data hash valid |
| 5 | Google NotebookLM sample.jpg | JPEG | PASS -- Provenance Verified | External interoperability confirmed (Google-signed) |

### File Inspector Supported Formats

**Images (11 types)**: JPEG, PNG, WebP, TIFF, GIF, HEIC, HEIF, AVIF, SVG, DNG, JXL

**Audio (5 types)**: MP3, WAV, FLAC, M4A, AAC

**Video (5 types)**: MP4, MOV, AVI, M4V, WebM

**Text/Documents**: PDF, TXT, MD, HTML, JSON, XML, and other text-based formats

Size limits: 10 MB (images), 25 MB (audio), 100 MB (video), 5 MB (text/PDF)

### Verification Architecture

```
Browser (File Inspector)
  |
  | fetch() to Next.js proxy routes
  v
Next.js API Routes
  /api/tools/verify-image   (base64 JSON -> /api/v1/verify/image)
  /api/tools/verify-audio   (base64 JSON -> /api/v1/verify/audio)
  /api/tools/verify-video   (FormData   -> /api/v1/verify/video)
  |
  | HTTPS
  v
Encypher Enterprise API
  /api/v1/verify/image
  /api/v1/verify/audio
  /api/v1/verify/video
```

---

## 3. Verification Summary

| Method | Formats Tested | Result |
|--------|---------------|--------|
| API (curl) | JPEG, WAV, MP4 | 3/3 PASS -- all return valid with full C2PA manifest |
| Web Tool (Puppeteer) | JPEG, PNG, WAV, MP4, Google JPEG | 5/5 PASS -- provenance verified for all |
| Cross-tool | JPEG, WAV, MP4 verified via both API and Web Tool | Consistent results |

All verification outputs confirm: valid C2PA manifest, claim signature validated,
data hash / BMFF hash match, RFC 3161 timestamp validated via SSL.com TSA.
Signer identity: CN=Encypher Conformance Test Cert, O=Encypher Corporation.
