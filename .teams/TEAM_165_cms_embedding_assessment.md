# TEAM_165 — CMS Embedding Assessment + Micro Modes Refactor

## Session: 2026-02-11
## Goal: Assess embedding methods for CMS integration, implement micro modes, rename public API

## Status: Complete

## Work Done

### 1. CMS Embedding Assessment
- Wrote `PRDs/CURRENT/PRD_CMS_Embedding_Assessment.md`

### 2. Public Mode Rename (Breaking)
Removed all `vs256` terminology from public API surfaces:
- `vs256_embedding` → **`micro`** (36 chars, 128-bit HMAC)
- `vs256_rs_embedding` → **`micro_ecc`** (44 chars, 128-bit HMAC + RS)
- **`micro_c2pa`** — micro markers + full C2PA document manifest
- **`micro_ecc_c2pa`** — micro_ecc markers + full C2PA document manifest

### 3. ECC Security Upgrade (Breaking)
Upgraded `vs256_rs_crypto.py` from 36-char to **44-char** layout:
- Old: UUID(16) + HMAC-64(8) + RS(8) = 32 payload → 36 total (64-bit HMAC)
- New: UUID(16) + HMAC-128(16) + RS(8) = 40 payload → 44 total (128-bit HMAC)
- Now matches the security level of non-ECC mode (both 128-bit HMAC)

### 4. SSOT Refactor
Created `app/schemas/signing_constants.py` — single source of truth for `MANIFEST_MODES`, `EMBEDDING_STRATEGIES`, `SEGMENTATION_LEVELS`, `MERKLE_SEGMENTATION_LEVELS`, `DISTRIBUTION_TARGETS`, `C2PA_ACTIONS`. All 3 schema files import from here.

### 5. Verify Endpoint
Returns `manifest_data` + `segment_location` for micro_c2pa/micro_ecc_c2pa refs.

### Files Changed
- `app/utils/vs256_rs_crypto.py` — 44-char layout (HMAC-128 + RS)
- `app/schemas/signing_constants.py` — **NEW** SSOT
- `app/schemas/embeddings.py` — SSOT imports, `SegmentLocation`, `manifest_data` on `C2PAInfo`
- `app/schemas/sign_schemas.py` — SSOT imports
- `app/schemas/streaming.py` — SSOT imports
- `app/services/embedding_service.py` — 4 micro branches (micro, micro_ecc, micro_c2pa, micro_ecc_c2pa)
- `app/services/verification_logic.py` — public mode names in fallback verification
- `app/api/v1/public/verify.py` — DB-backed manifest + segment location

### Naming Convention
- **Public API:** `micro`, `micro_ecc`, `micro_c2pa`, `micro_ecc_c2pa`
- **Internal code/filenames:** may reference VS256 for developer context

