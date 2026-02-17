# TEAM_197: Ghost webhook URL and connected UI

**Active PRD**: `PRDs/CURRENT/PRD_Hosted_Ghost_Webhook_Endpoint.md`
**Working on**: Return live Ghost webhook URL from backend, clarify webhook event mapping, improve connected-state dashboard UX
**Started**: 2026-02-15 16:15 UTC
**Status**: completed

## Session Progress
- [x] 1.1 — baseline verification — ✅ pytest
- [x] 1.2 — tests first for live webhook URL behavior (red -> green) — ✅ pytest
- [x] 2.1 — backend implementation
- [x] 2.2 — dashboard connected-state UX improvements
- [x] 2.3 — dashboard feature-gating hotfix
- [x] 3.1 — verification (pytest/lint + UI check) — ✅ pytest ✅ ruff ✅ npm lint ✅ npm type-check ✅ puppeteer(login-gate)
- [x] 3.2 — targeted test verification for dashboard feature-gating hotfix

## Changes Made
- `enterprise_api/app/routers/integrations.py`
  - `_build_webhook_url(...)` now returns absolute/live URL using request base URL fallback to `settings.api_base_url`.
  - Create/get/regenerate endpoints now pass `request` through response/url builders.
  - Masked webhook URL in GET response is now absolute as well.
- `enterprise_api/tests/test_ghost_integration.py`
  - Added TDD coverage for webhook URL generation with configured `api_base_url`.
  - Updated response schema fixture URLs to absolute webhook URL examples.
- `apps/dashboard/src/app/integrations/GhostIntegrationCard.tsx`
  - Clarified event labels: "Published post/page updated" with fallback note for Ghost versions showing "Post/Page updated".
  - Redesigned connected state to include dedicated webhook URL block + copy action.
  - Fixed overflow/readability issues for long masked API key and long webhook URLs.
  - Improved action layout wrapping for regenerate/disconnect confirms.
- `apps/dashboard/src/app/billing/page.tsx`: Fixed current-plan price label rendering so enterprise orgs without a fixed recurring amount render `Custom` instead of `Free`.
- `apps/dashboard/src/app/billing/page.tsx`: Removed eager `apiClient.getSubscription(...)` call from billing page load path to avoid expected/noisy `GET /api/v1/billing/subscription` 404s for orgs without Stripe-managed subscriptions.
- `apps/dashboard/src/app/audit-logs/page.tsx`: Expanded audit-log gate to allow super-admin access (`enterprise || isSuperAdmin`), reusing `apiClient.isSuperAdmin`.
- `apps/dashboard/src/components/layout/DashboardLayout.tsx`: Fixed enterprise nav filtering to keep enterprise-only items visible for super admins.
- `apps/dashboard/tests/e2e/feature-gating.super-admin-and-billing.test.mjs`: Added targeted regression coverage for billing label behavior, audit-log super-admin gating, and nav visibility.
- `apps/dashboard/tests/e2e/billing.subscription-intent.test.mjs`: Added targeted regression test to enforce billing page intent (tier sourced from org/session, no eager legacy subscription endpoint fetch).

## Blockers
- Could not fully validate connected-state UI via puppeteer because localhost session routes to sign-in page without authenticated test credentials.
- `npm run test:e2e` currently fails on pre-existing playground contract tests unrelated to Ghost integration changes.

## Handoff Notes
- Ghost webhook URL now copies as absolute/live URL from backend (`https://.../api/v1/integrations/ghost/webhook?token=...`) instead of relative path.
- Ghost event guidance now explicitly handles both naming variants for updated events.
- Connected card UX no longer overflows on long values and surfaces webhook URL as a first-class field.
- Targeted verification run only (per request):
  - `node --test tests/e2e/feature-gating.super-admin-and-billing.test.mjs tests/e2e/billing.enterprise-revshare.test.mjs` 
- Additional targeted verification for billing 404 fix:
  - `node --test tests/e2e/billing.subscription-intent.test.mjs tests/e2e/feature-gating.super-admin-and-billing.test.mjs` ✅
