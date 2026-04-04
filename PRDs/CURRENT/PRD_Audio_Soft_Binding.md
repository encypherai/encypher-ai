# Audio Soft-Binding (Signal-Domain Watermarking)

**Status:** In Progress
**Current Goal:** Remaining: 1.7 (MP3/M4A format support), 5.2-5.3 (tier validation, DB migration), 6.2-6.12 (robustness tests)
**Driven By:** NPR evaluation (Erica, BD/Licensing). NPR's distribution team needs audio provenance that survives podcast distribution pipelines (MP3 re-encoding, loudness normalization, format conversion). Current audio signing is C2PA file-header metadata only, which gets stripped by these operations.

## Overview

Audio signing currently embeds C2PA manifests into container metadata (RIFF chunks for WAV, ID3 GEOB frames for MP3, BMFF boxes for M4A). This metadata is stripped by MP3 re-encoding, loudness normalization, format conversion, and podcast platform processing. Signal-domain watermarking embeds provenance directly into the audio signal, surviving these transformations. The architecture follows the established TrustMark pattern: a separate microservice for heavy DSP processing, an async httpx client in the enterprise API, and a `c2pa.soft_binding.v1` assertion declaring the method.

## Objectives

- Build a spread-spectrum audio watermarking microservice that embeds a 64-bit payload into the audio signal
- Survive MP3 re-encoding at 128kbps+, loudness normalization (-14 to -24 LUFS), and format conversion between MP3/AAC/WAV
- Maintain imperceptibility (configurable SNR: -20 dB for speech, -30 dB for music)
- Integrate into the existing audio signing pipeline (applied after C2PA hard-binding, same as TrustMark for images)
- Gate to Enterprise tier
- Add `c2pa.soft_binding.v1` assertion to audio C2PA manifests when watermarking is enabled

## Tasks

### 1.0 Audio Watermark Microservice

- [x] 1.1 Create `services/audio-watermark-service/` scaffold (FastAPI app, Dockerfile, pyproject.toml) following `services/image-service/` pattern -- DONE
- [x] 1.2 Implement time-domain spread-spectrum embedding core: generate PN sequences per bit, add alpha-scaled composite watermark to samples -- DONE (rewrote from broken STFT approach)
- [x] 1.3 Implement time-domain spread-spectrum detection core: correlate samples with PN sequences, extract payload from correlation signs -- DONE
- [x] 1.4 Implement configurable SNR scaling (alpha derived from watermark-to-signal ratio, -20 dB speech / -30 dB music) -- DONE
- [x] 1.5 Expose `POST /api/v1/audio/watermark` endpoint (embed) accepting audio bytes + payload -- DONE
- [x] 1.6 Expose `POST /api/v1/audio/detect` endpoint (detect) accepting audio bytes, returning payload + confidence -- DONE
- [ ] 1.7 Support WAV, MP3, M4A input/output formats (WAV done, MP3/M4A requires ffmpeg integration)
- [x] 1.8 Docker build and health check endpoint -- DONE

### 2.0 Enterprise API Client

- [x] 2.1 Create `enterprise_api/app/services/audio_watermark_client.py` (async httpx client, mirrors `trustmark_client.py`) -- DONE
- [x] 2.2 Implement `apply_watermark(audio_b64, mime_type, payload) -> Optional[Tuple[str, float]]` -- DONE
- [x] 2.3 Implement `detect_watermark(audio_b64, mime_type) -> Optional[Tuple[bool, Optional[str], float]]` -- DONE
- [x] 2.4 Implement `compute_audio_watermark_payload(audio_id, org_id) -> str` (HMAC-SHA256 truncated to 64-bit / 16 hex chars) -- DONE
- [x] 2.5 Add `audio_watermark_service_url` to `app/config.py` -- DONE

### 3.0 Signing Pipeline Integration

- [x] 3.1 Update `_sign_audio()` in `media_signing.py` and `audio_signing_executor.py` to add watermark step after C2PA signing -- DONE
- [x] 3.2 Add `c2pa.soft_binding.v1` assertion via custom_assertions when watermarking enabled -- DONE
- [x] 3.3 Add `enable_audio_watermark` form field to `/sign/media` endpoint -- DONE
- [x] 3.4 Recompute `signed_hash` over watermarked bytes after watermark application -- DONE

### 4.0 Verification Pipeline Integration

