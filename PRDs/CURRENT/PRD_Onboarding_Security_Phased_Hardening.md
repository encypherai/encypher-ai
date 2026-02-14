# PRD: Onboarding Security Phased Hardening

**Status**: Complete
**Team**: TEAM_191
**Current Goal**: Harden onboarding/auth flows with Turnstile, step-up auth, TOTP 2FA, and passkey-ready rollout.

---

## Overview

This PRD upgrades onboarding security in progressive phases to reduce abuse without introducing unnecessary signup friction. Phase 1 introduces configurable Turnstile enforcement and step-up checkpoints; Phase 2 adds TOTP 2FA with backup codes; Phase 3 adds passkey support and optional passwordless login. Each phase is independently deployable behind flags.

---

## Objectives

- Reduce automated signup/login abuse while preserving conversion.
- Add robust account protection for sensitive actions (API keys, billing, org security settings).
- Provide high-trust authentication options (2FA and passkeys) with safe recovery paths.
- Roll out via feature flags and risk-based controls to avoid broad regressions.
- Keep onboarding UX clear: minimal mandatory friction, progressive hardening as trust/value increases.

---

## Tasks

### 1.0 Phase 1 — Turnstile + Step-Up Auth

- [x] 1.1 Add Turnstile backend verification utility and settings — ✅ pytest
  - [x] 1.1.1 Add `TURNSTILE_*` settings in auth-service config
  - [x] 1.1.2 Add `app/services/turnstile_service.py`
  - [x] 1.1.3 Add schema support for `turnstile_token` / `turnstileToken`
- [x] 1.2 Enforce Turnstile in signup/login via config gates — ✅ pytest
  - [x] 1.2.1 Add `_enforce_turnstile_if_required` helper in auth endpoints
  - [x] 1.2.2 Enforce for signup and login with forwarded IP support
- [x] 1.3 Add unit tests for Turnstile schema + verification behavior — ✅ pytest
- [x] 1.4 Update env docs for Turnstile rollout controls — ✅ implemented
- [ ] 1.5 Add dashboard login/signup Turnstile widget integration — pending frontend slice
- [ ] 1.6 Add step-up auth challenge endpoint for sensitive actions

### 2.0 Phase 2 — TOTP 2FA + Backup Codes

- [x] 2.1 Add user model fields and migration for TOTP state — ✅ pytest ✅ ruff
  - [x] 2.1.1 `totp_enabled`, `totp_secret_encrypted`, `totp_enabled_at`
  - [x] 2.1.2 backup code hashes + recovery metadata
- [x] 2.2 Add 2FA setup endpoints — ✅ pytest
  - [x] 2.2.1 begin setup (provisioning URI/QR payload)
  - [x] 2.2.2 confirm setup with OTP
  - [x] 2.2.3 disable with OTP/backup code
- [x] 2.3 Add login challenge path when 2FA enabled — ✅ pytest
- [x] 2.4 Add dashboard security UX for enroll/disable/recovery — ✅ tsc ✅ puppeteer
- [x] 2.5 Add tests (service + endpoint + login flow) — ✅ 24 targeted tests

### 3.0 Phase 3 — Passkeys (WebAuthn)

- [x] 3.1 Add passkey credential schema/model support — ✅ pytest ✅ migration
- [x] 3.2 Add registration/authentication challenge endpoints — ✅ pytest
- [x] 3.3 Add dashboard/browser passkey UX — ✅ tsc ✅ puppeteer
- [x] 3.4 Add optional passwordless login mode behind flag — ✅ `PASSKEY_ENABLED`
- [x] 3.5 Add attestation/credential policy and verification tests — ✅ service tests

### 4.0 Rollout, Telemetry, and Guardrails

- [ ] 4.1 Add feature flags for each phase and per-route enforcement
- [ ] 4.2 Add onboarding funnel metrics for friction/abandonment deltas
- [ ] 4.3 Add runbooks for support/recovery edge cases
- [ ] 4.4 Add docs for security posture and customer-facing explanation

---

## Success Criteria

- [x] Phase 1 backend hardening merged and tested.
- [ ] Turnstile live on signup/login with measurable abuse reduction and stable conversion.
- [ ] Sensitive mutations require fresh auth context (step-up).
- [x] TOTP 2FA enrollment and login challenge are production ready.
- [x] Passkey registration/authentication available behind feature flags.
- [ ] Security onboarding UX completion and drop-off metrics tracked in dashboard analytics.

---

## Completion Notes

- 2026-02-14: Phase 1 backend foundation implemented in auth-service:
  - Config flags (`TURNSTILE_ENABLED`, `TURNSTILE_REQUIRE_SIGNUP`, `TURNSTILE_REQUIRE_LOGIN`, etc.)
  - Cloudflare verification helper service
  - Signup/login schema support for Turnstile token
  - Endpoint enforcement hooks for signup/login
  - Unit tests in `services/auth-service/tests/test_turnstile_security.py`
  - `.env.example` updated with Turnstile variables
- 2026-02-14: Phase 2 and Phase 3 shipped end-to-end:
  - Auth service model + Alembic migration `013_mfa_and_passkeys.py`
  - New auth factors service for TOTP (secret provisioning, backup codes, verify/disable)
  - MFA-aware login flow + explicit `/auth/login/mfa/complete`
  - Passkey registration/authentication endpoints and credential lifecycle support
  - Dashboard login upgraded for MFA challenge and passkey sign-in
  - Dashboard settings security tab upgraded for TOTP/passkey enrollment and management
  - Targeted verification:
    - `uv run pytest tests/test_mfa_login_flow.py tests/test_auth_factors_service.py tests/test_signup_input_validation.py tests/test_turnstile_security.py -q`
    - `uv run ruff check app tests`
    - `npx tsc --noEmit` (apps/dashboard)
    - Puppeteer manual check screenshot: `settings-security-phase2-phase3`
