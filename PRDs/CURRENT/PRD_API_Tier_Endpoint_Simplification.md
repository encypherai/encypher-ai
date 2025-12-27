# PRD: API Tier + Endpoint Simplification (Coalition-First)

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Confirm final tier decisions (Merkle, webhooks, BYOK, custom assertions) and lock the public-facing endpoint contract.  
**Team:** TEAM_034

## Overview
We will simplify the public Enterprise API surface to a small, clear set of endpoints aligned with Encypher’s coalition-first GTM: frictionless Starter adoption, clear Professional upgrade drivers, and Business/Enterprise features that enable legal transformation (willful infringement) and AI licensing workflows. This work aligns tier promises (SSOT: `packages/pricing-config/src/tiers.ts`) with what is actually enforced in `enterprise_api`, while adding missing upgrade drivers (webhooks gating, customer-facing BYOK) and rights/license signaling for downstream AI consumption.

## Objectives
- Clarify and standardize the public-facing API contract (especially signing) with an explicit “basic” vs “advanced” path.
- Align tier gating enforcement with the published tier model (Starter/Professional/Business/Enterprise) and remove mismatches.
- Support publisher licensing workflows by embedding machine-readable rights/license signals in signed content and surfacing them in verification responses.
- Ensure BYOK (public-key trust anchors only) and revocation (per-document and per-key) are usable as customer-facing primitives.
- Preserve strong upgrade drivers without introducing unnecessary complexity for small publishers.

## Tasks

### 1.0 Product Decisions (Lock Contract)
- [ ] 1.1 Confirm final answers to `.questions/TEAM_033_api_tier_schema_questions.md` (lookup visibility, sentence storage behavior, Merkle positioning, team/audit tier, webhooks tier, endpoint shape, BYOK endpoint exposure)
- [ ] 1.2 Confirm tier policy for custom assertions:
  - [ ] 1.2.1 Business: can use built-in rights/license templates
  - [ ] 1.2.2 Enterprise: can create custom schemas/templates
- [ ] 1.3 Confirm Merkle business value positioning:
  - [ ] 1.3.1 Business+: Merkle encode + attribution + plagiarism endpoints
  - [ ] 1.3.2 Professional: allow advanced signing that *produces* sentence-level artifacts without enabling corpus search (if desired)

### 2.0 Public Endpoint Contract (DX Simplification)
- [ ] 2.1 Standardize signing surface area:
  - [ ] 2.1.1 `POST /api/v1/sign` = document-level C2PA signing (Starter+)
  - [x] 2.1.2 `POST /api/v1/sign/advanced` = sentence-level embeddings / advanced provenance (Professional+)
- [x] 2.2 Ensure `/batch/*` endpoints are strictly multi-document operations (Business+)
- [ ] 2.3 Define and document canonical “verify and scan” behavior:
  - [x] 2.3.1 `POST /api/v1/verify` scans for multiple embeddings and returns per-embedding verdicts
- [ ] 2.4 OpenAPI + SDK alignment:
  - [x] 2.4.1 Ensure aliases are represented cleanly (or deprecated) in OpenAPI
  - [ ] 2.4.2 Confirm SDK generation remains compatible (or intentionally break + regenerate)

### 3.0 Tier Gating Enforcement (Make Promises True)
- [ ] 3.1 Webhooks gating:
  - [x] 3.1.1 Enforce Business+ for webhook CRUD (strong upgrade driver)
  - [x] 3.1.2 Add/verify quota/limit semantics (webhook count, delivery attempts)
- [ ] 3.2 BYOK customer-facing endpoints:
  - [x] 3.2.1 Expose `/api/v1/byok/public-keys` (Business+)
  - [x] 3.2.2 Keep `/admin/public-keys` as internal/super-admin (or remove if redundant)
- [ ] 3.3 Custom assertion management gating:
  - [x] 3.3.1 Gate schema creation endpoints as Enterprise-only
  - [x] 3.3.2 Allow template usage selection (Business+) without enabling schema authoring
- [ ] 3.4 Merkle endpoints gating:
  - [ ] 3.4.1 Ensure `merkle_enabled` accurately maps to Business+ (or updated tier policy)
  - [ ] 3.4.2 Confirm quota types for encode/attribute/plagiarism match pricing config

### 4.0 Rights / License Signals (AI Licensing Workflow)
- [ ] 4.1 Align with `PRDs/CURRENT/PRD_Enterprise_Rights_Metadata_AI_Licensing.md` (this PRD is the authoritative spec for fields)
- [ ] 4.2 Implement built-in rights/license templates:
  - [ ] 4.2.1 “All rights reserved”
  - [ ] 4.2.2 “No AI training”
  - [ ] 4.2.3 “RAG allowed with attribution”
  - [ ] 4.2.4 “Real-time quotes allowed with attribution”
- [ ] 4.3 Signing integration:
  - [ ] 4.3.1 Allow selecting a rights template in `/sign` and `/sign/advanced`
  - [ ] 4.3.2 Embed rights signals into the manifest as standards-aligned assertions (and Encypher custom assertion only if necessary)
- [ ] 4.4 Verification integration:
  - [ ] 4.4.1 Surface extracted rights signals in `/verify` responses
  - [ ] 4.4.2 Ensure public verifier can return “what license applies” for AI companies

### 5.0 Revocation & Trust Anchors (Operational + Legal Requirements)
- [ ] 5.1 Per-document revocation:
  - [ ] 5.1.1 Confirm revocation is enforced during verification (status list check)
  - [x] 5.1.2 Ensure revocation status is visible in verification outputs
- [ ] 5.2 Per-public-key revocation:
  - [x] 5.2.1 Confirm revoked keys fail verification consistently
  - [ ] 5.2.2 Ensure key revocation reason is auditable (where appropriate)

### 6.0 Documentation Updates
- [ ] 6.1 Update `docs/guides/publisher-integration-guide.md` for:
  - [x] 6.1.1 `/sign` vs `/sign/advanced` contract
  - [ ] 6.1.2 Rights template usage and expected verifier outputs
  - [x] 6.1.3 BYOK customer-facing endpoints
  - [x] 6.1.4 Webhooks tier policy
- [x] 6.2 Ensure docs don’t claim features that are not enforced by tier

### 7.0 Testing & Validation
- [x] 7.1 Tier gating tests (Starter/Professional/Business/Enterprise) — ✅ pytest
- [ ] 7.2 Rights template embed + extract tests — ✅ pytest
- [ ] 7.3 BYOK public-key lifecycle tests (register/list/revoke) — ✅ pytest
- [ ] 7.4 Revocation verification behavior tests — ✅ pytest
- [x] 7.5 Lint + type checks — ✅ ruff
- [ ] 7.6 Frontend verification — ✅ puppeteer (if dashboard UI is updated)

## Success Criteria
- The public API contract is simple and unambiguous:
  - `POST /api/v1/sign` for basic signing
  - `POST /api/v1/sign/advanced` for advanced sentence-level capabilities
- Tier gating is consistent and matches tier promises (no “silent” enterprise features in lower tiers).
- Business customers can use rights/license templates and BYOK as customer-facing features.
- Enterprise customers can author custom assertion schemas/templates when needed.
- Verification returns clear rights/licensing signals and revocation status.
- All tests passing with verification markers (✅ pytest, ✅ puppeteer if applicable).

## Completion Notes
(Filled when complete. Include final endpoint contract, gating decisions, and links to updated docs/tests.)
