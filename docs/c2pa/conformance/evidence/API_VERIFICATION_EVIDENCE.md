# API and Web Tool Verification Evidence

**Product**: Encypher Enterprise API v2.0.0
**Date**: 2026-03-27
**Verification methods**: REST API (curl), Web File Inspector (Puppeteer)
**Certificate**: CN=Encypher Conformance Test Cert, O=Encypher Corporation (SSL.com c2pasign)

---

## 1. API Verification -- Tested curl Output

All requests were executed against the live production Encypher Enterprise API v2.0.0
at `https://api.encypher.com`. Test files were signed with the SSL.com c2pasign
conformance certificate (CN="Encypher Conformance Test Cert", O="Encypher Corporation",
ECC P-256 / ES256).

**Unified media verify endpoint**: `POST /api/v1/public/verify/media` accepts any
C2PA-signed media file via multipart/form-data. No authentication required.

**Note on trust status**: `signingCredential.untrusted` and `timeStamp.untrusted` are
expected informational statuses for conformance test certificates not yet enrolled on
the C2PA trust list. They do not indicate a validation failure -- `validation_state`
is "Valid" for all test files.

### 1.1 Image Verification (JPEG)

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@signed_test.jpg;type=image/jpeg" \
  -F "mime_type=image/jpeg"
