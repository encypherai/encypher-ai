# Video Soft-Binding (Signal-Domain Watermarking)

**Status:** In Progress
**Current Goal:** Waves 1-4 complete. 103 tests passing. Remaining: codec robustness tests (7.4-7.8, 7.12), audio extreme robustness (10.7-10.8).
**Driven By:** Platform distribution gap. Video platforms (YouTube, social media, CDNs) transcode uploaded video, stripping container-level C2PA metadata (ISO BMFF uuid boxes, RIFF C2PA chunks). Current video signing provides C2PA hard-binding only. Signal-domain watermarking embeds provenance directly into video frame pixels, surviving H.264/H.265 re-encoding, resolution scaling, bitrate changes, and platform transcoding.

## Overview

Video signing currently embeds C2PA manifests into container metadata (ISO BMFF uuid boxes for MP4/MOV/M4V, RIFF C2PA chunks for AVI). This metadata is stripped by H.264/H.265 re-encoding, resolution scaling, bitrate changes, and platform transcoding pipelines (YouTube, Facebook, Twitter, TikTok). Signal-domain watermarking embeds a 64-bit payload into the luminance (Y) channel of decoded video frames using spread-spectrum pseudo-noise sequences, the same mathematical technique proven for audio in the `audio-watermark-service`. The architecture follows the established pattern: a separate microservice for heavy frame-level DSP, an async httpx client in the enterprise API, and a `c2pa.soft_binding.v1` assertion declaring the method.

Two integration surfaces exist: VOD signing (`POST /sign/media`, `POST /enterprise/video/sign`) and live stream signing (`POST /enterprise/video/stream/{id}/segment`). VOD watermarking processes the full file after C2PA hard-binding. Live stream watermarking processes each segment independently, embedding the same payload across the session so detection on any segment recovers the provenance link.

## Objectives

- Build a spread-spectrum video watermarking microservice that embeds a 64-bit payload into the luminance channel of decoded video frames
- Survive H.264 re-encoding at 1-10 Mbps, H.265 re-encoding at 0.5-5 Mbps, resolution scaling (1080p to 720p, 4K to 1080p), and platform-typical transcoding pipelines
- Maintain visual imperceptibility (configurable watermark-to-signal ratio, target -30 dB to -40 dB depending on content type)
- Integrate into both VOD and live stream signing pipelines (applied after C2PA hard-binding)
- Gate to Enterprise tier
- Add `c2pa.soft_binding.v1` assertion to video C2PA manifests when watermarking is enabled
- Reuse the proven PN sequence generation (`HMAC-SHA256` per bit, `default_rng(SeedSequence(32 bytes))`) and correlation-based detection from the audio implementation

## Algorithm

The video algorithm extends the audio spread-spectrum approach to 2D frame data:

### Embedding

1. Encode the 64-bit payload through the concatenated ECC pipeline: RS(32,8) outer code produces 256 bits, rate-1/3 K=7 convolutional inner code produces ~774 coded bits.
2. Decode video to raw frames using ffmpeg (via PyAV or subprocess).
3. Extract the luminance (Y) channel from each frame (convert RGB to YCbCr if needed).
4. Flatten all Y-channel pixels across all frames into a single 1D signal vector.
5. For each of ~774 coded bits, generate a PN chip sequence of length equal to the total pixel count using `HMAC-SHA256(seed, bit_index)`, identical to the audio approach.
6. Compute embedding strength alpha from the target watermark-to-signal ratio (WSR) and signal power: `alpha = sqrt(signal_power * 10^(wsr_db/10) / coded_bits)`.
7. Add `alpha * sum(bit_sign[i] * pn[i])` to the flattened Y signal.
8. Reshape back to per-frame Y channels, merge with original CbCr, convert back to RGB.
9. Re-encode video with original codec settings using ffmpeg.

### Detection

