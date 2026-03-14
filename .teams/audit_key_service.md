# Key Service Audit Report

Date: 2026-03-14
Scope: `services/key-service/` (excluding `.venv/`, `node_modules/`)
Skills applied: unix-agent-design, simplify, security-review

---

## 1. Unix Agent Design Audit

### Summary

The key-service is a FastAPI HTTP microservice (not an MCP server or CLI). All 10 criteria were applied to its HTTP route handlers. The service has no agent-harness wrapper, so no criteria auto-pass. The most critical gaps are the complete absence of metadata footers on any response path, bare error messages with no next-step navigation hints, no pagination on the list endpoint, and all presentation/error logic woven directly into handler functions rather than a shared layer.

### Scorecard

| Criterion | Score | Worst Endpoint |
|---|---|---|
| 1. Navigation errors | FAIL | All endpoints: bare "API key not found" with no hint |
| 2. Overflow mode | PARTIAL | GET / (list): no pagination, no cursor |
| 3. Binary guard | N/A | Service deals only in JSON |
| 4. Metadata footer | FAIL | No timing/status footer on any response path |
| 5. Progressive help L1 | FAIL | No usage string on invalid-arg errors |
| 6. Progressive help L0 | PARTIAL | Docstrings present but root GET / returns no endpoint index |
| 7. Stderr attachment | N/A | HTTP service; exception is analogue: 500s drop root cause |
| 8. Two-layer separation | FAIL | All error formatting woven into each handler |
| 9. Tool surface area | PASS | 10 RESTful routes on a single resource |
| 10. Chain composition | FAIL | No batch or composed operations |

### Priority Improvements (not implemented - audit findings only)

1. **Navigation errors** (`endpoints.py:258-540`): append a `hint` field to all 4xx/5xx responses pointing to the relevant endpoint. Most impactful for programmatic/agent callers.
2. **Two-layer separation**: extract a `make_error_response(status, message, hint)` helper to `app/core/response.py` and use it from all handlers.
3. **Overflow on list** (`endpoints.py:216-235`): add `limit`/`offset` query params. Unbounded org key lists can overwhelm callers.
4. **Root endpoint navigation** (`main.py:77-84`): return an endpoint index at `GET /` or link to `/docs`.
5. **Request ID on 500s** (`endpoints.py:209-212`): include a `request_id` in 500 responses for log correlation.

---

## 2. Simplify Review

### Findings and Fixes Applied

All fixes verified: `uv run pytest` passes 15/15 tests. `uv run ruff check` passes clean.

#### R2 - Dead Code Removed: `_ensure_user_has_organization`

**File:** `app/services/key_service.py` (was lines 241-256)
**Issue:** Method imported `text` from sqlalchemy, had a full docstring, and unconditionally returned `None`. Never called anywhere.
**Fix:** Method removed entirely.

#### R3 - Module-Level Import: `from sqlalchemy import text`

**File:** `app/services/key_service.py`
**Issue:** `from sqlalchemy import text` was repeated as a local import inside three separate method bodies (`create_key`, `verify_key_minimal`, `verify_key_with_org`).
**Fix:** Moved to module-level import (`key_service.py:8`). All three in-method imports removed.

#### Q1 - Hardcoded Superadmin UUID Moved to Config

**Files:** `app/core/config.py`, `app/services/key_service.py`
**Issue:** `SUPERADMIN_USER_IDS = {"a1621dd6-..."}` was a hardcoded set literal inside the hot-path `verify_key_with_org` method. This is stringly-typed, leaks a specific identity into library code, and cannot be changed without a code deploy.
**Fix:** Added `SUPERADMIN_USER_IDS: str = ""` env var to `config.py` with a `superadmin_user_ids_set` property that parses it as a comma-separated list into a set. `key_service.py` now uses `settings.superadmin_user_ids_set`. Deployments must set `SUPERADMIN_USER_IDS=a1621dd6-3298-473f-b2ad-232ca72c3df5` in their environment.

**config.py additions:**
```python
SUPERADMIN_USER_IDS: str = ""

@property
def superadmin_user_ids_set(self) -> set:
    """Parse SUPERADMIN_USER_IDS into a set for O(1) lookup."""
    return {uid.strip() for uid in self.SUPERADMIN_USER_IDS.split(",") if uid.strip()}
```

#### Q5 - Duplicated Request-State Boilerplate Extracted

**File:** `app/api/v1/endpoints.py`
**Issue:** Identical 3-line `if request is not None: request.state.{x} = ...` block appeared in both `validate_key_with_org` and `validate_key_minimal`.
**Fix:** Extracted to `_bind_key_context_to_request(request, context)` helper at module level. Both handlers now call the helper.

#### E6 - N+1 Query Fixed in `get_key_usage_stats`

**File:** `app/services/key_service.py`
**Issue:** `get_key_usage_stats` made two separate DB queries: one `COUNT(*)` for total, then a `GROUP BY endpoint` for per-endpoint breakdown.
**Fix:** Single `GROUP BY endpoint` query; `total_requests` is derived as `sum(requests_by_endpoint.values())`.

