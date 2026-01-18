# PRD: API Schema Rebrand

**Status:** 🔄 In Progress  
**Current Goal:** Task 3.2 — Regenerate SDKs from updated OpenAPI schema.

## Overview

We will rebrand the Enterprise API endpoint schema to a clearer, more intuitive naming convention for users. Because the API is not yet in use, we can make breaking changes to simplify routes, align streaming endpoints with their parent actions (sign/chat), and ensure consistency across SSE and WebSocket workflows.

## Objectives

- Establish a clear, user-friendly endpoint naming convention across signing, streaming, verification, and chat.
- Align streaming and session endpoints with their parent actions (e.g., sign + chat) for discoverability.
- Update backend routes, SDK/OpenAPI, and dashboard playground to reflect the new schema.
- Update documentation and examples to match the new contract.
- Ensure tests and linting pass after the rebrand.

## Tasks

### 1.0 Product Decisions (Lock Contract)
- [x] 1.1 Choose canonical naming scheme for signing + streaming endpoints
- [x] 1.2 Decide OpenAI-compatible chat path naming (e.g., `/chat/completions` vs `/chat/stream`)
- [x] 1.3 Decide WebSocket path conventions (shared vs explicit `/ws` suffix)
- [x] 1.4 Confirm whether to keep any legacy aliases (or remove entirely)

### 2.0 Backend Route Updates
- [x] 2.1 Update streaming router paths to new schema
- [x] 2.2 Update chat router paths to new schema
- [x] 2.3 Update OpenAPI tags/descriptions for new paths
- [x] 2.4 Update or add backend tests for new routes

### 3.0 Client + SDK Updates
- [x] 3.1 Update dashboard playground endpoint catalog
- [ ] 3.2 Update SDK generation/OpenAPI references (if needed)
- [x] 3.3 Update examples and integration snippets

### 4.0 Documentation Updates
- [x] 4.1 Update `enterprise_api/README.md`
- [x] 4.2 Update `docs/company_internal_strategy/Encypher_API_Sandbox_Strategy.md`
- [x] 4.3 Update any API docs or integration guides referencing streaming endpoints

### 5.0 Testing & Validation
- [x] 5.1 Enterprise API tests passing — ✅ pytest
- [ ] 5.2 Lint/type checks passing — ✅ ruff (mypy missing)
- [x] 5.3 Dashboard tests passing — ✅ npm test:e2e
- [ ] 5.4 Frontend verification — ✅ puppeteer (if UI changes)

## Success Criteria

- New endpoint schema is consistent and documented across backend, docs, and dashboard.
- No stale references to old endpoint names remain.
- All tests pass with verification markers.

## Completion Notes

(Filled when complete.)