1. Decode video to frames, extract Y channel, flatten to 1D.
2. For each coded bit, correlate the Y signal with the expected PN sequence.
3. Extract soft values: correlation magnitude (confidence per bit) and sign (hard decision).
4. Feed soft values into inner Viterbi decoder to recover RS-coded bytes.
5. Feed RS-coded bytes into outer RS decoder (with erasure hints from low-confidence blocks).
6. Reconstruct 64-bit payload hex from decoded data symbols.

### Error Correction Coding (Concatenated Code)

Signal-domain watermarks face bit errors from codec quantization, resampling, and noise. A concatenated coding scheme provides maximum robustness by combining two complementary error-correction layers, exploiting the soft information (correlation magnitudes) that spread-spectrum detection naturally produces.

**Encode pipeline (embedding):**

```
64-bit payload (8 bytes)
    |
    v
Outer: Reed-Solomon RS(32, 8) over GF(2^8)
    -> 8 data symbols + 24 parity symbols = 32 bytes = 256 bits
    -> Corrects up to 12 symbol errors or 24 erasures (known positions)
    |
    v
Inner: Rate-1/3 convolutional code, K=7, generators [171, 133, 165] (octal)
    -> 256 data bits -> ~774 coded bits (with tail bits for trellis termination)
    -> Each data bit produces 3 coded bits for maximum redundancy
    |
    v
~774 PN sequences embedded into Y-channel pixels
```

**Decode pipeline (detection):**

```
Y-channel pixels
    |
    v
Correlate with ~774 PN sequences -> soft values (float, sign = bit, magnitude = confidence)
    |
    v
Inner: Soft-decision Viterbi decoder (exploits correlation magnitudes as channel reliability)
    -> ~774 soft inputs -> 256 hard bits (32 RS symbols)
    -> ~8-10 dB coding gain over hard decisions alone
    |
    v
Outer: RS(32, 8) decoder with erasure support
    -> Low-confidence Viterbi outputs flagged as erasures
    -> Corrects residual errors after Viterbi decoding
    -> Recovers original 8 data bytes = 64-bit payload
```

**Why concatenated coding:**

- **Outer RS corrects burst errors.** Video codecs quantize in 8x8 or 16x16 blocks, producing correlated (bursty) errors. RS over GF(2^8) treats each byte as a symbol, correcting up to 12 corrupted symbols regardless of which bits within each symbol are wrong.
- **Inner convolutional code corrects random errors.** Rate-1/3 K=7 is the standard deep-space code (Voyager, Mars rovers). The Viterbi decoder exploits soft information, the correlation magnitude from spread-spectrum detection, for ~8-10 dB coding gain over hard decisions. Text micro mode's RS cannot exploit soft information because character embedding is inherently binary (present/absent). Signal-domain watermarking produces continuous-valued correlations, making convolutional + Viterbi the natural fit.
- **Erasure bridging.** When the Viterbi decoder has low confidence on certain outputs, those positions are passed to the RS decoder as erasures (not errors). RS corrects twice as many erasures as errors (24 vs 12), so this soft-to-erasure bridge further improves robustness.
- **Proven combination.** This is the same concatenated coding architecture used in deep-space communication (CCSDS standard), chosen for the same reason: maximize reliability over a noisy channel with limited signal power.

**Implementation notes:**

- `reedsolo` is already used in the enterprise API for text ECC (`vs256_rs_crypto.py`, `legacy_safe_rs_crypto.py`). The watermark service will use the same library with `RSCodec(24)` (24 parity symbols).
- Rate-1/3 K=7 convolutional coding and Viterbi decoding will be implemented in pure numpy/Python within the watermark service. No external library needed; the trellis has only 64 states (2^(K-1)) and the implementation is straightforward. Alternatively, `commpy` provides a reference implementation if preferred.
- The total coded bit count (~774) replaces the raw 64 bits. Each coded bit gets its own PN sequence. This reduces the per-bit spreading gain by ~12x (774/64), but the ~10 dB ECC coding gain more than compensates: net improvement is ~2-4 dB over uncoded 64-bit at the same WSR.
- The same ECC scheme applies to audio watermarking. A shared `ecc/` module in the services directory or a `spread_spectrum_ecc.py` file within each service can provide the encode/decode functions.

