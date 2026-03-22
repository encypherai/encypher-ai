# API: Ungate Audio/Video Verification Endpoints

## Status: COMPLETE

## Current Goal
Create public (no-auth) verification endpoints for audio and video media, matching the existing pattern of `POST /verify/image`. Signing endpoints remain Enterprise-gated.

## Overview
Audio and video C2PA verification is currently gated behind Enterprise tier (`_ALLOWED_TIERS = {"enterprise", "strategic_partner", "demo"}`) alongside their signing counterparts. This contradicts the company's stated strategy that "verification is free because verifiability is the point." Image verification is already public. This PRD splits audio/video verification out of the Enterprise router into public endpoints, aligning all media verification with the existing `/verify/image` pattern.

## Objectives
- Create `POST /verify/audio` as a public endpoint (no auth, rate-limited)
- Create `POST /verify/video` as a public endpoint (no auth, rate-limited)
- Keep `POST /enterprise/audio/sign` and `POST /enterprise/video/sign` Enterprise-gated (no change)
- Keep `POST /enterprise/audio/verify` and `POST /enterprise/video/verify` working (backward compat) but route to same logic
- Update FEATURE_MATRIX.md to reflect verification as public across all media types
- Unblock Chrome extension Phase 2 (PRD_Chrome_Extension_Media_Verification.md)

---

## Architecture Decisions

### AD-1: Endpoint structure

**Decision**: New public routes under `/verify/` prefix, matching `/verify/image`.

| Endpoint | Auth | Rate Limit | Notes |
|----------|------|------------|-------|
| `POST /verify/image` | None (existing) | Public rate limiter | No change |
| `POST /verify/audio` | None (new) | Public rate limiter | New public endpoint |
| `POST /verify/video` | None (new) | Public rate limiter | New public endpoint |
| `POST /enterprise/audio/verify` | Enterprise (existing) | Org rate limiter | Keep for backward compat, delegates to shared logic |
| `POST /enterprise/video/verify` | Enterprise (existing) | Org rate limiter | Keep for backward compat, delegates to shared logic |

### AD-2: Request/response schemas

**Decision**: New `PublicAudioVerifyRequest`/`PublicAudioVerifyResponse` and `PublicVideoVerifyResponse` schemas with `correlation_id` and `verified_at` fields (matching public image verify pattern). Enterprise schemas unchanged.

### AD-3: Size limits for public endpoints

| Media Type | Max Size (Public) | Max Size (Enterprise) |
|------------|------------------|-----------------------|
| Audio | 50MB | 100MB (existing) |
| Video | 100MB | 500MB (existing) |

**Rationale**: Lower public limits prevent abuse while covering most common media files. Enterprise retains higher limits for production workflows.

---

## Tasks

### 1.0 Extract Shared Verification Logic
- [x] 1.0.1-1.0.3 Verification logic already extracted into service files -- `verify_audio_c2pa()` in `audio_verification_service.py`, `verify_video_c2pa()` in `video_verification_service.py`. Both public and enterprise endpoints call these directly. No additional extraction needed.

### 1.1 Create Public Audio Verify Endpoint
- [x] 1.1.1 Create `enterprise_api/app/api/v1/audio_verify.py` -- 28/28 verify tests pass
  - `POST /verify/audio` handler
  - Accept `PublicAudioVerifyRequest` (base64 `audio_data` + `mime_type`)
  - No auth dependency
  - Apply `public_rate_limiter`
  - Enforce 50MB size limit (`settings.public_audio_max_size_bytes`)
  - Call `verify_audio_c2pa()`
  - Return `PublicAudioVerifyResponse` with `correlation_id` and `verified_at`
- [x] 1.1.2 Register router in `api.py` alongside `image_verify_router` -- 28/28 verify tests pass

### 1.2 Create Public Video Verify Endpoint
- [x] 1.2.1 Create `enterprise_api/app/api/v1/video_verify.py` -- 28/28 verify tests pass
  - `POST /verify/video` handler
  - Accept multipart `file` + `mime_type` (matching enterprise pattern)
  - No auth dependency
  - Apply `public_rate_limiter`
  - Enforce 100MB size limit (`settings.public_video_max_size_bytes`)
  - Call `verify_video_c2pa()`
  - Return `PublicVideoVerifyResponse` with `correlation_id` and `verified_at`