- Full `npm run test:e2e` was intentionally not re-run because it contains unrelated pre-existing failures.

## Suggested Commit Message
```
fix(ghost): return absolute webhook URLs and improve connected integration UX

Backend:
- Build Ghost webhook URLs as absolute/live URLs using request base URL,
  with api_base_url fallback for non-request contexts.
- Pass request through Ghost integration create/get/regenerate response builders
  so dashboard receives copy-ready target URLs for Ghost Admin.
- Add/adjust tests for webhook URL generation against configured api_base_url.

Dashboard:
- Clarify Ghost webhook event labels for version differences
  (Published post/page updated vs Post/Page updated).
- Redesign connected Ghost card to show configured webhook URL with copy action.
- Fix overflow/readability issues for long API key masks and long URLs.
- Improve action button wrapping/confirm states for regenerate/disconnect.

Verification:
- uv run pytest enterprise_api/tests/test_ghost_integration.py
- uv run ruff check enterprise_api/app/routers/integrations.py enterprise_api/tests/test_ghost_integration.py
- npm run lint (apps/dashboard)
- npm run type-check (apps/dashboard)
```

---

## Continuation (2026-02-15 22:24 UTC)

**Scope:** finish remaining PRD doc task (6.3) by ensuring Ghost integration endpoints are explicitly documented in Enterprise API endpoint reference.

### Additional Changes Made
- `enterprise_api/tests/test_readme_openapi_contract.py`
  - Added focused regression test `test_readme_documents_ghost_integration_endpoints`.
  - This test enforces documentation presence of:
    - `POST /api/v1/integrations/ghost`
    - `GET /api/v1/integrations/ghost`
    - `DELETE /api/v1/integrations/ghost`
    - `POST /api/v1/integrations/ghost/regenerate-token`
    - `POST /api/v1/integrations/ghost/webhook`
    - `POST /api/v1/integrations/ghost/sign/{post_id}`
- `enterprise_api/README.md`
  - Added new **Ghost CMS Integration Endpoints** table under endpoint reference with auth/tier/description rows for all Ghost routes.
- `PRDs/CURRENT/PRD_Hosted_Ghost_Webhook_Endpoint.md`
  - Marked task `6.3` complete.
  - Added completion notes summarizing doc + regression-test coverage.

### Verification
- [x] 6.3.1 Docs coverage test (red -> green) — ✅ `uv run pytest tests/test_readme_openapi_contract.py::test_readme_documents_ghost_integration_endpoints -q`
- [x] 6.3.2 Ghost integration regression suite — ✅ `uv run pytest tests/test_ghost_integration.py -q`
- [x] 6.3.3 Lint updated test file — ✅ `uv run ruff check tests/test_readme_openapi_contract.py`

### Notes
- `uv run pytest tests/test_readme_openapi_contract.py -q` still reports pre-existing README/OpenAPI drift outside Ghost scope (verify microservice and org/audit/status-list table mismatches). Not introduced by this change.

### Updated Suggested Commit Message
```
docs(api): add Ghost integration endpoint docs and enforce with regression test

- add Ghost CMS integration endpoint table to enterprise_api README endpoint reference
- add focused test asserting all Ghost integration routes are documented
- mark PRD_Hosted_Ghost_Webhook_Endpoint task 6.3 complete with completion notes

Verification:
- uv run pytest tests/test_readme_openapi_contract.py::test_readme_documents_ghost_integration_endpoints -q
- uv run pytest tests/test_ghost_integration.py -q
- uv run ruff check tests/test_readme_openapi_contract.py
```

---

## Continuation (2026-02-16 03:00 UTC)

**Scope:** improve dashboard audit-log troubleshooting fidelity so failed sign/verify operations expose actionable diagnostics (API key prefix, request ID, error details/stack trace) and filtering.