### Live Stream Variant

For live stream segments, each segment is watermarked independently with the same payload and seed. Detection on any individual segment recovers the full 64-bit payload. This works because the PN sequences are seeded by the payload bit index and the shared secret, not by the video content. Segment length variation is handled by generating PN sequences matching each segment's pixel count.

## Dependencies

- `numpy` - array operations, PN sequence generation, Viterbi trellis computation (same as audio)
- `PyAV` - Python bindings for ffmpeg, frame-level video decode/encode without subprocess overhead
- `reedsolo` - Reed-Solomon codec over GF(2^8), already used in enterprise API (`vs256_rs_crypto.py`). Used for outer ECC code RS(32,8) with 24 parity symbols
- `fastapi`, `uvicorn`, `httpx` - established microservice pattern
- `pydantic`, `pydantic-settings` - config and request validation

System dependency: `ffmpeg` (required by PyAV, installed in Docker image via apt).

No scipy, no ML models, no GPU. The convolutional encoder and Viterbi decoder are implemented in pure numpy (64-state trellis, ~774 coded bits, trivial compute). The algorithm is pure numpy operating on decoded pixel arrays.

## Tasks

### 1.0 Video Watermark Microservice

- [x] 1.1 Create `services/video-watermark-service/` scaffold (FastAPI app, Dockerfile, pyproject.toml) following `audio-watermark-service/` pattern -- DONE
- [x] 1.2 Add `PyAV` dependency for frame-level video decode/encode; verify ffmpeg availability in Docker image -- DONE
- [x] 1.3 Implement `decode_video(video_bytes, mime_type) -> Tuple[NDArray, int, VideoMeta]` that returns Y-channel pixel array (flattened across frames), frame rate, and metadata needed for re-encoding (codec, resolution, pixel format, bitrate) -- DONE
- [x] 1.4 Implement `encode_video(y_frames, cb_frames, cr_frames, meta) -> bytes` that re-encodes frames back to the original container format -- DONE
- [x] 1.5 Adapt `_generate_chips()` from audio service (identical HMAC-SHA256 PN generation, no changes needed) -- DONE
- [x] 1.6 Implement `embed(y_signal, payload, seed, wsr_db) -> Tuple[NDArray, float]` operating on flattened Y-channel pixels -- DONE (ECC wiring in 9.7)
- [x] 1.7 Implement `detect(y_signal, seed) -> Tuple[bool, Optional[str], float]` operating on flattened Y-channel pixels -- DONE (ECC wiring in 9.8)
- [x] 1.8 Expose `POST /api/v1/video/watermark` endpoint accepting video bytes (base64 or multipart) + payload + optional WSR override -- DONE
- [x] 1.9 Expose `POST /api/v1/video/detect` endpoint accepting video bytes, returning detected payload + confidence -- DONE
- [x] 1.10 Health check endpoint (`GET /health`) -- DONE
- [x] 1.11 Docker build with ffmpeg system dependency, port 8012 -- DONE

### 2.0 Enterprise API Client

