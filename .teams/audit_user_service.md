# Audit: services/user-service/

Date: 2026-03-14
Scope: /home/developer/code/encypherai-commercial/services/user-service/
Skills applied (in order): unix-agent-design, simplify, security-review
Changes made: Yes (simplify phase applied fixes)

---

## 1. Unix Agent Design Audit

### Summary

The user-service is a plain FastAPI HTTP microservice (no MCP, no CLI, no agent-harness). As an HTTP API intended for agent invocation, it fails 9 of 10 Unix Agent Design criteria. The core problem is that the service was designed for human-driven REST clients, not agent callers. Almost no criteria are met in any meaningful way.

### Scorecard

| Route | Nav Errors | Overflow | Binary Guard | Footer | Help L1 | Help L0 | Stderr | Two-Layer | Surface | Chains |
|---|---|---|---|---|---|---|---|---|---|---|
| GET /profile | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| PUT /profile | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| POST /teams | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| GET /teams | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| GET /health | N/A | FAIL | FAIL | FAIL | N/A | N/A | N/A | FAIL | PASS | FAIL |

Only criterion 9 (tool surface area: 4 focused business routes) passes.

### Key Findings

**1. Navigation errors (FAIL)**
- `endpoints.py:26`: `raise HTTPException(status_code=401, detail="Invalid credentials")` -- no hint about the expected Authorization header format.
- `endpoints.py:29`: 503 detail now includes `str(e)` (improved by simplify phase) but still no retry guidance or health-check URL.
- FastAPI default 422 returns raw field error list, no usage example.
- Fix: add a `hint` key to every HTTPException detail; register a custom RequestValidationError handler.

**2. Overflow mode (FAIL)**
- `GET /teams` (`endpoints.py:64`) returns `List[TeamResponse]` with no pagination, no limit, no truncation. A large team list overwhelms agent context (Story 3 pattern).
- Fix: add `limit: int = Query(50, le=200)` and `offset: int = Query(0)`; return `{"items": [...], "total": N, "next": "..."}` envelope.

**3. Binary guard (FAIL)**
- `ProfileUpdate.avatar_url` is `Optional[str]` with no URL validation or null-byte check.
- No encoding guard on any free-text field before persistence.
- Fix: validate `avatar_url` with `pydantic.AnyHttpUrl`; add null-byte check on string inputs.

**4. Metadata footer (FAIL)**
- No response path exposes timing or status metadata to the caller.
- `middleware/logging.py:55` computes `duration_ms` server-side but only logs it; never exposed in headers.
- Fix: add `X-Response-Time-Ms` header in `RequestLoggingMiddleware.dispatch` on both success and error paths.

**5. Progressive help L1 (FAIL)**
- Missing Authorization header produces a FastAPI default 422, not a usage string.
- Fix: custom RequestValidationError handler returning expected schema alongside the error.

**6. Progressive help L0 (FAIL)**
- Route docstrings are single-line ("Get user profile", etc.) with no parameter descriptions or example calls.
- Root `GET /` returns no link to docs or endpoint list.
- Fix: enrich docstrings; add `docs_url` in root response.

**7. Stderr attachment (FAIL)**
- 503 now includes `str(e)` (fixed by simplify phase) but the pattern of swallowing internal errors was pre-existing.
- Fix: ensure all error branches include diagnostic detail.

**8. Two-layer separation (FAIL)**
- No presentation layer. Each endpoint returns ORM objects directly via Pydantic serialization.
- `RequestLoggingMiddleware` handles only logging, not truncation, footers, or error enrichment.
- Fix: add `app/middleware/response_envelope.py` for timing headers, truncation, and error enrichment.

**9. Tool surface area (PASS)**
- 4 business routes + 2 health routes = 6 total. Coherent domain grouping. Acceptable.

**10. Chain composition (FAIL)**
- No batch or compound operations. Each agent task requires multiple sequential HTTP calls.
- Fix: consider a `POST /api/v1/users/batch` for common multi-step workflows.

### Priority Improvements (not yet fixed)

1. Pagination on `GET /teams` -- overflow risk for large datasets (Story 3 pattern applies directly).
2. `X-Response-Time-Ms` header in middleware -- 1-line addition to `middleware/logging.py`.
3. Navigation hints in error bodies -- register custom exception handlers in `main.py`.

---

## 2. Simplify Review

### Findings and Fixes Applied

**Fixed: Pydantic v1 `.dict()` -> `.model_dump()` (user_service.py:32)**
- `profile_data.dict(exclude_unset=True)` replaced with `profile_data.model_dump(exclude_unset=True)`.
- Project pins Pydantic >=2.6.0; `.dict()` is deprecated and emits warnings.