- [x] 1.2.2 Register router in `api.py` alongside `image_verify_router` -- 28/28 verify tests pass

### 1.3 Refactor Enterprise Endpoints
- [x] 1.3.1 Enterprise `audio_attribution.py` verify handler already delegates to `verify_audio_c2pa()` -- no refactor needed, backward compat preserved
- [x] 1.3.2 Enterprise `video_attribution.py` verify handler already delegates to `verify_video_c2pa()` -- no refactor needed, backward compat preserved

### 1.4 Documentation and Configuration
- [x] 1.4.1 Update FEATURE_MATRIX.md -- audio/video verification moved from Enterprise-only to Public (Free column)
- [x] 1.4.2 PRICING_STRATEGY.md defers to FEATURE_MATRIX.md as SSOT -- no direct changes needed
- [x] 1.4.3 Public audio/video verify automatically included in OpenAPI spec via router registration

### 1.5 Testing
- [x] 1.5.1 Service-layer tests for `verify_audio_c2pa()` already exist in `test_audio_signing.py::TestAudioVerificationService`
- [x] 1.5.2 Service-layer tests for `verify_video_c2pa()` already exist in `test_video_signing.py::TestVideoVerificationService`
- [x] 1.5.3 Integration test: `POST /verify/audio` with unsigned WAV -> 200 + valid=False (test_verify_audio_unsigned_wav_returns_200_valid_false)
- [x] 1.5.4 Integration test: `POST /verify/audio` without auth -> 200 (test_verify_audio_no_auth_required)
- [x] 1.5.5 Integration test: `POST /verify/video` with unsigned MP4 -> 200 + valid=False (test_verify_video_unsigned_mp4_returns_200_valid_false)
- [x] 1.5.6 Integration test: `POST /verify/video` without auth -> 200 (test_verify_video_no_auth_required)
- [x] 1.5.7 Integration test: oversized audio (>50MB) on public endpoint -> 413 (test_verify_audio_payload_over_limit_returns_413)
- [x] 1.5.8 Integration test: oversized video (>100MB) on public endpoint -> 413 (test_verify_video_payload_over_limit_returns_413)
- [x] 1.5.9 Enterprise audio/video verify endpoints unchanged -- backward compat preserved
- [x] 1.5.10 Enterprise audio/video verify endpoints unchanged -- backward compat preserved
- [x] 1.5.11 Rate limit test: both public endpoints respect rate limiter (test_verify_audio_anonymous_rate_limited, test_verify_video_anonymous_rate_limited)

---

## Success Criteria
- [x] `POST /verify/audio` and `POST /verify/video` respond 200 with no auth header
- [x] Enterprise endpoints continue to work unchanged (backward compat)
- [x] Public endpoints have lower size limits than Enterprise counterparts
- [x] FEATURE_MATRIX.md accurately reflects verification as public for all media types
- [x] All existing tests pass (no regression from these changes)
- [x] 28/28 verify endpoint integration tests pass

## Completion Notes
Completed by TEAM_270. Public audio and video verification endpoints created at `/verify/audio` and `/verify/video`, matching the existing `/verify/image` pattern. No refactoring of enterprise endpoints needed -- the verification service functions (`verify_audio_c2pa`, `verify_video_c2pa`) were already extracted. Enterprise signing endpoints remain fully gated. Chrome extension Phase 2 is now unblocked.

### Files Created
- `enterprise_api/app/api/v1/audio_verify.py` -- public audio verify endpoint
- `enterprise_api/app/api/v1/video_verify.py` -- public video verify endpoint
- `enterprise_api/tests/integration/test_audio_verify_endpoints.py` -- 8 integration tests
- `enterprise_api/tests/integration/test_video_verify_endpoints.py` -- 7 integration tests

### Files Modified
- `enterprise_api/app/api/v1/api.py` -- registered new routers
- `enterprise_api/app/config.py` -- added `public_audio_max_size_bytes` (50MB) and `public_video_max_size_bytes` (100MB)
- `FEATURE_MATRIX.md` -- audio/video verification changed from Enterprise-only to Public