- [x] 2.1 Create `enterprise_api/app/services/video_watermark_client.py` (async httpx client, mirrors `audio_watermark_client.py` exactly) -- DONE
- [x] 2.2 Implement `apply_watermark(video_b64, mime_type, payload, wsr_db) -> Optional[Tuple[str, float]]` -- DONE
- [x] 2.3 Implement `detect_watermark(video_b64, mime_type) -> Optional[Tuple[bool, Optional[str], float]]` -- DONE
- [x] 2.4 Implement `compute_video_watermark_payload(video_id, org_id) -> str` (HMAC-SHA256 truncated to 64 bits / 16 hex chars) -- DONE
- [x] 2.5 Implement `compute_video_watermark_key(video_id, org_id) -> str` for DB storage -- DONE
- [x] 2.6 Add `SOFT_BINDING_ASSERTION_VIDEO` constant (`method: "encypher.spread_spectrum_video.v1"`) -- DONE
- [x] 2.7 Implement `apply_watermark_to_signed_video(signed_bytes, mime_type, video_id, org_id) -> Optional[Tuple[bytes, str, str]]` shared helper (mirrors `apply_watermark_to_signed_audio`) -- DONE
- [x] 2.8 Add `video_watermark_service_url` to `app/config.py` -- DONE

### 3.0 VOD Signing Pipeline Integration

- [x] 3.1 Add `enable_video_watermark: bool = Form(default=False)` to `sign_media()` endpoint in `media_signing.py` -- DONE
- [x] 3.2 Add non-video rejection validation (422 if `enable_video_watermark` on non-video files) -- DONE
- [x] 3.3 Update `_sign_video()` in `media_signing.py`: prepend `SOFT_BINDING_ASSERTION_VIDEO` to `custom_assertions` when enabled, call `apply_watermark_to_signed_video()` after C2PA signing -- DONE
- [x] 3.4 Update `execute_video_signing()` in `video_signing_executor.py` with same watermark-after-C2PA logic, using shared helper -- DONE
- [x] 3.5 Add `enable_video_watermark` form field to `POST /enterprise/video/sign` in `video_attribution.py` -- DONE
- [x] 3.6 Recompute `signed_hash` and `size_bytes` over watermarked bytes after watermark application -- DONE
- [x] 3.7 Return `watermark_applied` and `watermark_key` in signing responses -- DONE

### 4.0 Live Stream Signing Pipeline Integration

- [x] 4.1 Add `enable_video_watermark` parameter to `start_stream_session()` in `video_stream_signing_service.py`, store flag in `VideoStreamSession` -- DONE
- [x] 4.2 Update `sign_segment()` to apply watermark to each segment after C2PA signing when session flag is set -- DONE
- [x] 4.3 Add `c2pa.soft_binding.v1` assertion to per-segment manifests when watermarking enabled -- DONE
- [x] 4.4 Use same payload across all segments in a session (compute once at session start from `session_id` + `org_id`) -- DONE
- [x] 4.5 Add `enable_video_watermark` form field to `POST /enterprise/video/stream/start` in `video_stream_attribution.py` -- DONE
- [x] 4.6 Return `watermark_applied` in segment signing responses -- DONE

### 5.0 Verification Pipeline Integration

- [x] 5.1 Create `verify_video_with_watermark()` in video_verification_service.py, combining C2PA verification + watermark detection (mirrors `verify_audio_with_watermark`) -- DONE
- [x] 5.2 Update video verification endpoints (public + enterprise) to return `watermark_detected`, `watermark_payload`, `watermark_confidence` alongside C2PA results -- DONE
- [x] 5.3 DB migration: `video_watermark_records` table (mirrors `audio_watermark_records` structure) with `video_id`, `organization_id`, `document_id`, `session_id` (nullable, for stream segments), `watermark_applied`, `watermark_key`, `watermark_method`, `signed_hash`, `mime_type`, `created_at` -- DONE (migration 20260405_100000)

### 6.0 Tier Gating and Config

- [x] 6.1 Add `video_watermark` feature flag to `tier_config.py` (False for free, True for enterprise, True for strategic_partner) -- DONE
- [x] 6.2 Add validation in `sign_media()` to reject `enable_video_watermark` on non-video files (422) -- DONE
- [x] 6.3 Add validation in `video_attribution.py` to reject watermark requests from non-enterprise tiers (403) -- DONE (enterprise tier gate already covers this via `require_enterprise_video`)

### 7.0 Testing - Microservice

