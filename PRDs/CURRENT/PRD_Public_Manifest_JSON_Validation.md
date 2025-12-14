# Public Manifest JSON Validation

**Status:** 🔄 In Progress
**Current Goal:** Stabilize baseline tests and then add public C2PA manifest endpoints (validate + create helper) for plaintext/text workflows.

## Overview

We want a lightweight, file-format-independent way for users to supply a C2PA-like manifest (as JSON) and have the Enterprise API validate its structure and assertion payloads. This enables users to build manifests externally and then embed them using our existing signing/embedding flows.

## Objectives

- Provide an API endpoint that validates manifest JSON structure with clear errors/warnings.
- Optionally validate assertion `data` against standard and/or user-provided JSON Schemas.
- Keep the endpoint explicitly **non-cryptographic** (no signature/TSA/JUMBF parsing) while we design the full compliance path.
- Provide a helper endpoint to create a manifest payload from plaintext/text inputs (file-format-independent) that can be passed to existing signing/embedding and verification flows.

## Tasks

### 0.0 Baseline / Test Harness (Prerequisite)

- [x] 0.1 Baseline tests green — ✅ pytest (required before adding new endpoints)
- [x] 0.2 Tests use seeded test user/org context (no ad-hoc per-test data)
- [x] 0.3 Document local dev DB/ports assumptions for tests (Docker Compose)

### 1.0 API (Manifest JSON Validation)

- [x] 1.1 Add `POST /api/v1/public/c2pa/validate-manifest` endpoint (no auth)
- [x] 1.2 Define request/response schemas for manifest validation
- [x] 1.3 Validate basic manifest structure (required fields/types)
- [x] 1.4 Validate assertions (optional):
  - [x] 1.4.1 Validate each assertion has required keys (`label`, `data`)
  - [x] 1.4.2 Validate standard assertion labels using built-in schemas where available
  - [x] 1.4.3 Allow caller-provided JSON Schemas (label -> schema) for validation

### 1.5 API (Manifest Creation Helper for Text)

- [x] 1.5.1 Add `POST /api/v1/public/c2pa/create-manifest` endpoint (no auth)
- [x] 1.5.2 Define request/response schemas for manifest creation
- [x] 1.5.3 Support plaintext and `.txt` inputs (file-format-independent)
- [x] 1.5.4 Output a manifest JSON payload compatible with:
  - [x] 1.5.4.1 `POST /api/v1/public/c2pa/validate-manifest`
  - [x] 1.5.4.2 existing signing/embedding flow
  - [x] 1.5.4.3 existing verifier flow (structure-only for now)

### 2.0 Security/Spec Follow-ups (Researched — Dec 2025)

- [x] 2.1 Define requirements for signature verification/trust model (trusted roots vs org trust anchors) — ✅ Researched
- [x] 2.2 Determine if TSA is required / recommended per C2PA spec for our text workflow — ✅ Researched
- [x] 2.3 Evaluate support for raw C2PA JUMBF blobs and requirements to parse/verify — ✅ Researched

---

## 2.0 Strategic Findings: C2PA Infrastructure Decisions

### 2.1 Trust Model & CA Strategy

#### Current State
Encypher implements an **Org Trust Anchor** model:
- Each organization's public key is stored in the `organizations` table
- Verification extracts `signer_id` from the manifest and looks up the corresponding public key
- Signatures are cryptographically verified against the org's stored key
- This is **Valid** per C2PA spec (§14.3.5) but not **Trusted** (no public CA chain)

#### C2PA Spec Requirements (§14.4)
- **Trusted** status requires signing credential to chain to an entry in a **Trust List**
- C2PA maintains a public Trust List of approved CAs at https://spec.c2pa.org/conformance-explorer/
- Validators MUST include C2PA Trust List for the `c2pa-kp-claimSigning` EKU
- Private Credential Stores (§14.4.3) are allowed for out-of-band trust relationships

#### Strategic Options

