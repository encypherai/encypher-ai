# TEAM_188 — CERT_NOT_FOUND Verification Bug

**Status:** Complete  
**Started:** 2026-02-13  
**Task:** Fix CERT_NOT_FOUND error when verifying embeddings signed by free-tier orgs (e.g., test@encypherai.com / org_07dd7ff77fa7e949)

## Root Cause

Free-tier orgs created via auth-service get auto-provisioned signing keys
(`private_key_encrypted` + `public_key` columns) during their first signing
request. However, two verification paths failed to resolve these keys:

1. **`load_organization_public_key`** (used by trust-anchor endpoint): Only read
   the `public_key` raw bytes column. When NULL (org bootstrapped but key not yet
   written, or `public_key` column not populated), it raised `ValueError` → 404
   from the trust-anchor endpoint → verification-service got `None` for
   `trust_anchor_public_key` → `CERT_NOT_FOUND`.

2. **`CertificateResolver.refresh_cache`** (used by enterprise API's own verify):
   Skipped all orgs without `certificate_pem` (line 120: `if not certificate_pem: continue`).
   Free-tier auto-provisioned orgs have no certificate_pem — they only have
   `private_key_encrypted` / `public_key`.

## Fixes

### Fix 1: `enterprise_api/app/utils/crypto_utils.py` — `load_organization_public_key`
- Now queries both `public_key` AND `private_key_encrypted` columns
- Falls back to deriving public key from encrypted private key when `public_key` is NULL
- Mirrors the fallback logic already present in `load_organization_private_key`

### Fix 2: `enterprise_api/app/services/certificate_service.py` — `CertificateResolver`
- Added auto-provisioned key loading after the certificate_pem loop
- Queries orgs with `certificate_pem IS NULL AND (public_key IS NOT NULL OR private_key_encrypted IS NOT NULL)`
- Resolves public key from raw bytes or derives from encrypted private key
- Skips orgs already resolved via certificate_pem (certificate takes precedence)

## Tests
- `test_cert_not_found_regression.py` — 6 tests, all passing:
  - `test_load_public_key_from_public_key_column` — standard path
  - `test_load_public_key_fallback_to_private_key_encrypted` — TEAM_188 regression
  - `test_load_public_key_raises_when_org_missing` — error path
  - `test_load_public_key_raises_when_no_keys` — error path
  - `test_certificate_resolver_loads_auto_provisioned_key` — TEAM_188 regression
  - `test_certificate_resolver_prefers_certificate_pem_over_auto_provisioned` — precedence
- 147 existing tests pass, 7 pre-existing failures (unrelated 410 vs 404 status code)

## Session Log
- Traced full verification flow from verification-service → enterprise API trust anchor
- Identified `load_organization_public_key` as the root cause (no fallback to private key derivation)
- Identified `CertificateResolver` as secondary issue (skipping auto-provisioned orgs)
- Implemented both fixes, wrote 6 regression tests, verified no regressions

## Suggested Git Commit Message
```
fix(enterprise-api): resolve CERT_NOT_FOUND for auto-provisioned orgs

Free-tier orgs with auto-provisioned signing keys (private_key_encrypted)
but no certificate_pem were invisible to both verification paths:

1. load_organization_public_key: now falls back to deriving public key
   from private_key_encrypted when public_key column is NULL.

2. CertificateResolver.refresh_cache: now loads auto-provisioned keys
   for orgs without certificate_pem but with private_key_encrypted or
   public_key columns.

Fixes CERT_NOT_FOUND when verifying content signed by test@encypherai.com
and other free-tier users.

TEAM_188
```