### Root Cause Summary
- Dashboard audit logs were sourced from auth-service organization/team audit entries, while richer sign/verify telemetry lived in analytics activity feed.
- Enterprise API metrics stream events stringified nested metadata using Python repr, which prevented analytics consumer JSON parsing and dropped structured fields.
- Metrics middleware emitted status/latency but did not enrich events with request ID, API key prefix, or standardized error payload details.

### Changes Made
- `apps/dashboard/src/app/audit-logs/page.tsx`
  - Switched data source to `/analytics/activity`.
  - Added status filter (all/errors/success), API key filter, and richer search fields.
  - Rendered troubleshooting metadata (request ID, error code/message/details) and expandable stack trace.
- `apps/dashboard/tests/e2e/analytics.contract.test.mjs`
  - Added contract assertions that audit logs page is wired for analytics telemetry and failure-detail labels.
- `apps/dashboard/tests/e2e/audit-logs.telemetry.smoke.test.mjs`
  - Added Puppeteer smoke test validating end-to-end rendering of API key filter and rich failure diagnostics.
- `enterprise_api/app/services/metrics_service.py`
  - Updated `MetricEvent.to_dict()` to JSON-encode dict/list metadata so analytics stream consumer can parse metadata reliably.
- `enterprise_api/app/dependencies.py`
  - Added safe API key prefix capture on `request.state` for telemetry enrichment.
- `enterprise_api/app/middleware/metrics_middleware.py`
  - Added metadata enrichment for request ID, method, API key prefix.
  - Added structured extraction of error code/message/details/stack from JSON error responses.
  - Added response body buffering path for streaming responses to preserve output while extracting error metadata.
- `enterprise_api/tests/test_metrics_service.py`
  - Added regression test for JSON metadata serialization.
- `enterprise_api/tests/test_metrics_middleware.py`
  - Added regression test for middleware telemetry enrichment on failed responses.
- `services/analytics-service/app/services/analytics_service.py`
  - Extended activity mapping metadata to include error code/message/details/stack.
- `services/analytics-service/tests/test_activity_feed_mapping.py`
  - Added regression test ensuring error metadata is surfaced in activity payloads.

### Verification
- ✅ `uv run pytest tests/test_metrics_middleware.py tests/test_metrics_service.py -q` (enterprise_api)
- ✅ `uv run pytest tests/test_activity_feed_mapping.py -q` (services/analytics-service)
- ✅ `uv run ruff check app/middleware/metrics_middleware.py app/dependencies.py tests/test_metrics_service.py tests/test_metrics_middleware.py` (enterprise_api)
- ✅ `uv run ruff check app/services/analytics_service.py tests/test_activity_feed_mapping.py` (services/analytics-service)
- ✅ `npm run lint -- --file src/app/audit-logs/page.tsx` (apps/dashboard)
- ✅ `node --test ./tests/e2e/analytics.contract.test.mjs` (apps/dashboard)
- ✅ `node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs` (apps/dashboard, Puppeteer)

### Notes / Constraints
- Dashboard page now reflects API telemetry events rather than org team-management audit rows; this intentionally aligns displayed failure diagnostics with activity timeline source-of-truth.
- Stack traces require upstream services to include stack/traceback in standardized error payloads for full fidelity.

### Comprehensive Suggested Commit Message
```
feat(audit-logs): surface rich sign/verify failure telemetry with api-key filtering

Dashboard:
- switch audit-logs page data source to analytics activity feed
- add status + API key filters and broader troubleshooting search
- render request ID, error code/message/details, and expandable stack trace
- add contract + Puppeteer smoke coverage for telemetry-driven audit UX

Enterprise API:
- JSON-encode metrics metadata before writing stream events
- capture safe API key prefixes in request state
- enrich metrics middleware metadata with request ID/method/api-key prefix
- extract structured error diagnostics from JSON error responses
- preserve response body while parsing streaming error payloads

Analytics Service:
- include error_code/error_message/error_details/error_stack in activity metadata mapping
- add regression tests for enriched activity payloads

Verification:
- uv run pytest tests/test_metrics_middleware.py tests/test_metrics_service.py -q
- uv run pytest tests/test_activity_feed_mapping.py -q
- uv run ruff check app/middleware/metrics_middleware.py app/dependencies.py tests/test_metrics_service.py tests/test_metrics_middleware.py
- uv run ruff check app/services/analytics_service.py tests/test_activity_feed_mapping.py
- npm run lint -- --file src/app/audit-logs/page.tsx
- node --test ./tests/e2e/analytics.contract.test.mjs
- node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs
```

