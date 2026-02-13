# TEAM_181 — API Docs Option Detail

## Status: COMPLETE

## Problem
The `/api/v1/sign` and `/api/v1/verify/advanced` endpoint descriptions in the Swagger UI docs only show minimal examples without explaining what each option does, what values are accepted, or what tier is required.

## Fix
Added comprehensive option reference tables to the endpoint `description` fields in the router decorators so Swagger UI renders full documentation with types, defaults, accepted values, tier requirements, and usage examples.

## Tasks
- [x] Investigate all sign options from SignOptions schema — ✅ pytest
- [x] Investigate all verify/advanced options from VerifyAdvancedRequest schema — ✅ pytest
- [x] Update /sign endpoint description with detailed options reference — ✅ pytest ✅ puppeteer
- [x] Update /verify/advanced endpoint description with detailed options reference — ✅ pytest ✅ puppeteer
- [x] Run tests to verify no regressions — ✅ pytest (176 passed, 9 pre-existing failures unrelated)
- [x] Verify docs page renders correctly with Puppeteer — ✅ puppeteer

## Files Changed
- `enterprise_api/app/routers/signing.py` — Expanded /sign description from ~800 chars to ~7,300 chars with full options reference
- `enterprise_api/app/routers/verification.py` — Expanded /verify/advanced description from ~80 chars to ~3,800 chars with full request fields reference

## Git Commit Message Suggestion
```
docs(enterprise-api): add comprehensive option reference to /sign and /verify/advanced

The Swagger UI docs for /sign showed only a tier matrix and minimal
examples without explaining what each option does. /verify/advanced
had a one-line description.

Add detailed reference tables for all options covering:
- Type, default, accepted values, tier requirement, description
- Sections: Segmentation, Manifest & Embedding, C2PA Provenance,
  Advanced Features, Custom Assertions & Rights, Output Options
- Multiple usage examples (minimal, with options, batch, provenance)
- /verify/advanced: full request fields + fuzzy_search sub-object
```
