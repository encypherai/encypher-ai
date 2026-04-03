# TEAM_279: Media Signing Pipeline Gap Closure

## Status: Complete
## Current Goal: All 8 gaps closed

## Overview
Closed all identified gaps in the image and video signing pipelines. Image pipeline now has TrustMark actually wired to the microservice. Video pipeline has Redis-backed sessions, DB persistence, pHash, and correctness fixes.

## Changes Made

### 1. Fix old domain in video passthrough metadata
- `app/utils/video_metadata.py`: `verify.encypher.com` -> `verify.encypher.ai/`
- `tests/unit/test_video_metadata.py`: Updated assertions

### 2. Propagate digital_source_type through video executor
- `app/services/video_signing_executor.py`: Added `digital_source_type` parameter, forward to `sign_video()`
- `app/api/v1/enterprise/video_attribution.py`: Added `digital_source_type` Form field

### 3. WebM/MKV verify asymmetry
- `app/services/unified_verify_service.py`: Format guard returns `FORMAT_NOT_SUPPORTED_FOR_SIGNING` for unsupported video MIME types
- `tests/unit/test_unified_verify_format_guard.py`: New test file

### 4. Video pHash utility
- `app/utils/video_utils.py`: Added `compute_video_phash()` -- ffmpeg first-frame extraction + imagehash
- `tests/unit/test_video_phash.py`: New test file

### 5. SignedVideo DB model + migration
- `app/models/signed_video.py`: New model (mirrors ArticleImage)
- `app/models/__init__.py`: Registered model
- `alembic/versions/20260325_100000_add_signed_videos.py`: Migration
- `app/services/video_signing_executor.py`: Wired DB persistence + pHash after signing
- `tests/unit/test_signed_video_model.py`: New test file

### 6. Redis-backed video download cache
- `app/api/v1/enterprise/video_attribution.py`: Replaced in-memory dict with temp file + Redis metadata. In-memory fallback for dev mode.

### 7. Redis-backed video stream sessions
- `app/services/video_stream_signing_service.py`: Full rewrite of session storage. Redis primary, in-memory fallback. PEM encrypted via AESGCM. Session persisted after every mutation.
- `app/api/v1/enterprise/video_stream_attribution.py`: Updated callers for async `get_session()`

### 8. TrustMark HTTP client
- `app/services/trustmark_client.py`: New HTTP client (httpx, 30s timeout, graceful fallback)
- `app/services/rich_signing_service.py`: Wired TrustMark after sign + pHash. Updates signed bytes, hash, and DB row.
- `tests/unit/test_trustmark_client.py`: New test file

## Test Results
- 334 unit tests passing, 0 failures
- Lint clean (ruff check + format)
- Alembic chain: 20260324_100000 -> 20260325_100000 (head)

## Suggested Commit Message
```
feat(media-pipeline): close 8 image/video signing gaps

- Wire TrustMark HTTP client to image-service microservice for neural
  watermarking (Enterprise). HMAC-SHA256 payload ties watermark to
  image_id + org_id. Graceful fallback on service unavailability.
- Redis-back video stream sessions with encrypted PEM storage (AESGCM).
  In-memory fallback for dev mode. Fixes multi-worker deployment.
- Redis-back video download cache using temp files + metadata keys.
  Avoids storing 500MB blobs in Redis.
- Add SignedVideo DB model + Alembic migration. Every signed video now
  gets a persistent record with hashes, pHash, and C2PA references.
- Add compute_video_phash() using ffmpeg first-frame extraction +
  imagehash average_hash (64-bit, matches image pipeline).
- Propagate digital_source_type through video executor (was silently
  dropped).
- Fix old domain in video passthrough metadata (encypher.com ->
  encypher.ai).
- Add FORMAT_NOT_SUPPORTED_FOR_SIGNING guard for WebM/MKV verify
  requests (asymmetry with signing support).
```
