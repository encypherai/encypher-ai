# TEAM_185 — Consolidate verify + status subdomains

**Status:** In Progress
**Created:** 2026-02-13

## Objective
Consolidate `status.encypherai.com` into `verify.encypherai.com/status/...` so that:
1. No separate `status` subdomain is needed
2. The org_id is no longer exposed in public status list URLs
3. All public verification/status infrastructure lives under one subdomain + one service

## Changes
- `enterprise_api/app/config.py` — add `status_list_base_url` setting
- `enterprise_api/app/services/status_service.py` — use new base URL, update SSRF allowlist
- `enterprise_api/app/models/status_list.py` — update hardcoded `status_list_url` property
- `enterprise_api/app/services/unified_signing_service.py` — use `_build_verification_url` helper
- `enterprise_api/app/services/signing_executor.py` — already uses settings, no change needed
- `enterprise_api/app/routers/status.py` — update status list endpoint path
- `services/api-gateway/dynamic.yml` — route `/status/*` under verify host
- `services/verification-service/app/main.py` — add status list proxy/route
- `integrations/ghost-provenance/src/config.ts` — already correct (uses verify subdomain)
- All test files referencing `status.encypherai.com`
- All docs/READMEs referencing `status.encypherai.com`
- Dashboard support page

## Completion Notes

### Phase 1: Subdomain Consolidation
All `status.encypherai.com` references replaced with `verify.encypherai.com/status/...`.

### Phase 2: Opaque UUID URLs (privacy)
Replaced `org_id/list/{list_index}` in public status list URLs with opaque `StatusListMetadata.id` UUID.

**Old URL**: `https://verify.encypherai.com/status/v1/{org_id}/list/{list_index}`
**New URL**: `https://verify.encypherai.com/status/v1/lists/{uuid}`

Legacy endpoints kept for backward compatibility (hidden from OpenAPI schema).

25/25 directly-affected tests pass. 858/870 total suite passes (12 pre-existing failures unrelated).

### Files Changed

**Core infrastructure (enterprise_api):**
- `app/config.py` — added `status_list_base_url` setting (SSOT)
- `app/services/status_service.py` — SSRF allowlist → `verify.encypherai.com`; `_build_status_list_url` now accepts UUID; `allocate_status_index` passes `metadata.id`; `generate_status_list` accepts optional `list_id`; revoke/reinstate look up metadata UUID for cache invalidation
- `app/models/status_list.py` — `status_list_url` property uses `self.id` UUID
- `app/services/unified_signing_service.py` — added `settings` import; uses `settings.infrastructure_domain`
- `app/routers/status.py` — new `GET /status/lists/{list_id}` endpoint (UUID-based); legacy `GET /status/list/{org}/{index}` kept but hidden from OpenAPI; `get_document_status` looks up metadata UUID

**Routing / verification-service:**
- `services/api-gateway/dynamic.yml` — updated verify-portal comment
- `services/verification-service/app/main.py` — UUID-based proxy at `/status/v1/lists/{list_id}` + legacy proxy

**Tests (6 files):**
- All URL references updated to UUID-based pattern

**Documentation (9 files):**
- `enterprise_api/README.md`, `enterprise_api/docs/API.md`, `enterprise_api/docs/STREAMING_API.md`, `docs/api/C2PA_CUSTOM_ASSERTIONS_API.md`, `docs/architecture/SUBDOMAIN_MIGRATION_PLAN.md`, `PRDs/CURRENT/PRD_Enterprise_1.0_Launch.md`, `PRDs/CURRENT/PRD_Bitstring_Status_Lists.md`, `PRDs/ARCHIVE/PRD_Enterprise_API_C2PA_Security_Launch_Audit.md`

**Dashboard:**
- `apps/dashboard/src/app/support/page.tsx` — status page link updated

### Suggested Git Commit Message

```
feat: consolidate status subdomain + use opaque UUIDs for status list URLs

Phase 1: Eliminates the separate status.encypherai.com subdomain by
serving status lists under verify.encypherai.com/status/v1/...

Phase 2: Replaces org_id/list_index in public status list URLs with
opaque StatusListMetadata.id UUIDs for privacy (no org enumeration).

New URL: /status/v1/lists/{uuid}
Legacy:  /status/v1/{org_id}/list/{index} (kept, hidden from OpenAPI)

Changes:
- Add status_list_base_url setting to enterprise_api config (SSOT)
- Update SSRF allowlist from status.encypherai.com → verify.encypherai.com
- Refactor _build_status_list_url to use opaque UUID
- Add UUID-based status list endpoint + legacy backward-compat endpoint
- Add status list proxy endpoints to verification-service
- Update all test fixtures, docs, dashboard links, and PRDs

TEAM_185
```
