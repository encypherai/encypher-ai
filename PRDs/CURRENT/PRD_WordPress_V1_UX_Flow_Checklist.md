# PRD: WordPress Plugin v1 UX Flow Checklist

## Status
Complete

## Current Goal
Close the remaining v1 user-flow gaps for WordPress signing + verification so non-technical editors can successfully configure, sign, update, and verify content without backend-level troubleshooting.

## Overview
This PRD focuses on UX flow hardening, not cryptographic core changes. The signing and provenance-chain engine is now functional; this work makes the end-user path clear and recoverable by improving onboarding clarity, verification state messaging, and update/re-sign feedback. The outcome is a practical v1 flow that reduces support burden and increases successful first-run completion.

## Objectives
- Provide clear onboarding and connection guidance in admin surfaces.
- Show actionable verification states and error messages instead of generic failures.
- Confirm users can understand when update operations produced a new provenance step.
- Add regression tests to prevent UX-flow behavior drift.
- Validate the full local WordPress flow manually after changes.

## Tasks

### 1.0 PRD Checklist Definition
- [x] 1.1 Create dedicated v1 UX flow PRD checklist in `PRDs/CURRENT`.
- [x] 1.2 Define acceptance criteria for onboarding, verify state messaging, and update/re-sign clarity.

### 2.0 Verification UX State Improvements
- [x] 2.1 Add explicit client-side mapping for common verify failure categories (invalid API key, no manifest, tampered, backend unavailable).
- [x] 2.2 Present user-facing guidance/CTA text per category.
- [x] 2.3 Keep existing successful verification and provenance chain rendering intact.

### 3.0 Admin/Flow Clarity Improvements
- [x] 3.1 Ensure public verify path does not fail due to stale configured API keys.
- [x] 3.2 Add minimal user-facing copy that clarifies update re-sign behavior (`c2pa.edited`) when prior provenance exists.

### 4.0 Automated Validation (TDD)
- [x] 4.1 Add/adjust contract tests for verify auth-header behavior and UX-message mapping presence.
- [x] 4.2 Task — ✅ pytest (`enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`).

### 5.0 Manual UX Validation
- [x] 5.1 Verify update on a signed post triggers re-sign and provenance chain increment.
- [x] 5.2 Verify frontend badge modal shows actionable message for expected failure states.
- [x] 5.3 Verify happy-path verification returns valid manifest summary + chain details.
- [x] 5.4 Task — ✅ manual local validation (`http://localhost:8888`).

## Success Criteria
- Editors can distinguish unsigned/tampered/config/auth/network failures from generic "no manifest" failures.
- Verify flow works even when an invalid API key is configured for public verify requests.
- Post updates on already signed content produce a new `c2pa.edited` step and provenance chain continuity.
- Contract tests pass and cover new UX-flow guardrails.
- Manual localhost flow is validated for sign, update, and verify paths.

## Completion Notes
- Implemented actionable verification failure mapping in frontend modal (`buildVerificationFailureHint`) with local-key guidance copy and distinct hints.
- Added explicit success summary copy for edited provenance updates: `Latest action: Edited (provenance chain updated)`.
- Preserved public verify behavior by only sending auth headers when auth is required in REST backend calls.
- Added/updated contract tests covering:
  - verify auth-header behavior
  - frontend failure-hint mapping presence
  - frontend edited-action copy presence
- Automated verification:
  - ✅ `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` (23 passed)
- Manual + UI verification:
  - ✅ Runtime post-update check on post `91` showed `c2pa.edited` re-sign and changed `instance_id`.
  - ✅ Puppeteer check (localhost post page) confirmed success modal includes `Latest action:` and `Edited (provenance chain updated)`.
  - ✅ Puppeteer-injected failure response confirmed invalid-key hint copy includes `Invalid API key detected` and local E2E key guidance.
