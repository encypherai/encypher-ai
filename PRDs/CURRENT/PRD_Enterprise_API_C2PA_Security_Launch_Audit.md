
# Enterprise API C2PA Security Launch Audit

**Status:** 🔄 In Progress
**Current Goal:** Document security findings and deliver production-grade hardening for enterprise_api.

## Overview
This PRD captures a red-team security audit of the Enterprise API and the remediation work required to bring it to best‑in‑class security posture. It focuses on authentication, public endpoints, request trust boundaries, and transport protections, with concrete tests to prevent regressions.

## Objectives
- Enumerate high‑risk vulnerabilities and attack vectors in enterprise_api.
- Implement defense‑in‑depth controls (auth, request trust, headers, rate limiting).
- Add regression tests that lock in security guarantees.

## Tasks

### 1.0 Audit Findings
- [x] 1.1 Document auth and demo-key bypass risks.
- [x] 1.2 Review public verification endpoints for signature enforcement and data exposure.
- [x] 1.3 Review trust boundaries for proxy headers (X-Forwarded-For) and IP rate limiting.
- [x] 1.4 Review transport protections (security headers, trusted hosts, CORS).

#### Findings (Draft)
- **1.1 Auth/demo key bypass**
  - `DEMO_KEYS` in `app/dependencies.py` and `settings.demo_api_key` in `app/middleware/api_key_auth.py` are always accepted when Key Service is unavailable or when the demo key is configured, with no environment gating. This enables full demo access in production if the key is known or Key Service is down.
  - The marketing site production key is treated as a demo key with shared demo private key and can access sign/verify endpoints without explicit allowlisting.
- **1.2 Public verification signature enforcement**
  - `/api/v1/public/verify/{ref_id}` and `/api/v1/public/verify/batch` only validate signature length and do not compare against `content_references.signature_hash`. Any signature grants metadata for existing ref_ids, enabling enumeration and metadata disclosure.
  - `ContentReference.signature_hash` is empty for C2PA embeddings (`embedding_service.py`), so even legitimate signatures cannot be verified. `expires_at` is also not enforced in `/verify/{ref_id}`.
  - `extract-and-verify` logs full payloads and text previews; this can leak sensitive content into logs for public traffic.
- **1.3 Proxy header trust / IP rate limiting**
  - `PublicAPIRateLimiter` trusts `X-Forwarded-For` and `X-Real-IP` unconditionally without a trusted proxy allowlist. Clients can spoof IPs to bypass rate limits or cause denial of service for other users.
- **1.4 Transport protections**
  - CORS always appends localhost origins and allows credentials + wildcard headers/methods even in production (`app/main.py`), widening cross-origin surface.
  - No `TrustedHostMiddleware` or security response headers (HSTS, CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy).
  - Public docs endpoints are always exposed regardless of `enable_public_api_docs` flag.

### 2.0 Security Hardening
- [x] 2.1 Gate demo API keys by environment and explicit allowlist.
- [x] 2.2 Enforce signature validation for public verify endpoints (constant-time compare).
- [x] 2.3 Add trusted proxy configuration and only honor forwarded headers when enabled.
- [x] 2.4 Add response security headers middleware (HSTS, CSP, XFO, XCTO, Referrer-Policy, Permissions-Policy).
- [x] 2.5 Add TrustedHost middleware and tighten production CORS defaults.

### 3.0 Validation
- [x] 3.1 Security regression tests — ✅ pytest
- [ ] 3.2 Lint/type checks — ✅ ruff ❌ mypy (pre-existing script typing issues)
- [x] 3.3 Dependency audit — ✅ pip-audit

## Success Criteria
- Public verification endpoints require valid signatures for metadata disclosure.
- Demo keys cannot be used in production unless explicitly enabled.
- IP rate limiting trusts proxy headers only when configured.
- Security headers and host validation are enforced in production.
- All tests pass with verification markers.

## Completion Notes
- Added security headers + TrustedHost middleware, tightened CORS defaults, and gated public docs.
- Public verify now validates signatures with constant-time prefix compare and rejects malformed signatures.
- Content references now persist HMAC signatures; public verify tests updated.
- Trusted proxy IP allowlist now drives forwarded header trust.
- Tests: `uv run pytest enterprise_api/tests` ✅; `uv run ruff check .` ✅; `uv run pip-audit` ✅; `uv run mypy .` ❌ (pre-existing script typing errors in enterprise_api/scripts).
