# PRD — Verification Service: Public Verify + Trust List

## Status
In Progress

## Current Goal
Make `POST /api/v1/verify` in `services/verification-service` work without authentication and verify signers using the full C2PA trust list plus Encypher internal keys, while returning a distinct warning/reason for signatures that are valid-but-untrusted.

## Overview
The Dashboard Playground and public verification experiences require a verifier that third parties can call without API keys. Today, `services/verification-service` enforces API key auth and only resolves signer keys via the authenticated organization context, causing `401 API key required` and `SIGNER_UNKNOWN` for newly generated user/demo keys. This PRD defines and implements a robust verification contract with optional auth (for rate limits and enrichment), trust-list-based signer resolution, and explicit "untrusted signer" signaling.

## Objectives
- Ensure `POST /api/v1/verify` succeeds without an API key (public + rate-limited).
- Use C2PA trust list validation + internal key/cert sources to resolve signer identity and trust.
- Distinguish between:
  - Valid + trusted
  - Valid signature but untrusted signer (warning/reason)
  - Invalid/tampered
- Preserve existing authenticated behaviors (higher limits, org context where applicable).

## Tasks
- [x] 1.0 Baseline verification-service tests
- [x] 1.1 Task — ✅ pytest

- [x] 2.0 Add tests (TDD) for public verify + trust behavior
- [x] 2.1 Unauthenticated `POST /api/v1/verify` returns 200 for well-formed requests
- [x] 2.2 Unauthenticated verify can validate signatures against trust list / internal keys
- [x] 2.3 Valid signature with unknown/untrusted signer returns warning/reason distinct from `SIGNER_UNKNOWN`
- [x] 2.4 Regression: existing auth-required endpoints and prior verify tests remain green
- [x] 2.5 Task — ✅ pytest

- [x] 3.0 Implement public/optional-auth `POST /api/v1/verify`
- [x] 3.1 Make organization context optional (API key optional)
- [x] 3.2 Implement signer resolution strategy:
  - Internal org certs/keys
  - C2PA trust list
- [x] 3.3 Add explicit "untrusted signer" reason/warning code to response contract
- [x] 3.4 Task — ✅ pytest

- [ ] 4.0 Update Dashboard Playground behavior and labels
- [ ] 4.1 "Try Demo" / "Copy to Verify" no longer fails with 401
- [ ] 4.2 Surface trusted vs untrusted warnings clearly
- [ ] 4.3 Task — ✅ npm lint ✅ type-check ✅ puppeteer

- [ ] 5.0 Documentation / marketing alignment
- [ ] 5.1 Update docs/pricing copy to reflect `/verify` public behavior
- [ ] 5.2 If `/verify/advanced` is introduced, document it as auth-required and policy-heavy

## Success Criteria
- Unauthenticated `POST /api/v1/verify` works and produces correct verdicts.
- Signed content from demo/user flows does not incorrectly return `SIGNER_UNKNOWN`.
- A distinct untrusted-signer warning/reason exists for valid-but-untrusted signatures.
- ✅ `uv run pytest` passes for `services/verification-service`.
- ✅ Dashboard Playground verification flow passes (lint/type-check/puppeteer).

## Completion Notes
(Filled when complete.)
