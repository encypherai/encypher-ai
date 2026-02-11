# TEAM_163 — Fix enterprise-api migrations: cross-DB references

## Summary
Fixed startup crashes in enterprise-api when running against a fresh/copied DB. Multiple migrations referenced content-DB tables from core-DB migrations.

## Fixes Applied

### 1. `017_add_webhooks.sql` — `documents` table does not exist
- **Root cause:** Lines 79-87 had `ALTER TABLE documents` + `CREATE INDEX ON documents`. The `documents` table lives in the content DB.
- **Fix:** Removed the 3 statements. `deleted`/`deleted_at` columns are unused in Python code.

### 2. `021_add_fuzzy_fingerprints.sql` — `merkle_roots` table does not exist
- **Root cause:** Line 26 had `merkle_root_id UUID REFERENCES merkle_roots(id) ON DELETE SET NULL`. The `merkle_roots` table lives in the content DB.
- **Fix:** Changed to `merkle_root_id UUID` (plain column, no FK). The column is used in code but the FK constraint is invalid cross-DB.

### Audit
Verified no other enterprise_api migrations have cross-DB FK references.

## Status: COMPLETE
