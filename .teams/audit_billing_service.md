# Billing Service Audit Report

**Scope:** `services/billing-service/` (excluding `.venv/`, `.ruff_cache/`)
**Date:** 2026-03-14
**Skills applied:** unix-agent-design, simplify, security-review

---

## 1. Unix Agent Design Audit

The billing service is a FastAPI HTTP microservice — not an MCP/CLI tool. All 10 criteria were applied to the HTTP route handlers.

### Summary

The service scored FAIL on 8 of 10 criteria. Most critically: no metadata footer on any response path, no overflow protection, no binary guard, no progressive help, and bare error messages with no navigation hints. Two-layer separation partially exists via middleware. The surface area (14 routes) is reasonable but not consolidated.

### Scorecard

| Criterion | Score | Key Finding |
|---|---|---|
| 1. Navigation errors | FAIL | All errors are bare strings. No next-action hints. |
| 2. Overflow mode | FAIL | No truncation; `/coalition` returns up to 50 DB rows; `/invoices` defaults to limit=100 with no pagination. |
| 3. Binary guard | FAIL | No null-byte/encoding check on any passthrough data. |
| 4. Metadata footer | FAIL | No timing token or status footer on any response. Middleware logs but never attaches to response. |
| 5. Progressive help L1 | FAIL | Invalid input returns bare error strings; valid values not listed. |
| 6. Progressive help L0 | PARTIAL | FastAPI auto-generates /docs; root endpoint omits link. Most routes have docstrings. |
| 7. Stderr attachment | N/A | HTTP service; no subprocess invocation. |
| 8. Two-layer separation | PARTIAL | RequestLoggingMiddleware handles request ID and timing; no presentation wrapper for error format or truncation. |
| 9. Tool surface area | PARTIAL | 14 routes; /checkout and /upgrade overlap in intent; internal routes share the main router file. |
| 10. Chain composition | FAIL | No batch endpoint; each call is fully isolated. |

### Priority Improvements

1. **`endpoints.py:289`, `:332`, `:371`** — Replace `except Exception:` (bare) with `except Exception as e: logger.error(...); raise HTTPException(500, detail=f"Internal error: {type(e).__name__}")`. Never swallow exceptions silently.
2. **`endpoints.py:140`, `:300`, `:256`** — Return valid option lists in error detail: `"Valid add-ons: [attribution_analytics, enforcement_bundle, ...]"`.
3. **`endpoints.py:621-686`** (`_query_content_coalition_earnings`) — This 65-line DB-cross-query function inside endpoints.py creates a raw SQLAlchemy engine bypassing the connection pool. Move to `billing_service.py` or a dedicated `coalition_service.py`.
4. **`middleware/logging.py:57`** — Add `X-Response-Time-Ms` header alongside `X-Request-ID` to make timing observable to API consumers.
5. **`main.py:86-92`** — Enhance root endpoint to include `{"docs_url": "/docs", "openapi_url": "/openapi.json", "health_url": "/health"}`.

---

## 2. Simplify Review

### Code Reuse Findings

- `_build_subscription_response` hand-rolled field-by-field copy replaced with Pydantic `model_validate` + tier derivation.
- `price_cache.py` `get_add_on_price_id` rebuilt the dict on every call; moved to `__init__`.
- `PLANS` legacy dict in `billing_service.py` (lines 79-86) maps all legacy tiers to identical "Free" values — dead state. Only used by `create_subscription` which is orphaned since subscriptions arrive via Stripe webhooks.
- `utils.py` re-imported `PyPDF2`/`docx2txt` inside `extract_text_from_file` on every call, shadowing module-level availability flags.

### Code Quality Findings

- Dead `create_upgrade_checkout` method in `stripe_service.py` removed.
- Dead `TierName.PROFESSIONAL`/`TierName.BUSINESS`/`TierName.STARTER` references in upgrade endpoint (would cause `AttributeError`) removed; upgrade endpoint rewritten for 3-tier model.
- Emoji log messages in `main.py` removed (ASCII-only per project rules).
- Manual month-end calculation at `endpoints.py:534-537` has an edge case bug (day 31 in a 30-day month raises `ValueError`) — not fixed in this pass (requires `dateutil` dependency decision).
- `except Exception as e: message=f"Failed to create checkout: {str(e)}"` leaks raw Stripe exception strings to API callers — noted, not fixed (architectural decision).

### Efficiency Findings

- Two sequential HTTP calls to coalition-service replaced with `asyncio.gather` for concurrent execution.
- Redundant `extract_text_from_file` call in both `verify_content_integrity` branches of `scan_directory` eliminated; reuses `text_content` already in scope.

