# TEAM_180 — Enterprise API Docs CSP Fix

## Status: COMPLETE

## Problem
The `/docs` page renders as unstyled HTML because `SecurityHeadersMiddleware` applies a blanket restrictive CSP (`default-src 'none'`) to all responses, including the docs page. This blocks:
- External CSS/JS from `unpkg.com` (Swagger UI)
- External images from `encypherai.com` (logo/favicon)
- Inline `<style>` and `<script>` blocks

## Fix
Added `DOCS_CSP` constant with a relaxed Content-Security-Policy for `/docs*` routes that allows Swagger UI CDN resources, inline styles/scripts, and external images. The strict default CSP is preserved for all other API routes.

## Tasks
- [x] Identify root cause (CSP in SecurityHeadersMiddleware) — ✅ pytest
- [x] Update SecurityHeadersMiddleware to use relaxed CSP for /docs* routes — ✅ pytest
- [x] Write regression tests (3 new tests) — ✅ pytest (9/9 pass)
- [x] Verify fix — ✅ pytest

## Files Changed
- `enterprise_api/app/middleware/security_headers.py` — Added `DOCS_CSP`, `_build_docs_headers()`, path-based CSP selection in dispatch
- `enterprise_api/tests/test_transport_protections.py` — 3 new regression tests

## Git Commit Message Suggestion
```
fix(enterprise-api): relax CSP for /docs routes so Swagger UI loads

The SecurityHeadersMiddleware applied `default-src 'none'` to all
responses, blocking Swagger UI CDN resources (unpkg.com CSS/JS),
external images (encypherai.com logo), and inline styles/scripts
on the /docs page.

Add a dedicated DOCS_CSP that whitelists the required sources for
/docs* routes while preserving the strict default CSP for all other
API endpoints.

Includes 3 regression tests verifying CSP behavior for docs vs
non-docs routes.
```
