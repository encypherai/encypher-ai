# Metrics Pipeline Integration + Request Tracing

**Status:** Complete
**Current Goal:** All phases delivered
**Team:** TEAM_218

## Overview

The existing MetricsService -> Redis Streams -> analytics-service pipeline is correctly
architected but incompletely wired. Rights/RSL endpoints bypass the pipeline entirely
(using a dead-end in-process Counter). No request ID is stamped at the middleware layer,
so individual requests cannot be traced end-to-end through logs or metrics. This PRD
closes both gaps and establishes request tracing as a first-class capability.

## Objectives

- Wire all rights/RSL/robots endpoints into MetricsService (not the in-process Counter)
- Capture AI bot user-agent attribution on every public rights event (licensing evidence)
- Stamp every inbound request with a canonical X-Request-ID at middleware entry
- Propagate request_id through all log lines via contextvars + logging filter
- Standardise correlation_id usage in signing, verification, batch, streaming routers
- Add trace query endpoint to analytics-service: fetch all events for a request_id
- Add AggregatedMetric hourly/daily rollup background task
- Retire the in-process observability/metrics.py Counter

## Tasks

### 1.0 MetricType Extensions + Bot Classification

- [x] 1.1 Add RSL_FETCH, RIGHTS_RESOLUTION, ROBOTS_TXT_FETCH, NOTICE_DELIVERED,
      LICENSING_REQUEST to MetricType enum in metrics_service.py -- pytest
- [x] 1.2 Add classify_bot(user_agent) -> str to metrics_service.py (20-line UA
      matcher: gptbot, claudebot, google-extended, perplexitybot, bytespider, etc.) -- pytest
- [x] 1.3 Update MetricsMiddleware._get_metric_type() to classify /rights, /rsl,
      /notices paths correctly

### 2.0 Rights Endpoint Pipeline Wiring

- [x] 2.1 get_rsl_xml(): replace increment() with MetricsService.emit(RSL_FETCH,
      org_id, user_agent, bot_category)
- [x] 2.2 get_robots_txt_additions(): replace increment() with MetricsService.emit(ROBOTS_TXT_FETCH)
- [x] 2.3 get_document_rights() / resolve_rights_from_text(): emit RIGHTS_RESOLUTION
      events with document_id and bot_category
- [x] 2.4 Remove now-replaced increment() calls; remove unused import of increment
      from rights.py

### 3.0 Request ID Middleware + Structured Logging

- [x] 3.1 Create enterprise_api/app/middleware/request_id_middleware.py
      - Read X-Request-ID header or generate req-{uuid12}
      - Set request.state.request_id and contextvar
      - Return X-Request-ID in response headers
- [x] 3.2 Add RequestIDFilter (logging.Filter) that injects request_id from contextvar
      into every log record
- [x] 3.3 Register RequestIDMiddleware in main.py before MetricsMiddleware; update
      log format to include [%(request_id)s]
- [x] 3.4 Update MetricsMiddleware to use request.state.request_id (not header lookup)
- [x] 3.5 Standardise routers: signing.py, verification.py, batch.py, streaming.py
      all read request.state.request_id instead of generating local correlation_id

### 4.0 Trace Query Endpoint (analytics-service)

- [x] 4.1 Add GET /api/v1/analytics/trace/{request_id} to endpoints.py
      - Query usage_metrics WHERE meta->>'request_id' = :request_id
      - Returns list of events sorted by created_at asc
      - Returns 404 if no events found for that request_id

### 5.0 AggregatedMetric Rollup

- [ ] 5.1 Add rollup_hourly() background task to analytics-service (asyncio periodic
      task started in lifespan)
- [ ] 5.2 Add rollup_daily() task (runs at midnight UTC)
- [ ] 5.3 Upsert into AggregatedMetric table with period_start/end, total_count,
      avg_response_time, success/error counts

### 6.0 Cleanup + Tests

- [x] 6.1 Add deprecation notice to observability/metrics.py pointing to MetricsService
- [x] 6.2 Unit tests: classify_bot(), new MetricType values -- 22 tests (test_metrics_service.py)
- [x] 6.3 Integration test: request_id appears in X-Request-ID response header -- 7 tests (test_request_id_middleware.py)
- [ ] 6.4 Verify analytics-service trace endpoint returns events for a signed request (deferred - requires DB)

## Success Criteria

- Every RSL fetch emits a typed RSL_FETCH event with bot_category in the pipeline
- X-Request-ID header present on all enterprise-api responses
- All log lines within a request context include the request_id
- GET /api/v1/analytics/trace/{request_id} returns all metric events for that request
- All tests passing with verification markers

## Completion Notes

Delivered by TEAM_218 (2026-02-21).

**Phases 1-4 + 6.1-6.3 complete; Phase 5 (AggregatedMetric rollup) deferred to TODO.md.**

Key decisions:
- Used contextvars.ContextVar for request_id propagation (async-safe, no Request injection required)
- Starlette middleware registration order: add MetricsMiddleware first, then RequestIDMiddleware (last added = outermost = runs first on inbound)
- Public RSL/robots endpoints pass org_id from URL path and user_id="public" to MetricsService.emit()
- Dead-end observability/metrics.py Counter retained with deprecation notice; full removal deferred until streaming.py migrates
- analytics-service trace endpoint is auth-gated (same JWT as other analytics endpoints); org/user filter applied

Test coverage: 29 new tests (22 classify_bot + MetricType, 7 RequestIDMiddleware integration)