| Option | Description | Cost/Effort | Recommendation |
|--------|-------------|-------------|----------------|
| **A. Partner with SSL.com** | SSL.com is now a C2PA-conformant CA. They offer enterprise C2PA certificate issuance + TSA services. | ~$5K-50K/yr depending on volume | ✅ **Recommended for Phase 1** |
| **B. Become a Subordinate CA** | Partner with a Root CA to issue intermediate certificates under their chain. | $50K-150K setup + audit | Consider for Phase 2 if volume justifies |
| **C. Join C2PA Trust List as CA** | Become a conformant CA through C2PA Conformance Program. | $100K+ (audit, HSM, compliance) | Long-term strategic goal only |
| **D. External Verifier API** | Expose a public API for external verifiers to query our org trust anchor DB. | Low (engineering only) | ✅ **Yes — add as feature** |

#### Decision: Hybrid Approach
1. **Short-term (Q1 2026)**: Partner with **SSL.com** for C2PA certificate issuance. They are already on the C2PA Trust List and offer:
   - C2PA-conformant signing certificates
   - TSA services (on C2PA TSA Trust List)
   - Custom PKI integration
   - Contact: https://www.ssl.com/contact_us/

2. **Ongoing**: Keep org trust anchor model for enterprise B2B (closed ecosystems). This is explicitly endorsed by C2PA Implementation Guidance §6.3.2.2-6.3.2.3.

3. **Add External Verifier API**: Expose `GET /api/v1/public/trust-anchors/{signer_id}` returning org public key for external validators. This enables third-party verifiers to validate Encypher-signed content.

4. **Long-term (2027+)**: Evaluate becoming a subordinate CA if volume > 1M signatures/month.

---

### 2.2 TSA (Time Stamp Authority) Strategy

#### C2PA Spec Requirements (§15.8)
- TSA is **strongly recommended** but **not strictly required**
- If present, must be RFC 3161 compliant (`sigTst` or `sigTst2` COSE header)
- TSA must be on **C2PA TSA Trust List** (separate from signer trust list)
- Key benefit: Manifests remain **valid indefinitely** even after signing certificate expires

#### C2PA Implementation Guidance
> "Other examples, like 'News and Media Creation' and 'Insurance Underwriting and Claims Servicing,' may not have such a requirement. In these cases, the list of trust anchors for TSAs can be empty, and those applications can skip retrieving time-stamps."

#### Cost Analysis

| Option | Description | Cost | Latency Impact |
|--------|-------------|------|----------------|
| **A. Partner with SSL.com TSA** | SSL.com is on C2PA TSA Trust List | Bundled with cert pricing | +50-150ms/sign |
| **B. Use DigiCert TSA** | Free public TSA at http://timestamp.digicert.com | Free (public) | +50-150ms/sign |
| **C. Use FreeTSA.org** | Free public TSA | Free | +100-300ms/sign |
| **D. Become a TSA** | Host own RFC 3161 TSA, join C2PA TSA Trust List | $50K+ (HSM, audit, uptime) | N/A |
| **E. No TSA (current)** | Skip timestamps, rely on certificate validity | $0 | No impact |

#### Decision: Optional TSA as Premium Feature
1. **Default (all tiers)**: No TSA — acceptable for enterprise B2B with short-lived content per C2PA guidance.

2. **Premium Feature (Enterprise+ tier)**: Integrate with **DigiCert or SSL.com TSA** as opt-in:
   - Add `include_timestamp: bool = False` to `/api/v1/sign` request
   - Store `TimeStampToken` in `sigTst2` COSE header
   - Add TSA trust anchors to validator

3. **Do NOT become a TSA** — operational burden (HSM, 99.99% uptime, audits) outweighs benefits.

4. **Document limitation**: Current `/api/v1/verify` depends on signing certificate validity. With TSA, verification works indefinitely.

---

### 2.3 Text Workflow Alignment & Media Expansion

#### Current Implementation Audit

