# TEAM_218 - Metrics Pipeline Integration + Request Tracing

**Session Date:** 2026-02-21
**Branch:** feature/rights-management-system
**PRD:** PRDs/CURRENT/PRD_Metrics_Pipeline_Request_Tracing.md

## Status: COMPLETE

## Context

Two related gaps identified during TEAM_217 session:
1. Rights/RSL endpoints use a dead-end in-process Counter (observability/metrics.py)
   instead of the real MetricsService -> Redis Streams -> analytics-service pipeline.
   Bot attribution (which AI crawler is fetching RSL) is missing entirely.
2. No request-level tracing: requests generate local correlation_ids inconsistently,
   no middleware stamps X-Request-ID, log lines have no request context, no way to
   pull all events for a single failed request.

## Architecture Reference

Existing pipeline (correctly designed, incompletely wired):
  MetricsService.emit()
    -> asyncio buffer (1s flush)
    -> Redis Stream "encypher:metrics:events"
    -> StreamConsumer (analytics-service, consumer groups, ACK/retry)
    -> PostgreSQL usage_metrics + aggregated_metrics
    -> AnalyticsService (time series, audit log, export)

Dead-end (to be retired):
  observability/metrics.py Counter -> render_prometheus() -> /metrics (nothing scrapes it)

## Implementation Summary

### Phase 1: MetricType + Bot Classifier (metrics_service.py)
New MetricType values: RSL_FETCH, RIGHTS_RESOLUTION, ROBOTS_TXT_FETCH,
NOTICE_DELIVERED, LICENSING_REQUEST.

classify_bot(user_agent: str) -> str: maps known AI crawler UA strings to canonical
names: gptbot, claudebot, google-extended, perplexitybot, bytespider, meta, ccbot,
anthropic, openai, cohere, diffbot, amazonbot, bingbot, googlebot, python-sdk, unknown.

### Phase 2: Rights Wiring (api/v1/public/rights.py)
Replace increment("rsl_xml_requests") and increment("robots_txt_rsl_requests") with
MetricsService.emit() calls. Add RIGHTS_RESOLUTION events to get_document_rights()
and resolve_rights_from_text(). Pass org_id (from URL path), user_agent, bot_category,
request_id in metadata.

### Phase 3: Request ID Middleware (middleware/request_id_middleware.py)
- RequestIDMiddleware: reads X-Request-ID or generates req-{uuid12}. Sets
  request.state.request_id and a contextvars.ContextVar. Injects X-Request-ID
  into response headers.
- RequestIDFilter: logging.Filter that reads contextvar and adds request_id to
  every LogRecord.
- Registered in main.py before MetricsMiddleware.
- Log format updated to include [%(request_id)s].

### Phase 4: Router Standardisation
signing.py, verification.py, batch.py, streaming.py all changed to read
request.state.request_id (set by RequestIDMiddleware) instead of generating
local correlation_id = f"req-{uuid4().hex}".

### Phase 5: Analytics Trace Endpoint
GET /api/v1/analytics/trace/{request_id}: queries usage_metrics where
meta->>'request_id' = :request_id, returns sorted event list.

## Files Changed

- enterprise_api/app/services/metrics_service.py (new MetricTypes + classify_bot)
- enterprise_api/app/middleware/request_id_middleware.py (NEW)
- enterprise_api/app/middleware/metrics_middleware.py (use request.state.request_id)
- enterprise_api/app/main.py (register middleware, update log format)
- enterprise_api/app/api/v1/public/rights.py (MetricsService wiring, remove increment)
- enterprise_api/app/routers/signing.py (use request.state.request_id)
- enterprise_api/app/routers/verification.py (same)
- enterprise_api/app/routers/batch.py (same)
- enterprise_api/app/routers/streaming.py (same)
- enterprise_api/app/observability/metrics.py (deprecation notice)
- services/analytics-service/app/api/v1/endpoints.py (trace endpoint)
- TODO.md (entries added)

## Deferred

- AggregatedMetric rollup task (asyncio periodic task in analytics-service) - Phase 5
- Dashboard UI for trace lookup - future sprint

## Test Results

1211 passed, 58 skipped (full enterprise_api suite)
- 22 new tests in test_metrics_service.py (classify_bot, MetricType)
- 7 new tests in test_request_id_middleware.py (RequestIDMiddleware integration)

## Suggested Commit Message

```
feat(metrics): wire rights/RSL pipeline, add request tracing (TEAM_218)

MetricType extensions:
- Add RSL_FETCH, RIGHTS_RESOLUTION, ROBOTS_TXT_FETCH, NOTICE_DELIVERED,
  LICENSING_REQUEST to MetricType enum
- Add classify_bot() for AI crawler user-agent attribution
- Update MetricsMiddleware._get_metric_type for rights paths

Rights endpoint wiring:
- Replace dead-end increment() calls in rights.py with MetricsService.emit()
- RSL_FETCH events include org_id, bot_category, user_agent, request_id
- RIGHTS_RESOLUTION events on document rights lookups
- ROBOTS_TXT_FETCH events on robots-txt endpoint

Request tracing:
- New RequestIDMiddleware: stamps X-Request-ID on every request/response
- Uses contextvars to propagate request_id through entire call stack
- RequestIDFilter adds request_id to every log line in request context
- All routers (signing, verification, batch, streaming) standardised to use
  request.state.request_id instead of local correlation_id generation
- Deprecation notice on observability/metrics.py Counter

Analytics trace endpoint:
- GET /api/v1/analytics/trace/{request_id}: query all events for one request
```