- [x] 7.1 Unit tests: PN chip generation (determinism, uniqueness, value range) -- 3 tests passing
- [x] 7.2 Unit tests: embed/detect roundtrip on uncompressed frames (synthetic Y-channel pixels) -- 2 tests passing
- [x] 7.3 Unit tests: embed/detect roundtrip on short MP4 video (generate synthetic test video via PyAV) -- DONE (codec roundtrip tests)
- [ ] 7.4 Robustness test: survive H.264 CRF 23 re-encoding (default quality)
- [ ] 7.5 Robustness test: survive H.264 CRF 28 re-encoding (lower quality)
- [ ] 7.6 Robustness test: survive H.265 CRF 28 re-encoding
- [ ] 7.7 Robustness test: survive resolution scaling 1080p to 720p
- [ ] 7.8 Robustness test: survive bitrate reduction (10 Mbps to 2 Mbps)
- [x] 7.9 Robustness test: no false positive on clean video -- DONE
- [x] 7.10 Robustness test: wrong seed does not extract correct payload -- DONE
- [x] 7.11 Imperceptibility test: PSNR above threshold (target > 40 dB for -30 dB WSR) -- DONE
- [ ] 7.12 Performance test: processing time for 30-second 1080p video (target < 10 seconds)

### 8.0 Testing - Enterprise API

- [x] 8.1 Unit tests: `video_watermark_client.py` (configured/unconfigured, payload, key, assertion) -- 15 tests passing
- [x] 8.2 Unit tests: tier gating (`video_watermark` flag in FREE/ENTERPRISE/STRATEGIC_PARTNER) -- 8 tests passing
- [x] 8.3 Integration tests: VOD signing pipeline with mocked watermark service (assertion, payload, graceful degradation) -- 11 tests passing
- [x] 8.4 Integration tests: live stream signing pipeline with mocked watermark service (session storage, payload determinism) -- 6 tests passing
- [x] 8.5 Integration tests: verification pipeline returns combined C2PA + watermark results -- 4 tests passing
- [x] 8.6 All tests passing: 103/103 total (17 ECC + 13 video service + 29 audio service + 44 enterprise API)

### 9.0 Error Correction Coding

- [x] 9.1 Implement `spread_spectrum_ecc.py` in services/shared/: `ecc_encode(payload_bytes: bytes) -> NDArray[np.uint8]` that applies RS(32,8) outer code then rate-1/3 K=7 convolutional inner code, returning 786 coded bits -- DONE
- [x] 9.2 Implement `ecc_decode(soft_bits: NDArray[np.float64]) -> Tuple[Optional[bytes], int]` that applies soft Viterbi inner decoder then RS outer decoder, returning (payload_bytes_or_None, corrected_error_count) -- DONE
- [x] 9.3 Implement rate-1/3 K=7 convolutional encoder: generators [171, 133, 165] (octal), trellis termination via K-1 tail bits -- DONE
- [x] 9.4 Implement soft-decision Viterbi decoder: 64-state trellis, path metric accumulation using soft channel values (np.einsum), traceback to recover ML bit sequence -- DONE
- [x] 9.5 Implement Viterbi-to-RS erasure bridge: flag decoded bits where Viterbi path metric delta is below a confidence threshold as erasures for the RS decoder -- DONE
- [x] 9.6 Add `reedsolo` dependency to video-watermark-service `pyproject.toml`; use `RSCodec(24)` for 24 parity symbols over GF(2^8) -- DONE
- [x] 9.7 Wire ECC into `embed()`: call `ecc_encode()` on payload before PN sequence generation -- DONE (786 coded bits, alpha/CODED_BITS)
- [x] 9.8 Wire ECC into `detect()`: pass soft correlation values to `ecc_decode()` instead of hard-decision bit extraction -- DONE (soft Viterbi + RS decode)
- [x] 9.9 Unit tests: RS(32,8) encode/decode roundtrip, error injection (up to 12 symbol errors correctable) -- 4 tests passing
- [x] 9.10 Unit tests: convolutional encode/decode roundtrip, soft vs hard decision comparison -- 3 tests passing
- [x] 9.11 Unit tests: full ECC pipeline roundtrip (64-bit payload through encode -> add noise -> decode) -- 4 tests passing (no noise, moderate, heavy, extreme)
- [x] 9.12 Unit tests: erasure bridge (low-confidence bits correctly flagged, RS decoder exploits erasures) -- 2 tests passing

