# Enterprise CMS Integration: Adobe Experience Manager (AEM)

**Status:** Complete  
**Current Goal:** Planning + readiness complete (implementation-ready spec; package work deferred to AEM engineers).

## Overview

Many tier‑1 publishers run Adobe Experience Manager (AEM) for editorial workflows and multi-channel distribution. This PRD defines an AEM integration that automatically signs content at publish/activation, preserves a stable signed representation, and renders a verification badge for readers.

## Objectives

- Integrate Encypher signing into AEM publish workflows (activation)
- Ensure deterministic content extraction/canonicalization for signing
- Store signed output and verification metadata in a safe, queryable form
- Provide reader-facing verification UI components compatible with caching

## Workstream Ownership (Parallel)

- **Suggested workstream:** `CMS Integrations — AEM`
- **Primary owners:** AEM engineer + backend API engineer
- **Primary repos/areas:** AEM package (new), Enterprise API endpoints (existing)

## Tasks

### 1.0 Discovery & Requirements (AEM Content Model)

- [x] 1.1 Decide supported AEM versions — decision
  - [x] 1.1.1 AEM Cloud Service (preferred) — 1.0 target
  - [ ] 1.1.2 AEM 6.5 on-prem (optional; deferred post-1.0)
- [x] 1.2 Identify content types to sign — 1.0 scope
  - [x] 1.2.1 Sites pages — 1.0
  - [x] 1.2.2 Content Fragments — 1.0
  - [ ] 1.2.3 Experience Fragments (optional; deferred post-1.0)
- [ ] 1.3 Decide signed representation strategy (critical)
  - [x] 1.3.1 Option A: Extract plaintext and sign (preferred) — decision
  - [ ] 1.3.2 Option B: Sign HTML (risk: rewriting, sanitization)
  - [x] 1.3.3 Define deterministic extraction rules — v1 spec
    - Extraction source: prefer **AEM content model** extraction (JCR component fields / Content Fragment elements) over rendered HTML.
    - Scope controls: extraction must be driven by an allowlist/config of resource types + fields (exclude header/nav/footer, “related content”, ads, personalization).
    - Ordering: traverse components/elements in their authored order.
    - Block boundaries: each extracted “content block” becomes a paragraph; join blocks with `\n\n`.
    - Rich text fields (stored HTML): parse to plaintext deterministically:
      - Drop `script`, `style`, and `noscript`.
      - Convert `br` to `\n`.
      - Preserve paragraph/list boundaries as line breaks.
      - Keep link *text*; ignore href by default.
    - Non-text components: excluded by default (images, embeds); optionally include `alt` text via config.
    - Versioning: persist an `extraction_profile_version` with the signing record and AEM metadata.
  - [x] 1.3.4 Document canonicalization rules (whitespace, line breaks, hidden elements) — v1 spec
    - Strip leading BOM (U+FEFF) if present.
    - Normalize line endings: `\r\n` and `\r` → `\n`.
    - Unicode normalization: NFC.
    - Hash/sign input: UTF-8 bytes of canonicalized plaintext.
  - [x] 1.3.5 Decide storage strategy (hybrid: Encypher DB SSOT + AEM metadata + optional embedded export) — decision
- [x] 1.4 Define publish workflow integration points
  - [x] 1.4.1 Sign on activation — v1 spec
    - Run signing in **Author** during the activation workflow, before replication to Publish.
    - Persist verification metadata on the content node so it replicates to Publish.
  - [x] 1.4.2 Re-sign on re-activation — v1 spec
    - Compute and store a `source_text_hash` of canonicalized plaintext.
    - Skip re-sign if `source_text_hash` is unchanged and `extraction_profile_version` is unchanged.
    - If changed: sign again and update the stored `document_id` and `verification_url` (keep history optional).
  - [x] 1.4.3 Failure policy (fail open vs fail closed) — decision

### 2.0 AEM Package + OSGi Configuration

