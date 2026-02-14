# PRD: Enterprise API C2PA Doc Sync and Conformance Readiness

**Status**: Complete
**Current Goal**: Completed SSOT doc-sync for C2PA trust-policy hardening and conformance-readiness guidance

## Overview

This PRD synchronizes SSOT documentation with the implemented C2PA trust-policy hardening in `enterprise_api`. It also adds clear conformance-readiness guidance so teams can distinguish implemented technical controls from formal C2PA Conformance Program requirements.

## Objectives

- Update Enterprise API docs to reflect new trust-policy controls (EKU, denylist, TSA trust list).
- Ensure `/api/v1/byok/trusted-cas` response documentation includes new metadata fields.
- Regenerate or otherwise align OpenAPI documentation artifacts with current API response models.
- Add explicit readiness notes on what is still required for C2PA trust-list/conformance participation.

## Tasks

### 1.0 PRD and Scope Definition

- [x] 1.1 Create doc-sync PRD in `PRDs/CURRENT` with SSOT-compliant structure
- [x] 1.2 Define concrete documentation files to update

### 2.0 Documentation Synchronization

- [x] 2.1 Update `enterprise_api/docs/BYOK_CERTIFICATES.md` for trust-policy metadata and validation behavior
- [x] 2.2 Update `enterprise_api/README.md` endpoint docs for `/api/v1/byok/trusted-cas` metadata fields and trust-policy config
- [x] 2.3 Add concise conformance-readiness note distinguishing technical readiness vs C2PA program/governance requirements

### 3.0 OpenAPI/Artifact Consistency

- [x] 3.1 Ensure `enterprise_api/docs/openapi.json` reflects current BYOK response model
- [x] 3.2 Confirm no stale references remain for trust-policy field names

### 4.0 Validation and Handoff

- [x] 4.1 Run targeted checks (tests and/or schema/doc validation) — ✅ pytest
- [x] 4.2 Update TEAM_194 session log with completed doc-sync work and commit message suggestion
- [x] 4.3 Mark PRD complete and archive to `PRDs/ARCHIVE`

## Success Criteria

- Docs accurately describe implemented EKU, internal denylist, and TSA trust-list behavior.
- `/api/v1/byok/trusted-cas` docs include `required_signer_eku_oids`, `revocation_denylist`, and `tsa_trust_list`.
- OpenAPI artifact is updated or explicitly synchronized with current response models.
- Readiness section clearly states remaining C2PA conformance/trust-list application requirements.

## Completion Notes

- Completed by TEAM_194 on 2026-02-14.
- Updated `enterprise_api/README.md` with BYOK trust-policy metadata documentation, TSA/EKU/revocation env configuration, and conformance-readiness clarification.
- Updated `enterprise_api/docs/BYOK_CERTIFICATES.md` with trusted-cas metadata fields and EKU/denylist troubleshooting guidance.
- Regenerated `enterprise_api/docs/openapi.json` from current FastAPI schema using local env overrides to ensure model alignment.
- Verification:
  - `uv run pytest enterprise_api/tests/test_c2pa_trust_list.py enterprise_api/tests/test_byok_public_keys.py -q` ✅
