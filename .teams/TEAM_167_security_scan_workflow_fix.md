# TEAM_167 — Security Scan Workflow, Ruff Lint Fixes & Security Audit

## Status: COMPLETE

## Summary

### Phase 1: CI Workflow Fixes
1. **CodeQL Action v3 → v4**: Updated `github/codeql-action/upload-sarif@v3` to `@v4` (v3 deprecated Dec 2026).
2. **GHAS upload failure**: Added `continue-on-error: true` to SARIF upload + table-format Trivy step for log visibility.

### Phase 2: Ruff Lint Fixes (9 errors → 0)
3. **F401** `DiscoveryEvent` unused import — removed from `services/analytics-service/app/api/v1/endpoints.py`
4. **F401** `ReedSolomonError` unused import — removed from `services/verification-service/app/utils/vs256_detect.py`
5. **F401** `pytest`, `MAGIC_PREFIX_LEN`, `_VS_CHAR_SET`, `_VS_TO_BYTE` unused imports — removed from `services/verification-service/tests/test_vs256_detect.py`
6. **F401** `pytest` unused import — removed from `services/verification-service/tests/test_zw_detect.py`
7. **UP042** `DemoRequestStatus(str, Enum)` → `DemoRequestStatus(StrEnum)` in `services/web-service/app/schemas/demo_request.py`
8. **F821** Undefined name `db` → `core_db` in `enterprise_api/app/api/v1/public/verify.py:288` (bug fix — was querying organizations table with nonexistent variable)

### Phase 3: Comprehensive Security Audit
Full local security analysis covering: dependency audit (pip-audit, npm audit), secret scanning (detect-secrets, grep), SQL injection analysis, JWT/auth review, CORS review, Dockerfile security, error message leakage, insecure deserialization check, SSRF analysis.

**Key findings:** 3 CRITICAL (committed secrets, hardcoded JWT default), 4 HIGH (CVEs, root containers, error leakage), 4 MEDIUM (dynamic SQL, ILIKE injection, shared tokens, baseline noise).

Full report: `docs/SECURITY_AUDIT_2026_02_11.md`

### Phase 4: Security Remediation
Fixes applied for 5 of the 11 findings:

1. **C3 FIXED** — Hardcoded `"supersecretkey"` JWT default in `dashboard_app/backend/app/core/config.py`
   - Replaced with `secrets.token_urlsafe(48)` for dev, `RuntimeError` if unset in production
2. **H1 FIXED** — `python-multipart` CVE-2026-24486 (path traversal)
   - Bumped to `>=0.0.22` in 4 pyproject.toml files
3. **H2 FIXED** — 12 production Dockerfiles running as root
   - Added `groupadd/useradd appuser` + `USER appuser` to all production Dockerfiles
4. **H3 FIXED** — ~60+ endpoints leaking `str(e)` in HTTP responses
   - All replaced with `logger.exception()` for full server-side stack traces + generic client messages
   - Affected 15 files across enterprise_api, dashboard_app, and all microservices
5. **M2 FIXED** — ILIKE wildcard injection in document search
   - Escaped `%` and `_` in user-supplied search input

**Remaining (not code fixes):**
- C1/C2: Committed `.env` secrets — private repo, recommend rotating keys
- M1: Dynamic SQL patterns — mitigated (parameterized), recommend ORM migration
- M3: Shared internal service token — recommend per-service tokens
- M4: detect-secrets baseline noise — recommend periodic audit

## Files Changed

### Phase 1-2 (CI + Lint)
- `.github/workflows/security-scan.yml`
- `services/analytics-service/app/api/v1/endpoints.py`
- `services/verification-service/app/utils/vs256_detect.py`
- `services/verification-service/tests/test_vs256_detect.py`
- `services/verification-service/tests/test_zw_detect.py`
- `services/web-service/app/schemas/demo_request.py`
- `enterprise_api/app/api/v1/public/verify.py`

