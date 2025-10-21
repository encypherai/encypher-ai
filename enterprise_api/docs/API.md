# Encypher Enterprise API Documentation

**Base URL:** `https://api.encypherai.com`
**Environment:** Preview (C2PA spec pending public release)
**Version:** 1.0.0-preview

## Overview

The Encypher Enterprise API provides C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises. The API enables:

- **Content Signing**: Sign text content with C2PA manifests for provenance tracking
- **Verification**: Verify C2PA manifests to detect tampering
- **Sentence Lookup**: Track individual sentence provenance
- **Certificate Management**: Automated SSL.com certificate provisioning

## Authentication

All authenticated endpoints require an API key in the Authorization header:

```
Authorization: Bearer encypher_<your_api_key>
```

**Getting an API Key:**
- Preview phase: Contact sales@encypherai.com for beta access
- Production: Sign up at https://dashboard.encypherai.com

## Rate Limiting

Rate limits vary by tier:
- **Free**: 1,000 requests/month
- **Business**: 10,000 requests/month
- **Enterprise**: Unlimited

Rate limit headers are included in responses:
```
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 2025-02-01T00:00:00Z
```

---

## Endpoints

### POST /api/v1/sign

Sign content with C2PA manifest.

**Authentication:** Required
**Permission:** `can_sign`

**Request:**
```json
{
  "text": "Content to sign",
  "document_title": "Optional title",
  "document_url": "https://example.com/article",
  "document_type": "article"
}
```

**Parameters:**
- `text` (string, required): Content to sign (max 1MB)
- `document_title` (string, optional): Document title (max 500 chars)
- `document_url` (string, optional): Original document URL (max 1000 chars)
- `document_type` (string, optional): Document type
  - Options: `article`, `legal_brief`, `contract`, `ai_output`
  - Default: `article`

**Response:**
```json
{
  "success": true,
  "document_id": "doc_abc123xyz",
  "signed_text": "Content with invisible C2PA manifest...",
  "total_sentences": 5,
  "verification_url": "https://verify.encypherai.com/doc_abc123xyz"
}
```

**Example:**
```bash
curl -X POST https://api.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer encypher_test_..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The Senate passed a landmark bill today. The vote was 67-33.",
    "document_title": "Senate Passes Bill",
    "document_type": "article"
  }'
```

---

### POST /api/v1/verify

Verify C2PA manifest in signed content.

**Authentication:** Not required (public endpoint)

**Request:**
```json
{
  "text": "Signed content with embedded manifest..."
}
```

**Response:**
```json
{
  "success": true,
  "is_valid": true,
  "signer_id": "org_123",
  "organization_name": "Example Publisher",
  "signature_timestamp": "2025-01-15T10:30:00Z",
  "manifest": {
    "version": "1.0",
    "signer": "org_123",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "tampered": false
}
```

**Tampered Content Response:**
```json
{
  "success": true,
  "is_valid": false,
  "signer_id": "unknown",
  "organization_name": "Unknown",
  "signature_timestamp": null,
  "manifest": {},
  "tampered": true
}
```

**Example:**
```bash
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Signed content from previous step..."
  }'
```

---

### POST /api/v1/lookup

Look up sentence provenance by hash.

**Authentication:** Not required (public endpoint)

**Request:**
```json
{
  "sentence_text": "The Senate passed a landmark bill today."
}
```

**Response (Found):**
```json
{
  "success": true,
  "found": true,
  "document_title": "Senate Passes Bill",
  "organization_name": "Example Publisher",
  "publication_date": "2025-01-15T10:00:00Z",
  "sentence_index": 0,
  "document_url": "https://example.com/article"
}
```

**Response (Not Found):**
```json
{
  "success": true,
  "found": false
}
```

**Example:**
```bash
curl -X POST https://api.encypherai.com/api/v1/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "sentence_text": "The Senate passed a landmark bill today."
  }'
```

---

### POST /api/v1/onboarding/request-certificate

Request SSL.com code signing certificate for organization.

**Authentication:** Required
**Permission:** Any authenticated organization

**Request:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "cert_id": "cert_xyz789",
  "order_id": "ssl_order_123",
  "status": "pending_validation",
  "validation_url": "https://validation.ssl.com/...",
  "estimated_completion": "2-5 business days",
  "instructions": "Please complete identity verification at the validation URL..."
}
```

**Example:**
```bash
curl -X POST https://api.encypherai.com/api/v1/onboarding/request-certificate \
  -H "Authorization: Bearer encypher_test_..."
```

---

### GET /api/v1/onboarding/certificate-status

Get current certificate status for organization.

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "has_certificate": true,
  "cert_id": "cert_xyz789",
  "order_id": "ssl_order_123",
  "status": "issued",
  "validation_url": null,
  "ordered_at": "2025-01-10T14:00:00Z",
  "issued_at": "2025-01-12T16:30:00Z",
  "expires_at": "2027-01-12T16:30:00Z"
}
```

---

### GET /stats

Get organization usage statistics.

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "organization_id": "org_123",
  "organization_name": "Example Publisher",
  "tier": "enterprise",
  "usage": {
    "documents_signed": 150,
    "sentences_signed": 2500,
    "api_calls_this_month": 450,
    "monthly_quota": 10000,
    "quota_remaining": 9550
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional details (development only)"
  }
}
```

**Common Error Codes:**
- `INVALID_API_KEY`: API key is invalid or expired
- `QUOTA_EXCEEDED`: Monthly API quota exceeded
- `NO_PRIVATE_KEY`: Organization has no certificate configured
- `C2PA_EMBEDDING_FAILED`: Failed to embed C2PA manifest
- `DATABASE_ERROR`: Database operation failed
- `SSL_COM_API_ERROR`: SSL.com API request failed

---

## Webhooks (Coming Soon)

Future versions will support webhooks for:
- Certificate issuance notifications
- Quota warning notifications
- Tamper detection alerts

---

## Support

- **Documentation:** https://docs.encypherai.com
- **Email:** support@encypherai.com
- **Status:** https://status.encypherai.com
