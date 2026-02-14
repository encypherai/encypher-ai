# Enterprise API — C2PA Managed Signing + SSL.com Path

**Status:** ✅ Completed
**Current Goal:** Completed — managed signing runtime + BYOK/reseller documentation delivered

## Overview

Encypher needs a cost-efficient C2PA signing strategy that avoids mandatory per-tenant certificate purchases while preserving compatibility with C2PA trust-list expectations. The near-term plan is to support a default Encypher-managed signing mode (single CA relationship, e.g., SSL.com) plus optional BYOK and optional tenant certificate resale mode. This PRD defines the minimum product, API, and runtime changes needed to ship the architecture safely.

## Objectives

- Establish an SSOT signing mode model that supports managed, BYOK, and reseller tenant certificate flows.
- Ensure default signing can run with Encypher-managed certificate material while preserving signer attribution transparency.
- Preserve existing BYOK capabilities and trust-list policy validation.
- Deliver test-covered behavior changes and documentation updates.

## Tasks

### 1.0 SSOT Signing Mode Model

- [x] 1.1 Define canonical signing modes and semantics (`managed`, `byok`, `managed_tenant_cert`) for organization-level runtime decisions.
- [x] 1.2 Add settings/config support for Encypher-managed signer material and signer identity.
  - [x] 1.2.1 Add config values for managed signer private key and certificate chain inputs.
  - [x] 1.2.2 Add config validation and safe fallback behavior when managed signer config is absent.
- [x] 1.3 Add a deterministic signing mode resolver utility to centralize mode selection logic.

### 2.0 Runtime Signing + Verification Wiring

- [x] 2.1 Update signing executor to support managed signer selection when mode resolves to `managed`.
- [x] 2.2 Ensure verification certificate resolution can resolve the managed signer public key/certificate identity.
- [x] 2.3 Preserve existing organization-certificate and BYOK resolution precedence.
- [x] 2.4 Keep trust-list / EKU / denylist controls intact for uploaded BYOK and tenant certificates.

### 3.0 API + Product Surface

- [x] 3.1 Expose effective signing mode and signer identity metadata in a customer-visible endpoint.
- [x] 3.2 Keep BYOK endpoints unchanged for backward compatibility while documenting new mode semantics.
- [x] 3.3 Document reseller mode as optional workflow (operational process + API expectations).

### 4.0 Testing & Validation

- [x] 4.1 Add unit tests for signing mode resolver and managed signer selection — ✅ pytest
- [x] 4.2 Add integration tests for sign + verify path under managed mode and BYOK mode — ✅ pytest
- [x] 4.3 Regression tests for trust-list policy behavior (EKU/denylist/TSA metadata) — ✅ pytest
- [x] 4.4 Lint/type validation for touched files — ✅ ruff ✅ mypy (where configured)
- [x] 4.5 Frontend verification — ✅ puppeteer (not applicable; backend/docs-only change)

## Success Criteria

- Organizations can sign successfully using Encypher-managed signing mode without per-tenant certificate onboarding.
- BYOK and tenant-certificate paths remain functional and policy-enforced.
- Verification resolves managed signer signatures correctly.
- No regression in existing C2PA trust-list hardening behavior.
- All tests passing with verification markers.

## Completion Notes

- Added managed signing SSOT settings and mode resolver (`managed`, `organization`, `byok`, `managed_tenant_cert`).
- Updated signing runtime to use Encypher-managed signer key + signer ID when mode resolves to `managed`.
- Updated certificate resolver cache so managed signer signatures resolve during verification.
- Extended `/byok/trusted-cas` response with `default_signing_mode` and `managed_signer_id` metadata.
- Documented signing-mode semantics and optional SSL.com reseller tenant-certificate workflow in README + BYOK docs.
- Verification markers:
  - ✅ pytest: `enterprise_api/tests/test_managed_signing_mode.py`
  - ✅ pytest: `enterprise_api/tests/test_byok_public_keys.py enterprise_api/tests/test_c2pa_trust_list.py`
  - ✅ ruff: touched Python files
  - ✅ mypy: touched Python files