| Spec Requirement (`docs/c2pa/Manifests_Text.adoc`) | Encypher Implementation | Status |
|---------------------------------------------------|-------------------------|--------|
| Magic `C2PATXT\0` (0x4332504154585400) | ✅ `encypher.interop.c2pa.text_wrapper` | Compliant |
| Version = 1 | ✅ Implemented | Compliant |
| Byte-to-VS mapping (U+FE00-U+FE0F, U+E0100-U+E01EF) | ✅ Implemented | Compliant |
| ZWNBSP (U+FEFF) prefix | ✅ Implemented | Compliant |
| Placement at end of visible text | ✅ Implemented | Compliant |
| NFC normalization before hashing | ✅ `text_hashing.py:46-49` uses `unicodedata.normalize("NFC", text)` | **COMPLIANT** |
| `c2pa.hash.data` with `exclusions` field | ✅ `unicode_metadata.py:864-870` computes byte offsets correctly | **COMPLIANT** |
| Single contiguous wrapper block | ✅ Implemented | Compliant |
| JUMBF container inside wrapper | ✅ Implemented | Compliant |

#### Compliance Audit (Dec 2025)

✅ **NFC normalization**: Verified in `encypher-ai/encypher/interop/c2pa/text_hashing.py:46-49`
✅ **`exclusions` field**: Verified in `encypher-ai/encypher/core/unicode_metadata.py:864-870, 911-922`
✅ **Iterative stabilization**: Loop at lines 929-935 ensures hash+exclusions are stable before embedding

**Remaining (low priority)**:
- [ ] Add validation status codes `manifest.text.corruptedWrapper` and `manifest.text.multipleWrappers` to verifier response

#### Media Expansion Path

| Media Type | Manifest Format | Embedding Complexity | Encypher Support |
|------------|-----------------|---------------------|------------------|
| **Text (.txt, API text)** | `C2PATextManifestWrapper` (Unicode VS) | Low | ✅ Current |
| **Markdown** | Same as text | Low | ✅ Works today |
| **HTML** | Same as text (in `<body>`) | Low | ✅ Works today |
| **JSON/YAML** | Same as text | Low | ✅ Works today |
| **PDF** | JUMBF in incremental save | Medium | 🔧 Future (use `c2pa-python`) |
| **Images (JPEG, PNG, WebP)** | JUMBF in file metadata | Medium | 🔧 Future (use `c2pa-python`) |
| **Video (MP4, MOV)** | JUMBF in moov/uuid box | High | 🔧 Future (use `c2pa-rs`) |
| **Sidecar (.c2pa)** | Raw JUMBF file | Low | 🔧 Future |

#### Decision: Text-First, Staged Media Expansion
1. **Phase 1 (Current)**: Text-only workflows. Verify 100% spec compliance with `docs/c2pa/Manifests_Text.adoc`.

2. **Phase 2 (Q2 2026)**: Add PDF support using `c2pa-python` bindings. High enterprise demand.

3. **Phase 3 (Q3 2026)**: Add image support (JPEG, PNG, WebP) using `c2pa-python`.

4. **Phase 4 (2027)**: Evaluate video support based on customer demand.

5. **Sidecar support**: Add `/api/v1/verify-jumbf` endpoint accepting raw `.c2pa` files — low effort, enables interop with other C2PA tools.

---

## Summary: Infrastructure Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Trust Model** | Partner with SSL.com for C2PA certs + keep org trust anchors | Best of both: public trust + enterprise flexibility |
| **External Verifier API** | Yes — add public trust anchor lookup endpoint | Enables third-party verification |
| **TSA** | Optional premium feature (DigiCert/SSL.com) | Spec allows skipping; add for legal/media use cases |
| **Become a CA/TSA** | No (too expensive) | Partner instead |
| **Text Compliance** | Verify NFC normalization + exclusions field | 95% compliant, minor verification needed |
| **Media Expansion** | Text → PDF → Images → Video | Staged rollout based on demand |

---

## API Design: External Verifier Endpoint

