# PRD: Enterprise API C2PA Trust List Compliance Hardening

**Status**: Complete
**Current Goal**: Completed implementation and verification of trust-policy hardening for enterprise_api

## Overview

This PRD hardens `enterprise_api` C2PA trust handling to align with C2PA 2.x trust model expectations while keeping validation internally controlled where possible. Scope includes signer EKU enforcement, internally managed revocation denylist checks, and first-class handling of signer vs TSA trust list material.

## Objectives

- Enforce signer certificate EKU requirements for C2PA claim-signing trust decisions.
- Add internal revocation policy controls (serial/fingerprint denylist) that do not depend on live third-party checks.
- Support separate signer and TSA trust-list lifecycle metadata and refresh behavior.
- Expose trust metadata in BYOK endpoints for operational transparency.
- Preserve backward compatibility for existing certificate-chain validation call sites.

## Tasks

### 1.0 Trust Policy & Configuration

- [x] 1.1 Add config settings for trust policy controls — ✅ pytest
  - [x] 1.1.1 Add signer EKU OID config defaulting to C2PA claim-signing OID
  - [x] 1.1.2 Add internal revocation denylist config (serials + fingerprints)
  - [x] 1.1.3 Add TSA trust-list URL/pinning/refresh settings
- [x] 1.2 Add utility parsing helpers for denylist configuration

### 2.0 Validation Engine Hardening

- [x] 2.1 Add EKU validation in `validate_certificate_chain` — ✅ pytest
  - [x] 2.1.1 Reject leaf certs missing required EKU OID
  - [x] 2.1.2 Return deterministic error messages for policy failures
- [x] 2.2 Add internal revocation checks in chain validation — ✅ pytest
  - [x] 2.2.1 Reject leaf cert when serial is denylisted
  - [x] 2.2.2 Reject leaf cert when SHA-256 fingerprint is denylisted
- [x] 2.3 Add TSA trust-list store + metadata functions — ✅ pytest
  - [x] 2.3.1 Add separate TSA anchor loading/refresh path
  - [x] 2.3.2 Expose TSA trust-list metadata getter

### 3.0 API & Startup Wiring

- [x] 3.1 Update startup lifecycle to load signer and TSA trust lists — ✅ pytest
- [x] 3.2 Extend BYOK trust-list response with policy metadata — ✅ pytest
  - [x] 3.2.1 Report required signer EKUs
  - [x] 3.2.2 Report revocation policy mode and TSA metadata

### 4.0 Tests (TDD) and Validation

- [x] 4.1 Add failing unit tests for EKU requirements (red) — ✅ pytest
- [x] 4.2 Add failing unit tests for internal revocation denylist checks (red) — ✅ pytest
- [x] 4.3 Add failing unit tests for TSA trust-list metadata/refresh helpers (red) — ✅ pytest
- [x] 4.4 Implement code to make new tests pass (green) — ✅ pytest
- [x] 4.5 Run targeted enterprise_api regression tests — ✅ pytest
- [x] 4.6 Run repository Python quality gates relevant to touched code — ✅ ruff ✅ pytest

## Success Criteria

- `validate_certificate_chain` enforces required signer EKU policy.
- Revoked certificates can be blocked via internal denylist config without network dependency.
- Signer and TSA trust-list lifecycle metadata are tracked separately.
- Startup loads both trust stores (when configured) and fails safely in production.
- Existing trust-list tests pass plus new policy/regression tests.

## Completion Notes

- Completed by TEAM_194 on 2026-02-14.
- Added trust-policy configuration in `enterprise_api/app/config.py` for EKU requirements, signer/TSA trust-list refresh and pinning, and internal revocation denylist sources.
- Implemented EKU + internal revocation denylist enforcement and TSA trust-list lifecycle helpers in `enterprise_api/app/utils/c2pa_trust_list.py`.
- Updated startup trust initialization in `enterprise_api/app/main.py` to load signer + TSA trust stores and apply denylist policy.
- Updated BYOK trust-list response and certificate validation in `enterprise_api/app/routers/byok.py` to surface trust policy metadata and enforce configured signer EKU requirements.
- Added/expanded tests in `enterprise_api/tests/test_c2pa_trust_list.py` and `enterprise_api/tests/test_byok_public_keys.py`.
- Verification:
  - `uv run pytest enterprise_api/tests/test_c2pa_trust_list.py enterprise_api/tests/test_byok_public_keys.py -q` ✅
  - `uv run ruff check enterprise_api/app/config.py enterprise_api/app/utils/c2pa_trust_list.py enterprise_api/app/main.py enterprise_api/app/routers/byok.py enterprise_api/tests/test_c2pa_trust_list.py enterprise_api/tests/test_byok_public_keys.py` ✅
