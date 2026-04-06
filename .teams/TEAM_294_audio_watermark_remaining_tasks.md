# TEAM_294 - Audio Watermark: Remaining Tasks

## Session
- Date: 2026-04-04
- Branch: feat/segment-rights-audio-watermark
- Baseline: 17 tests passing in audio-watermark-service

## Work Completed

### 1.7: MP3/M4A Format Support
- Added pydub==0.25.1 to services/audio-watermark-service (uv add)
- Added _decode_via_pydub() helper in spread_spectrum.py
- Updated decode_audio() to detect pydub-required formats via fmt hint or libsndfile fallback
- Updated encode_audio() to support MP3 and M4A output via pydub/ffmpeg
- Tests use @requires_ffmpeg marker (skipif ffmpeg absent)

### 5.3: DB Migration
- Created enterprise_api/alembic/versions/20260404_100000_add_audio_watermark_records.py
- New table: audio_watermark_records (audio_id, org_id, doc_id, watermark_applied, watermark_key, watermark_method, signed_hash, mime_type, created_at)
- Created enterprise_api/app/models/audio_watermark_record.py (AudioWatermarkRecord)
- Registered in enterprise_api/app/models/__init__.py
- Alembic chain validated: 20260401_100000 -> 20260404_100000

### 6.2, 6.4-6.9: Robustness Tests (audio-watermark-service)
Added to services/audio-watermark-service/tests/test_spread_spectrum.py:
- TestMP3FormatSupport: MP3 encode/decode + MP3 watermark roundtrip
- TestRobustnessLossyCodecs: 128kbps, 64kbps, WAV->MP3->AAC chain
- TestRobustnessNonLossy: -14 LUFS, -24 LUFS normalization, leading-30s clip
- TestImperceptibilityExtended: SNR speech/music mode verification

### 6.10-6.11: Integration Tests (enterprise_api)
Created enterprise_api/tests/unit/test_audio_watermark_integration.py:
- TestSigningPipelineWithWatermark: 7 tests covering soft-binding assertion, payload binding, client calls
- TestVerificationPipelineWithWatermark: 4 tests covering combined C2PA+watermark results

## Final Test Results
- audio-watermark-service: 27/27 passed
- enterprise_api unit: 390/390 passed
- Alembic chain: 2/2 passed

## Status: COMPLETE

## Suggested Commit Message

feat(audio-watermark): add MP3/M4A support, DB tracking, and robustness tests

1.7: Add pydub/ffmpeg integration for MP3 and M4A input/output in
decode_audio() and encode_audio(). libsndfile fast path for WAV/FLAC/OGG;
pydub ffmpeg path for lossy formats. Tests marked @requires_ffmpeg.

5.3: Add audio_watermark_records table via Alembic migration
20260404_100000. Columns: watermark_applied (bool), watermark_key (str),
watermark_method (str). Adds AudioWatermarkRecord SQLAlchemy model.

6.2, 6.4-6.9: Add robustness tests covering MP3 128kbps, MP3 64kbps,
WAV->MP3->AAC transcoding chain, loudness normalization (-14/-24 LUFS),
partial leading-clip extraction, SNR imperceptibility (speech and music).

6.10-6.11: Add integration tests for signing and verification pipelines
with mocked watermark microservice HTTP calls. 27/27 microservice tests
and 390/390 enterprise_api unit tests pass.

Note: mid-stream partial clip detection is a known limitation of the
time-domain spread-spectrum approach; documented in PRD completion notes.
