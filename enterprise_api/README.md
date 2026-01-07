# Encypher Enterprise API

<div align="center">

![Encypher Logo](https://encypherai.com/encypher_full_logo_color.svg)

**Production-ready API for C2PA-compliant content signing and verification**

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://api.encypherai.com)
[![API Version](https://img.shields.io/badge/version-v1-blue)](https://docs.encypherai.com)
[![Uptime](https://img.shields.io/badge/uptime-99.9%25-brightgreen)](https://status.encypherai.com)
[![License](https://img.shields.io/badge/license-proprietary-red)](../LICENSE)

[Features](#-features) •
[Quick Start](#-quick-start) •
[API Reference](#-api-reference) •
[Architecture](#-architecture) •
[Documentation](#-documentation)

</div>

---

## 🎯 Overview

The Encypher Enterprise API provides cryptographic content signing and verification infrastructure for publishers, news organizations, legal firms, and content platforms. Built on **C2PA 2.2 standards** with enterprise-grade features for sentence-level tracking and source attribution.

**Part of the Encypher Microservices Ecosystem** - This API integrates with multiple backend microservices for authentication, key management, and coalition features.

### Why Encypher API?

- **🔒 C2PA 2.2 Compliant**: Industry-standard content authenticity
- **⚡ High Performance**: <100ms verification, 1000+ req/s capacity
- **🔗 Microservices Architecture**: Scalable, resilient, database-per-service design
- **📊 Enterprise Features**: Merkle trees, source attribution, plagiarism detection
- **🔐 SSL.com Integration**: Automated certificate lifecycle management
- **⚖️ Court-Admissible**: Tamper-evident manifests for legal evidence

---

## ✨ Features

### Complete Feature List

#### Core Capabilities
- ✅ **C2PA-Compliant Signing**: Full C2PA 2.2 text manifest support
- ✅ **Content Verification**: Cryptographic verification with tamper detection
- ✅ **Sentence-Level Tracking**: Track provenance of individual sentences
- ✅ **Public Verification Pages**: Shareable verification URLs
- ✅ **Batch Operations**: Sign/verify up to 100 documents at once
- ✅ **Streaming Support**: WebSocket and SSE for real-time operations
- ✅ **Custom Metadata**: Attach arbitrary metadata to signed content
- ✅ **API Key Management**: Via integrated Key Service

#### Enterprise Features
- ✅ **Merkle Tree Encoding**: Hierarchical content fingerprinting
- ✅ **Source Attribution**: Find original sources of quoted content
- ✅ **Plagiarism Detection**: Detect unauthorized content reuse
- ✅ **Invisible Embeddings**: Unicode-based portable content tracking
- ✅ **Custom C2PA Assertions**: Define custom assertion types
- ✅ **Assertion Templates**: Pre-built templates for various industries
- ✅ **Schema Registry**: Manage custom JSON schemas
- ✅ **C2PA Provenance Chain**: Full edit history tracking
- ✅ **Public Extraction API**: Third-party embedding verification

#### Coalition Features (via Coalition Service)
- ✅ **Auto-Enrollment**: Automatic coalition membership for free tier
- ✅ **Content Indexing**: Aggregate content for bulk licensing
- ✅ **Revenue Sharing**: 70/30 split (members/platform)
- ✅ **Access Tracking**: Monitor content usage by AI companies

#### Team & Administration
- ✅ **Team Management**: Multi-user organizations
- ✅ **Audit Logs**: Complete activity tracking
- ✅ **Usage Analytics**: Detailed usage metrics
- ✅ **Tier-Based Access**: Feature gating by subscription tier
- ✅ **Bring Your Own Keys (BYOK)**: Use your own signing keys (Professional+)
- ✅ **SSO Integration**: Single Sign-On (Enterprise)

---

## 📋 Complete API Endpoint Reference

### Core Endpoints

| Endpoint | Method | Auth | Tier | Description | Dependencies |
|----------|--------|------|------|-------------|--------------|
| `/api/v1/sign` | POST | ✅ | All | Sign content with C2PA manifest | Key Service, Coalition Service (optional) |
| `/api/v1/sign/advanced` | POST | ✅ | Professional+ | Sign content with advanced embedding controls (manifest mode, distribution, ECC) | Key Service, Coalition Service (optional) |
| `/api/v1/verify` | POST | ❌ | Public | Verify signed content | None |
| `/api/v1/verify/{document_id}` | GET | ❌ | Public | Verify a previously signed document by ID | None |
| `/api/v1/lookup` | POST | ❌ | Public | Lookup sentence provenance | None |
| `/api/v1/provenance/lookup` | POST | ❌ | Public | Lookup provenance for a document (structured) | None |
| `/api/v1/account` | GET | ✅ | All | Get account profile | Auth Service |
| `/api/v1/account/quota` | GET | ✅ | All | Get account quota and limits | Billing Service |
| `/api/v1/usage` | GET | ✅ | All | Get organization usage statistics | Key Service |
| `/api/v1/usage/history` | GET | ✅ | All | Get historical usage summaries | Analytics Service |

### Public C2PA Utilities

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/public/c2pa/validate-manifest` | POST | ❌ | Public | Validate manifest JSON structure + assertion schema payloads (non-cryptographic). Optional API key supported for higher limits |
| `/api/v1/public/c2pa/create-manifest` | POST | ❌ | Public | Create a manifest JSON payload from plaintext (non-cryptographic) and return a signing helper payload. Optional API key supported for higher limits |
| `/api/v1/public/c2pa/trust-anchors/{signer_id}` | GET | ❌ | Public | Lookup trust anchor (public key) for external C2PA validators (public, IP rate-limited) |

### Enterprise Merkle Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/merkle/encode` | POST | ✅ | Enterprise | Encode document into Merkle tree |
| `/api/v1/enterprise/merkle/attribute` | POST | ✅ | Enterprise | Find source documents via Merkle matching |
| `/api/v1/enterprise/merkle/detect-plagiarism` | POST | ✅ | Enterprise | Detect plagiarized content |

### Streaming Merkle Endpoints (NEW - Patent FIG. 5)

Real-time Merkle tree construction for streaming content signing (e.g., LLM output).

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/stream/merkle/start` | POST | ✅ | Professional+ | Start streaming Merkle session |
| `/api/v1/enterprise/stream/merkle/segment` | POST | ✅ | Professional+ | Add segment to session |
| `/api/v1/enterprise/stream/merkle/finalize` | POST | ✅ | Professional+ | Finalize session and compute root |
| `/api/v1/enterprise/stream/merkle/status` | POST | ✅ | Professional+ | Check session status |

### Evidence Generation Endpoints (NEW - Patent FIG. 11)

Generate court-ready evidence packages for content attribution.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/evidence/generate` | POST | ✅ | Enterprise | Generate evidence package with Merkle proofs |

### Fingerprint Endpoints (NEW)

Robust fingerprinting that survives text modifications.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/fingerprint/encode` | POST | ✅ | Enterprise | Encode keyed fingerprint into text |
| `/api/v1/enterprise/fingerprint/detect` | POST | ✅ | Enterprise | Detect fingerprint in text |

### Multi-Source Attribution Endpoints (NEW - Patent FIG. 8)

Look up content across multiple sources with chronological ordering.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/attribution/multi-source` | POST | ✅ | Business+ | Multi-source hash lookup with authority ranking |

### Public Verification Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/public/verify/{ref_id}` | GET | ❌ | Public | Verify embedding by reference ID |
| `/api/v1/public/verify/batch` | POST | ❌ | Public | Batch verify embeddings |
| `/api/v1/public/extract-and-verify` | POST | ❌ | Public | Extract and verify C2PA manifest |

### Enterprise C2PA Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/c2pa/schemas` | POST | ✅ | Enterprise | Register custom C2PA assertion schema |
| `/api/v1/enterprise/c2pa/schemas` | GET | ✅ | Enterprise | List custom schemas |
| `/api/v1/enterprise/c2pa/schemas/{schema_id}` | GET | ✅ | Enterprise | Get custom schema |
| `/api/v1/enterprise/c2pa/schemas/{schema_id}` | PUT | ✅ | Enterprise | Update custom schema |
| `/api/v1/enterprise/c2pa/schemas/{schema_id}` | DELETE | ✅ | Enterprise | Delete custom schema |
| `/api/v1/enterprise/c2pa/validate` | POST | ✅ | Enterprise | Validate assertion before embedding |
| `/api/v1/enterprise/c2pa/templates` | POST | ✅ | Enterprise | Create assertion template |
| `/api/v1/enterprise/c2pa/templates` | GET | ✅ | Enterprise | List assertion templates |
| `/api/v1/enterprise/c2pa/templates/{template_id}` | GET | ✅ | Enterprise | Get assertion template |
| `/api/v1/enterprise/c2pa/templates/{template_id}` | PUT | ✅ | Enterprise | Update assertion template |
| `/api/v1/enterprise/c2pa/templates/{template_id}` | DELETE | ✅ | Enterprise | Delete assertion template |

### Batch Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/batch/sign` | POST | ✅ | Business+ | Batch sign up to 100 documents |
| `/api/v1/batch/verify` | POST | ✅ | Business+ | Batch verify signed content |

### Streaming Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/stream/sign` | POST/WS | ✅ | Professional+ | Real-time signing via SSE (POST) and WebSocket (WS) |
| `/api/v1/stream/chat` | WS | ✅ | Professional+ | WebSocket chat stream (signing wrapper) |
| `/api/v1/stream/chat/openai-compatible` | POST | ✅ | Professional+ | OpenAI-compatible SSE chat completions with signing |
| `/api/v1/stream/chat/health` | GET | ❌ | Public | Streaming chat health check |
| `/api/v1/stream/events` | GET | ✅ | Professional+ | Server-Sent Events (SSE) heartbeat and events |
| `/api/v1/stream/session/create` | POST | ✅ | Professional+ | Create streaming session |
| `/api/v1/stream/session/{session_id}/close` | POST | ✅ | Professional+ | Close streaming session |
| `/api/v1/stream/runs/{run_id}` | GET | ✅ | Professional+ | Get streaming run state |
| `/api/v1/stream/stats` | GET | ✅ | Professional+ | Get organization streaming statistics |

### Account, Keys, BYOK, Documents, and Webhooks

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/keys` | GET | ✅ | All | List API keys |
| `/api/v1/keys` | POST | ✅ | All | Create API key |
| `/api/v1/keys/{key_id}` | PATCH | ✅ | All | Update API key (name/metadata) |
| `/api/v1/keys/{key_id}` | DELETE | ✅ | All | Delete API key |
| `/api/v1/keys/{key_id}/rotate` | POST | ✅ | All | Rotate API key |
| `/api/v1/byok/public-keys` | GET | ✅ | Professional+ | List BYOK public keys |
| `/api/v1/byok/public-keys` | POST | ✅ | Professional+ | Register BYOK public key |
| `/api/v1/byok/public-keys/{key_id}` | DELETE | ✅ | Professional+ | Delete BYOK public key |
| `/api/v1/byok/trusted-cas` | GET | ❌ | Public | List C2PA trusted Certificate Authorities |
| `/api/v1/byok/certificates` | POST | ✅ | Business+ | Upload CA-signed certificate (validated against C2PA trust list) |
| `/api/v1/documents` | GET | ✅ | Business+ | List signed documents |
| `/api/v1/documents/{document_id}` | GET | ✅ | Business+ | Get signed document |
| `/api/v1/documents/{document_id}/history` | GET | ✅ | Enterprise | Get document provenance history |
| `/api/v1/documents/{document_id}` | DELETE | ✅ | Business+ | Soft-delete a document |
| `/api/v1/webhooks` | GET | ✅ | Business+ | List webhooks |
| `/api/v1/webhooks` | POST | ✅ | Business+ | Create webhook |
| `/api/v1/webhooks/{webhook_id}` | GET | ✅ | Business+ | Get webhook |
| `/api/v1/webhooks/{webhook_id}` | PATCH | ✅ | Business+ | Update webhook |
| `/api/v1/webhooks/{webhook_id}` | DELETE | ✅ | Business+ | Delete webhook |
| `/api/v1/webhooks/{webhook_id}/deliveries` | GET | ✅ | Business+ | List webhook deliveries |
| `/api/v1/webhooks/{webhook_id}/test` | POST | ✅ | Business+ | Send a test delivery |

### Tools

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/tools/encode` | POST | ✅ | All | Encode content into a transport-safe representation |
| `/api/v1/tools/decode` | POST | ✅ | All | Decode previously encoded content |

### Coalition Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/coalition/dashboard` | GET | ✅ | All | Get coalition dashboard (content, earnings, payouts) |
| `/api/v1/coalition/content-stats` | GET | ✅ | All | Get historical content corpus statistics |
| `/api/v1/coalition/earnings` | GET | ✅ | All | Get detailed earnings history |
| `/api/v1/coalition/opt-out` | POST | ✅ | All | Opt out of coalition revenue sharing |
| `/api/v1/coalition/opt-in` | POST | ✅ | All | Opt in to coalition revenue sharing |

### Document Revocation Endpoints (NEW)

| Endpoint | Description | Tier |
|----------|-------------|------|
| `POST /api/v1/status/documents/{document_id}/revoke` | Revoke a document's authenticity | Enterprise |
| `POST /api/v1/status/documents/{document_id}/reinstate` | Reinstate a revoked document | Enterprise |
| `GET /api/v1/status/documents/{document_id}` | Get document revocation status | Enterprise |
| `GET /api/v1/status/list/{organization_id}/{list_index}` | Get status list credential (public, CDN-cacheable) | Public |
| `GET /api/v1/status/stats` | Get revocation statistics | Enterprise |

### Licensing Endpoints

Licensing endpoints are internal-only and intentionally excluded from the public OpenAPI schema.

For full details, see [docs/LICENSING_API.md](./docs/LICENSING_API.md).

### Onboarding & Provisioning Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/onboarding/request-certificate` | POST | ✅ | All | Request SSL.com code signing certificate |
| `/api/v1/onboarding/certificate-status` | GET | ✅ | All | Get current certificate status |

### Health & Monitoring Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/health` | GET | ❌ | Public | Health check |
| `/readyz` | GET | ❌ | Public | Readiness probe |
| `/` | GET | ❌ | Public | API information |

### Features by Tier

#### Starter Tier (Free)
- ✅ C2PA-compliant signing
- ✅ Content verification
- ✅ Public verification pages
- ✅ 10,000 requests/month
- ✅ Coalition membership (65% publisher / 35% Encypher revenue share)

#### Professional Tier ($99/month)
- ✅ All Starter features
- ✅ Sentence-level lookup
- ✅ Invisible signed embeddings
- ✅ Custom metadata
- ✅ Streaming support (WebSocket/SSE)
- ✅ **Lightweight UUID Manifest**: Smaller payload footprint (NEW)
- ✅ **Streaming Merkle Tree**: Real-time LLM signing (NEW)
- ✅ 100,000 requests/month
- ✅ Priority support
- ✅ Coalition membership (70% publisher / 30% Encypher revenue share)

#### Business Tier ($499/month)
- ✅ All Professional features
- ✅ Merkle tree encoding
- ✅ Custom C2PA assertions
- ✅ Batch operations
- ✅ Team management (up to 10 members)
- ✅ Audit logs
- ✅ Bring Your Own Keys (BYOK)
- ✅ **Distributed Embedding**: Resilient metadata placement (NEW)
- ✅ **Dual-Binding Manifest**: Enhanced tamper-evidence (NEW)
- ✅ **Multi-Source Lookup**: Content attribution across sources (NEW)
- ✅ 500,000 requests/month
- ✅ Coalition membership (75% publisher / 25% Encypher revenue share)

#### Enterprise Tier (Custom pricing)
- ✅ All Business features
- ✅ **C2PA Provenance Chain**: Full edit history
- ✅ **Assertion Templates**: Pre-built industry templates
- ✅ **Schema Registry**: Custom assertion schemas
- ✅ Source attribution
- ✅ Plagiarism detection
- ✅ **Evidence Generation**: Court-ready evidence packages (NEW)
- ✅ **Robust Fingerprinting**: Survives text modifications (NEW)
- ✅ **Authority Ranking**: Configurable source ranking (NEW)
- ✅ **Distributed + ECC**: Error-correcting redundancy (NEW)
- ✅ Unlimited team members
- ✅ SSO integration
- ✅ Unlimited requests
- ✅ SLA guarantee (99.9%)
- ✅ Dedicated support
- ✅ Coalition membership (80% publisher / 20% Encypher revenue share)

---

## 🚀 Quick Start

### Authentication

Authenticated API requests require an API key in the `Authorization` header.

Some endpoints are public (no auth required) and support an *optional* API key for higher limits.

```bash
curl -X POST https://api.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer encypher_..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your content here",
    "title": "Article Title"
  }'
```

### Get Your API Key

1. Sign up at [dashboard.encypherai.com](https://dashboard.encypherai.com)
2. Navigate to API Keys
3. Create new key
4. Copy and secure your key

---

## 📚 API Reference

### Interactive API Docs

The API exposes interactive OpenAPI documentation:

**Public Docs (recommended):**
- Production: `https://api.encypherai.com/docs` (branded docs landing page)
- Swagger UI: `https://api.encypherai.com/docs/swagger`
- OpenAPI JSON: `https://api.encypherai.com/docs/openapi.json`

**Internal Docs (super admin only):**
- Swagger UI: `https://api.encypherai.com/internal/docs`
- OpenAPI JSON: `https://api.encypherai.com/internal/openapi.json`

**Local development (direct to Enterprise API):**
- `http://localhost:9000/docs`
- `http://localhost:9000/docs/swagger`
- `http://localhost:9000/docs/openapi.json`
- `http://localhost:9000/internal/docs` (requires super admin)

The gateway URL is what you should give to external developers—it's the single entry point for all API operations.

For up-to-date per-tier limits and quotas, see [FEATURE_MATRIX.md](../FEATURE_MATRIX.md).

### POST /api/v1/sign

Sign content with C2PA-compliant manifest.

**Dependencies**: Key Service (required), Coalition Service (optional)

**Request:**

```json
{
  "text": "Your content here",
  "title": "Article Title",
  "metadata": {
    "author": "Jane Doe",
    "publisher": "Acme News",
    "license": "CC-BY-4.0",
    "category": "Technology",
    "tags": ["AI", "Technology"],
    "custom": {
      "department": "Editorial",
      "editor": "John Smith"
    }
  },
  "use_sentence_tracking": true
}
```

**Response:**

```json
{
  "success": true,
  "document_id": "doc_abc123xyz",
  "signed_text": "Your content here\u{FEFF}C2PATXT...",
  "verification_url": "https://encypherai.com/verify/doc_abc123xyz",
  "manifest": {
    "version": "2.2",
    "claim_generator": "Encypher Enterprise API v1.0",
    "assertions": [
      {
        "label": "c2pa.hash.data",
        "data": {
          "hash": "sha256:...",
          "algorithm": "sha256"
        }
      }
    ]
  },
  "metadata": {
    "author": "Jane Doe",
    "publisher": "Acme News",
    "signed_at": "2025-10-29T18:00:00Z"
  },
  "total_sentences": 42
}
```

---

### POST /api/v1/verify

Verify signed content and detect tampering.

**Dependencies**: None (public endpoint)

**Request:**

```json
{
  "text": "Your content here\uFEFFC2PATXT..."
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
    "signer_id": "org_demo",
    "signer_name": "Demo Publisher",
    "timestamp": "2025-11-11T22:11:12Z",
    "details": {
      "manifest": {
        "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
        "instance_id": "37fb375f-d294-4fcb-992d-e1be5a57b92a",
        "claim_generator": "encypher-ai/2.4.2",
        "assertions": [
          {"label": "c2pa.actions.v1", "kind": "Actions"},
          {"label": "c2pa.hash.data.v1", "kind": "ContentHash"}
        ]
      },
      "duration_ms": 41,
      "payload_bytes": 4988,
      "certificate_status": "active"
    }
  },
  "error": null,
  "correlation_id": "req-7f2c9c3f190141a3b5b7b1a5e3d98d61"
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
    "signer_id": "org_demo",
    "signer_name": "Demo Publisher",
    "details": {
      "manifest": {},
      "duration_ms": 18,
      "payload_bytes": 4996,
      "missing_signers": [],
      "exception": "wrapper hash mismatch"
    }
  },
  "error": null,
  "correlation_id": "req-0c2ec4c3f7104d6c87bbac44dc9d986a"
}
```

---

### POST /api/v1/lookup

Lookup sentence provenance (Professional+ tier).

**Dependencies**: None (public endpoint)

**Request:**

```json
{
  "sentence": "This is the sentence to look up.",
  "context_window": 2
}
```

**Response:**

```json
{
  "success": true,
  "found": true,
  "document_id": "doc_abc123xyz",
  "sentence_index": 5,
  "paragraph_index": 2,
  "document_title": "Article Title",
  "organization_name": "Acme News",
  "publication_date": "2025-10-29T18:00:00Z",
  "context": {
    "before": ["Previous sentence 1.", "Previous sentence 2."],
    "sentence": "This is the sentence to look up.",
    "after": ["Next sentence 1.", "Next sentence 2."]
  },
  "metadata": {
    "author": "Jane Doe",
    "publisher": "Acme News"
  }
}
```

---

### GET /api/v1/usage

Get usage statistics for your organizations current billing period.

**Dependencies**: Key Service (required)

**Response:**

```json
{
  "organization_id": "org_123",
  "tier": "business",
  "period_start": "2025-11-01T00:00:00Z",
  "period_end": "2025-12-01T00:00:00Z",
  "metrics": {
    "c2pa_signatures": {
      "name": "C2PA Signatures",
      "used": 1234,
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

## 🔬 Enterprise Features

### Merkle Tree Encoding

Encode documents into Merkle trees for sentence-level tracking.

**Endpoint:** `POST /api/v1/enterprise/merkle/encode`

**Request:**

```json
{
  "text": "Your document content here...",
  "document_id": "doc_abc123",
  "segmentation_levels": ["sentence", "paragraph"]
}
```

**Response:**

```json
{
  "success": true,
  "document_id": "doc_abc123",
  "roots": [
    {
      "level": "sentence",
      "root_hash": "sha256:abc123...",
      "node_count": 42
    },
    {
      "level": "paragraph",
      "root_hash": "sha256:def456...",
      "node_count": 8
    }
  ],
  "encoding_time_ms": 123
}
```

---

### Source Attribution

Find original sources of content using Merkle tree matching.

**Endpoint:** `POST /api/v1/enterprise/merkle/attribute`

**Request:**

```json
{
  "text": "Text to find sources for",
  "min_similarity": 0.85,
  "max_results": 10
}
```

**Response:**

```json
{
  "success": true,
  "matches": [
    {
      "document_id": "doc_original123",
      "similarity": 0.95,
      "matched_text": "Original text that matches...",
      "document_title": "Original Article",
      "organization_name": "Original Publisher",
      "publication_date": "2025-10-15T10:00:00Z"
    }
  ],
  "search_time_ms": 45
}
```

---

### Plagiarism Detection

Detect if content is plagiarized from signed documents.

**Endpoint:** `POST /api/v1/enterprise/merkle/detect-plagiarism`

**Request:**

```json
{
  "text": "Text to check for plagiarism",
  "threshold": 0.80
}
```

**Response:**

```json
{
  "success": true,
  "is_plagiarized": true,
  "similarity": 0.92,
  "original_document_id": "doc_original123",
  "original_title": "Original Article",
  "original_author": "Jane Doe",
  "original_publisher": "Acme News",
  "publication_date": "2025-10-15T10:00:00Z",
  "matched_segments": [
    {
      "query_text": "Plagiarized text segment...",
      "original_text": "Original text segment...",
      "similarity": 0.95
    }
  ]
}
```

---

### Invisible Signed Embeddings (Professional+)

Invisibly embed cryptographically signed references directly into content using Unicode variation selectors. The embeddings are completely invisible to readers but can be extracted and verified by third parties without requiring API keys.

**Endpoint:** `POST /api/v1/sign/advanced`

**Request:**

```json
{
  "document_id": "article_001",
  "text": "Full article text...",
  "segmentation_level": "sentence",
  "c2pa_manifest_url": "https://...",
  "license": {
    "type": "All Rights Reserved",
    "contact_email": "licensing@example.com"
  }
}
```

**Response:**

```json
{
  "success": true,
  "document_id": "article_001",
  "merkle_tree": {
    "root_hash": "abc123...",
    "total_leaves": 42,
    "tree_depth": 6
  },
  "embeddings": [
    {
      "leaf_index": 0,
      "text": "Sentence one.",
      "ref_id": "a3f9c2e1",
      "leaf_hash": "def456...",
      "embedded_text": "Sentence one."
    }
  ],
  "embedded_content": "Full article text with invisible embeddings...",
  "statistics": {
    "total_sentences": 42,
    "embeddings_created": 42,
    "processing_time_ms": 234.56
  }
}
```

**How It Works:**

The embedding uses **Unicode variation selectors (U+FE00-FE0F)** attached to characters in the text. These selectors are:
- **Completely invisible** - Rendering engines ignore them and display only the base character
- **Standards-compliant** - Using Unicode variation selectors as designed
- **Portable** - Preserved during copy/paste operations
- **Distributed** - Spread across multiple characters for resilience

Example (conceptual - actual variation selectors are invisible):
```
"Hello world" → "H[VS]e[VS]l[VS]l[VS]o[VS] w[VS]o[VS]r[VS]l[VS]d"
```

**Public Verification (No Auth Required):**

Extract embeddings from content and verify them:

```bash
# Extract and verify embeddings from text
curl -X POST https://api.encypherai.com/api/v1/public/extract-and-verify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Content with invisible embeddings..."
  }'
```

**Key Features:**
- ✅ **Invisible**: Zero visible footprint - readers see only the original text
- ✅ **Portable**: Travels with content when copied/scraped across the web
- ✅ **Verifiable**: Public API for third-party verification (no auth required)
- ✅ **Secure**: Cryptographic signatures prevent forgery
- ✅ **Resilient**: Distributed embedding survives partial text extraction
- ✅ **Standards-compliant**: Uses Unicode variation selectors as designed

**Use Cases:**
- Invisible content tracking across the web
- Partner integration (web scrapers, content monitors)
- Portable proof of origin that travels with text
- Legal evidence embedded directly in content
- AI-generated content authentication

**Documentation:** See [README_EMBEDDINGS.md](./app/services/README_EMBEDDINGS.md) for complete details.

---

### Document Revocation (Enterprise) ⭐ NEW

Revoke individual documents without affecting your entire signing certificate. Uses W3C StatusList2021 bitstrings for internet-scale revocation (10+ billion documents).

**Revoke a Document:**

```bash
curl -X POST https://api.encypherai.com/api/v1/status/documents/doc_abc123/revoke \
  -H "Authorization: Bearer encypher_..." \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "factual_error",
    "reason_detail": "Article contained incorrect statistics"
  }'
```

**Response:**

```json
{
  "success": true,
  "document_id": "doc_abc123",
  "action": "revoked",
  "timestamp": "2025-12-01T19:00:00Z",
  "message": "Document doc_abc123 has been revoked. Verification will fail within 5 minutes."
}
```

**Revocation Reasons:**

| Reason | Description |
|--------|-------------|
| `factual_error` | Content contains factual errors |
| `legal_takedown` | Legal request (DMCA, court order) |
| `copyright_claim` | Copyright infringement claim |
| `privacy_request` | Privacy/GDPR request |
| `publisher_request` | Publisher-initiated takedown |
| `security_concern` | Security vulnerability in content |
| `content_policy` | Violates content policy |
| `other` | Other reason (specify in reason_detail) |

**Verification of Revoked Documents:**

When a revoked document is verified, the response includes:

```json
{
  "success": true,
  "data": {
    "valid": false,
    "tampered": false,
    "reason_code": "DOC_REVOKED",
    "signer_id": "org_publisher",
    "signer_name": "Acme News",
    "details": {
      "document_revoked": true,
      "revocation_reason": "Document has been revoked by publisher"
    }
  }
}
```

**How It Works:**

1. **Signing**: Each document is assigned a position in a bitstring status list
2. **Revocation**: Setting the bit marks the document as revoked
3. **Verification**: Verifiers fetch the cached status list and check the bit
4. **Propagation**: Changes propagate within 5 minutes (CDN cache TTL)

**Scale:**

| Metric | Capacity |
|--------|----------|
| Documents per list | 131,072 |
| Storage per 1B docs | ~120 MB |
| Lookup time | O(1) |
| Revocation latency | <5 minutes |

**Public Status List Endpoint:**

Status lists are served publicly for third-party verification:

```
GET https://status.encypherai.com/v1/{org_id}/list/{index}
```

Returns a W3C StatusList2021Credential (JSON-LD) with 5-minute cache headers.

---

## 🏗️ Architecture

### Microservices Architecture

The Enterprise API is part of a comprehensive microservices ecosystem. Each service maintains its own database following the **database-per-service** pattern for scalability and resilience.

```
┌──────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
│          (SDK, CLI, WordPress, Direct API Calls)             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway (Traefik)                      │
│                        Port 8000                              │
│          Routes /api/v1/* to appropriate services             │
└──────────────────────────────────────────────────────────────┘
                              ↓
            ┌─────────────────┴─────────────────┐
            ↓                                   ↓
┌─────────────────────────┐       ┌─────────────────────────┐
│   Enterprise API        │       │    Key Service          │
│     Port 9000           │←──────│     Port 8003           │
│                         │       │                         │
│ - C2PA Signing          │       │ - API Key Validation    │
│ - Content Verification  │       │ - Org Context/Tier      │
│ - Merkle Trees          │       │ - Feature Permissions   │
│ - Embeddings            │       │ - Usage Quotas          │
│ - Sentence Tracking     │       │                         │
└─────────────────────────┘       └─────────────────────────┘
            ↓                                   ↓
┌─────────────────────────┐       ┌─────────────────────────┐
│  PostgreSQL Content DB  │       │  PostgreSQL Keys DB     │
│   (Enterprise API)      │       │   (Key Service)         │
│                         │       │                         │
│ - documents             │       │ - api_keys              │
│ - merkle_trees          │       │ - organizations         │
│ - sentence_records      │       │ - subscriptions         │
│ - manifests             │       │ - usage_records         │
│ - embeddings            │       │                         │
└─────────────────────────┘       └─────────────────────────┘

            ↓
┌─────────────────────────┐       ┌─────────────────────────┐
│  Coalition Service      │       │    Auth Service         │
│     Port 8009           │       │     Port 8001           │
│                         │       │                         │
│ - Content Indexing      │       │ - User Authentication   │
│ - Revenue Distribution  │       │ - JWT Management        │
│ - Licensing Management  │       │ - OAuth Integration     │
│ - Member Stats          │       │                         │
└─────────────────────────┘       └─────────────────────────┘
            ↓                                   ↓
┌─────────────────────────┐       ┌─────────────────────────┐
│ PostgreSQL Coalition DB │       │  PostgreSQL Auth DB     │
│  (Coalition Service)    │       │   (Auth Service)        │
│                         │       │                         │
│ - coalition_members     │       │ - users                 │
│ - coalition_content     │       │ - sessions              │
│ - licensing_agreements  │       │ - oauth_tokens          │
│ - revenue_distributions │       │                         │
└─────────────────────────┘       └─────────────────────────┘

                    ↓
┌──────────────────────────────────────────────────────────────┐
│                    Redis Cache Layer                          │
│                        Port 6379                              │
│                                                               │
│ - Key Validation Cache (5min TTL)                            │
│ - Session Management                                          │
│ - Rate Limiting State                                         │
│ - Streaming Session State                                    │
└──────────────────────────────────────────────────────────────┘

                    ↓
┌──────────────────────────────────────────────────────────────┐
│                  encypher-ai Core Library                     │
│                      (v2.9.0+)                               │
│                                                               │
│ - C2PA Manifest Generation                                    │
│ - Unicode Metadata Embedding                                  │
│ - Cryptographic Signature Verification                        │
│ - Merkle Tree Operations                                      │
└──────────────────────────────────────────────────────────────┘
```

### Database-Per-Service Pattern

Each microservice maintains its own PostgreSQL database for complete autonomy:

| Service | Database | Tables | Purpose |
|---------|----------|--------|---------|
| **Enterprise API** | `encypher_content` | documents, merkle_trees, sentence_records, manifests, embeddings | Content signing and verification data |
| **Key Service** | `encypher_keys` | api_keys, organizations, subscriptions, usage_records | API key management and billing |
| **Coalition Service** | `encypher_coalition` | coalition_members, coalition_content, licensing_agreements | Coalition membership and licensing |
| **Auth Service** | `encypher_auth` | users, sessions, oauth_tokens | User authentication |
| **User Service** | `encypher_users` | profiles, teams, team_members | User profiles and teams |
| **Analytics Service** | `encypher_analytics` | events, metrics, aggregations | Usage analytics |
| **Billing Service** | `encypher_billing` | invoices, payments, subscriptions | Billing and payments |

### Service Dependencies

#### Enterprise API Dependencies

**Required Services:**
- **Key Service** (Port 8003)
  - Purpose: API key validation, organization context, tier features
  - Used by: All authenticated endpoints
  - Fallback: Demo keys for local development
  - Health Impact: Critical - API cannot authenticate without it

**Optional Services:**
- **Coalition Service** (Port 8009)
  - Purpose: Content indexing, coalition membership, revenue distribution
  - Used by: `/api/v1/sign` endpoint for coalition members
  - Fallback: Graceful degradation (signing continues, indexing skipped)
  - Health Impact: Non-critical

**Infrastructure:**
- **PostgreSQL Content Database**: Required (own database)
- **Redis Cache**: Required for session management and key validation caching

### Unified Authentication Flow

```
1. Client → Enterprise API
   Authorization: Bearer encypher_abc123...

2. Enterprise API → Key Service
   POST /api/v1/keys/validate
   { "key": "encypher_abc123..." }

3. Key Service → PostgreSQL Keys DB
   SELECT * FROM api_keys WHERE key_hash = hash(...)
   JOIN organizations, subscriptions

4. Key Service → Enterprise API
   {
     "success": true,
     "data": {
       "organization_id": "org_xyz",
       "tier": "business",
       "features": {...},
       "permissions": ["sign", "verify", "lookup"],
       "usage": {...}
     }
   }

5. Enterprise API → Redis
   Cache validation result (5min TTL)

6. Enterprise API → Client
   Process request with org context
```

**Caching Strategy:**
- First request: Validates via Key Service, caches result in Redis (5min TTL)
- Subsequent requests: Uses cached validation (no Key Service call)
- Cache miss: Automatic re-validation via Key Service

### Coalition Integration Flow

```
1. Client signs content → Enterprise API
   POST /api/v1/sign

2. Enterprise API checks if user is coalition member

3. If coalition member:
   Enterprise API → Coalition Service
   POST /api/v1/coalition/content
   {
     "member_id": "...",
     "document_id": "...",
     "content_hash": "...",
     "word_count": 1500,
     "signed_at": "2025-12-01T10:00:00Z"
   }

4. Coalition Service → PostgreSQL Coalition DB
   INSERT INTO coalition_content (...)

5. Coalition Service tracks content for:
   - Bulk licensing to AI companies
   - Revenue distribution (70% members, 30% platform)
   - Access tracking and analytics
```

**Graceful Degradation:**
If Coalition Service is unavailable, content signing continues successfully. Coalition indexing is retried in background or skipped with warning log.

### C2PA Compliance

Our implementation follows **C2PA 2.3 Text Manifest Specification**:

- **Wrapper Format**: `C2PATXT\0` header with Unicode variation selectors
- **Prefix**: Single zero-width no-break space (U+FEFF)
- **Hash Algorithm**: SHA-256 with NFC normalization
- **Assertions**: `c2pa.hash.data`, `c2pa.claim.generator`, custom assertions
- **Validation**: Rejects malformed/duplicate wrappers per spec

**Reference:** [docs/c2pa/Manifests_Text.adoc](../docs/c2pa/Manifests_Text.adoc)

---

## 🔐 Security

### Unified Authentication Architecture

The Enterprise API uses the **Key Service** for all authentication:

1. **API Key Validation**: All API keys validated via Key Service `/api/v1/keys/validate` endpoint
2. **Caching**: Validation results cached in Redis (5-minute TTL) to reduce latency
3. **Organization Context**: Key Service returns complete organization context:
   - Tier (starter, professional, business, enterprise)
   - Features enabled for the tier
   - Usage limits and current usage
   - Permissions (sign, verify, lookup)
   - Coalition membership status

**Service Location**: `services/key-service` (Port 8003)

**Demo Keys**: For local development when Key Service is unavailable, Enterprise API falls back to demo keys defined in `app/dependencies.py`

### Authentication

- **API Keys**: Bearer token authentication via Key Service
- **Key Rotation**: Automatic rotation every 90 days
- **Scoped Keys**: Limit keys to specific endpoints/operations
- **Key Format**: `encypher_<random_32_chars>`

### Rate Limiting

Rate limits are enforced per organization with tier-aware limits. All responses include rate limit headers.

| Tier | Requests/Second | Requests/Minute | Monthly Quota |
|------|-----------------|-----------------|---------------|
| Starter | 10 | 600 | 10,000 |
| Professional | 50 | 3,000 | 100,000 |
| Business | 200 | 12,000 | 500,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |
| Strategic Partner | Unlimited | Unlimited | Unlimited |

**Rate Limit Headers:**

All API responses include the following headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests allowed in the current window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix timestamp when the rate limit window resets |
| `Retry-After` | Seconds until rate limit resets (only on 429 responses) |

**Example Response Headers:**
```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 542
X-RateLimit-Reset: 1733097600
```

**Public Endpoints (Unauthenticated):**

| Endpoint | Limit |
|----------|-------|
| `/api/v1/verify` | 1,000 requests/hour per IP |
| `/api/v1/public/verify/batch` | 100 requests/hour per IP |

### Data Security

- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Compliance**: SOC 2 Type II, GDPR compliant
- **Audit Logs**: Complete audit trail for all operations
- **Data Retention**: Configurable per organization

---

## 📊 Performance

### Benchmarks

See [BENCHMARK_BASELINE.md](BENCHMARK_BASELINE.md) for detailed analysis of the latest run (Nov 2025).

| Operation | Avg Latency | Throughput | Bottleneck |
|-----------|-------------|------------|------------|
| Sign (C2PA) | 3.61ms | ~277 req/s | CPU |
| Merkle Encode | 108ms | ~9 req/s | Database I/O |
| Key Validation (cached) | <1ms | N/A | Redis |
| Key Validation (uncached) | ~15ms | N/A | HTTP to Key Service |

### Scalability

- **Throughput**: 1,000+ requests/second
- **Availability**: 99.9% SLA (Enterprise tier)
- **Global CDN**: <50ms latency worldwide
- **Auto-scaling**: Handles traffic spikes automatically
- **Database Isolation**: Each service scales independently

---

## 🛠️ Error Handling

### Error Codes

#### Standard Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTH_MISSING_KEY` | API key not provided | 401 |
| `AUTH_INVALID_KEY` | Invalid API key | 401 |
| `AUTH_EXPIRED_KEY` | API key expired | 401 |
| `QUOTA_EXCEEDED` | Monthly quota exceeded | 429 |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429 |
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `SIGNING_ERROR` | Error during signing | 500 |
| `VERIFICATION_ERROR` | Error during verification | 500 |
| `NOT_FOUND` | Document not found | 404 |

#### Microservices Integration Errors

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `SERVICE_UNAVAILABLE` | Key Service or Coalition Service unavailable | 503 |
| `KEY_VALIDATION_FAILED` | Key Service validation error | 401 |
| `COALITION_INDEX_FAILED` | Failed to index content in coalition (non-blocking warning) | 200 |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "hint": "Optional suggestion for resolution"
  },
  "correlation_id": "req_abc123",
  "status_code": 400
}
```

---

## 🤝 Coalition Service Integration

The Enterprise API automatically indexes signed content with the Coalition Service for eligible users.

### Content Indexing Flow

When content is signed:
1. Enterprise API creates C2PA manifest and signs content
2. If user is a coalition member, content is indexed via Coalition Service
3. Coalition Service tracks content for licensing and revenue distribution

**Implementation**: See `app/utils/coalition_client.py`

**Service Endpoints Used**:
- `POST /api/v1/coalition/content` - Index signed content
- `GET /api/v1/coalition/status/{user_id}` - Check membership
- `GET /api/v1/coalition/stats/{user_id}` - Get member statistics

**Coalition Features**:
- ✅ Automatic content indexing for coalition members
- ✅ Revenue sharing (70-85% members / 15-30% platform, based on tier)
- ✅ Bulk licensing to AI companies
- ✅ Access tracking and analytics

**Service Location**: `services/coalition-service` (Port 8009)

**Documentation**: See `services/coalition-service/README.md`

---

## 🔧 Configuration

### Environment Variables

#### Microservices Integration

```bash
# Key Service (Required)
KEY_SERVICE_URL=http://localhost:8003

# Coalition Service (Optional)
COALITION_SERVICE_URL=http://localhost:8009

# Auth Service (Future)
AUTH_SERVICE_URL=http://localhost:8001
```

#### Database Configuration

```bash
# Enterprise API Content Database (Own Database)
DATABASE_URL=postgresql://user:pass@localhost:5432/encypher_content

# Legacy Configuration Support
# CORE_DATABASE_URL and CONTENT_DATABASE_URL are no longer used
# Each microservice maintains its own database
```

#### Redis Configuration

```bash
# Redis for caching and session management
REDIS_URL=redis://localhost:6379/0
```

#### SSL.com Configuration

```bash
# SSL.com API (Optional for staging/development)
SSL_COM_API_KEY=your_api_key
SSL_COM_ACCOUNT_KEY=your_account_key
SSL_COM_API_URL=https://api.ssl.com/v1
SSL_COM_PRODUCT_ID=your_product_id
```

#### Security Configuration

```bash
# Encryption keys (for private key storage)
KEY_ENCRYPTION_KEY=<hex_string>
ENCRYPTION_NONCE=<hex_string>
```

#### CORS Configuration

```bash
# Comma-separated list of allowed origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://dashboard.encypherai.com
```

---

## 📖 SDK Support

### Official SDKs

- **Python**: [encypher-enterprise](https://pypi.org/project/encypher-enterprise/)
- **JavaScript/TypeScript**: Coming soon
- **Go**: Coming soon
- **Ruby**: Coming soon

### Community SDKs

- **PHP**: [encypher-php](https://github.com/community/encypher-php)
- **.NET**: [Encypher.NET](https://github.com/community/encypher-dotnet)

---

## 🧪 Testing

### Test Environment
Base URL: `https://api-staging.encypherai.com/api/v1`

Test API keys available in dashboard (no charges applied).

### Example Test Request
```bash
curl -X POST https://api-staging.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer encypher_test_..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test content",
    "title": "Test"
  }'
```

### Local Development Setup

1. **Start Required Services:**
```bash
# From services directory
cd services
docker-compose -f docker-compose.dev.yml up -d postgres-keys redis

# Start Key Service
cd key-service
uv run python -m app.main
```

2. **Start Enterprise API:**
```bash
cd enterprise_api
cp .env.example .env
# Edit .env with your configuration
uv run python -m app.main
```

3. **Optional: Start Coalition Service:**
```bash
cd services/coalition-service
uv run python -m app.main
```

### Benchmarking & Load Testing
For detailed instructions on running local benchmarks and load tests, please refer to the [Scripts Documentation](scripts/README.md).

---

## 📚 Documentation

- **API Docs**: [docs.encypherai.com/api](https://docs.encypherai.com/api)
- **SDK Docs**: [docs.encypherai.com/sdk](https://docs.encypherai.com/sdk)
- **Microservices Overview**: [services/README.md](../services/README.md)
- **Key Service**: [services/key-service/README.md](../services/key-service/README.md)
- **Coalition Service**: [services/coalition-service/README.md](../services/coalition-service/README.md)
- **C2PA Custom Assertions API**: [docs/api/C2PA_CUSTOM_ASSERTIONS_API.md](../docs/api/C2PA_CUSTOM_ASSERTIONS_API.md)
- **C2PA Provenance Chain**: [docs/c2pa/C2PA_PROVENANCE_CHAIN.md](../docs/c2pa/C2PA_PROVENANCE_CHAIN.md)
- **C2PA Implementation**: [docs/c2pa/C2PA Implimentation Guidance.md](../docs/c2pa/C2PA%20Implimentation%20Guidance.md)
- **C2PA Spec**: [docs/c2pa/Manifests_Text.adoc](../docs/c2pa/Manifests_Text.adoc)
- **Architecture**: [docs/architecture/BACKEND_ARCHITECTURE.md](../docs/architecture/BACKEND_ARCHITECTURE.md)

---

## 🤝 Support

- **Email**: api@encypherai.com
- **Status Page**: [status.encypherai.com](https://status.encypherai.com)
- **Dashboard**: [dashboard.encypherai.com](https://dashboard.encypherai.com)
- **Community**: [community.encypherai.com](https://community.encypherai.com)

### SLA (Enterprise Tier)

- **Uptime**: 99.9% guaranteed
- **Response Time**: <100ms P95
- **Support**: 24/7 dedicated support
- **Incident Response**: <15 minutes

---

## 📄 License

Proprietary - See [LICENSE](../LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Caching and session management
- [Railway](https://railway.app/) - Hosting platform
- [C2PA](https://c2pa.org/) - Content authenticity standards
- [SSL.com](https://www.ssl.com/) - Certificate authority

---

<div align="center">

**Made with ❤️ by Encypher**

[Website](https://encypherai.com) • [Dashboard](https://dashboard.encypherai.com) • [Docs](https://docs.encypherai.com) • [Status](https://status.encypherai.com)

</div>
