# Billing Service Build Fix

**Status:** 🔄 In Progress
**Current Goal:** Task 1.3 — validate shared library installation flow

## Overview
The billing-service container build fails because the shared library dependency is declared as a UV workspace member that is not present inside the service build context. This PRD tracks the minimal changes needed to install the shared library reliably during Docker builds.

## Objectives

- Remove the UV workspace dependency mismatch during billing-service builds.
- Keep shared library installation consistent with other services.
- Verify build-related checks and document test status.

## Tasks

### 1.0 Build Configuration

- [x] 1.1 Confirm current billing-service packaging configuration
- [x] 1.2 Adjust packaging metadata to avoid workspace-only dependency
- [ ] 1.3 Validate shared library installation flow

### 2.0 Documentation

- [ ] 2.1 Update any service docs if build steps change

### 3.0 Testing & Validation

- [x] 3.1 Linting passes — ✅ ruff
- [x] 3.2 Service tests passing — ✅ pytest
- [ ] 3.3 Container build verification — ✅ manual

## Success Criteria

- Billing-service Docker build no longer fails on workspace dependency parsing.
- Shared library dependency resolves using the service build context.
- Verification steps are recorded in tasks.

## Completion Notes

( заполнить при завершении )
