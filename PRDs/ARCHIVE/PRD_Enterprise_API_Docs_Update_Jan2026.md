# PRD: Enterprise API Docs Update (Jan 2026)

**Status:** 🟢 Complete
**Current Goal:** Align `enterprise_api/README.md` and the sandbox strategy doc with the current Enterprise API surface (public + verification service) and remove outdated endpoint descriptions.

## Overview
We need to keep customer-facing and internal strategy documentation in sync with the live Enterprise API. The README must match the public OpenAPI surface used by SDK generation and verification-service endpoints, while the sandbox strategy should reference the current demo endpoints and flows for sign/verify/advanced verification.

## Objectives
- Ensure `enterprise_api/README.md` endpoint tables match the current public OpenAPI + verification-service paths.
- Update the sandbox strategy doc to reflect current sign/verify/advanced flows and supported streaming endpoints.
- Remove or flag deprecated endpoints in documentation while keeping tables accurate.

## Tasks
- [x] 1.0 Audit current API surface
  - [x] 1.1 Confirm public OpenAPI endpoints (enterprise API + verification service)
  - [x] 1.2 Compare README endpoint tables with OpenAPI output
  - [x] 1.3 Identify sandbox strategy endpoint mismatches
- [x] 2.0 Update `enterprise_api/README.md`
  - [x] 2.1 Add missing endpoints and correct existing paths
  - [x] 2.2 Mark deprecated endpoints with guidance to replacement endpoints
  - [x] 2.3 Update streaming endpoint coverage and health routes
- [x] 3.0 Update sandbox strategy documentation
  - [x] 3.1 Align core endpoints list with current API paths
  - [x] 3.2 Reflect advanced verification flow (attribution/plagiarism)
  - [x] 3.3 Update streaming and embedding demo references
- [x] 4.0 Verification
  - [x] 4.1 Run Enterprise API doc contract tests — ✅ pytest
  - [x] 4.2 Validate sandbox strategy references

## Success Criteria
- README endpoint tables match the public OpenAPI + verification-service paths.
- Sandbox strategy doc reflects current endpoints and flows.
- Doc contract tests pass for enterprise_api.

## Completion Notes
- ✅ Updated Enterprise API README + sandbox strategy docs to match public OpenAPI surface.
- ✅ `uv run pytest enterprise_api/tests/test_readme_openapi_contract.py enterprise_api/tests/test_customer_docs_contract.py`
