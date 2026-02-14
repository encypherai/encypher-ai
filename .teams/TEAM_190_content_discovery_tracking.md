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
- **DiscoveryService**: Full business logic with domain-mismatch detection (first domain = owned, subsequent new domains = external), domain summary upserts, alert tracking
- **`original_domain` field**: Stores the domain where content was originally signed/published. When provided, enables direct domain comparison instead of heuristic-based detection
- **New API endpoints**:
  - `GET /discovery/domains` — org-scoped domain summaries (where is my content?)
  - `GET /discovery/alerts` — unacknowledged external domain alerts
  - `POST /discovery/alerts/{id}/ack` — acknowledge an alert
  - `GET /discovery/events` — paginated discovery event list with external-only filter
- **Updated `POST /discovery`** — now writes to dedicated `content_discoveries` table alongside legacy `UsageMetric` for backward compatibility

### Chrome Extension
- **Non-optional discovery**: Removed `ANALYTICS_CONFIG.enabled` toggle; `const` instead of `let`; `SET_ANALYTICS_ENABLED` handler is now a no-op for backward compat
- **`originalDomain` in analytics events**: Extension now sends `original_domain` (from verify response) with discovery events for precise domain-mismatch detection
- **Screenshot-1 icon fix**: Chrome bar now shows checkmark icon instead of full logo
- **Privacy policy**: Added "Content Discovery Tracking (Always Active)" section with full disclosure

### Infrastructure
- **Root conftest.py**: Added `ANALYTICS_APP_PATH` and `analytics-service` handling in `pytest_collectstart` so analytics-service tests resolve `app` correctly

## Test Results
- **Discovery service tests**: 27/27 pass (test_discovery_service.py) — includes 4 new original_domain tests
- **Existing schema tests**: 12/12 pass (test_discovery_endpoint.py)
- **Chrome extension tests**: 42/42 pass (detector.test.js + editor-signer.test.js)

## Files Changed
- `services/analytics-service/app/db/models.py` — Added ContentDiscovery + DiscoveryDomainSummary models
- `services/analytics-service/alembic/versions/002_content_discoveries.py` — NEW migration
- `services/analytics-service/app/services/discovery_service.py` — NEW service with domain-mismatch detection
- `services/analytics-service/app/models/schemas.py` — Added DomainSummaryItem, DomainAlertItem, ContentDiscoveryItem, etc.
- `services/analytics-service/app/api/v1/endpoints.py` — Updated POST /discovery, added 4 new endpoints
- `services/analytics-service/tests/test_discovery_service.py` — NEW 27 tests (incl. original_domain)
- `services/analytics-service/conftest.py` — NEW root conftest for path resolution
- `integrations/chrome-extension/background/service-worker.js` — Made discovery non-optional
- `integrations/chrome-extension/PRIVACY.md` — Added discovery tracking disclosure
- `conftest.py` — Added analytics-service app path handling
- `PRDs/CURRENT/PRD_Content_Discovery_Tracking.md` — NEW PRD (complete)

## Suggested Git Commit Message
```
feat(analytics): content discovery tracking with domain-mismatch alerts

- Add dedicated content_discoveries + discovery_domain_summaries tables
- Add original_domain column for storing signer's publishing domain
- Implement DiscoveryService with domain-mismatch detection logic
- Support direct domain comparison when originalDomain is provided
- Add GET /discovery/domains, /alerts, /events endpoints for org dashboard
- Add POST /discovery/alerts/{id}/ack for alert acknowledgment
- Update POST /discovery to write to dedicated table (+ legacy compat)
- Make discovery analytics non-optional in Chrome extension
- Send originalDomain from verify response in extension analytics
- Fix screenshot-1 Chrome bar icon (checkmark instead of full logo)
- Update privacy policy with full discovery tracking disclosure
- Add 27 new discovery service tests (all pass)
- Fix root conftest.py to support analytics-service app resolution
```
