# TEAM_295 - Spread-Spectrum ECC + Video Watermark Implementation

**Status:** Substantially Complete
**Branch:** feat/segment-rights-audio-watermark
**PRD:** PRDs/CURRENT/PRD_Video_Soft_Binding.md

## Scope

Implement the concatenated ECC scheme (RS(32,8) + rate-1/3 K=7 convolutional + soft Viterbi) and the video watermark microservice. Backport ECC to the audio watermark service. Wire into all signing and verification pipelines.

## Completed Work

### Wave 1 (parallel): Foundations
- **ECC Core Module** (`services/shared/spread_spectrum_ecc.py`): RS(32,8) outer code + rate-1/3 K=7 convolutional inner code + 64-state soft Viterbi decoder + erasure bridge. 17 tests.
- **Video Watermark Service** (`services/video-watermark-service/`): FastAPI scaffold on port 8012, PyAV video codec, spread-spectrum embed/detect on Y-channel, block-based processing. 11 tests.
- **Enterprise API Client** (`enterprise_api/app/services/video_watermark_client.py`): httpx async client, tier gating, DB migration (video_watermark_records), config. 15 tests.

### Wave 2 (parallel): ECC Integration
- **Video ECC**: Wired ECC into video embed/detect (786 coded bits per 64-bit payload). 13 tests.
- **Audio ECC Backport**: Wired same ECC into audio embed/detect. All 27 pre-existing tests pass unchanged. Added 2 new ECC-specific tests. Updated soft-binding assertion with `"ecc": "rs32_8_conv_r3_k7"`. 29 tests.

### Wave 3 (parallel): Pipeline Integration
- **VOD Pipeline**: `enable_video_watermark` in media_signing.py `sign_media()` + `_sign_video()`, video_signing_executor.py, video_attribution.py. Full assertion + watermark-after-C2PA pattern.
- **Live Stream Pipeline**: Session-level watermark payload, per-segment embedding, Redis serialization, stream_attribution.py endpoints.
- **Verification Pipeline**: `verify_video_with_watermark()` combining C2PA + watermark detection. Updated public + enterprise verification endpoints.

### Wave 4 (parallel): Tests + Docs
- **Integration Tests**: 29 tests covering tier gating, signing pipeline, verification, stream watermark.
- **Documentation**: 8 files updated (FEATURE_MATRIX, CHANGELOG, DOCUMENTATION_INDEX, services/README, MICROSERVICES_ARCHITECTURE, COMPLIANCE, enterprise_api/README, root README).

## Test Summary

| Component | Tests | Status |
|-----------|-------|--------|
| ECC Core (services/shared) | 17 | Passed |
| Video Service | 13 | Passed |
| Audio Service | 29 | Passed |
| Enterprise API | 44 | Passed |
| **Total** | **103** | **All passed** |

## Remaining Tasks (not critical for this session)

- 7.4-7.8: Video codec robustness tests (H.264 CRF 23/28, H.265, resolution scaling, bitrate reduction) -- require encoding test videos
- 7.12: Performance benchmark (30-sec 1080p processing time)
- 10.7-10.8: Audio extreme robustness tests (48kbps MP3, triple transcode)
- 12.1: Video watermark service README

## Files Created (new)

- `services/shared/pyproject.toml`
- `services/shared/__init__.py`
- `services/shared/spread_spectrum_ecc.py`
- `services/shared/tests/__init__.py`
- `services/shared/tests/test_spread_spectrum_ecc.py`
- `services/video-watermark-service/` (full directory: app/, tests/, Dockerfile, pyproject.toml)
- `enterprise_api/app/services/video_watermark_client.py`
- `enterprise_api/app/models/video_watermark_record.py`
- `enterprise_api/alembic/versions/20260405_100000_add_video_watermark_records.py`
- `enterprise_api/tests/unit/test_video_watermark_client.py`
- `enterprise_api/tests/unit/test_video_watermark_integration.py`

## Files Modified

- `enterprise_api/app/config.py` (added video_watermark_service_url)
- `enterprise_api/app/core/tier_config.py` (added video_watermark feature)
- `enterprise_api/app/models/__init__.py` (registered VideoWatermarkRecord)
- `enterprise_api/app/routers/media_signing.py` (added enable_video_watermark to sign_media + _sign_video)
- `enterprise_api/app/services/video_signing_executor.py` (added watermark logic)
- `enterprise_api/app/services/video_verification_service.py` (added verify_video_with_watermark)
- `enterprise_api/app/services/video_stream_signing_service.py` (added session watermark + per-segment embedding)
- `enterprise_api/app/services/audio_watermark_client.py` (added ecc field to assertion)
- `enterprise_api/app/api/v1/enterprise/video_attribution.py` (watermark params + response fields)
- `enterprise_api/app/api/v1/enterprise/video_stream_attribution.py` (watermark form field + response)
- `enterprise_api/app/api/v1/video_verify.py` (watermark fields in response)
- `services/audio-watermark-service/app/services/spread_spectrum.py` (ECC backport)
- `services/audio-watermark-service/pyproject.toml` (added reedsolo)
- `services/audio-watermark-service/tests/test_spread_spectrum.py` (2 new ECC tests)
- 8 documentation files (FEATURE_MATRIX, CHANGELOG, DOCUMENTATION_INDEX, services/README, MICROSERVICES_ARCHITECTURE, COMPLIANCE, enterprise_api/README, root README)

## Suggested Commit Message

```
feat: add video spread-spectrum watermarking with concatenated ECC

Add video-watermark-service (port 8012) implementing spread-spectrum
watermarking on the Y-channel luminance of decoded video frames using
HMAC-SHA256 PN sequences, matching the audio watermark architecture.

Implement concatenated error-correction coding (RS(32,8) outer code +
rate-1/3 K=7 convolutional inner code + soft-decision Viterbi decoder)
in services/shared/spread_spectrum_ecc.py. The scheme expands the
64-bit payload to 786 coded bits, providing ~8-10 dB coding gain via
soft channel information that hard-decision RS cannot exploit.

Backport ECC to the audio watermark service (all 27 existing tests
pass unchanged). Wire video watermarking into all signing pipelines
(VOD via media_signing.py and video_signing_executor.py, live stream
via video_stream_signing_service.py) and verification pipeline
(verify_video_with_watermark combining C2PA + watermark detection).

Add enterprise API client, tier gating, DB migration, and 103 tests
across all components.
```