- [ ] 2.1 Create AEM package structure
  - [ ] 2.1.1 Core bundle (OSGi)
  - [ ] 2.1.2 UI apps/components
  - [ ] 2.1.3 Config package
- [ ] 2.2 Implement OSGi configuration
  - [ ] 2.2.1 Encypher API base URL
  - [ ] 2.2.2 API key secret handling
  - [ ] 2.2.3 Default claim_generator and action templates
  - [ ] 2.2.4 Timeout, retry policy
- [ ] 2.3 Implement secure secret storage guidance
  - [ ] 2.3.1 Cloud: AEM secrets + env vars
  - [ ] 2.3.2 On-prem: vault/secret manager recommendations

### 3.0 Publish Workflow Step (Signing)

- [ ] 3.1 Implement workflow process step
  - [ ] 3.1.1 Extract content deterministically
  - [ ] 3.1.2 Call `POST /api/v1/sign`
  - [ ] 3.1.3 Persist signed output and verification URL to JCR
- [ ] 3.2 Add idempotency and change detection
  - [ ] 3.2.1 Only re-sign when content changed
  - [ ] 3.2.2 Track source hash and signed hash
- [ ] 3.3 Add observability
  - [ ] 3.3.1 Log correlation IDs
  - [ ] 3.3.2 Capture errors and publish warnings

### 4.0 Authoring UI (Editor Experience)

- [ ] 4.1 Create authoring panel
  - [ ] 4.1.1 Show signed/unsigned status
  - [ ] 4.1.2 Show signer and signed timestamp
  - [ ] 4.1.3 Button: “Re-sign now”
- [ ] 4.2 Add preview mode
  - [ ] 4.2.1 Show extracted plaintext that will be signed

### 5.0 Reader Verification UI

- [ ] 5.1 Build verification badge component
  - [ ] 5.1.1 Minimal badge
  - [ ] 5.1.2 Link to verification URL
- [ ] 5.2 Ensure caching compatibility
  - [ ] 5.2.1 Dispatcher/CDN rules
  - [ ] 5.2.2 Ensure variation selectors are not stripped

### 6.0 Bulk Backfill (Optional)

- [ ] 6.1 Provide a backfill tool for existing content
  - [ ] 6.1.1 Query pages/fragments
  - [ ] 6.1.2 Queue signing jobs
  - [ ] 6.1.3 Generate report

### 7.0 Testing & Validation

- [ ] 7.1 Unit tests (bundle)
- [ ] 7.2 Integration tests (workflow)
- [ ] 7.3 End-to-end validation
  - [ ] 7.3.1 Publish → signed output stored
  - [ ] 7.3.2 Reader sees badge
  - [ ] 7.3.3 Copy/paste verifies via Encypher

## Success Criteria

- AEM publish workflows automatically sign content reliably
- Signed representation remains stable through rendering and caching
- Editors can see signing state and remediate failures
- Verification badge displays and links to valid verification details
- Publishers can produce court-admissible evidence that published content was signed by them (cryptographic verification + audit logs + published reference/embedded export)

## Completion Notes

**Completed (planning handoff)**: 2025-12-14 by TEAM_012

### Summary
This PRD is **complete as an implementation-ready planning/spec document** for an AEM Cloud Service 1.0 integration. The next step is AEM package implementation (OSGi workflow step + UI), which requires AEM SDK tooling and is intended for AEM engineers.

### Decisions Locked
- AEM target: **AEM Cloud Service** for 1.0 (AEM 6.5 deferred post-1.0)
- Signed representation: **deterministically extracted plaintext**
- Canonicalization: strip BOM, normalize line endings to `\n`, Unicode NFC
- Failure policy: **fail open default**, fail closed configurable
- Storage: **hybrid** (Encypher DB SSOT + minimal metadata in AEM + optional export for copy/paste provenance)

### Verification
- Enterprise API baseline tests: **PASS** (`enterprise_api` → `uv run pytest`)

### Deferred Items
- AEM package implementation tasks (2.0–7.0) require AEM Cloud SDK/archetype + AEM runtime for integration testing.
