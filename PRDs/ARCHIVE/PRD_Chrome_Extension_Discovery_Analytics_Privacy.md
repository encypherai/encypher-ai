# PRD: Chrome Extension Discovery Analytics Privacy Hardening

## Status: COMPLETE
## Current Goal: All checklist and implementation items complete

## Overview
We need a launch-ready analytics checklist and implementation for the Chrome extension that reliably reports where embeddings are found, especially when signed content appears on domains different from the original signing domain. The implementation must preserve user privacy by avoiding direct user identifiers and only collecting event data needed for provenance and abuse/distribution analysis. The final state must align UX copy, privacy docs, and backend ingestion behavior.

## Objectives
- Define and ship a concrete v1 analytics checklist for discovery events
- Capture domain-mismatch and embedding-context insights in extension analytics payloads
- Ensure payloads remain non-PII and privacy-minimized
- Keep discovery tracking behavior and user-facing disclosures consistent across UI/docs
- Cover changes with regression tests and end-to-end verification

## Tasks

### 1.0 Checklist and Event Contract
- [x] 1.1 Define required v1 discovery analytics fields and acceptance criteria
- [x] 1.2 Define explicit privacy constraints (no direct user identifiers, minimized URL/title handling)
- [x] 1.3 Map extension event fields to analytics-service schema contract

### 2.0 Extension Analytics Instrumentation
- [x] 2.1 Add robust origin-domain mismatch derivation in service worker event builder
- [x] 2.2 Add useful embedding context signals (verification status bucket, marker type, count, provenance context)
- [x] 2.3 Guard event construction to avoid malformed/PII-heavy payloads while preserving analysis value
- [x] 2.4 Keep queue/flush behavior stable under failures

### 3.0 Backend Ingestion and Classification
- [x] 3.1 Ensure analytics-service schema accepts new extension event fields where required
- [x] 3.2 Persist/derive external-domain classification with deterministic fallback logic
- [x] 3.3 Validate no user-identifying fields are required for ingestion

### 4.0 UX and Documentation Consistency
- [x] 4.1 Align extension UX copy/settings language with always-on discovery tracking behavior
- [x] 4.2 Update privacy/store-facing documentation for data minimization clarity

### 5.0 Verification
- [x] 5.1 Baseline test run before implementation — ✅ npm test (red baseline: 1 existing failing assertion)
- [x] 5.2 Add/adjust unit tests first (red), then implement (green) — ✅ node --test tests/discovery-analytics.test.js
- [x] 5.3 Run extension unit tests after implementation — ✅ npm test
- [x] 5.4 Run extension Puppeteer E2E checks after implementation — ✅ npm run test:e2e

## Success Criteria
- Discovery events include clear external-domain and embedding-context signals needed for v1 analytics
- Analytics payload remains privacy-safe with no direct user identifiers
- Extension and backend tests pass with coverage for new behavior
- UX/docs are truthful and consistent about discovery tracking behavior

## Completion Notes
- Added privacy-safe analytics event construction in extension service worker with URL sanitization (query/hash stripped), domain normalization, mismatch derivation, and content-context fields.
- Added discovery tracking for cached detections and immediate flush path for explicit cross-domain mismatch events.
- Propagated analytics context from detector to service worker (`discoverySource`, `visibleTextLength`, `embeddingByteLength`, and page domain metadata).
- Extended analytics-service discovery schema with optional mismatch/context fields and updated mismatch classification fallback logic for events without signer/org identifiers.
- Removed client IP persistence from legacy discovery metric metadata while preserving rate-limiting behavior.
- Aligned options UI copy with always-on discovery tracking and removed misleading analytics toggle wiring.
- Updated privacy and store listing docs to match actual always-on anonymous discovery analytics behavior.
- Fixed extension E2E popup-title expectation drift (`Verify` vs `Verifier`) and shadow-root scan regression path for LinkedIn interop mutation handling.
