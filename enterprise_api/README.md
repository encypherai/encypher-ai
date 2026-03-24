# Encypher Enterprise API

<div align="center">

![Encypher Logo](https://encypherai.com/encypher_full_logo_color.svg)

**Production-ready API for C2PA-compliant content signing and verification**

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://api.encypherai.com)
[![API Version](https://img.shields.io/badge/version-v2.0.0-blue)](https://docs.encypherai.com)
[![Uptime](https://img.shields.io/badge/uptime-99.9%25-brightgreen)](https://verify.encypherai.com/status)
[![License](https://img.shields.io/badge/license-proprietary-red)](../LICENSE)

[Features](#features) |
[Quick Start](#quick-start) |
[API Reference](#api-reference) |
[Architecture](#architecture) |
[Documentation](#documentation)

</div>

---

## Overview

The Encypher Enterprise API provides cryptographic content signing and verification infrastructure for publishers, news organizations, legal firms, and content platforms. Built on C2PA standards with enterprise-grade features for granular content attribution and court-admissible evidence generation.

**Part of the Encypher Microservices Ecosystem** - This API integrates with multiple backend microservices for authentication, key management, and coalition features.

### D2 Workflow Views

- [Enterprise API sign/verify flow](../docs/diagrams/workflows/enterprise-api-sign-verify.d2) --shows caller authentication, tier/rate-limit checks, router handoff, dependency calls, storage, and response generation.
- [Repo system context](../docs/diagrams/architecture/system-context.d2) --shows how the Enterprise API sits between client surfaces, microservices, and storage layers.

### Why Encypher API?

- **C2PA 2.3 Compliant**: Industry-standard content authenticity
- **High Performance**: <100ms verification, 1000+ req/s capacity
- **Microservices Architecture**: Scalable, resilient, database-per-service design
- **Advanced Features**: Merkle tree authentication, evidence generation, granular attribution
- **SSL.com Integration**: Automated certificate lifecycle management
- **Court-Admissible**: Tamper-evident manifests for legal evidence

---

## Features

### Complete Feature List

#### Core Capabilities
- **C2PA-Compliant Signing**: Full C2PA 2.3 text manifest support
- **Audio C2PA Signing**: WAV, MP3, M4A/AAC audio signing and verification
- **Video C2PA Signing**: MP4, MOV, M4V, AVI video signing and verification (multipart upload)
- **Live Video Stream Signing**: Per-segment C2PA signing with manifest chaining (C2PA 2.3 Section 19)
- **Content Verification**: Cryptographic verification with tamper detection
- **Granular Attribution**: Track provenance of individual sentences
- **Public Verification Pages**: Shareable verification URLs
- **Batch Operations**: Sign/verify up to 100 documents at once
- **Streaming Support**: WebSocket and SSE for real-time operations
- **Custom Metadata**: Attach arbitrary metadata to signed content
- **API Key Management**: Via integrated Key Service

#### Enterprise Features
- **Merkle Tree Encoding**: Hierarchical content fingerprinting with court-admissible evidence generation
- **Source Attribution**: Find original sources of quoted content
- **Plagiarism Detection**: Detect unauthorized content reuse
- **Fuzzy Fingerprinting**: Locality-sensitive fingerprints for paraphrased attribution (index on encode, search on verify)
- **Invisible Embeddings**: Unicode-based portable content tracking
- **Custom C2PA Assertions**: Define custom assertion types
- **Assertion Templates**: Pre-built templates for various industries
- **Schema Registry**: Manage custom JSON schemas
- **C2PA Provenance Chain**: Full edit history tracking
- **Public Extraction API**: Third-party embedding verification
- **Per-Document Revocation**: StatusList2021 assertions embedded on sign

#### Coalition Features (via Coalition Service)
- **Auto-Enrollment**: Automatic coalition membership for free tier
- **Content Indexing**: Aggregate content for bulk licensing
- **Revenue Sharing**: Two-track model (coalition 60/40, self-service 80/20)
- **Access Tracking**: Monitor where signed content appears across the web; ingestion-level tracking available when AI companies integrate provenance checking

#### Team & Administration
- **Team Management**: Multi-user organizations
- **Audit Logs**: Complete activity tracking
- **Usage Analytics**: Detailed usage metrics
- **Tier-Based Access**: Feature gating by subscription tier (Free + Enterprise)
- **Bring Your Own Keys (BYOK)**: Use your own signing keys (Enterprise)
- **SSO Integration**: Single Sign-On (Enterprise)

---

## Tier Feature Matrix

> **Pricing model:** Free (full signing + rights management) + Enforcement Add-ons (paid, analytics/notices/evidence) + Enterprise (unlimited + custom). Legacy tier names (starter, professional, business, business+) all map to Free.

### Signing Features (`/api/v1/sign`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| C2PA signing (document-level) | Yes | Yes |
| Sentence/paragraph/section segmentation | Yes | Yes |
| Merkle tree encoding | Yes | Yes |
| Invisible Unicode embeddings | Yes | Yes |
| Streaming signing (SSE/WebSocket) | Yes | Yes |
| Custom metadata & assertions | Yes | Yes |
| Advanced manifest modes | Yes | Yes |
| Word segmentation | No | Yes |
| Robust fingerprinting | No | Yes |
| Print Leak Detection (`enable_print_fingerprint`) | No | Yes |
| **Batch size limit** | 10 | 100 |
| **Monthly signing quota** | 1,000 | Unlimited |

### Audio Signing Features (`/api/v1/enterprise/audio`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Audio C2PA signing (WAV, MP3, M4A/AAC) | No | Yes |
| Audio C2PA verification | No | Yes |
| C2PA audio actions (created, dubbed, mixed, mastered, remixed) | No | Yes |
| Per-org signing credentials (SSL.com / BYOK) | No | Yes |

### Video Signing Features (`/api/v1/enterprise/video`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Video C2PA signing (MP4, MOV, M4V, AVI) | No | Yes |
| Video C2PA verification | No | Yes |
| Multipart upload (up to 500 MB) | No | Yes |
| Large file download endpoint (files > 50 MB) | No | Yes |
| Per-org signing credentials (SSL.com / BYOK) | No | Yes |

### Live Video Stream Signing (`/api/v1/enterprise/video/stream`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Per-segment C2PA manifest signing (C2PA 2.3 Section 19) | No | Yes |
| Manifest chaining (backwards-linked provenance) | No | Yes |
| Merkle root computation on finalize | No | Yes |
| Session-cached signing credentials | No | Yes |

### Verification Features (`/api/v1/verify`)

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| Basic verification & tamper detection | Yes | Yes |
| C2PA details | Yes | Yes |
| Document info | Yes | Yes |
| Licensing info | Yes | Yes |
| Merkle proof | Yes | Yes |
| Attribution lookup (`include_attribution`) | Yes | Yes |
| Plagiarism detection (`detect_plagiarism`) | Yes | Yes |
| Cross-org search (`search_scope=all`) | No | Yes |
| Fuzzy matching (`fuzzy_search`) | No | Yes |

### Account Features

| Feature | Free | Enterprise |
|---------|:----:|:----------:|
| API keys (up to 2) | Yes | Yes (unlimited) |
| Usage analytics | Yes | Yes |
| Audit logs | Yes | Yes |
| Coalition membership | Yes | Yes |
| BYOK (own keys) | No | Yes |
| Team management | No | Yes (unlimited members) |
| Webhooks | No | Yes |
| SSO/SAML | No | Yes |
| Document revocation | No | Yes |

---

## Complete API Endpoint Reference

### Core Endpoints

| Endpoint | Method | Auth | Tier | Description | Dependencies |
|----------|--------|------|------|-------------|--------------|
| `/api/v1/sign` | POST | Yes | All (features gated) | Sign content with C2PA manifest - features gated by tier | Key Service, Coalition Service (optional) |
| `/api/v1/sign/advanced` | POST | - | - | **REMOVED** - Returns 410 Gone, use `/sign` with options | - |
| `/api/v1/sign/rich` | POST | Yes | All | Sign rich article (text + embedded images) with C2PA | Key Service |
| `/api/v1/verify` | POST | Yes | All (features gated) | Verify signed content with optional attribution, plagiarism, and fuzzy search flags - features gated by tier | Key Service |
| `/api/v1/verify/image` | POST | No | Public | Verify a signed image. Checks embedded C2PA manifest; falls back to XMP instance_id DB lookup for passthrough-mode images | None |
| `/api/v1/verify/rich` | POST | No | Public | Verify a signed rich article by document_id | None |
| `/api/v1/lookup` | POST | No | Public | Lookup sentence provenance | None |
| `/api/v1/provenance/lookup` | POST | No | Public | Lookup provenance for a document (structured) | None |
| `/api/v1/account` | GET | Yes | All | Get account profile | Auth Service |
| `/api/v1/account/quota` | GET | Yes | All | Get account quota and limits | Billing Service |
| `/api/v1/usage` | GET | Yes | All | Get organization usage statistics | Key Service |
| `/api/v1/usage/history` | GET | Yes | All | Get historical usage summaries | Analytics Service |

> **Design note:** Both `/sign` and `/verify` follow the same pattern --a single endpoint with optional feature flags (`include_attribution`, `detect_plagiarism`, `fuzzy_search`, `search_scope`) that are gated by tier or add-ons. No separate "advanced" endpoints.

### Public C2PA Utilities

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/public/c2pa/validate-manifest` | POST | No | Public | Validate manifest JSON structure + assertion schema payloads (non-cryptographic). Optional API key supported for higher limits |
| `/api/v1/public/c2pa/create-manifest` | POST | No | Public | Create a manifest JSON payload from plaintext (non-cryptographic) and return a signing helper payload. Optional API key supported for higher limits |
| `/api/v1/public/c2pa/trust-anchors/{signer_id}` | GET | No | Public | Lookup trust anchor (public key) for external C2PA validators (public, IP rate-limited) |
| `/api/v1/public/c2pa/zw/resolve/{segment_uuid}` | GET | No | Public | Resolve a ZW-embedded segment UUID to its source document and provenance metadata |
| `/api/v1/public/c2pa/zw/resolve` | POST | No | Public | Bulk resolve multiple ZW segment UUIDs in a single call |

### Verification Service Endpoints

The following endpoints are provided by the verification microservice (merged into the public API spec):

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/verify/health` | GET | No | Public | Verification service health check |
| `/api/v1/verify/stats` | GET | Yes | All | Get verification statistics |
| `/api/v1/verify/{document_id}` | GET | Yes | All | Get verification history for a document |
| `/api/v1/verify/history/{document_id}` | GET | Yes | All | Get full verification history for a document |
| `/api/v1/verify/document` | POST | Yes | All | Verify document authenticity |
| `/api/v1/verify/signature` | POST | Yes | All | Verify a C2PA signature |
| `/api/v1/verify/advanced` | POST | Yes | All | Advanced verification with attribution and plagiarism detection |
| `/api/v1/verify/quote-integrity` | POST | No | Public | Verify AI attribution accuracy --check if a cited quote matches signed source documents (accurate/approximate/hallucinated/unverifiable) |

### Enterprise Merkle Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/merkle/encode` | POST | Yes | All | Encode document into Merkle tree |

Deprecated Merkle attribution/plagiarism endpoints return HTTP 410 and redirect to `/api/v1/verify`.

### Streaming Merkle Endpoints
Real-time Merkle tree construction for streaming content signing (e.g., LLM output).

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/stream/merkle/start` | POST | Yes | All | Start streaming Merkle session |
| `/api/v1/enterprise/stream/merkle/segment` | POST | Yes | All | Add segment to session |
| `/api/v1/enterprise/stream/merkle/finalize` | POST | Yes | All | Finalize session and compute root |
| `/api/v1/enterprise/stream/merkle/status` | POST | Yes | All | Check session status |

### Evidence Generation Endpoints
Generate court-ready evidence packages for content attribution.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/evidence/generate` | POST | Yes | Enterprise | Generate evidence package with Merkle proofs |

### Fingerprint Endpoints

Robust fingerprinting that survives text modifications.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/fingerprint/encode` | POST | Yes | Enterprise | Encode keyed fingerprint into text |
| `/api/v1/enterprise/fingerprint/detect` | POST | Yes | Enterprise | Detect fingerprint in text |

### Multi-Source Attribution Endpoints
Look up content across multiple sources with chronological ordering.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/attribution/multi-source` | POST | Yes | All (authority ranking: Enterprise) | Multi-source hash lookup with authority ranking |

### Image Attribution Endpoints

Search for images by perceptual similarity (pHash Hamming distance). Scope "org" is
available to all tiers; scope "all" (cross-organization) requires Enterprise.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/images/attribution` | POST | Yes | All (cross-org: Enterprise) | Find images by perceptual similarity (pHash) | None |

### Audio Attribution Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/audio/sign` | POST | Yes | Enterprise | Sign audio with C2PA manifest (WAV, MP3, M4A/AAC) |
| `/api/v1/enterprise/audio/verify` | POST | Yes | Enterprise | Verify C2PA manifest in audio file |

### Video Attribution Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/video/sign` | POST (multipart) | Yes | Enterprise | Sign video with C2PA manifest (MP4, MOV, M4V, AVI) |
| `/api/v1/enterprise/video/verify` | POST (multipart) | Yes | Enterprise | Verify C2PA manifest in video file |
| `/api/v1/enterprise/video/download/{video_id}` | GET | Yes | Enterprise | Download signed video (files > 50 MB, 10-min TTL) |

### Live Video Stream Signing Endpoints (C2PA 2.3 Section 19)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/video/stream/start` | POST | Yes | Enterprise | Start stream signing session |
| `/api/v1/enterprise/video/stream/{session_id}/segment` | POST (multipart) | Yes | Enterprise | Sign individual stream segment |
| `/api/v1/enterprise/video/stream/{session_id}/finalize` | POST | Yes | Enterprise | Finalize session, compute Merkle root |
| `/api/v1/enterprise/video/stream/{session_id}/status` | GET | Yes | Enterprise | Check session status |

### Public Verification Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/public/verify/{ref_id}` | GET | No | Public | Verify embedding by reference ID (optional API key for higher limits) |
| `/api/v1/public/verify/batch` | POST | No | Public | Batch verify embeddings (optional API key for higher limits) |
| `/api/v1/public/extract-and-verify` | POST | - | - | **DEPRECATED** - Returns 410 Gone, use `POST /api/v1/verify` via verification-service |

### Enterprise C2PA Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/enterprise/c2pa/schemas` | POST | Yes | Enterprise | Register custom C2PA assertion schema |
| `/api/v1/enterprise/c2pa/schemas` | GET | Yes | Enterprise | List custom schemas |
| `/api/v1/enterprise/c2pa/schemas/{schema_id}` | GET | Yes | Enterprise | Get custom schema |
| `/api/v1/enterprise/c2pa/schemas/{schema_id}` | PUT | Yes | Enterprise | Update custom schema |
| `/api/v1/enterprise/c2pa/schemas/{schema_id}` | DELETE | Yes | Enterprise | Delete custom schema |
| `/api/v1/enterprise/c2pa/validate` | POST | Yes | Enterprise | Validate assertion before embedding |
| `/api/v1/enterprise/c2pa/templates` | POST | Yes | Enterprise | Create assertion template |
| `/api/v1/enterprise/c2pa/templates` | GET | Yes | Enterprise | List assertion templates |
| `/api/v1/enterprise/c2pa/templates/{template_id}` | GET | Yes | Enterprise | Get assertion template |
| `/api/v1/enterprise/c2pa/templates/{template_id}` | PUT | Yes | Enterprise | Update assertion template |
| `/api/v1/enterprise/c2pa/templates/{template_id}` | DELETE | Yes | Enterprise | Delete assertion template |

### Batch Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/batch/sign` | POST | Yes | Enterprise | Batch sign up to 100 documents |
| `/api/v1/batch/verify` | POST | Yes | Enterprise | Batch verify signed content |

### Streaming Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/sign/stream` | POST/WS | Yes | All | Real-time signing via SSE (POST) and WebSocket (WS) |
| `/api/v1/sign/stream/sessions` | POST | Yes | All | Create streaming session |
| `/api/v1/sign/stream/sessions/{session_id}/events` | GET | Yes | All | Server-Sent Events (SSE) heartbeat and events |
| `/api/v1/sign/stream/sessions/{session_id}/close` | POST | Yes | All | Close streaming session |
| `/api/v1/sign/stream/runs/{run_id}` | GET | Yes | All | Get streaming run state |
| `/api/v1/sign/stream/stats` | GET | Yes | All | Get organization streaming statistics |
| `/api/v1/chat/completions` | POST | Yes | All | OpenAI-compatible SSE chat completions with signing |
| `/api/v1/chat/health` | GET | No | Public | Chat streaming health check |

### Account, Keys, BYOK, Documents, and Webhooks

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/keys` | GET | Yes | All | List API keys |
| `/api/v1/keys` | POST | Yes | All | Create API key |
| `/api/v1/keys/{key_id}` | PATCH | Yes | All | Update API key (name/metadata) |
| `/api/v1/keys/{key_id}` | DELETE | Yes | All | Delete API key |
| `/api/v1/keys/{key_id}/rotate` | POST | Yes | All | Rotate API key |
| `/api/v1/byok/public-keys` | GET | Yes | Enterprise | List BYOK public keys |
| `/api/v1/byok/public-keys` | POST | Yes | Enterprise | Register BYOK public key |
| `/api/v1/byok/public-keys/{key_id}` | DELETE | Yes | Enterprise | Delete BYOK public key |
| `/api/v1/byok/trusted-cas` | GET | No | Public | List C2PA trusted Certificate Authorities |
| `/api/v1/byok/certificates` | POST | Yes | Enterprise | Upload CA-signed certificate (validated against C2PA trust list) |
| `/api/v1/documents` | GET | Yes | Enterprise | List signed documents |
| `/api/v1/documents/{document_id}` | GET | Yes | Enterprise | Get signed document |
| `/api/v1/documents/{document_id}/history` | GET | Yes | Enterprise | Get document provenance history |
| `/api/v1/documents/{document_id}` | DELETE | Yes | Enterprise | Soft-delete a document |
| `/api/v1/webhooks` | GET | Yes | Enterprise | List webhooks |
| `/api/v1/webhooks` | POST | Yes | Enterprise | Create webhook |
| `/api/v1/webhooks/{webhook_id}` | GET | Yes | Enterprise | Get webhook |
| `/api/v1/webhooks/{webhook_id}` | PATCH | Yes | Enterprise | Update webhook |
| `/api/v1/webhooks/{webhook_id}` | DELETE | Yes | Enterprise | Delete webhook |
| `/api/v1/webhooks/{webhook_id}/deliveries` | GET | Yes | Enterprise | List webhook deliveries |
| `/api/v1/webhooks/{webhook_id}/test` | POST | Yes | Enterprise | Send a test delivery |

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
| `/api/v1/integrations/ghost` | POST | Yes | All | Create or update Ghost integration configuration and return webhook URL/token on first create |
| `/api/v1/integrations/ghost` | GET | Yes | All | Get current Ghost integration configuration with masked API key and configured webhook URL |
| `/api/v1/integrations/ghost` | DELETE | Yes | All | Deactivate Ghost integration for the current organization |
| `/api/v1/integrations/ghost/regenerate-token` | POST | Yes | All | Rotate webhook token and return a new ready-to-paste webhook URL |
| `/api/v1/integrations/ghost/webhook` | POST | No | Public (token-scoped) | Receive Ghost publish/update webhook events using scoped `ghwh_...` query token |
| `/api/v1/integrations/ghost/sign/{post_id}` | POST | Yes | All | Manually trigger signing for a Ghost post or page |

#### BYOK Trust Policy Metadata (`GET /api/v1/byok/trusted-cas`)

In addition to trusted CA subjects, this endpoint returns active trust-policy metadata:

- `required_signer_eku_oids`: required signer EKU OIDs enforced during certificate upload validation.
- `revocation_denylist`: internal denylist counters (`serial_count`, `fingerprint_count`).
- `tsa_trust_list`: TSA trust-list URL/fingerprint/load metadata used for timestamp trust handling.

`POST /api/v1/byok/certificates` enforces certificate chaining, signer EKU policy, and internal revocation denylist checks.

### Coalition Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/coalition/dashboard` | GET | Yes | All | Get coalition dashboard (content, earnings, payouts) |
| `/api/v1/coalition/content-stats` | GET | Yes | All | Get historical content corpus statistics |
| `/api/v1/coalition/earnings` | GET | Yes | All | Get detailed earnings history |
| `/api/v1/coalition/opt-out` | POST | Yes | All | Opt out of coalition revenue sharing |
| `/api/v1/coalition/opt-in` | POST | Yes | All | Opt in to coalition revenue sharing |
| `/api/v1/coalition/public/stats` | GET | No | Public | Aggregate coalition stats for marketing display (no auth) |

### Team Management Endpoints

> **Note:** Team management endpoints are tagged internal in the public API spec but are accessible to Enterprise users.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/org/members` | GET | Yes | Internal | List team members |
| `/api/v1/org/members/invite` | POST | Yes | Internal | Invite a team member |
| `/api/v1/org/members/invites` | GET | Yes | Internal | List pending invitations |
| `/api/v1/org/members/invites/{invite_id}` | DELETE | Yes | Internal | Revoke an invitation |
| `/api/v1/org/members/{member_id}/role` | PATCH | Yes | Internal | Update member role |
| `/api/v1/org/members/{member_id}` | DELETE | Yes | Internal | Remove a team member |
| `/api/v1/org/members/accept-invite` | POST | Yes | Internal | Accept an invitation |
| `/api/v1/org/invites/public/{token}` | GET | None | Public | Look up invite metadata by token |
| `/api/v1/org/invites/public/{token}/accept-new` | POST | None | Public | Register new user and accept invite |

### Audit Log Endpoints

> **Note:** Audit log endpoints are tagged internal in the public API spec but are accessible to all authenticated users.

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/audit-logs` | GET | Yes | Internal | Get paginated audit logs |
| `/api/v1/audit-logs/export` | GET | Yes | Internal | Export audit logs (JSON or CSV) |

### Provisioning Endpoints (Internal)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/provisioning/auto-provision` | POST | Token | Internal | Auto-provision organization and API key |
| `/api/v1/provisioning/api-keys` | POST | Token | Internal | Create API key for an organization |
| `/api/v1/provisioning/api-keys` | GET | Token | Internal | List API keys for an organization |
| `/api/v1/provisioning/api-keys/{key_id}` | DELETE | Token | Internal | Revoke an API key |
| `/api/v1/provisioning/users` | POST | Token | Internal | Create a user account |
| `/api/v1/provisioning/health` | GET | No | Internal | Provisioning service health check |

### Document Revocation Endpoints

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

### Rights Management Endpoints

Machine-readable deed system for publishers to define and enforce licensing terms across AI use cases. Built on top of the existing enterprise_api; all data stored in the Core DB.

#### Publisher-Facing (Authenticated)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/rights/profile` | PUT | Yes | Free | Create or update default rights profile (versioned) |
| `/api/v1/rights/profile` | GET | Yes | Free | Get current rights profile |
| `/api/v1/rights/profile/history` | GET | Yes | Free | Get full version history of rights profile |
| `/api/v1/rights/documents/{document_id}` | PUT | Yes | Free | Override rights for a specific document |
| `/api/v1/rights/collections/{collection_id}` | PUT | Yes | Free | Override rights for a collection |
| `/api/v1/rights/content-types/{content_type}` | PUT | Yes | Free | Override rights for a content type |
| `/api/v1/rights/bulk-update` | POST | Yes | Free | Bulk update rights across documents/collections/types |
| `/api/v1/rights/templates` | GET | Yes | All | List available rights template presets |
| `/api/v1/rights/profile/from-template/{template_id}` | POST | Yes | Free | Initialize profile from a template |
| `/api/v1/rights/profile/delegated-setup` | POST | Yes | Strategic Partner | Platform partner sets up rights profile on behalf of publisher |
| `/api/v1/partner/publishers/provision` | POST | Yes | Strategic Partner | Bulk-provision publisher orgs, rights profiles, and claim emails in one call |
| `/api/v1/rights/rsl/import` | POST | Yes | Free | Import existing RSL 1.0 XML document |
| `/api/v1/rights/analytics/detections` | GET | Yes | Enforcement Add-on | Phone-home detection analytics (signed content encountered by AI systems) |
| `/api/v1/rights/analytics/crawlers` | GET | Yes | Free | AI crawler activity breakdown |
| `/api/v1/rights/analytics/crawlers/timeseries` | GET | Yes | Free | Daily crawler activity timeseries |
| `/api/v1/rights/analytics/content-spread` | GET | Yes | Enterprise | External domain detection analytics (content spread) |

Rights profiles support three licensing tiers:
- **Bronze** --Scraping / crawling terms
- **Silver** --RAG / retrieval / search terms
- **Gold** --Training / fine-tuning terms

#### Public Rights Resolution (Unauthenticated)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/public/rights/{document_id}` | GET | No | Resolve rights for a specific signed document |
| `/api/v1/public/rights/resolve` | POST | No | Resolve rights from raw signed text |
| `/api/v1/public/rights/organization/{org_id}` | GET | No | Get organization's default rights profile |
| `/api/v1/public/rights/{document_id}/json-ld` | GET | No | Machine-readable rights in JSON-LD (Schema.org) format |
| `/api/v1/public/rights/{document_id}/odrl` | GET | No | Machine-readable rights in W3C ODRL format |
| `/api/v1/public/rights/organization/{org_id}/robots-meta` | GET | No | AI-specific robots meta tag directives |
| `/api/v1/public/rights/organization/{org_id}/rsl` | GET | No | Generate RSL 1.0 XML document |
| `/api/v1/public/rights/organization/{org_id}/robots-txt` | GET | No | robots.txt additions with RSL/AI directives |
| `/api/v1/public/rights/rsl/olp/token` | POST | No | RSL Open License Protocol --generate access token |
| `/api/v1/public/rights/rsl/olp/validate/{token}` | GET | No | Validate RSL OLP token |

#### Formal Notices (Authenticated)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/notices/` | GET | Yes | Enforcement Add-on | List all formal notices for the organization |
| `/api/v1/notices/create` | POST | Yes | Enforcement Add-on | Create an immutable formal notice |
| `/api/v1/notices/{notice_id}` | GET | Yes | Enforcement Add-on | Retrieve a formal notice |
| `/api/v1/notices/{notice_id}/deliver` | POST | Yes | Enforcement Add-on | Deliver notice to an AI company |
| `/api/v1/notices/{notice_id}/evidence` | GET | Yes | Enforcement Add-on | Get cryptographic evidence package (court-ready) |
| `/api/v1/notices/{notice_id}/evidence/pdf` | GET | Yes | Enforcement Add-on | Download Encypher-branded PDF evidence package |

Notices are append-only with SHA-256 content hashing for tamper-evidence. Each evidence package includes a linked `notice_evidence_chain` for chain-of-custody documentation.

#### Rights Licensing Transactions (Authenticated)

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/rights-licensing/request` | POST | Yes | All | Submit a licensing request |
| `/api/v1/rights-licensing/requests` | GET | Yes | All | List licensing requests |
| `/api/v1/rights-licensing/requests/{request_id}/respond` | PUT | Yes | All | Approve or reject a licensing request |
| `/api/v1/rights-licensing/agreements` | GET | Yes | All | List active licensing agreements |
| `/api/v1/rights-licensing/agreements/{agreement_id}` | GET | Yes | All | Get a specific licensing agreement |
| `/api/v1/rights-licensing/agreements/{agreement_id}/usage` | GET | Yes | All | Get usage metrics for an agreement |

### CDN Integration Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/cdn/cloudflare` | POST | Yes | Enterprise | Create or update Cloudflare Logpush integration |
| `/api/v1/cdn/cloudflare` | GET | Yes | Enterprise | Get current Cloudflare Logpush integration config |
| `/api/v1/cdn/cloudflare` | DELETE | Yes | Enterprise | Remove Cloudflare Logpush integration |

### Onboarding & Provisioning Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/api/v1/onboarding/request-certificate` | POST | Yes | All | Request SSL.com code signing certificate |
| `/api/v1/onboarding/certificate-status` | GET | Yes | All | Get current certificate status |
| `/api/v1/onboarding/progression-status` | GET | Yes | All | Publisher value journey progression (6-stage Sign->Earnings) |

### Health & Monitoring Endpoints

| Endpoint | Method | Auth | Tier | Description |
|----------|--------|------|------|-------------|
| `/health` | GET | No | Public | Health check |
| `/readyz` | GET | No | Public | Readiness probe |
| `/metrics` | GET | No | Internal | Prometheus-compatible metrics |
| `/` | GET | No | Public | API information |

## Quick Start

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

## API Reference

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

The gateway URL is what you should give to external developers -- it's the single entry point for all API operations.

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

Features are gated by tier --free tier gets basic verification, attribution, and plagiarism detection; Enterprise unlocks cross-org search and fuzzy matching.

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

## Enterprise Features

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

### POST /api/v1/enterprise/audio/sign

Sign an audio file with a C2PA manifest. Enterprise tier only.

**Request:**

```json
{
  "audio_data_base64": "<base64-encoded-audio>",
  "mime_type": "audio/wav",
  "title": "Interview Recording",
  "action": "c2pa.created",
  "custom_assertions": [],
  "rights_data": {}
}
```

**Response:**

```json
{
  "success": true,
  "audio_id": "aud_a1b2c3d4e5f67890",
  "document_id": "doc_f8e7d6c5b4a39021",
  "signed_audio_base64": "<base64-encoded-signed-audio>",
  "original_hash": "sha256:abc123...",
  "signed_hash": "sha256:def456...",
  "c2pa_instance_id": "urn:uuid:550e8400-e29b-41d4-a716-446655440000",
  "c2pa_manifest_hash": "sha256:789abc...",
  "size_bytes": 1048576,
  "mime_type": "audio/wav",
  "c2pa_signed": true
}
```

Supported formats: WAV (RIFF), MP3 (ID3), M4A/AAC (ISO BMFF).
Supported actions: `c2pa.created`, `c2pa.dubbed`, `c2pa.mixed`, `c2pa.mastered`, `c2pa.remixed`.

---

### POST /api/v1/enterprise/video/sign

Sign a video file with a C2PA manifest. Multipart upload (not base64). Enterprise tier only.

**Request** (multipart/form-data):

```
file: <video-file-binary>
mime_type: video/mp4
title: News Footage
action: c2pa.created
custom_assertions: []
rights_data: {}
```

**Response:**

```json
{
  "success": true,
  "video_id": "vid_a1b2c3d4e5f67890",
  "document_id": "doc_f8e7d6c5b4a39021",
  "signed_video_base64": "<base64 for files under 50 MB, null for larger>",
  "download_url": "/api/v1/enterprise/video/download/vid_a1b2c3d4e5f67890",
  "original_hash": "sha256:abc123...",
  "signed_hash": "sha256:def456...",
  "c2pa_instance_id": "urn:uuid:550e8400-e29b-41d4-a716-446655440000",
  "c2pa_manifest_hash": "sha256:789abc...",
  "size_bytes": 52428800,
  "mime_type": "video/mp4",
  "c2pa_signed": true
}
```

Supported formats: MP4, MOV, M4V (ISO BMFF), AVI (RIFF). Max 500 MB.
Files over 50 MB return a `download_url` instead of inline base64 (10-min TTL).

---

### Live Video Stream Signing (C2PA 2.3 Section 19)

Sign live video streams per-segment with backwards-linked provenance chain.

**1. Start session:**

```bash
curl -X POST https://api.encypherai.com/api/v1/enterprise/video/stream/start \
  -H "Authorization: Bearer encypher_..."
```

```json
{
  "session_id": "vstream_a1b2c3d4e5f6",
  "status": "active",
  "message": "Stream signing session created."
}
```

**2. Sign segments** (multipart upload, repeat per segment):

```
POST /api/v1/enterprise/video/stream/{session_id}/segment
file: <fmp4-segment-binary>
mime_type: video/mp4
```

Each segment's C2PA manifest includes a `com.encypher.stream.chain.v1` assertion
referencing the previous segment's manifest hash.

**3. Finalize and get Merkle root:**

```bash
curl -X POST .../enterprise/video/stream/{session_id}/finalize
```

```json
{
  "session_id": "vstream_a1b2c3d4e5f6",
  "segment_count": 42,
  "merkle_root": "sha256:abc123...",
  "status": "finalized"
}
```

The Merkle root proves complete stream integrity over all segment manifest hashes.

---

### Invisible Signed Embeddings

Embed signed references directly into content so it can be extracted and verified later. With
`manifest_mode="micro"` (the default), each segment receives a compact marker while a full C2PA manifest
is appended at the document end by default (set `disable_c2pa=true` to skip the document-level manifest).

**Endpoint:** `POST /api/v1/sign` (with embedding options)

**Request:**

```json
{
  "document_id": "article_001",
  "text": "Full article text...",
  "segmentation_level": "sentence",
  "manifest_mode": "micro",
  "c2pa_manifest_url": "https://...",
  "license": {
    "type": "All Rights Reserved",
    "contact_email": "licensing@example.com"
  }
}
```

**Manifest Modes:** `full`, `micro` (default: `micro`)

**`micro` mode sub-variants** (controlled by `ecc` and `legacy_safe` flags):
- `ecc=true, legacy_safe=false` (default): VS256-RS, 44-char markers with Reed-Solomon error correction
- `ecc=false, legacy_safe=false`: VS256, 36-char markers, not Word-safe
- `ecc=false, legacy_safe=true`: zero-width chars, 100-char markers, Word/terminal-safe
- `ecc=true, legacy_safe=true`: zero-width chars with ECC, 112-char markers, Word-safe + error correction

**Recommended configuration by use case:**

| Use case | `manifest_mode` | `ecc` | `legacy_safe` | Notes |
|---|---|---|---|---|
| Web / browser / PDF (default) | `micro` | `true` | `false` | VS256-RS, 44 chars/segment, best density + ECC |
| Low-character-budget web | `micro` | `false` | `false` | VS256, 36 chars/segment, no ECC |
| Microsoft Word / Office / copy-paste | `micro` | `true` | `true` | ZWC-RS, 112 chars/segment, survives Word round-trip |
| Word + tight budget | `micro` | `false` | `true` | ZWC, 100 chars/segment, Word-safe, no ECC |
| Full C2PA manifest embedded in document | `full` | n/a | n/a | Larger payload; use when the doc must be self-contained |

**Rule of thumb:** start with the default (`micro`, `ecc=true`, `legacy_safe=false`). Switch `legacy_safe=true` only when the signed content will pass through Microsoft Word or a terminal that strips variation selectors.

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

### Rich Article Signing (Text + Images)

Sign an article containing embedded images as a single provenance unit. Each image
receives provenance data embedded directly in the image binary. The article-level
composite manifest references each image as an ingredient, binding text and images
together under one cryptographic record.

**Endpoint:** POST /api/v1/sign/rich

**Storage model:** Sign-and-return. Signed image bytes (with embedded provenance) are
returned as base64 in the response. Publishers store and serve signed images from their
own CDN. Only metadata (hashes, pHash, c2pa_instance_id) is stored in the Encypher DB.

**Image binding layers:**

| Layer | Mechanism | Survives re-encode? | Tier |
|-------|-----------|---------------------|------|
| Hard binding | SHA-256 of pixel bytes (original_hash) | No | All |
| In-file reference | XMP (ISO 16684) carrying `instance_id` in APP1/iTXt | Yes (CDN-compatible) | All |
| C2PA manifest | Full cryptographic manifest embedded in file | Yes | When cert configured |
| Soft binding | TrustMark neural watermark (survives JPEG recompression, moderate crop) | Yes | Enterprise only |
| pHash fuzzy index | Perceptual hash for near-duplicate search (Hamming distance) | Near-duplicate | All |

**Passthrough mode** (local dev / no signing cert configured): C2PA manifest embedding is
skipped. XMP provenance is still injected into each signed image so verification by
`instance_id` works correctly. `c2pa_signed=false` in the response indicates this mode.
`signed_hash` will differ from `original_hash` because XMP bytes are appended inside
the binary (JPEG: APP1 segment after SOI; PNG: iTXt chunk after IHDR).

**XMP namespace:** `https://encypher.ai/schemas/v1` -- fields: `instance_id` (urn:uuid),
`org_id`, `document_id`, `image_hash` (SHA-256 of original pixels), `verify` (URL).
Readable by standard XMP tooling. WebP and TIFF are not XMP-modified; they still
receive hard binding and pHash registration.

**Free tier:** Hard binding + XMP + pHash. C2PA manifest signing requires a configured signing cert.

**Enterprise tier:** All Free features plus TrustMark neural soft binding and
cross-organization pHash attribution search.

**Request (abbreviated):**

```json
{
  "content": "<h1>Title</h1><p>Text...</p>",
  "content_format": "html",
  "document_id": "article-2026-0001",
  "document_title": "Breaking News",
  "images": [
    {
      "data": "<base64-encoded-jpeg>",
      "filename": "photo1.jpg",
      "mime_type": "image/jpeg",
      "position": 0,
      "alt_text": "Caption"
    }
  ],
  "options": {
    "segmentation_level": "sentence",
    "manifest_mode": "micro",
    "enable_trustmark": false,
    "image_quality": 95
  }
}
```

**Image verification:**

- POST /api/v1/verify/image -- accepts base64 image. Two-step verification:
  1. Extracts and validates the embedded C2PA manifest (if present).
  2. If no C2PA manifest or hash miss, reads the XMP `instance_id` and looks up
     the image record in the Encypher DB. Returns `valid=true` if the DB record
     is found, regardless of whether a full C2PA manifest is embedded. This allows
     passthrough-mode images and CDN-re-encoded copies to verify successfully.
  Note: in the local dev Traefik stack this endpoint is served by the enterprise-api
  (not verification-service). `verify-image-router` (priority 110) in
  `infrastructure/traefik/routes-local.yml` overrides the catch-all `verify-router`
  (priority 100). See `docs/image-signing/implementation-guide.md` for details.
- POST /api/v1/verify/rich -- looks up signed article by document_id, verifies all
  components (text, images, composite manifest integrity).

**Image attribution (fuzzy):**

POST /api/v1/enterprise/images/attribution -- finds similar images by pHash Hamming distance.
scope="org" is available to all tiers; scope="all" (cross-org) requires Enterprise.

---

## Architecture

### Microservices Architecture

The Enterprise API is part of a comprehensive microservices ecosystem. Each service maintains its own database following the **database-per-service** pattern for scalability and resilience.

```
+--------------------------------------------------------------+
|                    Client Applications                        |
|          (SDK, CLI, WordPress, Direct API Calls)              |
+--------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------+
|                    API Gateway (Traefik)                       |
|                        Port 8000                              |
|          Routes /api/v1/* to appropriate services             |
+--------------------------------------------------------------+
                              |
              +---------------+---------------+
              v                               v
+-------------------------+       +-------------------------+
|   Enterprise API        |       |    Key Service          |
|     Port 9000           |<------|     Port 8003           |
|                         |       |                         |
| - C2PA Signing          |       | - API Key Validation    |
| - Content Verification  |       | - Org Context/Tier      |
| - Merkle Trees          |       | - Feature Permissions   |
| - Embeddings            |       | - Usage Quotas          |
| - Sentence Tracking     |       |                         |
+-------------------------+       +-------------------------+
              |                               |
              v                               v
+-------------------------+       +-------------------------+
|  PostgreSQL Content DB  |       |  PostgreSQL Keys DB     |
|   (Enterprise API)      |       |   (Key Service)         |
|                         |       |                         |
| - documents             |       | - api_keys              |
| - merkle_trees          |       | - organizations         |
| - sentence_records      |       | - subscriptions         |
| - manifests             |       | - usage_records         |
| - embeddings            |       |                         |
+-------------------------+       +-------------------------+

              |
              v
+-------------------------+       +-------------------------+
|  Coalition Service      |       |    Auth Service         |
|     Port 8009           |       |     Port 8001           |
|                         |       |                         |
| - Content Indexing      |       | - User Authentication   |
| - Revenue Distribution  |       | - JWT Management        |
| - Licensing Management  |       | - OAuth Integration     |
| - Member Stats          |       | - Org Provisioning      |
+-------------------------+       +-------------------------+
              |                               |
              v                               v
+-------------------------+       +-------------------------+
| PostgreSQL Coalition DB |       |  PostgreSQL Auth DB     |
|  (Coalition Service)    |       |   (Auth Service)        |
|                         |       |                         |
| - coalition_members     |       | - users                 |
| - coalition_content     |       | - sessions              |
| - licensing_agreements  |       | - oauth_tokens          |
| - revenue_distributions |       |                         |
+-------------------------+       +-------------------------+

                    |
                    v
+--------------------------------------------------------------+
|                    Redis Cache Layer                           |
|                        Port 6379                              |
|                                                               |
| - Key Validation Cache (5min TTL)                             |
| - Session Management                                          |
| - Rate Limiting State                                         |
| - Streaming Session State                                     |
+--------------------------------------------------------------+

                    |
                    v
+--------------------------------------------------------------+
|                  encypher-ai Core Library                      |
|                      (v2.9.0+)                                |
|                                                               |
| - C2PA Manifest Generation                                    |
| - Unicode Metadata Embedding                                  |
| - Cryptographic Signature Verification                        |
| - Merkle Tree Operations                                      |
+--------------------------------------------------------------+
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
1. Client -> Enterprise API
   Authorization: Bearer encypher_abc123...

2. Enterprise API -> Key Service
   POST /api/v1/keys/validate
   { "key": "encypher_abc123..." }

3. Key Service -> PostgreSQL Keys DB
   SELECT * FROM api_keys WHERE key_hash = hash(...)
   JOIN organizations, subscriptions

4. Key Service -> Enterprise API
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

5. Enterprise API -> Redis
   Cache validation result (5min TTL)

6. Enterprise API -> Client
   Process request with org context
```

**Caching Strategy:**
- First request: Validates via Key Service, caches result in Redis (5min TTL)
- Subsequent requests: Uses cached validation (no Key Service call)
- Cache miss: Automatic re-validation via Key Service

### Coalition Integration Flow

```
1. Client signs content -> Enterprise API
   POST /api/v1/sign

2. Enterprise API checks if user is coalition member

3. If coalition member:
   Enterprise API -> Coalition Service
   POST /api/v1/coalition/content
   {
     "member_id": "...",
     "document_id": "...",
     "content_hash": "...",
     "word_count": 1500,
     "signed_at": "2025-12-01T10:00:00Z"
   }

4. Coalition Service -> PostgreSQL Coalition DB
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

## Security

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

## Performance

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

## Error Handling

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
    "code": "E_UNAUTHORIZED",
    "message": "API key required",
    "hint": "Optional suggestion for resolution",
    "next_action": "Provide an API key via the Authorization: Bearer <key> header.",
    "docs_url": "/docs#/API%20Keys"
  },
  "correlation_id": "req-abc123def456",
  "meta": {
    "api_version": "v1",
    "processing_time_ms": 12,
    "status": "error"
  }
}
```

Every error includes a `next_action` field with a concrete next step, and
optionally a `docs_url` pointing to the relevant API documentation section.
Validation errors (422) additionally include grouped `field_errors` in
`error.details`.

### API Discovery

`GET /api/v1/` returns a public, unauthenticated index of all available
endpoints with their HTTP methods, summaries, and tags. Internal/admin
routes are filtered out. The response is cached after the first request.

### Binary Content Guard

Text input fields (`text` in sign/verify/batch requests) reject null bytes
and ASCII control characters (except tab, newline, CR) with a clear error
message. This prevents binary data from being submitted to text endpoints.

---

## Coalition Service Integration

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
- Automatic content indexing for coalition members
- Revenue sharing (70-85% members / 15-30% platform, based on tier)
- Bulk licensing to AI companies
- Access tracking and analytics

**Service Location**: `services/coalition-service` (Port 8009)

**Documentation**: See `services/coalition-service/README.md`

---

## Configuration

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
DATABASE_URL=postgresql://db_user:<db_password>@localhost:5432/encypher_content

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
SSL_COM_API_KEY=non_real_api_key
SSL_COM_ACCOUNT_KEY=non_real_account_key
SSL_COM_API_URL=https://api.ssl.com/v1
SSL_COM_PRODUCT_ID=non_real_product_id
```

#### Security Configuration

```bash
# Encryption keys (for private key storage)
KEY_ENCRYPTION_KEY=non_real_hex_string
ENCRYPTION_NONCE=non_real_hex_string
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
EMBEDDING_SIGNATURE_SECRET=non_real_hex_or_ascii_secret
```

#### Image Signing Configuration

```bash
# Max image size per upload (bytes, default 10MB)
IMAGE_MAX_SIZE_BYTES=10485760

# Max images per /sign/rich request
IMAGE_MAX_COUNT_PER_REQUEST=20

# Passthrough mode: skip C2PA manifest embedding (XMP provenance still injected).
# Auto-enabled when MANAGED_SIGNER_PRIVATE_KEY_PEM / MANAGED_SIGNER_CERTIFICATE_CHAIN_PEM
# are absent. Set explicitly for local dev / CI.
IMAGE_SIGNING_PASSTHROUGH=false

# Generic passthrough mode: skip C2PA manifest embedding for ALL media types
# (audio, future video, etc.). Auto-enabled when per-org signing credentials
# are absent. Set explicitly for local dev / CI.
SIGNING_PASSTHROUGH=false

# TrustMark microservice URL (empty = disabled, Enterprise only)
IMAGE_SERVICE_URL=

# Max video size per upload (bytes, default 500MB)
VIDEO_MAX_SIZE_BYTES=524288000
```

#### C2PA Trust List Configuration

```bash
# Optional override for the upstream trust list URL
C2PA_TRUST_LIST_URL=https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem

# Optional SHA-256 pin (hex) to prevent trust list tampering
C2PA_TRUST_LIST_SHA256=non_real_sha256_hex

# Refresh interval (hours) for reloading the trust list
C2PA_TRUST_LIST_REFRESH_HOURS=24

# Optional override for the TSA trust list URL
C2PA_TSA_TRUST_LIST_URL=https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem

# Optional SHA-256 pin (hex) for TSA trust list
C2PA_TSA_TRUST_LIST_SHA256=non_real_sha256_hex

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
MANAGED_SIGNER_PRIVATE_KEY_PEM="<paste_private_key_pem_here>"
MANAGED_SIGNER_CERTIFICATE_PEM="<paste_certificate_pem_here>"
MANAGED_SIGNER_CERTIFICATE_CHAIN_PEM="<paste_certificate_chain_pem_here>"
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

## SDK Support

### Official SDKs

- **Python**: [encypher-enterprise](https://pypi.org/project/encypher-enterprise/)
- **JavaScript/TypeScript**: Coming soon
- **Go**: Coming soon
- **Ruby**: Coming soon

### Community SDKs

- **PHP**: [encypher-php](https://github.com/community/encypher-php)
- **.NET**: [Encypher.NET](https://github.com/community/encypher-dotnet)

---

## Testing

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
   - Open `dashboard.encypherai.com` -> Settings -> Publisher identity.
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

## Documentation

- **API Docs**: [docs.encypherai.com/api](https://docs.encypherai.com/api)
- **SDK Docs**: [docs.encypherai.com/sdk](https://docs.encypherai.com/sdk)
- **Microservices Overview**: [services/README.md](../services/README.md)
- **Key Service**: [services/key-service/README.md](../services/key-service/README.md)
- **Coalition Service**: [services/coalition-service/README.md](../services/coalition-service/README.md)
- **Image Signing Implementation Guide**: [docs/image-signing/implementation-guide.md](../docs/image-signing/implementation-guide.md) -- XMP embedding details, passthrough mode, two-step verification, Traefik routing
- **Audio C2PA Signing**: Endpoints at `/enterprise/audio/sign` and `/enterprise/audio/verify` -- WAV (RIFF), MP3 (ID3), M4A/AAC (ISO BMFF) via c2pa-python; see `app/services/audio_signing_service.py`
- **Video C2PA Signing**: Endpoints at `/enterprise/video/sign` and `/enterprise/video/verify` -- MP4, MOV, M4V (ISO BMFF), AVI (RIFF); multipart upload up to 500 MB; see `app/services/video_signing_service.py`
- **Live Video Stream Signing**: Session-based per-segment signing at `/enterprise/video/stream/*` -- C2PA 2.3 Section 19; see `app/services/video_stream_signing_service.py`
- **Inspect Tool (marketing site)**: [apps/marketing-site/src/app/tools/inspect/README.md](../apps/marketing-site/src/app/tools/inspect/README.md)
- **C2PA Custom Assertions API**: [docs/api/C2PA_CUSTOM_ASSERTIONS_API.md](../docs/api/C2PA_CUSTOM_ASSERTIONS_API.md)
- **C2PA Provenance Chain**: [docs/c2pa/C2PA_PROVENANCE_CHAIN.md](../docs/c2pa/C2PA_PROVENANCE_CHAIN.md)
- **C2PA Implementation**: [docs/c2pa/C2PA Implimentation Guidance.md](../docs/c2pa/C2PA%20Implimentation%20Guidance.md)
- **C2PA Spec**: [docs/c2pa/Manifests_Text.adoc](../docs/c2pa/Manifests_Text.adoc)
- **Architecture**: [docs/architecture/BACKEND_ARCHITECTURE.md](../docs/architecture/BACKEND_ARCHITECTURE.md)

---

## Support

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

## License

Proprietary - See [LICENSE](../LICENSE) for details.

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Caching and session management
- [Railway](https://railway.app/) - Hosting platform
- [C2PA](https://c2pa.org/) - Content authenticity standards
- [SSL.com](https://www.ssl.com/) - Certificate authority

---

<div align="center">

**Made by Encypher**

[Website](https://encypherai.com) |[Dashboard](https://dashboard.encypherai.com) |[Docs](https://docs.encypherai.com) |[Status](https://verify.encypherai.com/status)

</div>