### Follow-up (export + alert workflows completed)
- Implemented backend export + alert APIs on analytics service:
  - `GET /analytics/activity/audit-events/export` with `format=csv|json`
  - `GET /analytics/activity/audit-events/alerts`
- Added shared endpoint helpers for consistent time-window + filter parsing.
- Extended analytics service with reusable query builder and new methods:
  - `get_activity_export_rows(...)`
  - `get_activity_alert_summary(...)`
  - `_build_activity_query(...)` to keep filter parity with paginated endpoint.
- Added/extended schemas for alert responses:
  - `ActivityAlertCodeCount`
  - `ActivityAlertSummary`
- Added tests first for export/alerts service behavior:
  - `test_get_activity_export_rows_include_unified_fields`
  - `test_get_activity_alert_summary_aggregates_failures_and_error_codes`
- Wired dashboard audit logs UI to new workflows:
  - Export buttons: **Export CSV** / **Export JSON**
  - Alert widgets: **Failure Rate**, **Critical Failures**, **Top Error Codes**
  - Alert query uses `/analytics/activity/audit-events/alerts`

Verification:
- `uv run pytest tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py -q` (services/analytics-service)
- `uv run ruff check app/services/analytics_service.py app/api/v1/endpoints.py app/models/schemas.py tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py` (services/analytics-service)
- `npm run lint -- --file src/app/audit-logs/page.tsx` (apps/dashboard)
- `node --test ./tests/e2e/analytics.contract.test.mjs` (apps/dashboard)
- `node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs` (apps/dashboard, Puppeteer)

Comprehensive suggested commit message:
```
feat(audit-logs): add export and alert workflows for telemetry-backed audit events

Analytics service:
- add reusable activity query builder to ensure filter parity across list/export/alerts
- add get_activity_export_rows for flattened CSV/JSON exports
- add get_activity_alert_summary for failure-rate and top-error aggregations
- add GET /analytics/activity/audit-events/export with csv/json download support
- add GET /analytics/activity/audit-events/alerts with typed summary response
- add ActivityAlertCodeCount + ActivityAlertSummary schemas

Tests:
- extend activity filters test suite with export row and alert summary coverage
- keep unified contract mapping regression coverage for metadata fields

Dashboard:
- add audit export controls (Export CSV / Export JSON)
- add alert visibility cards (Failure Rate, Critical Failures, Top Error Codes)
- update contract assertions for export/alert UI labels

Verification:
- uv run pytest tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py -q
- uv run ruff check app/services/analytics_service.py app/api/v1/endpoints.py app/models/schemas.py tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py
- npm run lint -- --file src/app/audit-logs/page.tsx
- node --test ./tests/e2e/analytics.contract.test.mjs
- node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs
```

### Follow-up (full stack trace telemetry)
- Added unhandled-exception telemetry emission in metrics middleware so 500s always capture a full traceback string in `metadata.error_stack`, even when response payload does not include stack fields.
- Added regression test to assert traceback capture for raised runtime exceptions on sign routes.

Verification:
- `uv run pytest tests/test_metrics_middleware.py -q`
- `uv run ruff check app/middleware/metrics_middleware.py tests/test_metrics_middleware.py`