### 10.0 Audio Watermark ECC Backport

The same concatenated ECC scheme improves the existing audio watermark service. These tasks are scoped here rather than re-opening the audio PRD.

- [x] 10.1 Create shared `spread_spectrum_ecc.py` module in `services/shared/` -- DONE (17 tests passing)
- [x] 10.2 Wire ECC into audio `embed()` in `spread_spectrum.py`: encode 64-bit payload to 786 coded bits before PN spreading -- DONE
- [x] 10.3 Wire ECC into audio `detect()` in `spread_spectrum.py`: soft Viterbi + RS decode on correlation values -- DONE
- [x] 10.4 Update audio watermark API contracts: `/api/v1/audio/watermark` and `/api/v1/audio/detect` responses unchanged (payload hex in, payload hex out), ECC is internal -- DONE (all 27 pre-existing tests pass unchanged)
- [x] 10.5 Update `c2pa.soft_binding.v1` assertion data to include `"ecc": "rs32_8_conv_r3_k7"` method field -- DONE
- [x] 10.6 Re-run all 27 audio watermark tests (robustness, imperceptibility, integration) with ECC enabled -- DONE (29/29 passing, all 27 original + 2 new)
- [ ] 10.7 Add new robustness test: survive MP3 re-encoding at 48 kbps (currently untested, expected to fail without ECC)
- [ ] 10.8 Add new robustness test: survive double transcoding WAV -> MP3 64kbps -> AAC 64kbps -> MP3 128kbps

### 11.0 Image Spread-Spectrum Watermarking (Future PRD)

Image watermarking currently uses TrustMark (Adobe Research, neural model, Apache 2.0). TrustMark has internal ECC (`use_ECC=True`) but we do not own the algorithm, cannot tune the ECC parameters, and have not verified its robustness against specific codec pipelines. The same spread-spectrum + concatenated ECC architecture used for audio and video should replace TrustMark for full algorithm ownership.

Scope: new `services/image-watermark-service/`, spread-spectrum embedding in spatial-domain luminance (same Y-channel approach as video but on single frames), concatenated RS + convolutional ECC, integration into the existing image signing pipeline (`rich_signing_service.py`), verification pipeline, tier gating. TrustMark remains available as a fallback or Phase 2 neural option.

This section is a placeholder. A dedicated PRD will be created when this work is scoped. Tracked in `TODO.md`.

### 12.0 Documentation

