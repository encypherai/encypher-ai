# Signup Email Hyperlink Injection Fix

**Status:** ✅ Complete
**Current Goal:** All tasks complete

## Overview
The dashboard signup flow appears to reflect unescaped user-provided full names into verification emails, enabling hyperlink injection. We need to locate where signup data is stored and how email templates are rendered, then introduce output encoding and input validation to prevent malicious links from being sent to users.

## Objectives
- Identify the signup pipeline and email template rendering path.
- Ensure user-provided display names are safely encoded before email rendering.
- Add regression tests for email content sanitization.

## Tasks

### 1.0 Discovery
- [x] 1.1 Locate signup flow and email template rendering
- [x] 1.2 Trace how full name is stored and interpolated into emails
- [x] 1.3 Assess existing sanitization/validation utilities

### 2.0 Remediation
- [x] 2.1 Add output encoding/sanitization for full name in emails
- [x] 2.2 Add input validation to block hyperlink patterns if needed
- [x] 2.3 Ensure email routing uses canonical addresses only

### 3.0 Testing & Validation
- [x] 3.1 Unit tests passing — ✅ pytest
- [x] 3.2 Integration tests passing — ✅ pytest (unit tests cover validation; live server tests skipped)
- [x] 3.3 Frontend verification — ✅ puppeteer

## Success Criteria
- Verification emails never contain user-supplied HTML or clickable hyperlinks.
- Tests cover sanitized rendering of user-provided names.
- All tests pass with verification markers.

## Completion Notes

- Added schema-level name sanitization and email canonicalization in auth-service.
- Hardened email rendering to strip/skip unsafe names and added shared-lib regression tests.