### Follow-up (requested features 1-5 + TS error fixes)
- Fixed dashboard TypeScript implicit-any issues in `audit-logs/page.tsx` by explicitly typing callback params in alert-summary parsing and render mappings.
- Implemented feature 1: server-side free-text search filter (`query`) across endpoint, metric type, request/error/event fields.
- Implemented feature 2: date-range UX with presets (24h/7d/30d) and custom `start_at`/`end_at` handling.
- Implemented feature 3: multi-select filters for event types and severities.
- Implemented feature 4: `has_stack` toggle for "only failures with stack trace".
- Implemented feature 5: saved filter views (localStorage-backed) with save/apply controls.
- Added backend filter parity for export endpoint so all active filters apply to CSV/JSON exports too.
- Added regression tests first for advanced filtering in analytics service.
- Updated contract + Puppeteer smoke checks to assert new control labels and mocked alert endpoint response.

Verification:
- `uv run ruff check app/services/analytics_service.py app/api/v1/endpoints.py tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py` (services/analytics-service)
- `uv run pytest tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py -q` (services/analytics-service)
- `npm run lint -- --file src/app/audit-logs/page.tsx` (apps/dashboard)
- `npm run type-check` (apps/dashboard)
- `node --test ./tests/e2e/analytics.contract.test.mjs` (apps/dashboard)
- `node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs` (apps/dashboard, Puppeteer)

### Follow-up (unified audit contract + filterable audit-events API)
- Added unified audit metadata mapping in analytics activity transformer:
  - `event_type`, `actor_type`, `actor_id`, `resource_type`, `resource_id`, `organization_id`, `severity`
  - retained operational diagnostics (`request_id`, `error_code`, `error_message`, `error_details`, `error_stack`)
- Added paginated audit-events query service + endpoint with filters:
  - Endpoint: `GET /analytics/activity/audit-events`
  - Filters: `api_key_prefix`, `endpoint`, `status`, `error_code`, `request_id`, `event_type`, `actor_id`, `start_at`, `end_at`, `days`, `page`, `limit`
- Updated dashboard audit logs to consume paginated audit-events endpoint and expose stronger visibility UX:
  - server-side page/status/api-key filtering
  - severity filter + severity badge column
  - event/actor metadata in details panel
  - request-ID correlation action
- Added tests first, then implementation:
  - `services/analytics-service/tests/test_activity_feed_filters.py`
  - expanded `services/analytics-service/tests/test_activity_feed_mapping.py`
  - updated dashboard contract + Puppeteer smoke coverage

Verification:
- `uv run pytest tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py -q` (services/analytics-service)
- `uv run ruff check app/services/analytics_service.py app/api/v1/endpoints.py app/models/schemas.py tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py` (services/analytics-service)
- `npm run lint -- --file src/app/audit-logs/page.tsx` (apps/dashboard)
- `node --test ./tests/e2e/analytics.contract.test.mjs` (apps/dashboard)
- `node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs` (apps/dashboard, Puppeteer)

Comprehensive suggested commit message:
```
feat(audit-logs): unify audit event contract and add filterable paginated audit-events API

Analytics service:
- add ActivityFeedPage schema for paginated audit activity responses
- extend activity mapping with unified audit metadata fields
  (event_type, actor/resource context, org id, severity)
- add get_activity_events query with audit-focused filters and pagination
- expose GET /analytics/activity/audit-events with filters for status, key, request/error/event context and time range
- add regression tests for unified metadata mapping and filter/pagination behavior

Dashboard:
- switch audit logs page to /analytics/activity/audit-events
- move status and API-key filtering server-side with paginated fetch
- add severity filter and severity badge column
- show event and actor context in details panel
- add request-id correlation action for troubleshooting chains
- update contract and Puppeteer smoke tests for new endpoint + visibility controls

Verification:
- uv run pytest tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py -q
- uv run ruff check app/services/analytics_service.py app/api/v1/endpoints.py app/models/schemas.py tests/test_activity_feed_mapping.py tests/test_activity_feed_filters.py
- npm run lint -- --file src/app/audit-logs/page.tsx
- node --test ./tests/e2e/analytics.contract.test.mjs
- node --test ./tests/e2e/audit-logs.telemetry.smoke.test.mjs
```