### 6. SignerIdentity / CA Trust Chain (Option 2)
Micro markers are HMAC-based (symmetric key derived from org's Ed25519 private key). A root CA certificate can't be embedded in 36/44 invisible chars. Instead, the trust chain resolves via DB: marker → UUID → DB → org → CA cert.

**Implementation:**
- Added `SignerIdentity` schema: `organization_id`, `organization_name`, `certificate_status`, `ca_backed`, `issuer`, `certificate_expiry`, `trust_level`
- `trust_level` values: `none` (no cert), `self_signed` (Encypher-managed key), `ca_verified` (chains to C2PA-trusted CA)
- Verify endpoint (`/api/v1/public/verify/{ref_id}`) now looks up org cert status from DB and populates `signer_identity` in response
- When org uploads a CA cert via `/byok/certificates`, existing micro markers automatically upgrade to `ca_verified` trust level — no re-signing needed

**Files changed:**
- `app/schemas/embeddings.py` — added `SignerIdentity` schema, added `signer_identity` to `VerifyEmbeddingResponse`
- `app/api/v1/public/verify.py` — org cert lookup + `SignerIdentity` population

**Tests:** 3 unit tests for `SignerIdentity` schema + 1 integration test (sign → verify → check signer_identity)

## Test Results
- **67 unit tests passed** (38 vs256_crypto + 25 vs256_rs_crypto + 4 micro/ecc unit + 3 SignerIdentity schema — all no-DB tests green)
- Integration tests require Docker DB stack (not available in this environment)
- SSOT validation confirmed across all 3 schema files

---

## Session: 2026-02-17
## Goal: Micro/micro_ecc default C2PA manifest persistence + signer identity display parity

## Status: In Progress (feature slice complete, broader repo lint baseline still noisy)

### Work Completed
- Added TDD coverage for `/api/v1/sign` micro modes default behavior and opt-out storage flag:
  - `test_sign_micro_modes_embed_and_store_c2pa_manifest_by_default`
  - `test_sign_micro_modes_can_opt_out_of_manifest_storage`
  - File: `enterprise_api/tests/test_micro_c2pa_embedding.py`
- Implemented backend option plumbing for manifest DB persistence toggle:
  - Added `store_c2pa_manifest` option (default `true`) to unified sign schemas
  - Propagated option through unified signing -> embedding executor -> embedding service
  - Files: `app/schemas/sign_schemas.py`, `app/schemas/embeddings.py`, `app/services/unified_signing_service.py`, `app/services/embedding_executor.py`
- Updated micro + micro_ecc embedding behavior:
  - Both now embed a full document-level C2PA wrapper by default (when `disable_c2pa=false`)
  - Manifest extraction and DB persistence now controlled by `store_c2pa_manifest`
  - File: `app/services/embedding_service.py`
- Added verification signer-name fallback logic to prefer human-readable manifest identity when cert name unavailable:
  - New helper `_resolve_signer_name`
  - File: `app/services/verification_logic.py`
- Added focused unit coverage for verification signer-name resolution paths:
  - File: `enterprise_api/tests/test_verification_logic.py`
- Updated marketing-site verify mapping to prefer human-readable manifest identity when `signer_name` is missing/equal to `signer_id`:
  - File: `apps/marketing-site/src/lib/enterpriseApiTools.ts`
  - Test: `apps/marketing-site/src/lib/enterpriseApiTools.test.ts`
- Updated `/sign` docs for new behavior/options:
  - File: `enterprise_api/app/routers/signing.py`

### Validation Run (this session)
- `uv run ruff check app/services/verification_logic.py tests/test_verification_logic.py tests/test_micro_c2pa_embedding.py` ✅
- `uv run pytest -q tests/test_verification_logic.py tests/test_micro_c2pa_embedding.py` ✅ (27 passed, 1 skipped)
- `npm test -- --runInBand src/lib/enterpriseApiTools.test.ts` ✅

### Known Baseline Noise / Blockers
- `npm run lint` in marketing-site reports pre-existing workspace lint errors unrelated to this change set.
- `next lint <file>` and direct ESLint v9 CLI invocation are not usable in this repo as-is due to local lint config/tooling mismatch.

### Suggested Comprehensive Commit Message
```
feat(sign+verify): default micro/micro_ecc to full C2PA manifests with DB persistence toggle and signer identity fallback

- add SignOptions.store_c2pa_manifest (default true) and propagate through unified sign pipeline
- extend EncodeWithEmbeddingsRequest with store_c2pa_manifest
- update embedding service micro/micro_ecc modes to embed full document-level C2PA manifests by default
- support opt-out of manifest JSON persistence in content_references via store_c2pa_manifest=false
- preserve micro marker behavior while adding C2PA wrapper + manifest extraction/storage controls
- improve verification signer_name resolution via certificate -> manifest metadata -> signer_id fallback
- improve marketing-site verify mapping to prefer human-readable manifest identity labels
- add regression tests for micro/micro_ecc default manifest embedding + storage opt-out
- add verification_logic unit tests for signer identity resolution behavior
- update /sign option docs to describe micro default C2PA behavior and store_c2pa_manifest

Tested:
- uv run ruff check app/services/verification_logic.py tests/test_verification_logic.py tests/test_micro_c2pa_embedding.py
- uv run pytest -q tests/test_verification_logic.py tests/test_micro_c2pa_embedding.py
- npm test -- --runInBand src/lib/enterpriseApiTools.test.ts
```