- [ ] 12.1 Create `services/video-watermark-service/README.md` following audio service pattern
- [x] 12.2 Update `FEATURE_MATRIX.md` with video soft-binding rows -- DONE (v2.3)
- [x] 12.3 Update `CHANGELOG.md` with video watermarking entry -- DONE
- [x] 12.4 Update `DOCUMENTATION_INDEX.md` with video watermark service and PRD reference -- DONE
- [x] 12.5 Update `services/README.md` with video-watermark-service in service table and diagram -- DONE
- [x] 12.6 Update `docs/architecture/MICROSERVICES_ARCHITECTURE.md` with service entry -- DONE (service #11, port 8012)
- [x] 12.7 Update `docs/c2pa/COMPLIANCE.md` with video soft-binding assertion reference and audit log entry -- DONE
- [x] 12.8 Update `enterprise_api/README.md` tier matrix with video watermarking row -- DONE
- [x] 12.9 Update root `README.md` with service count and enterprise features -- DONE

## Key Architectural Decisions

- **Luminance-only embedding.** The watermark is applied to the Y (luma) channel only, not chroma (Cb/Cr). Video codecs allocate most bits to luma and subsample chroma (4:2:0), so luma embedding survives compression better. Chroma artifacts from watermarking would also be more visually noticeable.
- **Full-video spreading.** Each payload bit's PN sequence spans all pixels across all frames (flattened to 1D). This maximizes spreading gain and robustness. The trade-off: detection requires the full video (or a leading segment of known length). This mirrors the audio approach.
- **Live stream: per-segment embedding with shared payload.** Each segment is watermarked independently with the same payload and seed. PN sequence length matches the segment's pixel count, not the full stream. Detection on any single segment recovers the payload. This avoids requiring the full stream for detection, which is critical for live content.
- **PyAV over subprocess.** PyAV provides Python bindings to ffmpeg's libav* libraries with frame-level access, avoiding shell-out overhead and temporary files. Decoding and encoding happen in memory.
- **Applied after C2PA hard-binding.** Same trade-off as audio and image watermarking. The `c2pa.soft_binding.v1` assertion documents the method in the manifest, enabling verifiers to understand why the hard-binding hash no longer matches.
- **Separate microservice.** Video frame decoding and pixel-level DSP is compute-intensive. Isolating it from the enterprise API event loop prevents watermarking latency from blocking other requests. The httpx client handles timeouts and graceful degradation.
- **64-bit payload.** Same as audio. Sufficient for HMAC-based lookup key. More bits = lower robustness per bit at a given WSR.
- **No GPU, no ML.** Pure numpy on decoded pixel arrays. Keeps the service lightweight and deterministic. Neural video watermarking (e.g., HiDDeN, RivaGAN) is a Phase 2 option if spread-spectrum robustness proves insufficient against aggressive quantization.
- **Concatenated ECC (RS + convolutional + soft Viterbi).** The same architecture used in deep-space communication (CCSDS). Outer RS(32,8) corrects burst errors from codec block quantization. Inner rate-1/3 K=7 convolutional code with soft-decision Viterbi exploits the continuous-valued correlation magnitudes that spread-spectrum detection produces. This is the key advantage over text micro mode's hard-decision RS: signal-domain watermarks provide soft channel information, and soft Viterbi captures ~8-10 dB of coding gain that hard decisions leave on the table. The 64-bit payload expands to ~774 coded bits, a 12x redundancy factor that trades per-bit spreading gain for ECC gain, with a net improvement of ~2-4 dB.
- **Rate-1/3 over rate-1/2.** Rate-1/3 provides an additional ~1.5 dB coding gain over rate-1/2 at the cost of ~50% more coded bits (774 vs 518). Since the watermark channel bandwidth (total Y-channel pixels per video) is enormous relative to the coded bit count, the extra bits are negligible. Maximum robustness is the stated priority.
- **Shared ECC module across audio and video.** The ECC encode/decode pipeline is media-agnostic: it operates on payload bytes in, soft correlation values out. Both watermark services share the same implementation to avoid drift.

## Performance Considerations

Video files are larger than audio, and frame decoding adds overhead. Estimated processing times:

| Content | Resolution | Duration | Estimated Embed Time |
|---------|-----------|----------|---------------------|
| Short clip | 720p | 30 sec | 2-5 sec |
| Standard video | 1080p | 5 min | 15-30 sec |
| Long video | 1080p | 30 min | 60-120 sec |
| 4K content | 2160p | 5 min | 30-60 sec |

Timeouts should be generous: `_WATERMARK_TIMEOUT = 300.0` (5 min) for the enterprise API client, scaling with file size. The microservice should stream frames rather than loading all into memory at once for videos exceeding available RAM.

For large files (> 50 MB), the existing video signing pipeline already uses a download URL pattern with Redis-cached temp files. The watermark step should operate on the same bytes before the download URL is generated.

### Memory Management

A 5-minute 1080p video at 30 fps = 9,000 frames x 1920 x 1080 pixels = ~18.7 billion Y-channel values (as float64: ~149 GB). This exceeds available memory.

Two strategies:

1. **Block-based processing (recommended for Phase 1).** Process the video in fixed-size blocks (e.g., 300 frames / 10 seconds at 30 fps). Generate PN sequences per block. Detection correlates per block and averages. This caps memory at ~4 GB for 1080p and enables streaming.
2. **Spatial subsampling.** Embed into every Nth pixel. Reduces the effective signal length but also reduces memory. Requires careful handling to avoid aliasing with codec block boundaries (8x8 or 16x16 macroblocks).

Block-based processing is the better fit because it aligns with the live stream per-segment approach (a block is conceptually a segment), and it enables the same detection algorithm for both VOD and live content.

### Block-Based Embedding Detail

1. Split video into blocks of B frames (e.g., B=300 for 10 seconds at 30 fps).
2. For each block, flatten Y-channel pixels to a 1D vector of length `B * width * height`.
3. Generate PN sequences of that length per coded bit (~774 sequences per block, same HMAC-SHA256 seeding, with block_index appended to the seed material).
4. Embed all ~774 coded bits into each block independently.
5. For detection, correlate each block independently to extract ~774 soft values per block. Average soft values across blocks before feeding into the Viterbi decoder. This provides soft combining gain: even if individual blocks have high noise, averaging across N blocks improves the effective SNR by 10*log10(N) dB. A 5-minute video at 10-second blocks gives 30 blocks, yielding ~15 dB of combining gain on top of the ECC coding gain.

## Constraints and Limitations

- **Partial clip detection.** Same limitation as audio: detecting from an arbitrary position within a block requires knowing the block boundaries. For VOD content, block boundaries are deterministic (every B frames from the start). For re-encoded content where frames may be dropped, frame-counting from the start may drift. Phase 2 can address this with sync markers.
- **Variable frame rate.** VFR video (common in screen recordings) means frame count per block varies. The algorithm should use a fixed frame count per block, padding or truncating the last block.
- **Resolution changes.** If the video is downscaled after watermarking, the PN sequence length no longer matches. Detection must decode at the watermarked resolution or use spatial subsampling with a fixed grid that survives common scaling ratios (e.g., embed at 360p grid, detect at any resolution >= 360p).
- **Multipart upload.** Video files can be large (up to 500 MB per existing limits). The microservice should accept multipart upload in addition to base64, unlike the audio service which uses base64 only. The enterprise API client should support both.

## Success Criteria

- Watermark survives H.264 CRF 23 re-encoding with 100% payload recovery (ECC-corrected)
- Watermark survives H.264 CRF 28 re-encoding with 100% payload recovery (ECC-corrected)
- Watermark survives H.265 CRF 28 re-encoding with 100% payload recovery (ECC-corrected)
- Watermark survives 1080p to 720p downscaling with > 95% payload recovery
- Raw bit error rate before ECC < 15% for H.264 CRF 28 (within RS correction capacity)
- Watermark is visually imperceptible (PSNR > 40 dB at default WSR)
- VOD signing pipeline produces C2PA manifest with `c2pa.soft_binding.v1` assertion + detectable watermark
- Live stream signing produces per-segment watermarks, all recoverable independently
- Verification pipeline returns combined C2PA + watermark results
- Free tier callers receive 403 when using `enable_video_watermark`
- Processing time under 30 seconds for a 5-minute 1080p video
- Memory usage under 4 GB for 1080p content of any duration (block-based processing)
- ECC coding gain demonstrated: at least 6 dB improvement in detection threshold vs uncoded baseline
- Audio ECC backport: all existing audio robustness tests still pass, MP3 48kbps test newly passes
- All tests passing with verification markers