### Tests Fixed

- `tests/test_stripe_webhooks.py` — Updated 5 stale test cases that asserted `"professional"`/`"business"` tier resolution (never implemented) and used `TierName.BUSINESS` (not in enum).
- `tests/test_internal_trials.py` — Updated 2 stale test cases using `TierName.BUSINESS` -> `TierName.ENTERPRISE`.

**Test result after fixes: 9/9 pass (was 2/9 before).**

---

## 3. Security Review

### CRITICAL: Authentication Bypass on Internal Trial Provisioning Endpoint

**File:** `services/billing-service/app/api/v1/endpoints.py:202-204`
**Severity:** HIGH | Confidence: 0.97
**Category:** `authentication_bypass`

**Description:**
The `/internal/trials` endpoint had a fail-open authentication guard. The outer check `if settings.INTERNAL_SERVICE_TOKEN:` was falsy when `INTERNAL_SERVICE_TOKEN=""` (the default), causing the entire token check to be skipped. Any unauthenticated caller could POST to the endpoint to provision arbitrary enterprise trial subscriptions for any `organization_id` / `user_id` combination.

**Exploit:**
```
POST /api/v1/billing/internal/trials
Content-Type: application/json

{"organization_id": "victim-org-id", "user_id": "attacker", "tier": "enterprise", "trial_months": 24}
```
No token required. Response: `{"success": true, "data": {"plan_id": "enterprise", "status": "trialing", ...}}`

**Fix applied (`endpoints.py:202-204`):** Inverted guard logic to fail-closed:
```python
if not settings.INTERNAL_SERVICE_TOKEN:
    raise HTTPException(status_code=503, detail="Internal endpoint not configured")
if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
    raise HTTPException(status_code=401, detail="Invalid internal token")
```

The endpoint now returns 503 when the token is not configured, and 401 when the wrong token is provided.

### Additional Notes (not exploitable in isolation)

- **`success_url`/`cancel_url` user-controlled** (`endpoints.py:262-263`, `:308-309`): Caller-supplied redirect URLs are passed to Stripe without application-level domain validation. Stripe's own allowlist typically mitigates this, but defense-in-depth would validate URLs against `settings.DASHBOARD_URL` prefix before passing to Stripe.
- **`return_url` user-controlled** (`endpoints.py:332-354`): Same pattern as above for the billing portal endpoint.
- **Cross-DB query in endpoint** (`endpoints.py:568`): `_query_content_coalition_earnings` constructs a new SQLAlchemy engine to a separate DB (`encypher_content`) at request time, bypassing the connection pool. The query itself is parameterized (safe from SQLi), but the engine creation creates a new connection per request when the coalition service is unreachable.

---

## Files Changed

| File | Change |
|---|---|
| `app/api/v1/endpoints.py` | Security fix (auth bypass), dead code removal (PROFESSIONAL/BUSINESS/STARTER tiers), _build_subscription_response rewrite, asyncio.gather for coalition, import asyncio |
| `app/main.py` | Emoji -> ASCII in log messages |
| `app/services/price_cache.py` | Build add-on price map once at __init__ |
| `app/services/stripe_service.py` | Remove dead create_upgrade_checkout method |
| `shared_libs/src/encypher_commercial_shared/core/utils.py` | Remove redundant per-call imports; eliminate duplicate extract_text_from_file calls in verify_content_integrity |
| `tests/test_stripe_webhooks.py` | Update stale tier assertions |
| `tests/test_internal_trials.py` | Replace TierName.BUSINESS with TierName.ENTERPRISE |

## Suggested Commit Message

```
fix(billing-service): close auth bypass on /internal/trials, remove dead tier code, improve efficiency

- Invert INTERNAL_SERVICE_TOKEN guard from fail-open to fail-closed; endpoint
  now returns 503 when token not configured and 401 on bad token
- Remove dead TierName.PROFESSIONAL/BUSINESS/STARTER references in upgrade
  endpoint (AttributeError at runtime); rewrite for current 3-tier model
- Remove dead StripeService.create_upgrade_checkout (never called)
- Replace sequential coalition-service HTTP calls with asyncio.gather
- Build add-on price map once at PriceCache.__init__ instead of per-call
- Eliminate redundant extract_text_from_file calls in verify_content_integrity
- Remove redundant per-call PyPDF2/docx2txt imports in extract_text_from_file
- Replace hand-rolled _build_subscription_response with model_validate
- Remove emoji from log messages (ASCII-only policy)
- Fix 7 stale tests (TierName.BUSINESS -> ENTERPRISE, tier assertions updated)

Tests: 9/9 pass (was 2/9)
```
