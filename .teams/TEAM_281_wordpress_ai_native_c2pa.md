# TEAM_281 -- WordPress AI Native C2PA Signing

**PRD:** PRDs/CURRENT/PRD_WordPress_AI_Native_C2PA.md
**Status:** In Progress
**Created:** 2026-03-26

## Context

PR #294 on the official WordPress AI canonical plugin (wordpress/ai) has been reviewed by Jeff (Core AI lead) and James LePage (Automattic) is requesting it be finalized for WordPress 7.0. The current implementation uses a custom JSON manifest format that is not C2PA-compliant. This team replaces it with native PHP C2PA signing (JUMBF/COSE/ES256) to produce manifests that any standard C2PA verifier can validate.

## Key Relationships

- **James LePage** (Automattic): Actively championing PR for WordPress 7.0 inclusion
- **Anne McCarthy** (Automattic): Strategic guidance -- hold PR #302 until #294 has clarity
- **Jeff** (Core AI lead): Technical reviewer with outstanding comments on PR #294
- **Parie Meshberg** (WordPress VIP VP BD): Enterprise distribution track running in parallel

## Design Decisions

- ES256 (not Ed25519) for SSL.com/DigiCert C2PA trust list CA compatibility
- JUMBF containers + COSE_Sign1 envelopes (replacing custom JSON)
- Document-level only (sentence-level is commercial moat)
- Connected signer pre-populated with Encypher API URL
- CDN workers extracted from PR #302 to separate repo
- Zero Composer dependencies (PHP openssl only)

## Session Log

### Session 1 (2026-03-26)
- Strategic review of WordPress AI contributions against business strategy
- Discovered PR #294 uses custom JSON format, not real C2PA
- Confirmed ES256 over Ed25519 (SSL.com cert compatibility)
- Created PRD with full task breakdown
- Next: Pull Jeff's review comments, begin Epic 1 (JUMBF box writer)
