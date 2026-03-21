# TEAM_265 -- C2PA Audio Signing Implementation

## Status: Complete

## Summary

Researched the C2PA v2.3 specification for audio format support and implemented a full audio signing pipeline for the enterprise API.

## What Was Done

### Research
- Analyzed C2PA v2.3 spec (Dec 2025) audio format support
- Validated c2pa-python 0.29.0 (c2pa-rs 0.78.4) audio capabilities
- Ran proof-of-concept: WAV sign + verify round-trip with ES256 CA->EE cert chain

### Spec Findings
- C2PA v2.3 supports: WAV (RIFF), MP3 (ID3 GEOB), FLAC (ID3), M4A/AAC (BMFF uuid box), Ogg Vorbis (new in v2.3)
- c2pa-python 0.29.0 supports: WAV, MP3, M4A/AAC -- NOT yet FLAC or Ogg Vorbis
- No audio-specific assertions needed; same manifest/JUMBF/COSE structure as images

### Implementation
- `app/utils/audio_utils.py` -- validation, format detection, MIME canonicalization
- `app/services/audio_signing_service.py` -- C2PA signing via c2pa.Builder (mirrors image_signing_service.py)
- `app/services/audio_verification_service.py` -- C2PA verification via c2pa.Reader
- `app/api/v1/enterprise/audio_attribution.py` -- POST /enterprise/audio/sign and /verify endpoints
- `app/api/v1/api.py` -- registered audio attribution router
- `tests/test_audio_signing.py` -- unit tests for utils, passthrough mode, verification

### Tests
- All audio_utils tests pass (canonicalize, detect, validate, hash, wav_info)
- Verification service handles unsigned audio and empty bytes correctly
- Signing passthrough mode works when no cert configured
- Lint (ruff check) and format (ruff format) clean

## Suggested Commit Message

```
feat: add C2PA audio signing and verification (WAV, MP3, M4A)

Implement C2PA v2.3 audio signing pipeline supporting WAV (RIFF),
MP3 (ID3), and M4A/AAC (BMFF) formats via c2pa-python. Adds audio
validation utilities, signing/verification services mirroring the
existing image pipeline, and enterprise API endpoints.

New files:
- app/utils/audio_utils.py (format detection, MIME canonicalization)
- app/services/audio_signing_service.py (C2PA Builder signing)
- app/services/audio_verification_service.py (C2PA Reader verification)
- app/api/v1/enterprise/audio_attribution.py (sign + verify endpoints)
- tests/test_audio_signing.py (unit tests)
```
