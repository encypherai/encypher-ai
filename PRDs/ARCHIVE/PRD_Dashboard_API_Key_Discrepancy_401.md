# PRD: Dashboard API Key Discrepancy + 401

**Status**: Complete
**Current Goal**: Fix API key list inconsistency in Dashboard and resolve 401 “Invalid API key” for newly created keys
**Team**: TEAM_133

---

## Overview
Users can create API keys in the Dashboard, but newly-created keys return `401 Invalid API key` when used against the API. Additionally, the Dashboard Overview shows multiple API keys while the API Keys page shows only the newly-created key. This PRD aligns UI data sources and ensures enterprise API auth properly validates key-service keys.

---

## Objectives
- Ensure Dashboard Overview and API Keys page use the same source-of-truth query and scope
- Ensure Enterprise API correctly validates key-service-issued API keys
- Avoid misleading `401 Invalid API key` when key-service is misconfigured/unreachable
- Add tests covering both behaviors

---

## Tasks

### 1.0 Investigation
- [x] 1.1 Reproduce / confirm discrepancy and 401 behavior — ✅ pytest
- [x] 1.2 Trace dashboard API key fetch paths (Overview vs API Keys page)
- [x] 1.3 Trace Enterprise API auth path (key-service validate + fallback)

### 2.0 Implementation
- [x] 2.1 Add tests for enterprise-api key-service validation behavior — ✅ pytest
- [x] 2.2 Align Dashboard Overview API key list with active organization scope — ✅ puppeteer
- [x] 2.3 Normalize `key_service_url` handling in enterprise-api (strip `/api/v1`, trailing slash) and improve failure semantics for key-service-formatted keys — ✅ pytest

---

## Success Criteria
- [x] Dashboard Overview shows the same key set as API Keys page for the selected organization — ✅ puppeteer
- [x] Newly created Dashboard API keys successfully authenticate with the API (key-service validate path) — ✅ pytest
- [x] Key-service URL misconfiguration no longer causes silent fallback + misleading 401 for key-service keys — ✅ pytest

---

## Completion Notes

- Dashboard Overview now fetches API keys with `organization_id` scope.
- Enterprise API normalizes key-service URL and avoids misleading 401s when key-service cannot validate new-style keys.
- Verified with ✅ pytest ✅ ruff ✅ dashboard e2e (puppeteer/node).