```

**Response (tested 2026-03-27T12:58:03Z):**

```json
{
    "success": true,
    "valid": true,
    "tampered": false,
    "reason_code": "OK",
    "media_type": "image",
    "verified_at": "2026-03-27T12:58:03.226193Z",
    "content": {
        "hash_verified": true,
        "c2pa_manifest_valid": true,
        "c2pa_instance_id": "xmp:iid:0c4ea553-9e25-460a-b1f5-210df7c17af9",
        "manifest_data": {
            "active_manifest": "urn:c2pa:d3bec9f2-b3de-4b9f-bcdf-3778f4f12cad",
            "manifests": {
                "urn:c2pa:d3bec9f2-b3de-4b9f-bcdf-3778f4f12cad": {
                    "claim_generator_info": [
                        {"name": "Encypher", "version": "1.0", "org.contentauth.c2pa_rs": "0.78.4"}
                    ],
                    "title": "C2PA Conformance Test -- JPEG",
                    "instance_id": "xmp:iid:0c4ea553-9e25-460a-b1f5-210df7c17af9",
                    "thumbnail": {
                        "format": "image/jpeg",
                        "identifier": "self#jumbf=/c2pa/urn:c2pa:d3bec9f2-b3de-4b9f-bcdf-3778f4f12cad/c2pa.assertions/c2pa.thumbnail.claim"
                    },
                    "assertions": [
                        {
                            "label": "c2pa.actions.v2",
                            "data": {
                                "actions": [{
                                    "action": "c2pa.created",
                                    "when": "2026-03-27T10:19:45Z",
                                    "softwareAgent": {"name": "Encypher Enterprise API", "version": "1.0"},
                                    "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture"
                                }]
                            }
                        },
                        {
                            "label": "com.encypher.provenance",
                            "data": {
                                "document_id": "conformance-jpeg",
                                "image_id": "060c98af-586a-42fc-9a08-680fbb71ac6a",
                                "organization_id": "encypher-conformance",
                                "signed_at": "2026-03-27T10:19:45Z"
                            }
                        }
                    ],
                    "signature_info": {
                        "alg": "Es256",
                        "issuer": "Encypher Corporation",
                        "common_name": "Encypher Conformance Test Cert",
                        "cert_serial_number": "8149767912641611982350984011013689761321125",
                        "time": "2026-03-27T10:19:45+00:00"
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
        }
    }
}
```

**Key findings**: 8 success validation codes, claim signature valid, data hash valid, RFC 3161 timestamp validated via SSL.com TSA. Signer: CN=Encypher Conformance Test Cert, O=Encypher Corporation.

---

### 1.2 Audio Verification (WAV)

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@signed_test.wav;type=audio/wav" \
  -F "mime_type=audio/wav"
```

**Response (tested 2026-03-27T12:58:09Z):**

```json
{
    "success": true,
    "valid": true,
    "tampered": false,
    "reason_code": "OK",
    "media_type": "audio",
    "verified_at": "2026-03-27T12:58:09.592665Z",
    "content": {
        "hash_verified": true,
        "c2pa_manifest_valid": true,
        "c2pa_instance_id": "xmp:iid:b1073da0-2bf8-4d61-b90b-95a361a70d80",
        "manifest_data": {
            "active_manifest": "urn:c2pa:3ceb4bfa-1298-4be2-83ba-7fa50a5a446d",
            "manifests": {
                "urn:c2pa:3ceb4bfa-1298-4be2-83ba-7fa50a5a446d": {
                    "claim_generator_info": [
                        {"name": "Encypher", "version": "1.0", "org.contentauth.c2pa_rs": "0.78.4"}
                    ],
                    "title": "C2PA Conformance Test -- WAV",
                    "instance_id": "xmp:iid:b1073da0-2bf8-4d61-b90b-95a361a70d80",
                    "assertions": [
                        {
                            "label": "c2pa.actions.v2",
                            "data": {
                                "actions": [{
                                    "action": "c2pa.created",
                                    "when": "2026-03-27T10:19:50Z",
                                    "softwareAgent": {"name": "Encypher Enterprise API", "version": "1.0"},
                                    "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture"
                                }]
                            }
                        },
                        {
                            "label": "com.encypher.provenance",
                            "data": {
                                "audio_id": "f48c0145-3648-415e-a8ef-ad0354fa4603",
                                "document_id": "conformance-wav",
                                "organization_id": "encypher-conformance",
                                "signed_at": "2026-03-27T10:19:50Z"
                            }
                        }
                    ],
                    "signature_info": {
                        "alg": "Es256",
                        "issuer": "Encypher Corporation",
                        "common_name": "Encypher Conformance Test Cert",
                        "cert_serial_number": "8149767912641611982350984011013689761321125",
                        "time": "2026-03-27T10:19:50+00:00"
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
}
```

**Key findings**: 7 success validation codes, c2pa_manifest_valid: true, hash_verified: true, c2pa.hash.data binding confirmed. Signer: CN=Encypher Conformance Test Cert, O=Encypher Corporation.

---

### 1.3 Video Verification (MP4)

**Request:**

```bash
curl -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@signed_test.mp4;type=video/mp4" \
  -F "mime_type=video/mp4"
```

**Response (tested 2026-03-27T12:58:10Z):**

```json
{
    "success": true,
    "valid": true,
    "tampered": false,
    "reason_code": "OK",
    "media_type": "video",
    "verified_at": "2026-03-27T12:58:10.749269Z",
    "content": {
        "hash_verified": true,
        "c2pa_manifest_valid": true,
        "c2pa_instance_id": "xmp:iid:8b4e9e94-9b0a-46f9-915d-f86c12c4f3f7",
        "manifest_data": {
            "active_manifest": "urn:c2pa:0cc7adfe-3c77-4f13-927b-f20ca7401f65",
            "manifests": {
                "urn:c2pa:0cc7adfe-3c77-4f13-927b-f20ca7401f65": {
                    "claim_generator_info": [
                        {"name": "Encypher", "version": "1.0", "org.contentauth.c2pa_rs": "0.78.4"}
                    ],
                    "title": "C2PA Conformance Test -- MP4",
                    "instance_id": "xmp:iid:8b4e9e94-9b0a-46f9-915d-f86c12c4f3f7",
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
                                "hash": "z2IhCPFv/oTT+o7FcvCq+dZAiUdaWZhepv1o/eT8FKU=",  # pragma: allowlist secret
                                "name": "jumbf manifest"
                            }
                        },
                        {
                            "label": "c2pa.actions.v2",
                            "data": {
                                "actions": [{
                                    "action": "c2pa.created",
                                    "when": "2026-03-27T10:19:48Z",
                                    "softwareAgent": {"name": "Encypher Enterprise API", "version": "1.0"},
                                    "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture"
                                }]
                            }
                        },
                        {
                            "label": "com.encypher.provenance",
                            "data": {
                                "document_id": "conformance-mp4",
                                "organization_id": "encypher-conformance",
                                "signed_at": "2026-03-27T10:19:48Z",
                                "video_id": "2650f624-1652-4359-b474-d51e61dafc48"
                            }
                        }
                    ],
                    "signature_info": {
                        "alg": "Es256",
                        "issuer": "Encypher Corporation",
                        "common_name": "Encypher Conformance Test Cert",
                        "cert_serial_number": "8149767912641611982350984011013689761321125",
                        "time": "2026-03-27T10:19:49+00:00"
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
}
```

**Key findings**: 7 success validation codes, c2pa.hash.bmff.v3 ISOBMFF hashing with box exclusions (/uuid, /ftyp, /mfra, /free, /skip), BMFF hash valid. Signer: CN=Encypher Conformance Test Cert, O=Encypher Corporation.

---

### 1.4 Text Sign + Verify Round-Trip

**Sign request:**

```bash
curl -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Content to sign with provenance metadata"}'
```

**Verify request (with signed text from sign response):**

```bash
curl -X POST https://api.encypher.com/api/v1/public/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "<signed text with embedded metadata>"}'
```

**Verified (tested 2026-03-27T12:57:57Z):** `{"success": true, "valid": true}`

**Note**: Text C2PA manifest embedding per Manifests_Text.adoc is a production capability
not yet covered by the conformance program's submission categories. See the Extended
Capabilities section for evidence files.

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

**Audio (6 types)**: MP3, WAV, FLAC, M4A, OGG, AAC

**Video (4 types)**: MP4, MOV, AVI, WebM

**Documents (5 types)**: PDF, EPUB, DOCX, ODT, OXPS

**Fonts (2 types)**: OTF, TTF

**Text**: TXT, MD, HTML, JSON, XML

Size limits: 10 MB (images), 25 MB (audio/documents), 100 MB (video), 10 MB (fonts), 5 MB (text)

### Verification Architecture

```
Browser (File Inspector)
  |
  | fetch() to Next.js proxy routes
  v
Next.js API Routes
  /api/tools/verify-image     (base64 JSON  -> /api/v1/public/verify/media)
  /api/tools/verify-audio     (base64 JSON  -> /api/v1/public/verify/media)
  /api/tools/verify-video     (FormData     -> /api/v1/public/verify/media)
  /api/tools/verify-document  (base64 JSON  -> /api/v1/public/verify/media)
  |
  | HTTPS (TLS 1.3)
  v
Encypher Enterprise API
  /api/v1/public/verify/media  (unified -- routes by MIME type)
  /api/v1/public/verify        (text verification)
```

---

## 3. Verification Summary

| Method | Formats Tested | Result |
|--------|---------------|--------|
| API (curl) | JPEG, WAV, MP4 | 3/3 PASS -- all return valid with full C2PA manifest |
| API (curl) | Text sign+verify round-trip | 1/1 PASS |
| Web Tool (Puppeteer) | JPEG, PNG, WAV, MP4, Google JPEG | 5/5 PASS -- provenance verified for all |
| Cross-tool | JPEG, WAV, MP4 verified via both API and Web Tool | Consistent results |

All verification outputs confirm: valid C2PA manifest, claim signature validated,
data hash / BMFF hash match, RFC 3161 timestamp validated via SSL.com TSA.
Signer identity: CN=Encypher Conformance Test Cert, O=Encypher Corporation.
