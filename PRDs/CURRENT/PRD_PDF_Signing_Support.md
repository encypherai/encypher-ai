# PDF Signing Support

**Status:** 📋 Planning
**Current Goal:** Add C2PA-compliant PDF signing and verification to the Enterprise API.

## Overview

Extend the Enterprise API to support signing and verifying PDF documents with C2PA manifests. PDFs are a high-demand enterprise use case for document provenance, legal compliance, and audit trails.

## Objectives

- Enable PDF upload, signing, and C2PA manifest embedding via API
- Verify C2PA manifests in uploaded PDFs
- Maintain compatibility with existing text signing workflow patterns
- Support both embedded manifests and sidecar `.c2pa` files

## Background

### C2PA PDF Specification (Appendix A.4)

Per C2PA Technical Specification 2.2, PDF embedding requires:
- JUMBF manifest stored as incremental save in PDF structure
- `c2pa.hash.data` assertion with PDF-specific exclusion ranges
- Support for multi-page documents with single manifest
- Compatibility with existing PDF digital signatures

### Dependencies

- **`c2pa-python`**: Official C2PA SDK with PDF support
- **`pypdf` or `pikepdf`**: PDF parsing/manipulation
- **Enterprise API**: Existing auth, rate limiting, quota infrastructure

## Tasks

### 1.0 Research & Spike

- [ ] 1.1 Evaluate `c2pa-python` PDF capabilities and API
- [ ] 1.2 Determine PDF size limits and performance implications
- [ ] 1.3 Design storage strategy for uploaded PDFs (temp files vs streaming)
- [ ] 1.4 Identify security considerations (malicious PDFs, DoS via large files)

### 2.0 API Design

- [ ] 2.1 Design `POST /api/v1/sign-pdf` endpoint
  - Multipart form upload
  - Returns signed PDF as download or base64
  - Optional: return sidecar `.c2pa` manifest instead of embedded
- [ ] 2.2 Design `POST /api/v1/verify-pdf` endpoint
  - Accept PDF upload
  - Return verification verdict similar to text verify endpoint
- [ ] 2.3 Design request/response schemas
- [ ] 2.4 Define quota consumption model (per-PDF vs per-MB)

### 3.0 Implementation

- [ ] 3.1 Add `c2pa-python` dependency
- [ ] 3.2 Implement PDF signing service
- [ ] 3.3 Implement PDF verification service
- [ ] 3.4 Add API endpoints with auth + rate limiting
- [ ] 3.5 Integrate with existing quota system

### 4.0 Testing

- [ ] 4.1 Unit tests for PDF signing/verification logic
- [ ] 4.2 Integration tests for API endpoints
- [ ] 4.3 Security tests (malformed PDFs, oversized files)
- [ ] 4.4 Performance benchmarks

### 5.0 Documentation

- [ ] 5.1 Update API.md with new endpoints
- [ ] 5.2 Update QUICKSTART.md with PDF examples
- [ ] 5.3 Add PDF-specific error codes and troubleshooting

## API Specification (Draft)

### `POST /api/v1/sign-pdf`

**Authentication:** Required (API key)

**Request:**
```
Content-Type: multipart/form-data

file: <PDF binary>
document_title: "My Document" (optional)
claim_generator: "custom-generator" (optional)
actions: [...] (optional, JSON array)
output_format: "embedded" | "sidecar" (default: "embedded")
include_timestamp: true | false (default: false)
```

**Response (200 OK):**
```json
{
  "success": true,
  "document_id": "doc_abc123",
  "signed_pdf_url": "https://api.encypherai.com/downloads/signed_abc123.pdf",
  "expires_at": "2025-12-14T18:30:00Z",
  "manifest_hash": "sha256:abc123...",
  "page_count": 5,
  "file_size_bytes": 1048576
}
```

**Or with `output_format: "sidecar"`:**
```json
{
  "success": true,
  "document_id": "doc_abc123",
  "sidecar_url": "https://api.encypherai.com/downloads/manifest_abc123.c2pa",
  "original_pdf_hash": "sha256:def456...",
  "expires_at": "2025-12-14T18:30:00Z"
}
```

### `POST /api/v1/verify-pdf`

**Authentication:** Optional (higher limits with API key)

**Request:**
```
Content-Type: multipart/form-data

file: <PDF binary>
sidecar: <.c2pa file> (optional, if manifest is external)
```

**Response (200 OK):**
```json
{
  "success": true,
  "valid": true,
  "signer_id": "org_abc123",
  "signer_name": "Acme Corp",
  "signed_at": "2025-12-14T12:00:00Z",
  "manifest": {
    "claim_generator": "encypher-api/1.0.0",
    "assertions": [...]
  },
  "content_binding": {
    "valid": true,
    "algorithm": "sha256"
  },
  "timestamp_authority": {
    "valid": true,
    "tsa_url": "http://timestamp.digicert.com",
    "timestamp": "2025-12-14T12:00:00Z"
  }
}
```

## Limits & Quotas

| Tier | Max PDF Size | PDFs/Month | TSA |
|------|--------------|------------|-----|
| Free | 5 MB | 10 | ❌ |
| Professional | 25 MB | 500 | ✅ |
| Enterprise | 100 MB | Unlimited | ✅ |

## Security Considerations

1. **File validation**: Verify file is valid PDF before processing
2. **Size limits**: Enforce tier-based max file size
3. **Timeout**: Set processing timeout (30s) to prevent DoS
4. **Temp storage**: Use secure temp directory, auto-delete after processing
5. **Malware scanning**: Consider integration with antivirus for uploaded files

## Success Criteria

- PDF signing endpoint returns valid C2PA-compliant signed PDF
- PDF verification endpoint correctly validates signed PDFs
- Sidecar manifest support works for detached signatures
- Performance: < 5s for typical PDF (< 10 MB)
- All tier limits enforced correctly

## Dependencies on Other PRDs

- **PRD_Public_Manifest_JSON_Validation.md**: TSA integration design applies here
- **External verifier API**: PDFs signed by Encypher can be verified externally

## Timeline (Estimated)

- **Q2 2026**: Research spike + API design
- **Q2 2026**: Implementation + testing
- **Q3 2026**: Beta release to select customers
- **Q3 2026**: GA release

## Completion Notes

(Filled when PRD is complete.)
