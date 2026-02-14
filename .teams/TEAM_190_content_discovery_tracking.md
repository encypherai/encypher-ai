# TEAM_190 - Content Discovery Tracking

## Status: COMPLETE

## Summary
Enhance the existing content discovery analytics infrastructure to provide organizations with visibility into where their signed content appears across the web. The extension already reports discovery events; this work adds a dedicated DB model, domain-mismatch detection, org notification alerts, dashboard-facing endpoints, and makes discovery reporting non-optional.

## Key Findings
- Extension already sends `pageUrl` + `pageTitle` with `VERIFY_CONTENT` messages
- Service worker already has `trackEmbeddingDiscovery()` with batching + anonymous session IDs
- Analytics service already has `POST /discovery` and `GET /discovery/stats` endpoints
- Discovery events currently stored in generic `UsageMetric` table (JSON metadata)
- Missing: dedicated table, domain-mismatch detection, notifications, non-optional enforcement

## Changes Made

### Server-Side (Analytics Service)
- **New DB models**: `ContentDiscovery` (raw discovery events) and `DiscoveryDomainSummary` (aggregated per org+domain) with proper indexes for org-scoped queries
- **Alembic migration**: `002_content_discoveries.py` creates both tables with composite indexes
- **DiscoveryService**: Full business logic with 3-tier domain-mismatch detection, domain summary upserts, alert tracking
- **`original_domain` field**: Stores the domain where content was originally signed/published
- **`OwnedDomain` model + migration 003**: Org-configurable domain allowlist with wildcard support (`*.example.com`)
- **`domain_matches_pattern()`**: Wildcard domain matching using `fnmatch` (case-insensitive, supports `*.example.com`)
- **Domain-mismatch priority**: 1) Org's owned_domains allowlist → 2) originalDomain from event → 3) first-domain-seen heuristic
- **New API endpoints**:
  - `GET /discovery/domains` — org-scoped domain summaries (where is my content?)
  - `GET /discovery/alerts` — unacknowledged external domain alerts
  - `POST /discovery/alerts/{id}/ack` — acknowledge an alert
  - `GET /discovery/events` — paginated discovery event list with external-only filter
  - `GET /discovery/owned-domains` — list org's configured owned domains
  - `POST /discovery/owned-domains` — add a domain pattern (exact or wildcard)
  - `PATCH /discovery/owned-domains/{id}` — update pattern, label, or active status
  - `DELETE /discovery/owned-domains/{id}` — remove a domain pattern
- **Updated `POST /discovery`** — now writes to dedicated `content_discoveries` table alongside legacy `UsageMetric` for backward compatibility

### Chrome Extension
- **Non-optional discovery**: Removed `ANALYTICS_CONFIG.enabled` toggle; `const` instead of `let`; `SET_ANALYTICS_ENABLED` handler is now a no-op for backward compat
- **`originalDomain` in analytics events**: Extension now sends `original_domain` (from verify response) with discovery events for precise domain-mismatch detection
- **Screenshot-1 icon fix**: Chrome bar now shows checkmark icon instead of full logo
- **Privacy policy**: Added "Content Discovery Tracking (Always Active)" section with full disclosure

### Infrastructure
- **Root conftest.py**: Added `ANALYTICS_APP_PATH` and `analytics-service` handling in `pytest_collectstart` so analytics-service tests resolve `app` correctly

## Test Results
- **Discovery service tests**: 62/62 pass (test_discovery_service.py) — includes wildcard matching, CRUD, mismatch detection
- **Existing schema tests**: 12/12 pass (test_discovery_endpoint.py)
- **Chrome extension tests**: 42/42 pass (detector.test.js + editor-signer.test.js)
- **Total**: 116 tests, all passing

## Files Changed
- `services/analytics-service/app/db/models.py` — Added ContentDiscovery + DiscoveryDomainSummary models
- `services/analytics-service/alembic/versions/002_content_discoveries.py` — NEW migration
- `services/analytics-service/app/services/discovery_service.py` — NEW service with domain-mismatch detection
- `services/analytics-service/app/models/schemas.py` — Added DomainSummaryItem, DomainAlertItem, ContentDiscoveryItem, etc.
- `services/analytics-service/app/api/v1/endpoints.py` — Updated POST /discovery, added 4 new endpoints
- `services/analytics-service/tests/test_discovery_service.py` — 62 tests (discovery, CRUD, wildcards, mismatch)
- `services/analytics-service/alembic/versions/003_owned_domains.py` — NEW migration for owned_domains table
- `services/analytics-service/conftest.py` — NEW root conftest for path resolution
- `integrations/chrome-extension/background/service-worker.js` — Made discovery non-optional
- `integrations/chrome-extension/PRIVACY.md` — Added discovery tracking disclosure
- `conftest.py` — Added analytics-service app path handling
- `PRDs/CURRENT/PRD_Content_Discovery_Tracking.md` — NEW PRD (complete)

## Suggested Git Commit Message
```
feat(analytics): owned domain allowlist with wildcard matching

- Add OwnedDomain model + migration 003 for org domain allowlist
- Implement domain_matches_pattern() with fnmatch wildcard support
- Add CRUD endpoints: GET/POST/PATCH/DELETE /discovery/owned-domains
- Update domain-mismatch detection priority:
  1) Org's owned_domains allowlist (deterministic, wildcards)
  2) originalDomain from discovery event (direct comparison)
  3) First-domain-seen heuristic (fallback)
- Add 35 new tests: wildcard matching, CRUD, mismatch detection
- Total: 62 discovery service + 12 schema + 42 extension = 116 tests
```
