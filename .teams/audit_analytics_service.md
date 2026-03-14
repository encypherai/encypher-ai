# Audit Report: services/analytics-service/

**Date:** 2026-03-14
**Auditor:** Agent (three-skill pipeline: unix-agent-design, simplify, security-review)
**Scope:** `/home/developer/code/encypherai-commercial/services/analytics-service/` — all `.py` files, excluding `.venv/` and `node_modules/`.

---

## Skill 1: Unix Agent Design Audit

### Summary

This is a FastAPI HTTP service (not an MCP or CLI tool). The 10 Unix Agent Design criteria apply to its HTTP route handlers. The service has **no agent-harness wrapper, no metadata footers, no overflow protection, no binary guards, and no progressive help** — all FAIL. The surface area is fragmented across 21 distinct route handlers. Error messages lack concrete next-action hints.

### Tool Inventory

| Route Group | Nav Errors | Overflow | Binary Guard | Footer | Help L1 | Help L0 | Stderr | Two-Layer | Surface | Chains |
|---|---|---|---|---|---|---|---|---|---|---|
| metrics/usage/services/timeseries | PARTIAL | FAIL | FAIL | FAIL | FAIL | FAIL | PARTIAL | FAIL | FAIL | FAIL |
| activity/audit-events | PARTIAL | FAIL | FAIL | FAIL | FAIL | FAIL | PARTIAL | FAIL | FAIL | FAIL |
| discovery/* | PARTIAL | FAIL | FAIL | FAIL | FAIL | FAIL | PARTIAL | FAIL | FAIL | FAIL |
| admin/* | PARTIAL | FAIL | FAIL | FAIL | FAIL | FAIL | PARTIAL | FAIL | FAIL | FAIL |

### Key Findings

**1. Navigation errors [PARTIAL]**
- `endpoints.py:178` `"Failed to record metric"` — bare, no next action.
- `endpoints.py:129` `"Invalid authentication credentials"` — no token format hint.
- `endpoints.py:635` `"No events found for request_id: {request_id}"` — no suggestion for next query.
- Fix: Append `next_action` hints (e.g., which endpoint to call) to all error messages.

**2. Overflow mode [FAIL]**
- `get_activity_audit_events` allows up to 200 rows per page with no payload size cap.
- `get_time_series` can return 90 days * 24 hours = 2,160 data points in a single response.
- `get_analytics_report` aggregates stats + service metrics + time series in one call.
- No truncation, no temp-file write, no path-return, no overflow hint anywhere.
- Fix: Add payload size check; if bytes > ~50KB, write to temp file and return path + navigation hint.

**3. Binary guard [FAIL]**
- CSV export (`endpoints.py:453-466`) and JSON export (`endpoints.py:417-429`) serialize raw `meta` JSON field values (from external sources) with no null-byte or encoding sanitization.
- Fix: Add a sanitization pass over all string fields before export serialization.

**4. Metadata footer [FAIL]**
- Zero responses include timing or status tokens (`[OK | 42ms]` etc.).
- `RequestLoggingMiddleware` measures duration but does not expose it in response body or standardized header.
- Fix: Add `X-Response-Time-Ms` response header via middleware.

**5. Progressive help L1 [FAIL]**
- Missing `Authorization` header produces FastAPI's default 422 with schema validation detail — no usage string, no example call.
- Fix: Add custom exception handlers for 422 errors that include field-level hints and examples.

**6. Progressive help L0 [FAIL]**
- App description is `"Analytics and metrics microservice"` (`main.py:65`) — no command enumeration.
- Root `/` returns `{service, version, status}` — no listing of available routes.
- Fix: Add an endpoint index to `/` or `/api/v1/analytics` listing routes with one-line summaries.

**7. Stderr attachment [PARTIAL]**
- `RequestLoggingMiddleware` logs errors via structlog but does not attach them to HTTP responses.
- `except Exception:` at `endpoints.py:181` and `endpoints.py:611` silently swallows the root cause before raising a generic 500.
- Fix: Include an error code or truncated message in 500 responses.

**8. Two-layer separation [FAIL]**
- Presentation logic (response formatting, CSV/JSON serialization, error string literals) is woven directly into business endpoint handlers in `endpoints.py`.
- `RequestLoggingMiddleware` is a partial layer-2 for logging only.
- Fix: Extract a `response_layer.py` module with `format_response()`, `handle_overflow()`, and `make_error()` helpers.

**9. Tool surface area [FAIL]**
- 21 distinct route handlers. A unified `analytics`, `activity`, `discovery`, `admin`, `health` grouping with sub-command query params would reduce this to ~5.
- Fix: Group discovery CRUD under `/discovery` with an `action` query param; merge `/usage`, `/services`, `/timeseries` into `/report?include=...`.

**10. Chain composition [FAIL]**
- No pipe/sequence composition supported. Each endpoint is fully isolated.
- Fix: Add `?include=usage,services,timeseries` batch query support on `/report`.

### Priority Improvements

1. **Two-layer separation** (`endpoints.py` entire file): Extract `response_layer.py` with `make_error(detail, next_action, code)` and apply uniformly.
2. **Surface area consolidation** (`endpoints.py`): 21 routes is too fragmented. Group and merge.
3. **Exception swallowing** (`endpoints.py:181,611`): `except Exception:` must at minimum log the error and include an error code in the 500 response.
4. **429 Retry-After** (`endpoints.py:574-576`): Already fixed during simplify pass (added `Retry-After` header).
5. **Overflow guard on exports** (`endpoints.py:453-466`): Add hard row cap + streaming response hint.

### Patterns from Production

- **Story 3: 5000-line log -> context overwhelmed** (criterion 2): The `/activity/audit-events/export` endpoint with `days=90` and no pagination can return the entire 90-day audit log as a single CSV blob.
- **Story 2: pip install stderr dropped -> 10 blind retries** (criterion 7): `except Exception: pass` on the legacy metric path means an LLM agent sees a 202 success but the secondary write silently failed.
- **Story 1: PNG cat -> 20 iterations of thrashing** (criterion 3): The JSON/CSV export paths serialize raw `meta` dict content without sanitization; null bytes or binary-adjacent content from a corrupted upstream payload would return garbled content with no redirect hint.

---

## Skill 2: Simplify — Code Review and Cleanup

### Changes Made

All changes were verified with `uv run pytest` (94 tests, all passing) and `uv run ruff check --fix` (25 issues auto-fixed, 0 remaining).

**analytics_service.py**
- Extracted module-level `_user_or_org_filter(user_id)` helper — eliminates 3 duplicate inline closures that each re-imported `or_` and redefined the same OR filter pattern.
- Refactored `get_usage_stats` with shared `_sum_count`/`_count_rows` inner closures — eliminates 5 near-identical copy-paste query blocks.
- Refactored `get_activity_alert_summary` to push all aggregation to DB (`count()` calls) instead of loading the full table into Python with `.all()`. A hard cap of 1,000 rows is applied for the error-code fetch.
- Removed redundant `from sqlalchemy import or_` and duplicate `user_or_org_filter` closure from `_build_activity_query`.

**stream_consumer.py**
- Promoted `_coerce_int` from a nested function (redefined on every `_parse_metric` call) to a module-level helper.

**discovery_service.py**
- Moved `from datetime import timedelta` from inside `get_stats_for_org` body to the module-level import line.

**endpoints.py**
- Consolidated `_discovery_rl_store` + `_discovery_rate_limit` (duplicate sliding-window implementation) into the existing unified `_rl_store` + `_rate_limit` function. The discovery route now uses `_rate_limit(ip, "discovery", limit=100, window_sec=60)`.
- Extracted `_client_ip(request)` helper — removed 2 identical IP-extraction blocks from `record_pageview` and `record_discovery_events`.
- Added `Retry-After` header to all 429 responses.
- Fixed `except Exception: pass` in discovery endpoint — now `logger.warning("Legacy metric recording failed for discovery event: %s", exc)`.
- Fixed `except Exception: pass` for auth lookup — now `logger.debug("Auth lookup skipped for discovery event: %s", exc)`.
- Removed `api_key_id` field from `get_request_trace` response — the column does not exist in the `UsageMetric` SQLAlchemy model (would have raised `AttributeError` at runtime).
- Moved all function-body imports (`from sqlalchemy import func, distinct`, `from ...db.models import ContentDiscovery`) to top-level. Added `from ...db.session import get_db` which was missing from the import block.

**db/models.py**
- Removed dead `AggregatedMetric` model — never imported or used in any route or service.

**schemas.py**
- Removed dead `MessageResponse` schema — never imported or referenced anywhere.

**Import sort**
- ruff auto-fixed 25 import ordering issues across all modified files.

### Findings Not Fixed (Deferred)

- **N+1 in `get_service_metrics`**: The per-service loop fires 5N+1 DB queries. Flagged but not fixed — requires a GROUP BY CASE rewrite that would need new tests.
- **Surface area consolidation**: 21 routes is too many. Deferred — requires API contract coordination.
- **`get_discovery_stats` duplicates `DiscoveryService.get_stats_for_org`**: The endpoint re-implements discovery counting inline. Deferred — the schemas differ slightly and refactoring needs a dedicated PR.
- **httpx client per-request**: Both `get_current_user` and `record_discovery_events` create a new `httpx.AsyncClient()` per request. Should be a shared lifespan-managed client. Deferred — requires lifespan refactor.

---

## Skill 3: Security Review

### Summary

One high-severity, high-confidence finding. No other exploitable vulnerabilities were identified at or above the 0.80 confidence threshold.

---

### Vuln 1 (HIGH): Unauthenticated Organization Data Injection via `/discovery` Endpoint

**Files:**
- `services/analytics-service/app/api/v1/endpoints.py:681` (endpoint definition)
- `services/analytics-service/app/api/v1/endpoints.py:720-725` (record_batch call)
- `services/analytics-service/app/services/discovery_service.py:79` (event.organizationId written verbatim)

**Severity:** High
**Category:** authorization_bypass / data_injection
**Confidence:** 0.95

**Description:**
The `POST /api/v1/analytics/discovery` endpoint is public (no `get_current_user` dependency). It accepts a `DiscoveryBatchRequest` body whose events each carry a client-supplied `organizationId` field. The `DiscoveryService.record_batch` call passes these events directly to `record_discovery`, which writes `event.organizationId` verbatim into the `ContentDiscovery` table and upserts `DiscoveryDomainSummary` rows keyed on that same org ID. There is no check that the caller owns or is authorized to write records for the submitted `organizationId`. The optional JWT check only enriches the `organization_id` variable used for the legacy `UsageMetric` path — it does not gate or validate the `organizationId` values inside the event payloads passed to `record_batch`.

**Exploit Scenario:**
An attacker with no credentials sends:
```
POST /api/v1/analytics/discovery
Content-Type: application/json

{
  "events": [{
    "timestamp": "2026-03-14T00:00:00Z",
    "pageUrl": "https://evil.com/stolen-article",
    "pageDomain": "evil.com",
    "organizationId": "<victim-org-uuid>",
    "signerId": "<victim-signer-uuid>",
    "verified": true,
    "embeddingCount": 1
  }],
  "source": "chrome_extension"
}
```

This creates a `ContentDiscovery` row and upserts a `DiscoveryDomainSummary` attributed to the victim org. Concrete impacts:

1. **Alert suppression:** The attacker marks arbitrary external domains as "seen" for the victim org, suppressing legitimate domain-mismatch alerts that the org uses to detect content piracy.
2. **Alert flooding:** Submitting hundreds of events for attacker-chosen domains floods the victim org's `/discovery/alerts` queue with fabricated external domain alerts, causing alert fatigue.
3. **Dashboard poisoning:** The victim org's `/discovery/domains`, `/discovery/stats`, and `/discovery/events` endpoints display attacker-injected data as authoritative discovery history.
4. **`is_owned_domain` manipulation:** By racing the first-domain-seen heuristic, an attacker can mark an external domain as "owned" by the victim org, preventing future legitimate external-domain alerts for that domain.

**Recommendation:**
In `record_discovery_events` (`endpoints.py`), after resolving `organization_id` from the JWT, override or strip `organizationId` in each event before passing to `record_batch`:

```python
# After resolving organization_id from JWT auth:
sanitized_events = []
for event in batch.events:
    if organization_id:
        # Authenticated: use the server-verified org, ignore client claim
        sanitized_events.append(event.model_copy(update={"organizationId": organization_id}))
    else:
        # Unauthenticated: strip org claim entirely — cannot be trusted
        sanitized_events.append(event.model_copy(update={"organizationId": None}))

events_recorded = DiscoveryService.record_batch(
    db=db,
    events=sanitized_events,
    source=batch.source,
    extension_version=batch.version,
)
```

Alternatively, require authentication for any discovery event that carries an `organizationId` field, returning 401 if `organizationId` is set but no valid JWT is present.

---

### No Other High-Confidence Findings

The following were considered and excluded:

- **IP stored in pageview metadata** (`endpoints.py:605`): Client IP written to `metadata.ip` in the database. This is PII storage, but it is intentional (used for analytics) and not an injection or access-control vulnerability. Excluded as a hardening concern.
- **Role check trusts auth service response** (`endpoints.py:1185-1191`): `current_user.get("role")` and `is_super_admin` come from the auth service. Trusting the auth service is by design in a microservice architecture; this is not independently exploitable.
- **SQL injection via `ilike` patterns** (`analytics_service.py:434,453-514`): All query construction uses SQLAlchemy ORM parameterized queries. No raw SQL string interpolation. Not vulnerable.
- **Redis stream data injection** (`stream_consumer.py:276-317`): `_parse_metric` reads from a Redis stream. The stream is an internal broker, not a public endpoint. Assuming Redis is not directly attacker-accessible per the microservice threat model.

---

## Overall Recommendations (Priority Order)

1. **[SECURITY - HIGH]** Fix unauthenticated org data injection in `/discovery` endpoint — strip or override `organizationId` from client-supplied event payloads.
2. **[QUALITY]** Extract `response_layer.py` presentation module to enable uniform error formatting, overflow handling, and response footer across all endpoints.
3. **[QUALITY]** Fix N+1 query pattern in `get_service_metrics` — replace per-service sub-queries with a single `GROUP BY service_name` query.
4. **[QUALITY]** Consolidate `get_discovery_stats` endpoint to delegate to `DiscoveryService.get_stats_for_org()` rather than re-implementing DB queries inline.
5. **[QUALITY]** Create a shared `httpx.AsyncClient` lifespan dependency to replace per-request client instantiation in `get_current_user` and `record_discovery_events`.
6. **[UNIX-AGENT]** Add `?include=usage,services,timeseries` batch support to `/report` to enable chain composition.
7. **[UNIX-AGENT]** Add overflow guard (size check + temp file + path return) to the CSV/JSON export endpoints.
