# Encypher Enterprise API

<div align="center">

![Encypher Logo](https://encypherai.com/logo.svg)

**Production-ready API for C2PA-compliant content signing and verification**

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://api.encypherai.com)
[![API Version](https://img.shields.io/badge/version-v1-blue)](https://docs.encypherai.com)
[![Uptime](https://img.shields.io/badge/uptime-99.9%25-brightgreen)](https://status.encypherai.com)
[![License](https://img.shields.io/badge/license-proprietary-red)](../LICENSE)

[Features](#-features) •
[Quick Start](#-quick-start) •
[API Reference](#-api-reference) •
[Enterprise Features](#-enterprise-features) •
[Documentation](#-documentation)

</div>

---

## 🎯 Overview

The Encypher Enterprise API provides cryptographic content signing and verification infrastructure for publishers, news organizations, legal firms, and content platforms. Built on **C2PA 2.2 standards** with enterprise-grade features for sentence-level tracking and source attribution.

### Why Encypher API?

- **🔒 C2PA 2.2 Compliant**: Industry-standard content authenticity
- **⚡ High Performance**: <100ms verification, 1000+ req/s capacity
- **🌍 Global CDN**: Low-latency endpoints worldwide
- **📊 Enterprise Features**: Merkle trees, source attribution, plagiarism detection
- **🔐 SSL.com Integration**: Automated certificate lifecycle management
- **⚖️ Court-Admissible**: Tamper-evident manifests for legal evidence

---

## ✨ Features

### Core API Endpoints

| Endpoint | Description | Tier |
|----------|-------------|------|
| `POST /api/v1/sign` | Sign content with C2PA manifest | All |
| `POST /api/v1/verify` | Verify signed content | All |
| `POST /api/v1/lookup` | Lookup sentence provenance | All |
| `GET /stats` | Usage statistics | All |

### Enterprise Endpoints

| Endpoint | Description | Tier |
|----------|-------------|------|
| `POST /api/v1/enterprise/merkle/encode` | Encode document into Merkle tree | Enterprise |
| `POST /api/v1/enterprise/merkle/attribute` | Find source documents | Enterprise |
| `POST /api/v1/enterprise/merkle/detect-plagiarism` | Detect plagiarism | Enterprise |
| `POST /api/v1/enterprise/embeddings/encode-with-embeddings` | Create portable signed embeddings with C2PA provenance chain | Professional+ |
| `GET /api/v1/public/verify/{ref_id}` | Verify embedding (public, no auth) | Public |
| `POST /api/v1/public/verify/batch` | Batch verify embeddings (public) | Public |
| `POST /api/v1/public/extract-and-verify` | Extract and verify C2PA manifest with full provenance chain | Public |

### Streaming Endpoints (NEW)

| Endpoint | Description | Tier |
|----------|-------------|------|
| `WS /api/v1/stream/sign` | Real-time WebSocket signing | Professional+ |
| `WS /api/v1/stream/chat` | Chat application wrapper | Professional+ |
| `GET /api/v1/stream/events` | Server-Sent Events (SSE) | Professional+ |
| `POST /api/v1/stream/session/create` | Create streaming session | Professional+ |
| `POST /api/v1/stream/session/{id}/close` | Close streaming session | Professional+ |

### Features by Tier

#### Basic Tier
- ✅ C2PA-compliant signing
- ✅ Content verification
- ✅ Public verification pages
- ✅ 1,000 requests/month

#### Professional Tier
- ✅ All Basic features
- ✅ Sentence-level lookup
- ✅ Invisible signed embeddings (Unicode variation selectors)
- ✅ Custom metadata
- ✅ 10,000 requests/month
- ✅ Priority support

#### Enterprise Tier
- ✅ All Professional features
- ✅ Merkle tree encoding
- ✅ **C2PA Provenance Chain**: Full edit history with ingredient references
- ✅ Public embedding extraction & verification API (no auth required)
- ✅ Partner integration tools (extraction libraries, web scraping)
- ✅ Source attribution
- ✅ Plagiarism detection
- ✅ Unlimited requests
- ✅ SLA guarantee (99.9%)
- ✅ Dedicated support

---

## 🚀 Quick Start

### Authentication

All API requests require an API key in the `Authorization` header:

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

### POST /api/v1/sign

Sign content with C2PA-compliant manifest.

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

**Error Response:**

```json
{
  "success": false,
  "error": "Invalid API key",
  "error_code": "AUTH_INVALID_KEY",
  "status_code": 401
}
```

---

### POST /api/v1/verify

Verify signed content and detect tampering.

**Request:**

```json
{
  "signed_text": "Your content here\u{FEFF}C2PATXT..."
}
```

**Response:**

```json
{
  "success": true,
  "is_valid": true,
  "tampered": false,
  "document_id": "doc_abc123xyz",
  "organization_name": "Acme News",
  "document_title": "Article Title",
  "publication_date": "2025-10-29T18:00:00Z",
  "verification_details": {
    "signature_valid": true,
    "manifest_valid": true,
    "hash_match": true,
    "wrapper_valid": true
  },
  "metadata": {
    "author": "Jane Doe",
    "publisher": "Acme News",
    "license": "CC-BY-4.0"
  },
  "manifest": {
    "version": "2.2",
    "claim_generator": "Encypher Enterprise API v1.0"
  }
}
```

**Tampered Content Response:**

```json
{
  "success": true,
  "is_valid": false,
  "tampered": true,
  "document_id": "doc_abc123xyz",
  "verification_details": {
    "signature_valid": true,
    "manifest_valid": true,
    "hash_match": false,
    "wrapper_valid": true
  },
  "tampering_detected": {
    "reason": "Content hash mismatch",
    "expected_hash": "sha256:abc...",
    "actual_hash": "sha256:xyz..."
  }
}
```

---

### POST /api/v1/lookup

Lookup sentence provenance (Professional+ tier).

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

### GET /stats

Get usage statistics for your API key.

**Response:**

```json
{
  "success": true,
  "period": "current_month",
  "usage": {
    "sign_requests": 1234,
    "verify_requests": 5678,
    "lookup_requests": 234,
    "total_requests": 7146
  },
  "quota": {
    "tier": "professional",
    "monthly_limit": 10000,
    "remaining": 2854,
    "reset_date": "2025-11-01T00:00:00Z"
  },
  "performance": {
    "avg_sign_time_ms": 45,
    "avg_verify_time_ms": 23,
    "success_rate": 99.8
  }
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

### Minimal Signed Embeddings (Professional+)

Invisibly embed cryptographically signed references directly into content using Unicode variation selectors. The embeddings are completely invisible to readers but can be extracted and verified by third parties without requiring API keys.

**Endpoint:** `POST /api/v1/enterprise/embeddings/encode-with-embeddings`

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

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────┐
│ Client Applications                     │
│ (SDK, CLI, WordPress, Direct API)      │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ API Gateway (Railway)                   │
│ - Rate limiting                         │
│ - Authentication                        │
│ - Load balancing                        │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ FastAPI Application                     │
│ - /api/v1/sign                         │
│ - /api/v1/verify                       │
│ - /api/v1/lookup                       │
│ - /api/v1/enterprise/*                 │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ encypher-ai Core Library (v2.9.0)     │
│ - C2PA manifest generation             │
│ - Unicode metadata embedding           │
│ - Signature verification               │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ PostgreSQL Database                     │
│ - Document metadata                     │
│ - Merkle tree nodes                     │
│ - Usage statistics                      │
└─────────────────────────────────────────┘
```

### C2PA Compliance

Our implementation follows **C2PA 2.2 Text Manifest Specification**:

- **Wrapper Format**: `C2PATXT\0` header with Unicode variation selectors
- **Prefix**: Single zero-width no-break space (U+FEFF)
- **Hash Algorithm**: SHA-256 with NFC normalization
- **Assertions**: `c2pa.hash.data`, `c2pa.claim.generator`, custom assertions
- **Validation**: Rejects malformed/duplicate wrappers per spec

**Reference:** [docs/c2pa/Manifests_Text.adoc](../docs/c2pa/Manifests_Text.adoc)

---

## 🔐 Security

### Authentication

- **API Keys**: Bearer token authentication
- **Key Rotation**: Automatic rotation every 90 days
- **Scoped Keys**: Limit keys to specific endpoints/operations

### Rate Limiting

| Tier | Requests/Second | Requests/Month |
|------|----------------|----------------|
| Basic | 10 | 1,000 |
| Professional | 50 | 10,000 |
| Enterprise | Unlimited | Unlimited |

### Data Security

- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Compliance**: SOC 2 Type II, GDPR compliant
- **Audit Logs**: Complete audit trail for all operations
- **Data Retention**: Configurable per organization

---

## 📊 Performance

### Benchmarks

| Operation | Avg Latency | P95 Latency | P99 Latency |
|-----------|-------------|-------------|-------------|
| Sign (1KB) | 45ms | 78ms | 120ms |
| Sign (10KB) | 67ms | 105ms | 150ms |
| Verify | 23ms | 45ms | 67ms |
| Lookup | 34ms | 56ms | 89ms |
| Merkle Encode | 123ms | 200ms | 300ms |

### Scalability

- **Throughput**: 1,000+ requests/second
- **Availability**: 99.9% SLA (Enterprise tier)
- **Global CDN**: <50ms latency worldwide
- **Auto-scaling**: Handles traffic spikes automatically

---

## 🛠️ Error Handling

### Error Codes

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

### Error Response Format

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "status_code": 400,
  "details": {
    "field": "Additional context"
  },
  "request_id": "req_abc123"
}
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

---

## 📚 Documentation

- **API Docs**: [docs.encypherai.com/api](https://docs.encypherai.com/api)
- **SDK Docs**: [docs.encypherai.com/sdk](https://docs.encypherai.com/sdk)
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
- [Railway](https://railway.app/) - Hosting platform
- [C2PA](https://c2pa.org/) - Content authenticity standards
- [SSL.com](https://www.ssl.com/) - Certificate authority

---

<div align="center">

**Made with ❤️ by Encypher**

[Website](https://encypherai.com) • [Dashboard](https://dashboard.encypherai.com) • [Docs](https://docs.encypherai.com) • [Status](https://status.encypherai.com)

</div>