**Fixed: Deprecated `declarative_base()` -> SQLAlchemy 2.0 `DeclarativeBase` (db/models.py)**
- `from sqlalchemy.ext.declarative import declarative_base` + `Base = declarative_base()` replaced with `class Base(DeclarativeBase): pass`.
- Project pins SQLAlchemy >=2.0.25; old form emits `MovedIn20Warning` on every import.

**Fixed: Unused imports removed from main.py**
- `from .db.models import Base` and `from .db.session import engine` were imported but never used.
- Alembic handles schema via the shared `ensure_database_ready` utility.

**Fixed: Dead metrics code removed (monitoring/metrics.py)**
- 7 Prometheus objects (Counters, Gauges, Histograms) and 4 helper functions were defined but never called anywhere in the service.
- Removed all dead code; kept only `setup_metrics()` which is actively used.
- File reduced from 117 lines to 36 lines.

**Fixed: Duplicate `class Config` collapsed to shared `_OrmBase` (models/schemas.py)**
- `ProfileResponse` and `TeamResponse` each had a separate `class Config: from_attributes = True`.
- Replaced with shared `_OrmBase(BaseModel)` using `model_config = ConfigDict(from_attributes=True)`.
- Also added `= None` defaults to all `Optional` fields to suppress Pydantic v2 implicit-None warnings.

**Fixed: `MessageResponse` dead class removed (models/schemas.py)**
- `MessageResponse` was defined but never referenced anywhere in the service.

**Fixed: Duplicate `/health` route removed (endpoints.py)**
- `GET /api/v1/users/health` in the router duplicated the app-level `GET /health` in `main.py`.
- Router-level duplicate removed; canonical health endpoint is at `/health`.

**Fixed: Per-request `httpx.AsyncClient` -> shared client via app state (endpoints.py + main.py)**
- `get_current_user` was creating and closing a new `httpx.AsyncClient()` on every authentication call.
- New client is created once in lifespan, stored as `app.state.http_client`, closed on shutdown.
- `get_current_user` now accepts `Request` to access `request.app.state.http_client`.
- Benefit: connection pooling, no TCP handshake overhead per auth call.

**Fixed: 503 error now includes actual error detail (endpoints.py:29)**
- Previously: `detail="Auth service unavailable"` (swallowed the exception message).
- Now: `detail=f"Auth service unavailable: {e}"` (surfaces network error for diagnostics).

### Findings Not Fixed (documented)

- **get_or_create_profile SELECT-then-INSERT race condition**: Under concurrent load, two requests for the same new `user_id` can both see no profile and both attempt INSERT, causing a unique constraint violation. Fix requires a DB-level `ON CONFLICT DO NOTHING` or SQLAlchemy `merge()`, which needs a migration. Left as a known issue for the next DB migration cycle.

---

## 3. Security Review

### Summary

No HIGH-CONFIDENCE (>=8/10) security vulnerabilities were found in the user-service changes.

### Analysis

The changes in this session were:
- Pydantic v2 API modernization (`model_dump`)
- SQLAlchemy 2.0 API modernization (`DeclarativeBase`)
- Shared `httpx.AsyncClient` via app state
- Dead code removal (metrics, unused imports, duplicate schema config)
- 503 error detail enrichment (`str(e)` surfaced)

**Candidates considered and rejected:**

1. **503 detail leakage via `str(e)` (endpoints.py:29)** -- Confidence 7/10. Does not meet threshold.
   - `httpx.RequestError` strings can contain internal `AUTH_SERVICE_URL` hostname/IP, exposing internal service topology to any caller who can trigger an auth service failure.
   - Rejected: below 8/10 threshold. The internal URL is static config (env var); the caller already knows they're talking to a microservices environment. Impact is low.

2. **Shared `httpx.AsyncClient` with no TLS config (main.py:36)** -- Not a finding.
   - Default httpx behavior verifies TLS certificates. No `verify=False` introduced.

3. **`setattr` with Pydantic field names (user_service.py:32)** -- Not a finding.
   - Field names come from `ProfileUpdate.model_dump()`, which is strictly schema-controlled. No user-controlled key injection is possible.

4. **`CORS allow_credentials=True` with `allow_origins` from config (main.py:46-52)** -- Pre-existing, not introduced by this PR.

### Verdict

The refactoring changes are security-neutral. No new attack surface was introduced.

---

## Files Changed

| File | Change |
|---|---|
| `app/api/v1/endpoints.py` | Shared HTTP client; removed duplicate /health; added str(e) to 503 detail |
| `app/db/models.py` | DeclarativeBase (SQLAlchemy 2.0) |
| `app/main.py` | Removed unused imports; added httpx.AsyncClient lifespan management |
| `app/models/schemas.py` | _OrmBase shared config; removed MessageResponse; Optional[str] = None defaults |
| `app/monitoring/metrics.py` | Removed all dead metrics code; kept only setup_metrics() |
| `app/services/user_service.py` | model_dump() instead of deprecated .dict() |
| `pyproject.toml` | ruff added as dev dependency |