### `GET /api/v1/public/trust-anchors/{signer_id}`

**Purpose:** Enable third-party C2PA validators to verify Encypher-signed content by looking up the signer's public key.

**Authentication:** None required (public endpoint)

**Rate Limiting:** IP-based, 100 requests/minute

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `signer_id` | string | The signer identifier extracted from the manifest (e.g., org ID or `encypher.public`) |

**Response (200 OK):**
```json
{
  "signer_id": "org_abc123",
  "signer_name": "Acme Corp",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMCo...\n-----END PUBLIC KEY-----",
  "public_key_algorithm": "Ed25519",
  "key_id": "key_xyz789",
  "issued_at": "2025-01-15T00:00:00Z",
  "expires_at": "2026-01-15T00:00:00Z",
  "revoked": false,
  "trust_anchor_type": "organization"
}
```

**Response (404 Not Found):**
```json
{
  "error": "SIGNER_NOT_FOUND",
  "message": "No trust anchor found for signer_id 'unknown_signer'"
}
```

**Special Cases:**
- `signer_id = encypher.public` → Returns Encypher's official public key (free tier signatures)
- `signer_id = demo-*` → Returns demo/test keys (non-production)

**Privacy Considerations:**
- Only returns public key and minimal metadata
- Does not expose org email, billing, or internal details
- Rate-limited to prevent enumeration attacks

---

## API Design: Optional TSA Integration

### Updated `POST /api/v1/sign` Request

Add optional `include_timestamp` parameter:

```json
{
  "text": "Content to sign...",
  "document_title": "My Document",
  "include_timestamp": true  // NEW - optional, default false
}
```

**Behavior when `include_timestamp: true`:**
1. After signing, call TSA (DigiCert or SSL.com) with hash of signature
2. Store `TimeStampToken` in `sigTst2` COSE header per C2PA spec
3. Return additional `timestamp_authority` field in response

**Updated Response:**
```json
{
  "success": true,
  "document_id": "doc_abc123",
  "signed_text": "...",
  "timestamp_authority": {
    "tsa_url": "http://timestamp.digicert.com",
    "timestamp": "2025-12-14T17:30:00Z",
    "token_hash": "sha256:abc123..."
  }
}
```

**Tier Restrictions:**
| Tier | TSA Access |
|------|------------|
| Free | ❌ Not available |
| Professional | ✅ Available (quota-limited) |
| Enterprise | ✅ Available (unlimited) |

**Latency Impact:** +50-150ms per request when enabled

---

## Next Steps (Post-PRD)

- [ ] Contact SSL.com for C2PA partnership pricing
- [x] Verify `encypher-ai` NFC normalization and `exclusions` field compliance — ✅ COMPLIANT (Dec 2025)
- [x] Design `/api/v1/public/trust-anchors/{signer_id}` endpoint — ✅ Implemented + Tested (Dec 2025)
- [x] Design optional TSA integration for `/api/v1/sign` — ✅ Designed (Dec 2025)
- [x] Create new PRD for PDF signing support — ✅ Created `PRDs/CURRENT/PRD_PDF_Signing_Support.md` (Dec 2025)

### 3.0 Testing & Validation

- [x] 3.1 Unit tests passing — ✅ pytest
- [x] 3.2 Integration tests passing — ✅ pytest
- [x] 3.3 Validate-manifest tasks 1.1-1.4.3 passing — ✅ pytest
- [x] 3.4 Create-manifest tasks 1.5.1-1.5.4.1 passing — ✅ pytest
- [x] 3.5 Create-manifest -> sign -> verify flow passing — ✅ pytest
- [ ] 3.6 Frontend verification — ✅ puppeteer (not applicable)

## Success Criteria

- Endpoint exists and returns deterministic validation output for valid/invalid manifests.
- Schema validation works for both built-in schemas and caller-provided schemas.
- No cryptographic claims are made by this endpoint.
- All tests passing with verification markers.

## Completion Notes

(Filled when PRD is complete.)
