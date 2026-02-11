# TEAM_163 — Fix 017 Migration: documents table does not exist

## Summary
Fixed startup crash in enterprise-api when running against a fresh DB. Migration `017_add_webhooks.sql` contained `ALTER TABLE documents` statements, but the `documents` table lives in the **content DB**, not the core DB that this migration runs against.

## Root Cause
Lines 79-87 of `enterprise_api/migrations/017_add_webhooks.sql` attempted to add `deleted` and `deleted_at` columns plus an index to the `documents` table. This table is defined in `services/migrations/content_db/001_content_schema.sql`, not in the core DB.

## Fix
Removed the three offending statements (2 ALTER TABLE + 1 CREATE INDEX) from the migration. Verified:
- The `deleted`/`deleted_at` columns are not referenced anywhere in the Python codebase
- No other enterprise_api migrations have the same issue
- The remaining migration statements (webhooks tables, api_keys columns) are valid

## Status: COMPLETE
