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

## SDK Integration

Python teams can call the Enterprise API through the official SDK that ships with this repository.

```bash
pip install encypher-enterprise
```

```python
from encypher_enterprise import EncypherClient

client = EncypherClient(
    api_key="encypher_live_xxx",
    base_url="https://api.encypherai.com",
)

sign_response = client.sign(
    text="Example article content",
    title="SDK quick start",
)

verify_response = client.verify(sign_response.signed_text)
```

See `enterprise_sdk/README.md` for streaming, async, and framework integrations, and track upcoming milestones in `enterprise_sdk/SDK_WBS.md`.

## C2PA Text Embedding Compliance

The `POST /api/v1/sign` endpoint produces text that follows the [`C2PATextManifestWrapper`](../../docs/c2pa/Manifests_Text.adoc) guidance. Key guarantees:

- Each response appends a single zero-width no-break space (U+FEFF) followed by one contiguous block of variation selectors encoding the manifest store.
- The wrapper header contains the literal `C2PATXT\0` magic value, wrapper version `1`, and the manifest length before the JUMBF payload.
- Text is NFC-normalised prior to hashing and the wrapper byte-range is recorded in the `c2pa.hash.data` assertion `exclusions`, enabling deterministic validation.
- Verification (`POST /api/v1/verify`) rejects malformed wrappers and multiple wrappers, returning the spec-aligned `manifest.text.corruptedWrapper` or `manifest.text.multipleWrappers` statuses.

These behaviours allow any downstream validator that implements the C2PA unstructured text spec to parse and trust our basic embedding format.

## Authentication

All authenticated endpoints require an API key in the Authorization header:

```
Authorization: Bearer encypher_<your_api_key>
```

**Getting an API Key:**
- Preview phase: Contact sales@encypherai.com for beta access
- Production: Sign up at https://dashboard.encypherai.com
- Local development: set `DEMO_API_KEY` in `.env` to enable a sandbox key that bypasses database lookups

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
  "data": {
    "valid": true,
    "tampered": false,
    "reason_code": "OK",
    "signer_id": "org_123",
    "signer_name": "Example Publisher",
    "timestamp": "2025-01-15T10:30:00Z",
    "details": {
      "manifest": {
        "version": "1.0",
        "signer": "org_123",
        "timestamp": "2025-01-15T10:30:00Z"
      },
      "duration_ms": 35,
      "payload_bytes": 4800
    }
  },
  "error": null,
  "correlation_id": "req-123"
}
```

**Tampered Content Response:**
```json
{
  "success": true,
  "data": {
    "valid": false,
    "tampered": true,
    "reason_code": "SIGNATURE_INVALID",
    "signer_id": "org_123",
    "signer_name": "Example Publisher",
    "details": {
      "manifest": {},
      "exception": "hash mismatch"
    }
  },
  "error": null,
  "correlation_id": "req-456"
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

### GET /api/v1/usage

Get organization usage statistics for the current billing period.

**Authentication:** Required

**Response:**
```json
{
  "organization_id": "org_123",
  "tier": "enterprise",
  "period_start": "2025-11-01T00:00:00Z",
  "period_end": "2025-12-01T00:00:00Z",
  "metrics": {
    "c2pa_signatures": {
      "name": "C2PA Signatures",
      "used": 150,
      "limit": -1,
      "remaining": -1,
      "percentage_used": 0.0,
      "available": true
    },
    "api_calls": {
      "name": "API Calls",
      "used": 450,
      "limit": 10000,
      "remaining": 9550,
      "percentage_used": 4.5,
      "available": true
    }
  },
  "reset_date": "2025-12-01T00:00:00Z"
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

## Webhooks (Planned)

Webhook delivery is planned for a future Enterprise API release. The paths and payloads below represent the intended design, but **no `/api/v1/webhooks` endpoints are currently exposed by the service**.

### Supported Events
- `certificate.issued` - SSL.com certificate issued/renewed
- `quota.warning` - monthly usage exceeds configurable thresholds
- `verification.tamper_detected` - a signed asset fails validation

### POST /api/v1/webhooks
Register a webhook endpoint for your organization.

**Authentication:** Required - `can_sign` or `can_verify`

**Request**
```json
{
  "url": "https://example.com/webhooks/encypher",
  "description": "Primary monitoring hook",
  "events": ["certificate.issued", "verification.tamper_detected"],
  "secret": "optional-shared-secret"
}
```

**Response**
```json
{
  "success": true,
  "webhook_id": "wh_01HX...",
  "status": "pending",
  "events": ["certificate.issued", "verification.tamper_detected"],
  "url": "https://example.com/webhooks/encypher"
}
```

> **Note:** While in preview the endpoint returns `status: "pending"`. Events are queued but not delivered until the webhook worker is enabled.

### GET /api/v1/webhooks
List registered webhooks.

```json
{
  "success": true,
  "webhooks": [
    {
      "webhook_id": "wh_01HX...",
      "url": "https://example.com/webhooks/encypher",
      "events": ["certificate.issued"],
      "status": "pending",
      "created_at": "2025-02-12T18:44:00Z"
    }
  ]
}
```

### DELETE /api/v1/webhooks/{webhook_id}
Remove a webhook registration. Returns `{ "success": true }` on success.

### Delivery Format
Delivered events POST a JSON body with HMAC-SHA256 authentication if a secret is supplied:

```json
{
  "id": "evt_01HX...",
  "type": "verification.tamper_detected",
  "created_at": "2025-02-13T09:30:00Z",
  "data": {
    "document_id": "doc_abc123",
    "signer_id": "org_123",
    "verification_summary": {
      "is_valid": false,
      "failure_reason": "manifest.text.corruptedWrapper"
    }
  }
}
```

Preview deliveries are synchronous and retried up to three times. Production delivery will move to an asynchronous worker with exponential backoff and dead-letter queues.

---

## Batch Operations

- `POST /api/v1/batch/sign`  
  Body: `mode`, `segmentation_level`, `items[]`, `idempotency_key`. Returns per-item results plus a batch summary object. Retries with the same idempotency key reuse the stored run and prevent duplicate writes.

- `POST /api/v1/batch/verify`  
  Identical request schema, but returns `verdict` objects for each document. Tampered documents show `status: "error"` while valid documents continue.

## Streaming Signing (SSE)

- `POST /api/v1/stream/sign`  
  Streams `start`, `progress`, `partial`, and `final` events via Server-Sent Events. The final event includes the signed text, verification URL, and runtime statistics. Provide an optional `run_id` to make retries idempotent.

- `GET /api/v1/stream/runs/{run_id}`  
  Returns the most recent persisted state for a streaming run, enabling clients to resume after reconnects.

---

## Support

- **Documentation:** https://docs.encypherai.com
- **Email:** support@encypherai.com
- **Status:** https://status.encypherai.com