### Findings Noted But Not Fixed (out of scope or architectural)

- **R1** - `_DummyResult`/`_DummyDB` in tests: different row shapes serve different test scenarios; genuine reuse would require parameterization that obscures intent.
- **Q2** - Redundant `is_active`+`is_revoked` dual-flag: architectural issue requiring schema migration.
- **Q4** - `_normalize_tier_name` misleading name: functional but confusingly named; no behavior change needed.
- **Q6** - `KeyRotation.organization_id` nullable=False may fail for user-level keys: architectural issue; left for schema migration.
- **E1/E2** - `httpx.AsyncClient` per-request and sync httpx in async context: architectural refactor required.
- **E3** - Certificate fetch on every `verify_key_with_org` call: requires caching layer.
- **R4/R5** - `RequestLoggingMiddleware` and `setup_metrics` never registered: orphaned modules; leaving for owner to decide.

---

## 3. Security Review

### Summary

One HIGH-severity privilege escalation vulnerability found. No SQL injection, XSS, or authentication bypass found in the remaining changes.

---

### VULN 1 (HIGH): Privilege Escalation via Unrestricted Permission Self-Assignment

**Files:** `app/api/v1/endpoints.py:273-301`, `app/services/key_service.py:616`, `app/models/schemas.py:62-66`
**Confidence:** 9/10
**Category:** privilege_escalation / authorization_bypass

**Description:**
The `PUT /api/v1/keys/{key_id}` endpoint allows any authenticated user to replace their own key's `permissions` array with arbitrary values, including `"super_admin"`. `KeyService.update_key` writes the caller-supplied list directly to the database with no allowlist check. `verify_key_with_org` then evaluates `"super_admin" in key_permissions` to grant full enterprise-tier superadmin status.

**Exploit Scenario:**
1. Attacker creates a normal account and generates an API key.
2. Attacker calls `PUT /api/v1/keys/{key_id}` with `{"permissions": ["sign", "verify", "super_admin"]}`.
3. No server-side validation prevents this write.
4. Attacker calls `POST /api/v1/keys/validate` with their key.
5. `verify_key_with_org` returns `tier: "enterprise"`, `monthly_api_limit: -1` (unlimited), and all enterprise feature flags enabled.
6. All downstream services that use `/validate` for feature gating treat the attacker as an enterprise superadmin.

The same issue exists on `POST /api/v1/keys/generate`: the `ApiKeyCreate.permissions` field is also user-supplied with no server-side allowlist, so an attacker can inject `"super_admin"` at key creation time without needing to call the update endpoint at all.

**Recommendation:**
Add a server-side allowlist enforced in both `create_key` and `update_key`. Regular users should only be permitted to assign `{"sign", "verify", "read"}`. Any privileged permission (`super_admin`, `admin`, `merkle`) must require the caller to already be a superadmin.

Suggested fix in `key_service.py`:
```python
ALLOWED_USER_PERMISSIONS = {"sign", "verify", "read"}
PRIVILEGED_PERMISSIONS = {"super_admin", "admin", "merkle"}

# In create_key and update_key, before writing permissions:
if permissions is not None:
    requested = set(permissions)
    disallowed = requested & PRIVILEGED_PERMISSIONS
    if disallowed and not caller_is_superadmin:
        raise ValueError(f"Cannot assign privileged permissions: {disallowed}")
    permissions = list(requested & (ALLOWED_USER_PERMISSIONS | (PRIVILEGED_PERMISSIONS if caller_is_superadmin else set())))
```

The `generate_key` endpoint in `endpoints.py:174-179` already auto-adds `super_admin` for auth-service-verified superadmins, which is correct. The gap is that non-superadmin users can manually include it in their request body.

---

## Changes Made (Summary)

| File | Change |
|---|---|
| `app/services/key_service.py` | Removed dead `_ensure_user_has_organization` method; moved `from sqlalchemy import text` to module level; moved superadmin ID check to config; fixed N+1 query in `get_key_usage_stats` |
| `app/core/config.py` | Added `SUPERADMIN_USER_IDS` env var and `superadmin_user_ids_set` property |
| `app/api/v1/endpoints.py` | Extracted `_bind_key_context_to_request` helper; removed duplicated request-state blocks |
| `tests/test_validate_key_with_org.py` | Added `SUPERADMIN_USER_IDS` monkeypatch to superadmin identity test |

## Changes NOT Made (Require Follow-Up)

- No fix for the privilege escalation vulnerability (VULN 1) - requires product decision on allowlist design
- No pagination on list endpoint - architectural change
- No `httpx` client pooling - architectural refactor
- Orphaned `RequestLoggingMiddleware` and `setup_metrics` - owner decision
- `SUPERADMIN_USER_IDS` env var must be populated in all deployment environments that previously relied on the hardcoded UUID