- [x] 4.1 Update `audio_verification_service.py` with `verify_audio_with_watermark()` combining C2PA + watermark detection -- DONE
- [ ] 4.2 If watermark detected: extract payload, look up `audio_id` + `org_id` from DB (deferred, requires DB schema)
- [x] 4.3 Return combined result: `PublicAudioVerifyResponse` includes `watermark_detected`, `watermark_payload`, `watermark_confidence` -- DONE

### 5.0 Tier Gating and Config

- [x] 5.1 Add `audio_watermark` feature flag to `app/core/tier_config.py` (False for free, True for enterprise, True for strategic_partner) -- DONE
- [x] 5.2 Add validation in media signing router to reject `enable_audio_watermark` on non-audio files (422) -- DONE
- [ ] 5.3 DB tracking: add `watermark_applied` (bool), `watermark_key` (str), `watermark_method` (str) to audio content tracking (new migration)

### 6.0 Robustness Testing

- [x] 6.1 Unit tests: watermark embed/detect roundtrip on WAV (12/12 passing) -- DONE
- [ ] 6.2 Unit tests: watermark embed/detect roundtrip on MP3
- [x] 6.3 Unit tests: tier gating (7/7 passing) -- DONE
- [x] 6.3a Robustness test: survive PCM16 quantization (WAV encode/decode roundtrip) -- DONE
- [x] 6.3b Robustness test: survive amplitude scaling (loudness normalization sim) -- DONE
- [x] 6.3c Robustness test: survive additive noise at -30 dB -- DONE
- [x] 6.3d Robustness test: no false positive on clean audio -- DONE
- [x] 6.3e Robustness test: wrong seed does not extract correct payload -- DONE
- [ ] 6.4 Robustness test: survive MP3 re-encoding at 128kbps
- [ ] 6.5 Robustness test: survive MP3 re-encoding at 64kbps (lower bound)
- [ ] 6.6 Robustness test: survive loudness normalization (-14 LUFS Spotify, -16 LUFS Apple, -24 LUFS broadcast)
- [ ] 6.7 Robustness test: survive WAV -> MP3 -> AAC format conversion chain
- [ ] 6.8 Robustness test: survive partial clip extraction (30-second segment from 30-minute file)
- [ ] 6.9 Imperceptibility test: SNR measurement, PESQ/POLQA score above threshold
- [ ] 6.10 Integration test: full signing pipeline with watermark enabled produces valid C2PA manifest + detectable watermark
- [ ] 6.11 Integration test: verification pipeline returns combined C2PA + watermark results
- [ ] 6.12 All tests passing -- pytest

## Key Architectural Decisions

- **Spread-spectrum first, neural later.** Spread-spectrum requires no ML training or GPU. Numpy only (scipy was removed). Neural watermarking (AudioSeal or similar) is Phase 2 for maximum robustness.
- **Time-domain, not STFT.** Initial STFT-based approach failed (modified magnitudes + original phases do not survive the STFT-ISTFT-STFT roundtrip). Time-domain spread-spectrum adds PN sequences directly to audio samples, correlates in time domain for detection. Simpler and more robust.
- **Microservice pattern.** Follows the TrustMark architecture exactly. Keeps DSP-heavy processing off the main API event loop. Estimated 200-500ms for a 30-minute episode.
- **Applied after C2PA hard-binding.** Watermarking modifies content bytes, so the C2PA hard-binding hash no longer matches. This is by design (same trade-off as TrustMark for images). The `c2pa.soft_binding.v1` assertion documents the method.
- **64-bit payload.** Sufficient for HMAC-based lookup key (16 hex chars). More bits = lower robustness per bit. Matches the TrustMark pattern.
- **Configurable SNR.** Speech content (NPR's primary use case) is more forgiving than music. -20 dB for speech, -30 dB for music. Exposed as a parameter, not hardcoded.

## Dependencies

- `numpy` (already in project)
- `soundfile` (new -- format-agnostic audio I/O via libsndfile)
- `fastapi`, `uvicorn`, `httpx` (established pattern from image-service)
- Note: `scipy` was removed -- time-domain approach requires only numpy

## Success Criteria

- Watermark survives MP3 re-encoding at 128kbps with >95% detection rate
- Watermark survives loudness normalization at -14 LUFS with >90% detection rate
- Watermark is imperceptible (SNR below configured threshold, no audible artifacts in speech or music)
- Full signing pipeline produces C2PA manifest with `c2pa.soft_binding.v1` assertion + detectable watermark
- Verification pipeline returns combined C2PA + watermark result
- Free tier callers receive 403 when using `enable_audio_watermark`
- All tests passing with verification markers

## Completion Notes

(Filled when PRD is complete.)
