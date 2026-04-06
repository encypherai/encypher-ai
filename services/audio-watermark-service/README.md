# Audio Watermark Service

Spread-spectrum audio watermarking microservice. Embeds a 64-bit payload into the audio signal domain, surviving transformations that strip container metadata (MP3 re-encoding, loudness normalization, format conversion).

## Architecture

Follows the TrustMark image service pattern: a standalone FastAPI microservice for heavy DSP processing, called from the enterprise API via an async httpx client (`audio_watermark_client.py`).

The watermark is applied after C2PA hard-binding. A `c2pa.soft_binding.v1` assertion in the C2PA manifest declares the method.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/audio/watermark` | POST | Embed spread-spectrum watermark into audio |
| `/api/v1/audio/detect` | POST | Detect and extract watermark from audio |
| `/health` | GET | Health check |

## Algorithm

Time-domain spread-spectrum embedding:

1. For each of the 64 payload bits, generate a pseudo-noise (PN) chip sequence of length equal to the audio sample count using `HMAC-SHA256(seed, bit_index)`.
2. Compute embedding strength alpha from the target watermark-to-signal ratio and signal power.
3. Add `alpha * sum(bit_sign[i] * pn[i])` to the time-domain samples.

Detection correlates the received signal with each PN sequence. Positive correlation indicates bit=1, negative indicates bit=0.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PORT` | 8011 | Service port |
| `LOG_LEVEL` | INFO | Logging level |
| `WATERMARK_SECRET` | (empty) | HMAC secret for PN sequence generation (shared with enterprise API) |
| `MAX_AUDIO_SIZE_BYTES` | 524288000 | Maximum audio file size (500 MB) |
| `DEFAULT_SNR_DB` | -20.0 | Default watermark-to-signal ratio (-20 dB for speech, -30 dB for music) |
| `PAYLOAD_BITS` | 64 | Payload length in bits |
| `CHIP_RATE` | 8 | Reserved for future use |

## Dependencies

- `numpy` - array operations and PN sequence generation
- `soundfile` - format-agnostic audio I/O via libsndfile
- `fastapi`, `uvicorn` - HTTP server
- `pydantic`, `pydantic-settings` - config and request validation

No scipy, no ML models, no GPU.

## Running

```bash
# Install dependencies
uv sync

# Run the service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8011

# Run tests
uv run pytest tests/ -v
```

## Docker

```bash
docker build -t audio-watermark-service .
docker run -p 8011:8011 -e WATERMARK_SECRET=your-secret audio-watermark-service
```

## Tests

17 tests covering:
- PN chip sequence generation (determinism, uniqueness, value range)
- Embed/detect roundtrip (sine wave, speech-like, white noise, multiple payloads)
- Imperceptibility (SNR within tolerance, output range)
- Robustness (PCM16 quantization, amplitude scaling, additive noise, no false positives, wrong-seed rejection)
- Audio I/O (WAV roundtrip, stereo-to-mono)

## Related Files

- Enterprise API client: `enterprise_api/app/services/audio_watermark_client.py`
- Signing integration: `enterprise_api/app/routers/media_signing.py` (`_sign_audio`)
- Signing executor: `enterprise_api/app/services/audio_signing_executor.py`
- Verification: `enterprise_api/app/services/audio_verification_service.py`
- Tier gating: `enterprise_api/app/core/tier_config.py` (`audio_watermark` flag)
