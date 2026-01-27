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
The `verify_key_with_org()` method in `services/key-service/app/services/key_service.py` has a SQL query (lines 277-298) that doesn't select `certificate_pem` from the organizations table, but line 385 attempts to access `result.certificate_pem`, causing a `NoSuchColumnError`.

## Objectives
- [x] Add `certificate_pem` to SQL query SELECT clause
- [x] Verify fix with existing test `test_validate_key_returns_certificate_pem`
- [x] Run full test suite to ensure no regressions
- [x] Verify linting passes

## Tasks
- [x] 1.1 Identify root cause of 500 error in backend logs
- [x] 1.2 Locate SQL query missing certificate_pem column
- [x] 1.3 Add certificate_pem to SELECT clause (line 294)
- [x] 2.1 Run pytest on test_validate_key_with_org.py — ✅ pytest
- [x] 2.2 Run ruff linting — ✅ ruff
- [x] 2.3 Update TEAM_133 log with fix details

## Success Criteria
- ✅ key-service `/api/v1/keys/validate` endpoint returns 200 for valid org-level keys
- ✅ No 500 errors in backend logs
- ✅ Test `test_validate_key_returns_certificate_pem` passes
- ✅ All linting checks pass

## Completion Notes (2026-01-27 14:00 UTC)
Fixed by adding `o.certificate_pem` to SQL query SELECT clause in `verify_key_with_org()`. Test suite passes. User can now successfully use newly created API keys.

**Related**: This fix completes the API key validation flow started in PRD_Dashboard_API_Key_Discrepancy_401.md
