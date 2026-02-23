# PRD: Cloudflare Logpush + AI Scraping Analytics

**Status:** Complete
**Team:** TEAM_226 — see `.teams/TEAM_226_cloudflare_logpush_ai_scraping_analytics.md`
**Branch:** feature/rights-management-system

## Current Goal
Implement passive AI bot detection via Cloudflare Logpush webhook ingestion, covering
all traffic (not just Encypher-signed content), and add explicit robots.txt bypass
detection by cross-referencing raw access logs against RSL OLP protocol checks.

## Overview
The existing AI crawler analytics system (ContentDetectionEvent + rights_service) only
captures events when a bot explicitly hits an Encypher-backed endpoint. Bots that crawl
without checking RSL or the rights API are invisible today. This PRD adds a server-side
log ingestion pipeline starting with Cloudflare Logpush, enabling detection of any bot
UA in access logs and flagging bots that bypass the robots.txt/RSL protocol.

## Objectives
- Publishers can connect their Cloudflare zone via a single webhook URL + shared secret
- All AI bot traffic in CDN logs is classified and stored as ContentDetectionEvent rows
- Bots that access content without prior RSL OLP token check are flagged as bypass events
- Analytics endpoints and dashboard reflect bypass counts and "Cloudflare Logpush" source
- System handles high-volume Logpush batches (100s of log lines per POST) without blocking

## Tasks

### 1.0 Database Layer
- [x] 1.1 Alembic migration `20260223_100000_add_cdn_integration_bypass_detection.py`
  - Create `cdn_integrations` table (id, org_id, provider, zone_id, webhook_secret, enabled, created_at, updated_at)
  - Add `robots_txt_bypassed BOOLEAN` column to `content_detection_events`
- [x] 1.2 SQLAlchemy model `enterprise_api/app/models/cdn_integration.py`
  - CdnIntegration: id (UUID PK), organization_id, provider (text, default "cloudflare"), zone_id, webhook_secret (hashed), enabled (bool), created_at, updated_at

### 2.0 Backend Service
- [x] 2.1 Update `enterprise_api/app/models/rights.py`
  - Add `robots_txt_bypassed = Column(Boolean, nullable=True)` to ContentDetectionEvent
- [x] 2.2 Create `enterprise_api/app/schemas/cdn_schemas.py`
  - CdnIntegrationCreate (provider, zone_id, webhook_secret)
  - CdnIntegrationResponse (id, provider, zone_id, enabled, created_at, webhook_url hint)
  - LogpushIngestResult (lines_received, bots_detected, bypass_flags, errors)
- [x] 2.3 Create `enterprise_api/app/services/logpush_service.py`
  - `parse_logpush_line(line: str) -> dict | None` -- parse Cloudflare NDJSON record
  - `_has_recent_rsl_check(org_id, bot_category, db) -> bool` -- RSL OLP cross-reference
  - `_get_rsl_respecting_categories(db) -> set[str]` -- DB lookup, cached per batch
  - `ingest_logpush_batch(org_id, body_bytes, db) -> LogpushIngestResult` -- main entry
- [x] 2.4 Create `enterprise_api/app/routers/cdn_integrations.py`
  - POST /cdn/cloudflare -- create/update integration config (auth required)
  - GET /cdn/cloudflare -- get current config (auth required)
  - DELETE /cdn/cloudflare -- remove integration (auth required)
  - POST /cdn/cloudflare/webhook/{org_id} -- receive Logpush (public, bcrypt auth)
- [x] 2.5 Register router in `enterprise_api/app/main.py`
- [x] 2.6 Update `enterprise_api/app/services/rights_service.py`
  - get_detection_summary: add robots_txt_bypass_count to return dict
  - get_crawler_summary: add bypass_count per crawler entry (via bypass_cnt query column)

### 3.0 Dashboard Frontend
- [x] 3.1 Update `apps/dashboard/src/lib/api.ts`
  - Add CdnIntegration types (CdnIntegrationCreate, CdnIntegrationResponse)
  - Add getCdnIntegration, saveCdnIntegration, deleteCdnIntegration methods
  - Add robots_txt_bypass_count to DetectionSummary type
  - Add bypass_count to CrawlerSummaryEntry type
- [x] 3.2 Update `apps/dashboard/src/app/ai-crawlers/page.tsx`
  - Add "cloudflare_logpush" to SOURCE_LABELS map
  - Add "Bypass Attempts" stat card (red when > 0, neutral when 0)
  - Show bypass_count column in crawler details table (red for non-zero)
  - Updated callout from waitlist to real feature description

### 4.0 Tests
- [x] 4.1 Create `enterprise_api/tests/test_logpush_service.py` -- 19/19 passed
  - test_parse_timestamp_* (4 cases)
  - test_parse_logpush_line_* (9 cases: valid, empty, malformed, skipped paths/methods)
  - test_ingest_* (6 cases: empty body, non-bot, bypass/no-bypass, unknown bot, multi-line)
- [x] 4.2 Create `enterprise_api/tests/test_cdn_integrations_router.py` -- 6/6 passed
  - test_get_cdn_integration_not_found
  - test_create_cdn_integration
  - test_webhook_missing_secret_rejected
  - test_webhook_invalid_secret_rejected
  - test_webhook_valid_secret_empty_body_accepted
  - test_webhook_no_integration_returns_401

## Success Criteria
- Cloudflare Logpush webhook endpoint ingests NDJSON batches and creates ContentDetectionEvent rows with detection_source="cloudflare_logpush"
- Bots with respects_rsl=True in KnownCrawler that bypass RSL are flagged with robots_txt_bypassed=True
- /analytics/detections returns robots_txt_bypass_count
- /analytics/crawlers returns bypass_count per crawler
- Dashboard ai-crawlers page shows "Bypass Attempts" stat and "Cloudflare Logpush" source
- All tests pass: uv run pytest tests/test_logpush_service.py tests/test_cdn_integrations_router.py

## Completion Notes
Completed 2026-02-23 by TEAM_226.

All 25 tests pass (19 logpush service + 6 router). Ruff clean.

New files:
- alembic/versions/20260223_100000_add_cdn_integration_bypass_detection.py
- app/models/cdn_integration.py
- app/schemas/cdn_schemas.py
- app/services/logpush_service.py
- app/routers/cdn_integrations.py
- tests/test_logpush_service.py
- tests/test_cdn_integrations_router.py

Modified files:
- app/models/rights.py (robots_txt_bypassed column on ContentDetectionEvent)
- app/services/rights_service.py (bypass stats in analytics + detection event insert)
- app/main.py (cdn_integrations router registered)
- apps/dashboard/src/lib/api.ts (CDN types + 3 API methods + updated DetectionSummary)
- apps/dashboard/src/app/ai-crawlers/page.tsx (Bypass Attempts card, Cloudflare source label, bypass column in table)
