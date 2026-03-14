# PRD: Notification Service Audit Fixes

**Status:** COMPLETE
**Current Goal:** Fix critical open email relay vulnerability and implement audit findings
**Branch:** feat/codebase-audit-fixes

## Overview
Apply fixes identified by the notification-service audit. CRITICAL: authenticated open email relay allows any authenticated user to send arbitrary HTML email to any recipient using Encypher's trusted sender identity.

## Objectives
- Close the open email relay vulnerability
- Restrict email recipients to authorized targets
- Sanitize or template email content
- Add input validation

## Tasks

### 1.0 Critical Security - Open Email Relay
- [x] 1.1 Restrict `recipient` field: after auth verification, compare `notification_data.recipient` against `current_user["email"]` and reject with HTTP 403 if they don't match (or implement an allowlist)
- [x] 1.2 Change `recipient` field type from `str` to `EmailStr` (Pydantic) in `app/models/schemas.py:16-24`
- [x] 1.3 Sanitize or reject raw HTML in `content` field -- either accept plain text only and render through fixed templates, or use `bleach` with strict allowlist before sending
- [x] 1.4 Add rate limiting on the send endpoint

### 2.0 Unix Agent Design Improvements
- [x] 2.1 Add navigation hints to error responses
- [x] 2.2 Add request-ID and timing metadata to responses
- [x] 2.3 Add binary/encoding guard on content field

### 3.0 Linting
- [x] 3.1 Run ruff check and fix all issues
- [x] 3.2 Run ruff format

## Success Criteria
- All tasks checked off
- Email relay restricted to authorized recipients only
- No raw unsanitized HTML in email bodies
- `ruff check .` and `ruff format --check .` pass on `services/notification-service/`

## Completion Notes
All tasks implemented. Changes confined to:
- `app/models/schemas.py`: recipient -> EmailStr, content validator rejects HTML tags and high-ratio non-ASCII (binary guard), MessageResponse gains optional hint field, NotificationResponse gains request_id/duration_ms fields.
- `app/api/v1/endpoints.py`: recipient restricted to current_user["email"] (HTTP 403 otherwise), in-process sliding-window rate limiter (10/60s per user_id), navigation hints on all error detail dicts, request_id and duration_ms attached to send response.
- ruff check and ruff format both pass clean.
