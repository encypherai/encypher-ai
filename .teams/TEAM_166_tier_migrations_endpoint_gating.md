# TEAM_166 — Tier Migrations, Endpoint Gating & SSOT Refactor

## Session Summary
Continuation of TEAM_145 tier consolidation work. Three phases:

### Phase 1: Alembic Migrations
- `enterprise_api/alembic/versions/20260211_consolidate_tiers_add_addons.py`
- `services/auth-service/alembic/versions/009_consolidate_tiers_add_addons.py`

### Phase 2: Endpoint Gating Updates (35+ files)
- **Free tier now has**: signing, segmentation (except word), manifest modes, attribution, plagiarism, merkle, streaming merkle, multi-source lookup, custom assertions, batch (up to 10), **audit logs**
- **Enterprise-only**: word segmentation, dual binding, fingerprinting, distributed_redundant, BYOK, SSO, team management, webhooks, evidence, authority ranking, custom assertion authoring

### Phase 3: SSOT Tier Config Refactor
Created `enterprise_api/app/core/tier_config.py` as the single source of truth for all tier configuration. Refactored 11 consumer files to import from it instead of hardcoding:

| File | What was removed |
|------|-----------------|
| `dependencies.py` | Hardcoded demo key feature dicts → `get_tier_features()` |
| `routers/account.py` | `TIER_FEATURES`, `TIER_LIMITS`, `_coerce_tier_name()` |
| `routers/usage.py` | `TIER_LIMITS`, `_coerce_tier()` |
| `routers/coalition.py` | `TIER_REV_SHARE`, `_coerce_tier_for_rev_share()` |
| `routers/team.py` | `TIER_MEMBER_LIMITS` |
| `routers/keys.py` | `tier_limits` dict |
| `services/admin_service.py` | `tier_features` dict, `legacy_map` |
| `middleware/api_rate_limiter.py` | `TIER_RATE_LIMITS_PER_SECOND` |
| `schemas/api_response.py` | `TIER_HIERARCHY`, `BATCH_LIMITS`, `get_batch_limit()` |
| `utils/quota.py` | `TIER_RATE_LIMITS`, `TIER_REV_SHARE`, `TIER_FEATURES` (now derived from SSOT) |
| `services/embedding_executor.py` | Fixed `org_tier_level` NameError → `is_enterprise_tier()` |

### Phase 4: Test Updates
Updated 10 test files to reflect new tier structure:
- `test_audit_api.py` — audit logs now free tier
- `test_batch_endpoints.py` — business→enterprise for bulk ops
- `test_builtin_c2pa_templates.py` — templates available to free
- `test_byok_public_keys.py` — business→enterprise
- `test_nma_member_flag.py` — tier name free not starter
- `test_rate_limiter.py` — consolidated rate limits
- `test_org_context_composition.py` — professional coerced to free
- `test_team_api.py` — business→enterprise for team mgmt
- `test_webhooks_tier_gating.py` — business→enterprise
- `test_webhook_limits.py` — business→enterprise
- `test_api_key_auth.py` — embedding permission for all tiers
- `conftest.py` — added enterprise_admin/owner fixtures

### Phase 5: Fix All Remaining Test Failures
- Replaced incorrect Alembic migration with proper SQL migration `migrations/022_consolidate_tiers_add_addons.sql`
  (Enterprise API uses raw SQL migrations via `db_startup.py`, not Alembic)
- Fixed `TierName.STARTER/PROFESSIONAL/BUSINESS` references in `sign_schemas.py` (production bug)
- Fixed `README.md` restricted wording ("Unicode Variation Selectors" → customer-safe language)
- Added missing endpoint `GET /api/v1/public/c2pa/zw/resolve/{segment_uuid}` to README
- Regenerated `sdk/openapi.public.json` to match runtime
- Fixed `start-dev.sh` test (Docker Compose service names, not directory paths)
- Fixed `test_stream_runs_access_control.py` org_id mismatch (`org_business` → `org_free_legacy_biz`)
- Fixed `test_sign_advanced_revocation_status_assertion.py` → enterprise_auth_headers
- Updated 6 more test files for tier consolidation

## Status
✅ **833 tests pass**, 52 skipped, 0 failures
✅ All syntax checks pass
✅ SQL migration idempotent and tested

## Suggested Git Commit Message
```
feat(tier-consolidation): SSOT tier config, SQL migration, fix all 28 test failures

TEAM_166: Complete tier consolidation to free/enterprise/strategic_partner.

- Create `enterprise_api/app/core/tier_config.py` as single source of truth
- Refactor 11 consumer files to import from tier_config SSOT
- Replace incorrect Alembic migration with SQL migration 022
- Fix TierName.STARTER/PROFESSIONAL/BUSINESS references in sign_schemas.py
- Fix org_tier_level NameError in embedding_executor.py
- Move audit_logs to free tier
- Regenerate sdk/openapi.public.json
- Fix README restricted wording + add missing endpoint
- Update 20+ test files for consolidated tier structure
- All 833 tests pass, 0 failures
```
