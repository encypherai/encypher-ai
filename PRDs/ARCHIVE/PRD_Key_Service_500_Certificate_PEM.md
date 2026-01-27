# PRD: Fix key-service 500 error - Missing certificate_pem in SQL query

**Status**: Complete  
**Team**: TEAM_133  
**Date**: 2026-01-27  
**Priority**: P0 (Critical - blocking API key validation)

## Current Goal
Fix key-service returning 500 Internal Server Error when validating organization-level API keys due to missing `certificate_pem` column in SQL query.

## Overview
Users creating new API keys in the Dashboard receive 401 errors when attempting to use them. Backend logs show key-service returning 500 error with `NoSuchColumnError: Could not locate column in row for column 'certificate_pem'`.

## Root Cause
Production DB schema mismatch:
- The production `key-service` database's `organizations` table does not yet have the `certificate_pem` column.
- The `verify_key_with_org()` method referenced `o.certificate_pem` in the SQL SELECT and attempted to read `result.certificate_pem`, causing 500s with `UndefinedColumn` / `NoSuchColumnError`.

## Objectives
- [x] Make key validation query backward compatible (works with and without `organizations.certificate_pem`)
- [x] Add/adjust tests to cover both schemas
- [x] Run full test suite to ensure no regressions
- [x] Verify linting passes

## Tasks
- [x] 1.1 Identify root cause of 500 error in backend logs
- [x] 1.2 Confirm production DB missing `organizations.certificate_pem`
- [x] 1.3 Implement fallback query when `certificate_pem` column is missing
- [x] 2.1 Run pytest on key-service tests — ✅ pytest
- [x] 2.2 Run ruff linting — ✅ ruff
- [x] 2.3 Update TEAM_133 log with fix details

## Success Criteria
- ✅ key-service `/api/v1/keys/validate` endpoint returns 200 for valid org-level keys
- ✅ No 500 errors in backend logs
- ✅ When `certificate_pem` column is absent, validation succeeds and returns `certificate_pem: null`
- ✅ Tests cover both with/without certificate column
- ✅ All linting checks pass

## Completion Notes (2026-01-27 14:00 UTC)
Fixed by making `verify_key_with_org()` schema-compatible:
- Try query selecting `o.certificate_pem`
- If DB raises undefined column error, retry without it
- Use safe `getattr(result, "certificate_pem", None)` when building response

Key-service tests and lint pass.

**Related**: This fix completes the API key validation flow started in PRD_Dashboard_API_Key_Discrepancy_401.md