### Phase 3 (Audit Report)
- `docs/SECURITY_AUDIT_2026_02_11.md` (NEW)

### Phase 4 (Remediation)
- `dashboard_app/backend/app/core/config.py` — C3 fix
- `dashboard_app/backend/pyproject.toml` — H1 fix
- `services/auth-service/pyproject.toml` — H1 fix
- `services/web-service/pyproject.toml` — H1 fix
- `tools/sign-verify-app/pyproject.toml` — H1 fix
- `enterprise_api/Dockerfile` — H2 fix
- `services/auth-service/Dockerfile` — H2 fix
- `services/billing-service/Dockerfile` — H2 fix
- `services/analytics-service/Dockerfile` — H2 fix
- `services/encoding-service/Dockerfile` — H2 fix
- `services/key-service/Dockerfile` — H2 fix
- `services/verification-service/Dockerfile` — H2 fix
- `services/web-service/Dockerfile` — H2 fix
- `services/notification-service/Dockerfile` — H2 fix
- `services/user-service/Dockerfile` — H2 fix
- `services/coalition-service/Dockerfile` — H2 fix
- `enterprise_api/app/routers/streaming.py` — H3 fix
- `enterprise_api/app/routers/licensing.py` — H3 fix
- `enterprise_api/app/routers/status.py` — H3 fix
- `enterprise_api/app/api/v1/enterprise/c2pa.py` — H3 fix
- `enterprise_api/app/api/v1/endpoints/merkle.py` — H3 fix
- `enterprise_api/app/services/embedding_executor.py` — H3 fix
- `enterprise_api/app/routers/documents.py` — M2 fix
- `dashboard_app/backend/app/api/endpoints/coalition.py` — H3 fix
- `dashboard_app/backend/app/api/endpoints/auth.py` — H3 fix
- `dashboard_app/backend/app/api/endpoints/audit_log.py` — H3 fix
- `dashboard_app/backend/app/api/endpoints/audit_logs.py` — H3 fix
- `services/coalition-service/app/api/v1/endpoints.py` — H3 fix
- `services/billing-service/app/api/v1/endpoints.py` — H3 fix
- `services/encoding-service/app/api/v1/endpoints.py` — H3 fix
- `services/key-service/app/api/v1/endpoints.py` — H3 fix
- `services/verification-service/app/api/v1/endpoints.py` — H3 fix
- `services/analytics-service/app/api/v1/endpoints.py` — H3 fix
- `services/auth-service/app/api/v1/endpoints.py` — H3 fix
- `services/auth-service/app/api/v1/organizations.py` — H3 fix

## Note for Repo Admin
- The SARIF upload to GitHub's Security tab requires **GHAS** (paid for private repos)
- **RECOMMENDED**: Rotate committed Stripe keys and service tokens (see audit report C1, C2)
- **RECOMMENDED**: Remove `.env` files from git history

## Git Commit Message Suggestion
```
fix(security): comprehensive security audit and remediation

CI Workflow:
- Bump github/codeql-action/upload-sarif from v3 to v4 (v3 deprecated Dec 2026)
- Add continue-on-error to SARIF upload step for repos without GHAS
- Add table-format Trivy output so results are always visible in logs

Ruff Lint (F401, UP042, F821):
- Remove unused imports across analytics, verification, and web services
- Replace str+Enum with StrEnum in DemoRequestStatus (Python 3.11+)
- Fix undefined 'db' → 'core_db' in public verify endpoint (runtime bug)

Security Remediation:
- [C3] Replace hardcoded JWT secret with secrets.token_urlsafe() + production guard
- [H1] Bump python-multipart to >=0.0.22 (CVE-2026-24486) across 4 services
- [H2] Add non-root USER to 12 production Dockerfiles
- [H3] Replace ~60 detail=str(e) with logger.exception() + generic client messages
- [M2] Escape ILIKE wildcards in document search to prevent pattern injection
- Add comprehensive security audit report (docs/SECURITY_AUDIT_2026_02_11.md)
```
