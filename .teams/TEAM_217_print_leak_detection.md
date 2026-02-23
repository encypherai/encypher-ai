# TEAM_217 — Print Leak Detection

**Session Date**: 2026-02-21
**Branch**: feature/rights-management-system

## Status: COMPLETE — ✅ pytest (11 tests) ✅ tsc (zero errors)

## Feature Summary

Add Enterprise-tier `enable_print_fingerprint` option to `/api/v1/sign`.
Encodes 16-byte HMAC payload into inter-word spaces using U+2009 THIN SPACE (1-bit) vs U+0020 (0-bit).
Survives printing → scanning → high-quality OCR. Invisible to readers.
Passively detected by `/api/v1/verify/advanced`.

## Implementation Checklist

- [x] `enterprise_api/app/utils/print_stego.py` — core encode/decode — ✅ pytest
- [x] `enterprise_api/app/schemas/sign_schemas.py` — `enable_print_fingerprint` field + tier validation — ✅ pytest
- [x] `enterprise_api/app/schemas/api_response.py` — FEATURE_REGISTRY entry — ✅ pytest
- [x] `enterprise_api/app/services/unified_signing_service.py` — no change needed (post-sign hook pattern)
- [x] `enterprise_api/app/routers/signing.py` — post-sign hook `_apply_print_fingerprint` — ✅ pytest
- [x] `enterprise_api/app/routers/verification.py` — passive detection in verify/advanced — ✅ pytest
- [x] `enterprise_api/tests/test_print_fingerprint.py` — 11 tests — ✅ pytest
- [x] `apps/dashboard/src/app/playground/page.tsx` — Enterprise checkbox — ✅ tsc
- [x] `apps/dashboard/src/lib/playgroundRequestBuilder.mjs` — form builder — ✅ tsc
- [x] `apps/dashboard/src/app/docs/page.tsx` — guide card — ✅ tsc
- [x] `apps/dashboard/src/app/docs/print-leak-detection/page.tsx` — NEW docs page — ✅ tsc
- [x] `sdk/openapi.public.json` — schema field
- [x] `enterprise_api/README.md` — note field

## Key Design Decisions

- `enable_print_fingerprint` in `SignOptions` (not a top-level field) — matches existing pattern
- Post-sign hook in `signing.py` (like `_attach_rights_snapshot`) — works for both basic and advanced signing paths
- Passive detection in `verify/advanced` — always runs, no flag needed from caller
- `build_payload(org_id, document_id)` = HMAC-SHA256(key=org_id, msg=doc_id)[:16]
- Encoding: U+0020 = 0-bit, U+2009 = 1-bit, first 128 inter-word spaces only
- Graceful no-op when text < 128 spaces (no error raised, warning logged)
- False-positive protection: returns None if no U+2009 detected in first 128 spaces

## Suggested Commit Message

```
feat(signing): add Print Leak Detection (enable_print_fingerprint)

Enterprise-tier option that encodes a 16-byte HMAC-SHA256 fingerprint
into inter-word spaces using U+2009 THIN SPACE (1-bit) vs U+0020 (0-bit).
Fingerprint survives PDF copy-paste, high-quality OCR, and printing.

Changes:
- enterprise_api/app/utils/print_stego.py — encode/decode/build_payload
- enterprise_api/app/schemas/sign_schemas.py — enable_print_fingerprint field
- enterprise_api/app/schemas/api_response.py — FEATURE_REGISTRY entry
- enterprise_api/app/routers/signing.py — _apply_print_fingerprint hook
- enterprise_api/app/routers/verification.py — passive scan in verify/advanced
- enterprise_api/tests/test_print_fingerprint.py — 11 tests
- apps/dashboard/src/app/playground/page.tsx — Enterprise-gated checkbox
- apps/dashboard/src/lib/playgroundRequestBuilder.mjs — form builder
- apps/dashboard/src/app/docs/page.tsx — guide card
- apps/dashboard/src/app/docs/print-leak-detection/page.tsx — docs page
- sdk/openapi.public.json — schema field
- enterprise_api/README.md — tier matrix update

Tests: uv run pytest tests/test_print_fingerprint.py -v → 11 passed
TypeScript: npx tsc --noEmit → zero errors
```
