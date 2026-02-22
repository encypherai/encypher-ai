# Encypher Enterprise API

<div align="center">

![Encypher Logo](https://encypherai.com/encypher_full_logo_color.svg)

**Production-ready API for C2PA-compliant content signing and verification**

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://api.encypherai.com)
[![API Version](https://img.shields.io/badge/version-v1-blue)](https://docs.encypherai.com)
[![Uptime](https://img.shields.io/badge/uptime-99.9%25-brightgreen)](https://verify.encypherai.com/status)
[![License](https://img.shields.io/badge/license-proprietary-red)](../LICENSE)

[Features](#-features) •
[Quick Start](#-quick-start) •
[API Reference](#-api-reference) •
[Architecture](#-architecture) •
[Documentation](#-documentation)

</div>

---

## 🎯 Overview

The Encypher Enterprise API provides cryptographic content signing and verification infrastructure for publishers, news organizations, legal firms, and content platforms. Built on C2PA standards with enterprise-grade features for granular content attribution and court-admissible evidence generation.

**Part of the Encypher Microservices Ecosystem** - This API integrates with multiple backend microservices for authentication, key management, and coalition features.

### Why Encypher API?

- **🔒 C2PA 2.3 Compliant**: Industry-standard content authenticity
- **⚡ High Performance**: <100ms verification, 1000+ req/s capacity
- **🔗 Microservices Architecture**: Scalable, resilient, database-per-service design
- **📊 Advanced Features**: Merkle tree authentication, evidence generation, granular attribution
- **🔐 SSL.com Integration**: Automated certificate lifecycle management
- **⚖️ Court-Admissible**: Tamper-evident manifests for legal evidence

---

## ✨ Features

### Complete Feature List

#### Core Capabilities
- ✅ **C2PA-Compliant Signing**: Full C2PA 2.3 text manifest support
- ✅ **Content Verification**: Cryptographic verification with tamper detection
- ✅ **Granular Attribution**: Track provenance of individual sentences
- ✅ **Public Verification Pages**: Shareable verification URLs
- ✅ **Batch Operations**: Sign/verify up to 100 documents at once
- ✅ **Streaming Support**: WebSocket and SSE for real-time operations
- ✅ **Custom Metadata**: Attach arbitrary metadata to signed content
- ✅ **API Key Management**: Via integrated Key Service

#### Enterprise Features
- ✅ **Merkle Tree Encoding**: Hierarchical content fingerprinting with court-admissible evidence generation
- ✅ **Source Attribution**: Find original sources of quoted content
- ✅ **Plagiarism Detection**: Detect unauthorized content reuse
- ✅ **Fuzzy Fingerprinting**: Locality-sensitive fingerprints for paraphrased attribution (index on encode, search on verify)
- ✅ **Invisible Embeddings**: Unicode-based portable content tracking
- ✅ **Custom C2PA Assertions**: Define custom assertion types
- ✅ **Assertion Templates**: Pre-built templates for various industries
- ✅ **Schema Registry**: Manage custom JSON schemas
- ✅ **C2PA Provenance Chain**: Full edit history tracking
- ✅ **Public Extraction API**: Third-party embedding verification
- ✅ **Per-Document Revocation**: StatusList2021 assertions embedded on sign

#### Coalition Features (via Coalition Service)
- ✅ **Auto-Enrollment**: Automatic coalition membership for free tier
- ✅ **Content Indexing**: Aggregate content for bulk licensing
- ✅ **Revenue Sharing**: Two-track model (coalition 60/40, self-service 80/20)
- ✅ **Access Tracking**: Monitor where signed content appears across the web; ingestion-level tracking available when AI companies integrate provenance checking

#### Team & Administration
- ✅ **Team Management**: Multi-user organizations
- ✅ **Audit Logs**: Complete activity tracking
- ✅ **Usage Analytics**: Detailed usage metrics
- ✅ **Tier-Based Access**: Feature gating by subscription tier (Free + Enterprise)
- ✅ **Bring Your Own Keys (BYOK)**: Use your own signing keys (Enterprise)
- ✅ **SSO Integration**: Single Sign-On (Enterprise)

---

## Tier Feature Matrix

> **Pricing model:** Freemium + Enterprise. Legacy tier names (starter, professional, business) map to Free.

### Signing Features (`/api/v1/sign`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| C2PA signing (document-level) | ✅ | ✅ |
| Sentence/paragraph/section segmentation | ✅ | ✅ |
| Merkle tree encoding | ✅ | ✅ |
| Invisible Unicode embeddings | ✅ | ✅ |
| Streaming signing (SSE/WebSocket) | ✅ | ✅ |
| Custom metadata & assertions | ✅ | ✅ |
| Advanced manifest modes | ✅ | ✅ |
| Word segmentation | ❌ | ✅ |
| Robust fingerprinting | ❌ | ✅ |
| Print Leak Detection (`enable_print_fingerprint`) | ❌ | ✅ |
| **Batch size limit** | 10 | 100 |
| **Monthly signing quota** | 1,000 | Unlimited |

### Verification Features (`/api/v1/verify`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Basic verification & tamper detection | ✅ | ✅ |
| C2PA details | ✅ | ✅ |
| Document info | ✅ | ✅ |
| Licensing info | ✅ | ✅ |
| Merkle proof | ✅ | ✅ |
| Attribution lookup (`include_attribution`) | ✅ | ✅ |
| Plagiarism detection (`detect_plagiarism`) | ✅ | ✅ |
| Cross-org search (`search_scope=all`) | ❌ | ✅ |
| Fuzzy matching (`fuzzy_search`) | ❌ | ✅ |

### Account Features

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| API keys (up to 2) | ✅ | ✅ (unlimited) |
| Usage analytics | ✅ | ✅ |
| Audit logs | ✅ | ✅ |
| Coalition membership | ✅ | ✅ |
| BYOK (own keys) | ❌ | ✅ |
| Team management | ❌ | ✅ (unlimited members) |
| Webhooks | ❌ | ✅ |
| SSO/SAML | ❌ | ✅ |
| Document revocation | ❌ | ✅ |

---

## Complete API Endpoint Reference

### Core Endpoints

| Endpoint | Method | Auth | Tier | Description | Dependencies |
|----------|--------|------|------|-------------|--------------|
| `/api/v1/sign` | POST | ✅ | All (features gated) | Sign content with C2PA manifest - features gated by tier | Key Service, Coalition Service (optional) |
| `/api/v1/sign/advanced` | POST | - | - | ⚠️ **REMOVED** - Returns 410 Gone, use `/sign` with options | - |
| `/api/v1/verify` | POST | ✅ | All (features gated) | Verify signed content with optional attribution, plagiarism, and fuzzy search flags - features gated by tier | Key Service |
| `/api/v1/lookup` | POST | ❌ | Public | Lookup sentence provenance | None |
| `/api/v1/provenance/lookup` | POST | ❌ | Public | Lookup provenance for a document (structured) | None |
| `/api/v1/account` | GET | ✅ | All | Get account profile | Auth Service |
| `/api/v1/account/quota` | GET | ✅ | All | Get account quota and limits | Billing Service |
| `/api/v1/usage` | GET | ✅ | All | Get organization usage statistics | Key Service |
| `/api/v1/usage/history` | GET | ✅ | All | Get historical usage summaries | Analytics Service |

> **Design note:** Both `/sign` and `/verify` follow the same pattern — a single endpoint with optional feature flags (`include_attribution`, `detect_plagiarism`, `fuzzy_search`, `search_scope`) that are gated by tier or add-ons. No separate "advanced" endpoints.

### Public C2PA Utilities

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/public/c2pa/validate-manifest` | POST | ❌ | Public | Validate manifest JSON structure + assertion schema payloads (non-cryptographic). Optional API key supported for higher limits |
| `/api/v1/public/c2pa/create-manifest` | POST | ❌ | Public | Create a manifest JSON payload from plaintext (non-cryptographic) and return a signing helper payload. Optional API key supported for higher limits |
| `/api/v1/public/c2pa/trust-anchors/{signer_id}` | GET | ❌ | Public | Lookup trust anchor (public key) for external C2PA validators (public, IP rate-limited) |
| `/api/v1/public/c2pa/zw/resolve/{segment_uuid}` | GET | ❌ | Public | Resolve a ZW-embedded segment UUID to its source document and provenance metadata |
| `/api/v1/public/c2pa/zw/resolve` | POST | ❌ | Public | Bulk resolve multiple ZW segment UUIDs in a single call |

### Verification Service Endpoints

The following endpoints are provided by the verification microservice (merged into the public API spec):

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/verify/health` | GET | ❌ | Public | Verification service health check |
| `/api/v1/verify/stats` | GET | ✅ | All | Get verification statistics |
| `/api/v1/verify/{document_id}` | GET | ✅ | All | Get verification history for a document |
| `/api/v1/verify/history/{document_id}` | GET | ✅ | All | Get full verification history for a document |
| `/api/v1/verify/document` | POST | ✅ | All | Verify document authenticity |
| `/api/v1/verify/signature` | POST | ✅ | All | Verify a C2PA signature |
| `/api/v1/verify/advanced` | POST | ✅ | All | Advanced verification with attribution and plagiarism detection |
| `/api/v1/verify/quote-integrity` | POST | ❌ | Public | Verify AI attribution accuracy — check if a cited quote matches signed source documents (accurate/approximate/hallucinated/unverifiable) |

### Enterprise Merkle Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/merkle/encode` | POST | ✅ | All | Encode document into Merkle tree |

Deprecated Merkle attribution/plagiarism endpoints return HTTP 410 and redirect to `/api/v1/verify`.

### Streaming Merkle Endpoints (NEW - Patent FIG. 5)

Real-time Merkle tree construction for streaming content signing (e.g., LLM output).

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/stream/merkle/start` | POST | ✅ | All | Start streaming Merkle session |
| `/api/v1/enterprise/stream/merkle/segment` | POST | ✅ | All | Add segment to session |
| `/api/v1/enterprise/stream/merkle/finalize` | POST | ✅ | All | Finalize session and compute root |
| `/api/v1/enterprise/stream/merkle/status` | POST | ✅ | All | Check session status |

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
| `/api/v1/enterprise/attribution/multi-source` | POST | ✅ | All (authority ranking: Enterprise) | Multi-source hash lookup with authority ranking |

### Public Verification Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/public/verify/{ref_id}` | GET | ❌ | Public | Verify embedding by reference ID (optional API key for higher limits) |
| `/api/v1/public/verify/batch` | POST | ❌ | Public | Batch verify embeddings (optional API key for higher limits) |
| `/api/v1/public/extract-and-verify` | POST | - | - | ⚠️ **DEPRECATED** - Returns 410 Gone, use `POST /api/v1/verify` via verification-service |

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
| `/api/v1/batch/sign` | POST | ✅ | Enterprise | Batch sign up to 100 documents |
| `/api/v1/batch/verify` | POST | ✅ | Enterprise | Batch verify signed content |

### Streaming Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/sign/stream` | POST/WS | ✅ | All | Real-time signing via SSE (POST) and WebSocket (WS) |
| `/api/v1/sign/stream/sessions` | POST | ✅ | All | Create streaming session |
| `/api/v1/sign/stream/sessions/{session_id}/events` | GET | ✅ | All | Server-Sent Events (SSE) heartbeat and events |
| `/api/v1/sign/stream/sessions/{session_id}/close` | POST | ✅ | All | Close streaming session |
| `/api/v1/sign/stream/runs/{run_id}` | GET | ✅ | All | Get streaming run state |
| `/api/v1/sign/stream/stats` | GET | ✅ | All | Get organization streaming statistics |
| `/api/v1/chat/completions` | POST | ✅ | All | OpenAI-compatible SSE chat completions with signing |
| `/api/v1/chat/health` | GET | ❌ | Public | Chat streaming health check |

### Account, Keys, BYOK, Documents, and Webhooks

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/keys` | GET | ✅ | All | List API keys |
| `/api/v1/keys` | POST | ✅ | All | Create API key |
| `/api/v1/keys/{key_id}` | PATCH | ✅ | All | Update API key (name/metadata) |
| `/api/v1/keys/{key_id}` | DELETE | ✅ | All | Delete API key |
| `/api/v1/keys/{key_id}/rotate` | POST | ✅ | All | Rotate API key |
| `/api/v1/byok/public-keys` | GET | ✅ | Enterprise | List BYOK public keys |
| `/api/v1/byok/public-keys` | POST | ✅ | Enterprise | Register BYOK public key |
| `/api/v1/byok/public-keys/{key_id}` | DELETE | ✅ | Enterprise | Delete BYOK public key |
| `/api/v1/byok/trusted-cas` | GET | ❌ | Public | List C2PA trusted Certificate Authorities |
| `/api/v1/byok/certificates` | POST | ✅ | Enterprise | Upload CA-signed certificate (validated against C2PA trust list) |
| `/api/v1/documents` | GET | ✅ | Enterprise | List signed documents |
| `/api/v1/documents/{document_id}` | GET | ✅ | Enterprise | Get signed document |
| `/api/v1/documents/{document_id}/history` | GET | ✅ | Enterprise | Get document provenance history |
| `/api/v1/documents/{document_id}` | DELETE | ✅ | Enterprise | Soft-delete a document |
| `/api/v1/webhooks` | GET | ✅ | Enterprise | List webhooks |
| `/api/v1/webhooks` | POST | ✅ | Enterprise | Create webhook |
| `/api/v1/webhooks/{webhook_id}` | GET | ✅ | Enterprise | Get webhook |
| `/api/v1/webhooks/{webhook_id}` | PATCH | ✅ | Enterprise | Update webhook |
| `/api/v1/webhooks/{webhook_id}` | DELETE | ✅ | Enterprise | Delete webhook |
| `/api/v1/webhooks/{webhook_id}/deliveries` | GET | ✅ | Enterprise | List webhook deliveries |
| `/api/v1/webhooks/{webhook_id}/test` | POST | ✅ | Enterprise | Send a test delivery |

#### Supported Webhook Events

| Event | Description |
|-------|-------------|
| `document.signed` | Document was successfully signed |
| `document.verified` | Document was verified (any result) |
| `document.revoked` | Document revocation recorded |
| `document.reinstated` | Document revocation lifted |
| `quota.warning` | Quota usage crossed 80% threshold |
| `quota.exceeded` | Quota limit reached |
| `key.created` | API key created |
| `key.revoked` | API key revoked |
| `key.rotated` | API key rotated |
| `rights.profile.updated` | Publisher rights profile created or updated |
| `rights.notice.delivered` | Formal notice delivery confirmed |
| `rights.licensing.request_received` | Inbound licensing request from an AI company |
| `rights.licensing.agreement_created` | Licensing agreement created (request approved) |
| `rights.detection.event` | Crawler or AI system detected accessing signed content |

### Ghost CMS Integration Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/integrations/ghost` | POST | ✅ | All | Create or update Ghost integration configuration and return webhook URL/token on first create |
| `/api/v1/integrations/ghost` | GET | ✅ | All | Get current Ghost integration configuration with masked API key and configured webhook URL |
| `/api/v1/integrations/ghost` | DELETE | ✅ | All | Deactivate Ghost integration for the current organization |
| `/api/v1/integrations/ghost/regenerate-token` | POST | ✅ | All | Rotate webhook token and return a new ready-to-paste webhook URL |
| `/api/v1/integrations/ghost/webhook` | POST | ❌ | Public (token-scoped) | Receive Ghost publish/update webhook events using scoped `ghwh_...` query token |
| `/api/v1/integrations/ghost/sign/{post_id}` | POST | ✅ | All | Manually trigger signing for a Ghost post or page |

#### BYOK Trust Policy Metadata (`GET /api/v1/byok/trusted-cas`)

In addition to trusted CA subjects, this endpoint returns active trust-policy metadata:

- `required_signer_eku_oids`: required signer EKU OIDs enforced during certificate upload validation.
- `revocation_denylist`: internal denylist counters (`serial_count`, `fingerprint_count`).
- `tsa_trust_list`: TSA trust-list URL/fingerprint/load metadata used for timestamp trust handling.

`POST /api/v1/byok/certificates` enforces certificate chaining, signer EKU policy, and internal revocation denylist checks.

### Coalition Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/coalition/dashboard` | GET | ✅ | All | Get coalition dashboard (content, earnings, payouts) |
| `/api/v1/coalition/content-stats` | GET | ✅ | All | Get historical content corpus statistics |
| `/api/v1/coalition/earnings` | GET | ✅ | All | Get detailed earnings history |
| `/api/v1/coalition/opt-out` | POST | ✅ | All | Opt out of coalition revenue sharing |
| `/api/v1/coalition/opt-in` | POST | ✅ | All | Opt in to coalition revenue sharing |

### Team Management Endpoints

> **Note:** Team management endpoints are tagged internal in the public API spec but are accessible to Enterprise users.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/org/members` | GET | ✅ | Internal | List team members |
| `/api/v1/org/members/invite` | POST | ✅ | Internal | Invite a team member |
| `/api/v1/org/members/invites` | GET | ✅ | Internal | List pending invitations |
| `/api/v1/org/members/invites/{invite_id}` | DELETE | ✅ | Internal | Revoke an invitation |
| `/api/v1/org/members/{member_id}/role` | PATCH | ✅ | Internal | Update member role |
| `/api/v1/org/members/{member_id}` | DELETE | ✅ | Internal | Remove a team member |
| `/api/v1/org/members/accept-invite` | POST | ✅ | Internal | Accept an invitation |
| `/api/v1/org/invites/public/{token}` | GET | None | Public | Look up invite metadata by token |
| `/api/v1/org/invites/public/{token}/accept-new` | POST | None | Public | Register new user and accept invite |

### Audit Log Endpoints

> **Note:** Audit log endpoints are tagged internal in the public API spec but are accessible to all authenticated users.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/audit-logs` | GET | ✅ | Internal | Get paginated audit logs |
| `/api/v1/audit-logs/export` | GET | ✅ | Internal | Export audit logs (JSON or CSV) |

### Provisioning Endpoints (Internal)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/provisioning/auto-provision` | POST | Token | Internal | Auto-provision organization and API key |
| `/api/v1/provisioning/api-keys` | POST | Token | Internal | Create API key for an organization |
| `/api/v1/provisioning/api-keys` | GET | Token | Internal | List API keys for an organization |
| `/api/v1/provisioning/api-keys/{key_id}` | DELETE | Token | Internal | Revoke an API key |
| `/api/v1/provisioning/users` | POST | Token | Internal | Create a user account |
| `/api/v1/provisioning/health` | GET | ❌ | Internal | Provisioning service health check |

### Document Revocation Endpoints (NEW)

| Endpoint | Description | Tier |
|----------|-------------|------|
| `POST /api/v1/status/documents/{document_id}/revoke` | Revoke a document's authenticity | Enterprise |
| `POST /api/v1/status/documents/{document_id}/reinstate` | Reinstate a revoked document | Enterprise |
| `GET /api/v1/status/documents/{document_id}` | Get document revocation status | Enterprise |
| `GET /api/v1/status/lists/{list_id}` | Get status list credential (public, CDN-cacheable) | Public |
| `GET /api/v1/status/stats` | Get revocation statistics | Enterprise |

Signing endpoints embed an `org.encypher.status` C2PA assertion containing the
`statusListCredential` URL and `statusListIndex` bit position for revocation checks.

### Licensing Endpoints

Licensing endpoints are internal-only and intentionally excluded from the public OpenAPI schema.

For full details, see [docs/LICENSING_API.md](./docs/LICENSING_API.md).

### Rights Management Endpoints (NEW)

Machine-readable deed system for publishers to define and enforce licensing terms across AI use cases. Built on top of the existing enterprise_api; all data stored in the Core DB.

#### Publisher-Facing (Authenticated)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/rights/profile` | PUT | ✅ | Business+ | Create or update default rights profile (versioned) |
| `/api/v1/rights/profile` | GET | ✅ | Business+ | Get current rights profile |
| `/api/v1/rights/profile/history` | GET | ✅ | Business+ | Get full version history of rights profile |
| `/api/v1/rights/documents/{document_id}` | PUT | ✅ | Business+ | Override rights for a specific document |
| `/api/v1/rights/collections/{collection_id}` | PUT | ✅ | Business+ | Override rights for a collection |
| `/api/v1/rights/content-types/{content_type}` | PUT | ✅ | Business+ | Override rights for a content type |
| `/api/v1/rights/bulk-update` | POST | ✅ | Business+ | Bulk update rights across documents/collections/types |
| `/api/v1/rights/templates` | GET | ✅ | All | List available rights template presets |
| `/api/v1/rights/profile/from-template/{template_id}` | POST | ✅ | Business+ | Initialize profile from a template |
| `/api/v1/rights/profile/delegated-setup` | POST | ✅ | Strategic Partner | Platform partner sets up rights profile on behalf of publisher |
| `/api/v1/partner/publishers/provision` | POST | ✅ | Strategic Partner | Bulk-provision publisher orgs, rights profiles, and claim emails in one call |
| `/api/v1/rights/rsl/import` | POST | ✅ | Business+ | Import existing RSL 1.0 XML document |
| `/api/v1/rights/analytics/detections` | GET | ✅ | Business+ | Phone-home detection analytics |
| `/api/v1/rights/analytics/crawlers` | GET | ✅ | Business+ | AI crawler activity breakdown |
| `/api/v1/rights/analytics/crawlers/timeseries` | GET | ✅ | Business+ | Daily crawler activity timeseries |

Rights profiles support three licensing tiers:
- **Bronze** — Scraping / crawling terms
- **Silver** — RAG / retrieval / search terms
- **Gold** — Training / fine-tuning terms

#### Public Rights Resolution (Unauthenticated)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/public/rights/{document_id}` | GET | ❌ | Resolve rights for a specific signed document |
| `/api/v1/public/rights/resolve` | POST | ❌ | Resolve rights from raw signed text |
| `/api/v1/public/rights/organization/{org_id}` | GET | ❌ | Get organization's default rights profile |
| `/api/v1/public/rights/{document_id}/json-ld` | GET | ❌ | Machine-readable rights in JSON-LD (Schema.org) format |
| `/api/v1/public/rights/{document_id}/odrl` | GET | ❌ | Machine-readable rights in W3C ODRL format |
| `/api/v1/public/rights/organization/{org_id}/robots-meta` | GET | ❌ | AI-specific robots meta tag directives |
| `/api/v1/public/rights/organization/{org_id}/rsl` | GET | ❌ | Generate RSL 1.0 XML document |
| `/api/v1/public/rights/organization/{org_id}/robots-txt` | GET | ❌ | robots.txt additions with RSL/AI directives |
| `/api/v1/public/rights/rsl/olp/token` | POST | ❌ | RSL Open License Protocol — generate access token |
| `/api/v1/public/rights/rsl/olp/validate/{token}` | GET | ❌ | Validate RSL OLP token |

#### Formal Notices (Authenticated)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/notices/` | GET | ✅ | Business+ | List all formal notices for the organization |
| `/api/v1/notices/create` | POST | ✅ | Business+ | Create an immutable formal notice |
| `/api/v1/notices/{notice_id}` | GET | ✅ | Business+ | Retrieve a formal notice |
| `/api/v1/notices/{notice_id}/deliver` | POST | ✅ | Business+ | Deliver notice to an AI company |
| `/api/v1/notices/{notice_id}/evidence` | GET | ✅ | Business+ | Get cryptographic evidence package (court-ready) |

Notices are append-only with SHA-256 content hashing for tamper-evidence. Each evidence package includes a linked `notice_evidence_chain` for chain-of-custody documentation.

#### Rights Licensing Transactions (Authenticated)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/rights-licensing/request` | POST | ✅ | All | Submit a licensing request |
| `/api/v1/rights-licensing/requests` | GET | ✅ | All | List licensing requests |
| `/api/v1/rights-licensing/requests/{request_id}/respond` | PUT | ✅ | Business+ | Approve or reject a licensing request |
| `/api/v1/rights-licensing/agreements` | GET | ✅ | All | List active licensing agreements |
| `/api/v1/rights-licensing/agreements/{agreement_id}` | GET | ✅ | All | Get a specific licensing agreement |
| `/api/v1/rights-licensing/agreements/{agreement_id}/usage` | GET | ✅ | All | Get usage metrics for an agreement |

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
| `/metrics` | GET | ❌ | Internal | Prometheus-compatible metrics |
| `/` | GET | ❌ | Public | API information |

### Features by Tier

#### Free Tier ($0)
- ✅ C2PA 2.3-compliant document signing (1K/month)
- ✅ Sentence-level Merkle tree authentication
- ✅ Invisible Unicode embeddings
- ✅ Unlimited verifications and public API lookups
- ✅ Content verification with attribution and plagiarism detection
- ✅ Public verification pages
- ✅ Streaming support (WebSocket/SSE)
- ✅ Custom metadata and assertions
- ✅ Audit logs
- ✅ Coalition membership — auto-enrolled on first signed document
- ✅ WordPress plugin — auto-sign on publish
- ✅ REST API, CLI, GitHub Action
- ✅ Two-track licensing: Coalition deals (60% publisher / 40% Encypher) or Self-service deals (80% publisher / 20% Encypher)

#### Business+ Tier
- ✅ Everything in Free
- ✅ **Rights Management**: Bronze/Silver/Gold tier licensing profiles
- ✅ **Formal Notices**: Cryptographically-provable, court-ready notice infrastructure
- ✅ **Rights Resolution**: Public API for machine-readable deed discovery
- ✅ **RSL 1.0 Interoperability**: Import/export RSL XML; generate robots.txt directives
- ✅ **Licensing Transactions**: Request/respond/agreement lifecycle
- ✅ **AI Crawler Analytics**: Phone-home detection events and crawler activity

#### Enterprise Tier (Custom pricing)
- ✅ Everything in Business+ — unlimited (no caps on volume or API calls)
- ✅ **Cross-Org Search**: Verify content across all organizations (`search_scope=all`)
- ✅ **Fuzzy Matching**: Detect paraphrased/rewritten content via fuzzy fingerprinting
- ✅ **C2PA Provenance Chain**: Full edit history tracking
- ✅ **Assertion Templates**: Pre-built industry templates
- ✅ **Schema Registry**: Manage custom JSON schemas
- ✅ **Robust Fingerprinting**: Survives paraphrasing, rewriting, and translation
- ✅ **Evidence Generation**: Court-ready evidence packages
- ✅ **Authority Ranking**: Configurable source ranking
- ✅ Batch operations (up to 100 documents per request)
- ✅ Document revocation capability (StatusList2021)
- ✅ Unlimited team members with role-based access controls
- ✅ Webhooks for event notifications
- ✅ SSO integration (SAML, OAuth)
- ✅ Bring Your Own Keys (BYOK)
- ✅ Dedicated SLA (99.9%), 24/7 support, named account manager
- ✅ **Platform Partner Delegated Setup**: One-call publisher onboarding with rights profiles
- ✅ Two-track licensing: Coalition deals (60% publisher / 40% Encypher) or Self-service deals (80% publisher / 20% Encypher)

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

Free tier supports up to 1 custom assertion per request on this endpoint.

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
  "custom_assertions": [
    {
      "label": "org.encypher.user-provenance",
      "data": {
        "text": "User-supplied provenance text"
      }
    }
  ],
  "use_sentence_tracking": true,
  "options": {
    "use_rights_profile": true
  },
  "publisher_org_id": null
}
```

When `use_rights_profile: true`, the sign endpoint fetches the publisher's active rights profile, stores a snapshot on the content reference, and injects `rights_resolution_url` into the response for each document. This enables any downstream party (AI crawler, aggregator) to call the public rights endpoint directly from the signed content.

**Proxy Signing** (`publisher_org_id`): Platform partners with a `strategic_partner`-tier API key may set `publisher_org_id` to sign content on behalf of a provisioned publisher organization. The publisher's quota, rate limits, rights profile, and webhooks are used (publisher pays). The response includes `partner_org_id` and `publisher_org_id` fields to identify both parties. Requires the publisher org to exist (provisioned via `POST /api/v1/partner/publishers/provision`).

**Response:**

```json
{
  "success": true,
  "document_id": "doc_abc123xyz",
  "signed_text": "Your content here...",
  "verification_url": "https://encypherai.com/verify/doc_abc123xyz",
  "rights_resolution_url": "https://api.encypherai.com/api/v1/public/rights/doc_abc123xyz",
  "manifest": {
    "version": "2.2",
    "claim_generator": "Encypher Enterprise API v1.0",
    "assertions": [
      {
        "label": "c2pa.hash",
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

Verify signed content with optional attribution, plagiarism detection, and fuzzy search.

Features are gated by tier — free tier gets basic verification, attribution, and plagiarism detection; Enterprise unlocks cross-org search and fuzzy matching.

**Dependencies**: Key Service (required)

**Request:**

```json
{
  "text": "Your content here...",
  "include_attribution": false,
  "detect_plagiarism": false,
  "fuzzy_search": null,
  "search_scope": "organization"
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
          {"label": "c2pa.hash.v1", "kind": "ContentHash"}
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

Lookup sentence provenance.

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

Get usage statistics for your organization's current billing period.

**Dependencies**: Key Service (required)

**Response:**

```json
{
  "organization_id": "org_123",
  "tier": "free",
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

Optionally enable fuzzy fingerprint indexing (SimHash) in the same request to
tag sentence/paragraph segments with locality-sensitive fingerprints. This
enables detection of paraphrasing, misquotes, and lightly edited reuse while
tying every match back to the original work with Merkle proofs.

**Endpoint:** `POST /api/v1/enterprise/merkle/encode`

**Request:**

```json
{
  "text": "Your document content here...",
  "document_id": "doc_abc123",
  "segmentation_levels": ["sentence", "paragraph"],
  "fuzzy_fingerprint": {
    "enabled": true,
    "levels": ["sentence", "paragraph"],
    "include_document_fingerprint": false
  }
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
  "fuzzy_index": {
    "indexed_segments": 50,
    "levels": {
      "sentence": 42,
      "paragraph": 8
    }
  },
  "encoding_time_ms": 123
}
```

**Verify with fuzzy search:** Use `POST /api/v1/verify` with
`fuzzy_search.enabled=true` to return paraphrase/misquote matches, similarity
scores, and optional Merkle proofs.

---

### Source Attribution (Deprecated Endpoint)

The legacy Merkle attribution endpoint now returns HTTP 410. Use the unified verification endpoint instead.

**Replacement Endpoint:** `POST /api/v1/verify` with `include_attribution=true`

**Deprecated Endpoint:** `POST /api/v1/enterprise/merkle/attribute`

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

### Plagiarism Detection (Deprecated Endpoint)

The legacy plagiarism endpoint now returns HTTP 410. Use the unified verification endpoint instead.

**Replacement Endpoint:** `POST /api/v1/verify` with `detect_plagiarism=true`

**Deprecated Endpoint:** `POST /api/v1/enterprise/merkle/detect-plagiarism`

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

### Invisible Signed Embeddings

Embed signed references directly into content so it can be extracted and verified later. With
`manifest_mode="minimal_uuid"`, each segment receives a UUID-only pointer while a full C2PA manifest
is appended at the document end by default (set `disable_c2pa=true` to skip the document-level manifest).

**Endpoint:** `POST /api/v1/sign` (with embedding options)

**Request:**

```json
{
  "document_id": "article_001",
  "text": "Full article text...",
  "segmentation_level": "sentence",
  "manifest_mode": "minimal_uuid",
  "c2pa_manifest_url": "https://...",
  "license": {
    "type": "All Rights Reserved",
    "contact_email": "licensing@example.com"
  }
}
```

**Manifest Modes:** `full`, `lightweight_uuid`, `minimal_uuid`, `hybrid`, `zw_embedding`, `vs256_embedding`, `vs256_rs_embedding`

> For a comprehensive comparison of all modes with platform compatibility, PDF behavior, and security details, see [docs/architecture/EMBEDDING_MODES.md](../docs/architecture/EMBEDDING_MODES.md).

**`zw_embedding` Mode**
- Uses zero-width Unicode characters (ZWNJ, ZWJ, CGJ, MVS) for invisible signatures
- 128 chars per sentence (no magic number, contiguous sequence detection)
- **Word-compatible**: Survives Microsoft Word copy-paste perfectly
- Detected by scanning for 128 contiguous base-4 characters
- No visible spaces or gaps in any text editor
- Ideal for portable content tracking across web, Word, PDF, etc.

**`vs256_embedding` Mode**
- Uses a 256-character invisible alphabet for base-256 encoding
- **36 chars per sentence** — 3.6x more compact than ZW mode
- Magic prefix detection (VS240–VS243) for reliable extraction
- Works in Google Docs, PDF, browsers — **NOT Microsoft Word** (shows □ glyphs)
- Best for maximum density when Word compatibility is not needed

**`vs256_rs_embedding` Mode**
- Extends VS256 with **Reed-Solomon error correction** (8 parity symbols)
- Same 36-char footprint as VS256 — trades HMAC length for parity bytes
- Corrects up to 4 unknown errors or 8 known erasures per signature
- **Recommended for PDF signing** — recovers from chars dropped by PDF text extractors
- Same detection as VS256 (magic prefix); verification auto-distinguishes RS vs non-RS

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

**How It Works:**

Signed references are embedded in a transport-safe form that is designed to survive common copy/paste and publishing workflows.

**Use Cases:**
- Invisible content tracking across the web
- Partner integration (web scrapers, content monitors)
- Portable proof of origin that travels with text
- Legal evidence embedded directly in content
- AI-generated content authentication

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
│ - Member Stats          │       │ - Org Provisioning      │
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
       "tier": "free",
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

Signed text is produced in a C2PA-compatible form and can be verified using `POST /api/v1/verify`.

**Reference:** [docs/c2pa/Manifests_Text.adoc](../docs/c2pa/Manifests_Text.adoc)

---

## 🔐 Security

### Unified Authentication Architecture

The Enterprise API uses the **Key Service** for all authentication:

1. **API Key Validation**: All API keys validated via Key Service `/api/v1/keys/validate` endpoint
2. **Caching**: Validation results cached in Redis (5-minute TTL) to reduce latency
3. **Organization Context**: Key Service returns complete organization context:
   - Tier (free, enterprise, strategic_partner)
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

| Tier | Requests/Second | Monthly Quota |
|------|-----------------|---------------|
| Free | 10 | 10,000 |
| Enterprise | Unlimited | Unlimited |
| Strategic Partner | Unlimited | Unlimited |

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

# Auth Service (Required for proxy signing and bulk provisioning)
AUTH_SERVICE_URL=http://localhost:8001

# Internal service token (shared secret for inter-service calls)
INTERNAL_SERVICE_TOKEN=<shared-secret>

# Notification Service (Required for partner claim emails)
NOTIFICATION_SERVICE_URL=http://localhost:8005

# Dashboard base URL (used in partner claim email links)
DASHBOARD_URL=https://dashboard.encypherai.com
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

# Trusted hosts for Host header validation
ALLOWED_HOSTS=api.encypherai.com

# Trusted proxy IPs (comma-separated) to honor forwarded headers
TRUSTED_PROXY_IPS=10.0.0.10,10.0.0.11

# Embedding signature secret (required in production for public verification)
EMBEDDING_SIGNATURE_SECRET=<hex_or_ascii_secret>
```

#### C2PA Trust List Configuration

```bash
# Optional override for the upstream trust list URL
C2PA_TRUST_LIST_URL=https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem

# Optional SHA-256 pin (hex) to prevent trust list tampering
C2PA_TRUST_LIST_SHA256=<sha256_hex>

# Refresh interval (hours) for reloading the trust list
C2PA_TRUST_LIST_REFRESH_HOURS=24

# Optional override for the TSA trust list URL
C2PA_TSA_TRUST_LIST_URL=https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem

# Optional SHA-256 pin (hex) for TSA trust list
C2PA_TSA_TRUST_LIST_SHA256=<sha256_hex>

# Refresh interval (hours) for TSA trust list
C2PA_TSA_TRUST_LIST_REFRESH_HOURS=24

# Required signer EKU OIDs (comma-separated)
C2PA_REQUIRED_SIGNER_EKU_OIDS=1.3.6.1.4.1.62558.2.1

# Internal revocation denylist (comma-separated hex values)
C2PA_REVOKED_CERTIFICATE_SERIALS=
C2PA_REVOKED_CERTIFICATE_FINGERPRINTS=

# Signing mode defaults
# organization: per-org key/cert path (legacy/default compatibility)
# managed: Encypher-managed signer identity for default signing
# byok: org-managed keys/certs
# managed_tenant_cert: Encypher-managed issuance for tenant-specific certs (reseller flow)
DEFAULT_SIGNING_MODE=organization

# Encypher managed signer material (used when DEFAULT_SIGNING_MODE=managed or org signing_mode=managed)
MANAGED_SIGNER_ID=encypher_managed
MANAGED_SIGNER_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----..."
MANAGED_SIGNER_CERTIFICATE_PEM="-----BEGIN CERTIFICATE-----..."
MANAGED_SIGNER_CERTIFICATE_CHAIN_PEM="-----BEGIN CERTIFICATE-----..."
```

#### Signing Modes (Managed + BYOK + Reseller)

The Enterprise API supports an SSOT signing-mode model:

- `managed`: Sign with Encypher-managed signer key/cert material.
- `organization`: Legacy org key/cert path.
- `byok`: Customer-managed key/certificate path.
- `managed_tenant_cert`: Encypher-managed tenant-specific certificate workflow.

`GET /api/v1/byok/trusted-cas` now returns signing metadata:

- `default_signing_mode`
- `managed_signer_id`

This keeps BYOK endpoints backward compatible while exposing effective runtime defaults.

#### C2PA Conformance and Trust-List Readiness

The controls above harden validator behavior and BYOK policy enforcement. They do **not** by themselves place Encypher on the C2PA Trust List.

- **Generator Product path (typical)**: complete C2PA Conformance Program requirements and obtain certificates from a C2PA trust-list CA.
- **Trust anchor/CA path**: requires CA-level policy/governance and C2PA program approval for CA inclusion.

Treat this repository's trust-policy implementation as technical readiness, not final program approval.

#### Optional Reseller Workflow (SSL.com Tenant Certificates)

For customers that require tenant-specific certificate identity, use an opt-in reseller workflow:

1. Keep base platform traffic on `managed` signer mode for cost control and fast onboarding.
2. Provision tenant certs with SSL.com via API for selected tenants only.
3. Upload tenant certificate chain through `POST /api/v1/byok/certificates`.
4. Set tenant/org signing policy to `managed_tenant_cert` (or `byok` where customer-owned key custody is required).
5. Continue enforcing C2PA trust list + EKU + denylist checks on all uploaded certs.

This model avoids mandatory per-tenant cert spend while supporting premium tenant identity requirements.

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

### Local E2E Tests (Sign/Verify)

1. **Start Enterprise API locally** (see Local Development Setup below).
2. **Configure local test credentials:**
   ```bash
   cd enterprise_api/tests/e2e_local
   cp .env.local.example .env.local
   # Edit API_KEY/BASE_URL if needed
   ```
3. **Run local E2E suite:**
   ```bash
   LOCAL_API_TESTS=true uv run pytest enterprise_api/tests/e2e_local -m e2e
   ```

### Publisher Identity Setup (Avoid "Personal Account" in Verification)

To show a non-personal publisher name in verify responses and extension identity labels:

1. **Use an organization-scoped API key when possible**
   - Keys tied to an organization return organization identity fields directly.
2. **Set your publishing identity in Dashboard**
   - Open `dashboard.encypherai.com` → Settings → Publisher identity.
   - Set a `display_name` (for example, your newsroom or brand name).
   - For enterprise/custom identity, set signing identity mode to `custom` and define a custom label.
3. **Confirm identity fields via API**
   - Call `GET /api/v1/account` with your API key.
   - Ensure `publisher_display_name` is populated with the intended organization label.
4. **For user-level super-admin keys**
   - Configure Key Service env var `SUPERADMIN_PUBLISHER_DISPLAY_NAME`.
   - This value is used for synthetic user org contexts to avoid fallback to `Personal Account`.
5. **Re-verify content**
   - Run `POST /api/v1/verify` and confirm identity fields (`signing_identity`, `publisher_display_name`, `organization_name`) reflect the configured publisher name.

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
- **Status Page**: [verify.encypherai.com/status](https://verify.encypherai.com/status)
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

[Website](https://encypherai.com) • [Dashboard](https://dashboard.encypherai.com) • [Docs](https://docs.encypherai.com) • [Status](https://verify.encypherai.com/status)

</div>
