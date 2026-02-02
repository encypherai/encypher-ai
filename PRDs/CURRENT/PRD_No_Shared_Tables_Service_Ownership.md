# PRD: No Shared Tables — Service-Owned Data + API/Event Integration

**Status:** 🔄 In Progress
**Current Goal:** Task 1.1 — Establish the first service-owned contract (key-service no longer joins organizations)

## Overview
We will move to the long-term ideal microservices architecture where each service owns its data and **no service reads another service’s tables**. Cross-domain needs (org tier/features/certificates, membership roles, etc.) will be served via explicit internal APIs and/or events, eliminating schema drift outages caused by duplicated tables.

## Objectives
- Eliminate cross-service table duplication as a correctness dependency (no joins against “foreign” tables).
- Introduce explicit, versioned service-to-service contracts for identity/org context.
- Ensure production robustness: schema drift in one service DB cannot break other services.
- Provide a safe rollout strategy (feature flags, staged deploy, rollback).

## Tasks

### 1.0 Contract Definition (SSOT)
- [x] 1.1 Define v1 internal contract for key validation + org context composition
- [x] 1.2 Define internal auth-service endpoint(s) for org context retrieval (secured via `X-Internal-Token`)
- [ ] 1.3 Define deprecation plan for legacy `/api/v1/keys/validate` “full org context” payload

### 2.0 Implementation — First Vertical Slice
- [x] 2.1 Auth-service: Add internal org-context endpoint (no user token required; internal token only)
- [x] 2.2 Key-service: Add `/api/v1/keys/validate-minimal` (no `organizations` join); return key identity + permissions + organization_id/user_id only
- [x] 2.3 Enterprise-api: Compose auth context by calling key-service `validate-minimal` then auth-service internal org-context endpoint (feature-flagged)
- [x] 2.4 Add internal token wiring to enterprise-api config and callers
- [x] 2.5 Enterprise-api: bootstrap org row when composing org context (avoid signing key/template lookups failing due to missing local org record)
- [x] 2.6 Enterprise-api: auto-provision per-org encrypted signing key when missing (config-gated; default on)

### 3.0 Rollout / Backward Compatibility
- [ ] 3.1 Add feature flag `KEY_VALIDATION_V2=true|false` (default false) for safe rollout
- [ ] 3.2 Dual-read/dual-response period with metrics to compare legacy vs v2 outputs
- [ ] 3.3 Remove legacy behavior after verification window

### 4.0 Follow-on Migration (Other Services)
- [ ] 4.1 Verification-service: stop depending on key-service returning org tier/features; compose via auth-service as needed
- [ ] 4.2 Encoding-service: same
- [ ] 4.3 Analytics/billing/user services: remove duplicated tables and consume events/APIs

### 5.0 Testing & Validation
- [x] 5.1 Key-service unit tests passing — ✅ pytest
- [x] 5.1.1 Key-service: validate-key rollback+fallback when `organizations.certificate_pem` missing — ✅ pytest
- [x] 5.2 Auth-service unit tests passing — ✅ pytest
- [x] 5.3 Enterprise-api unit tests passing — ✅ pytest
- [x] 5.4 End-to-end smoke test: create key in dashboard, sign via enterprise-api — ✅ pytest (local e2e)

## Rollout Notes

### New Endpoints
- `auth-service`: `GET /api/v1/organizations/internal/{org_id}/context` (requires `X-Internal-Token`)
- `key-service`: `POST /api/v1/keys/validate-minimal` (public; returns minimal key context)

### Enterprise API Configuration
Set these environment variables:
- `COMPOSE_ORG_CONTEXT_VIA_AUTH_SERVICE=true`
- `INTERNAL_SERVICE_TOKEN=<shared secret>`

Deploy order:
1) auth-service
2) key-service
3) enterprise-api

## Success Criteria
- Key-service production can validate keys without any dependency on an `organizations` table existing or being up-to-date.
- Enterprise-api can authenticate and authorize using composed org context from auth-service.
- No 500s due to missing org schema columns in non-auth services.
- All tests passing with verification markers.

## Completion Notes
- Local E2E sign/verify via Traefik passes (`LOCAL_API_TESTS=true uv run pytest enterprise_api/tests/e2e_local`).
