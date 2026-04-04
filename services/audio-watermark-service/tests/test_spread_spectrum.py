"""
Unit tests for spread-spectrum audio watermarking.

Tests the embed/detect roundtrip on synthetic audio to verify
the core algorithm works before integration testing with real
audio files and lossy codecs.
"""

import numpy as np

from app.services.spread_spectrum import (
    _generate_chips,
    decode_audio,
    detect,
    embed,
    encode_audio,
)

SEED = b"test-secret-key-for-audio-watermark"
SAMPLE_RATE = 44100
PAYLOAD = "deadbeefcafebabe"  # 64-bit payload as 16 hex chars
PAYLOAD_BITS = 64
CHIP_RATE = 8


def _make_sine_wave(duration_s: float = 2.0, freq_hz: float = 440.0) -> np.ndarray:
    """Generate a pure sine wave for testing."""
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq_hz * t)


def _make_white_noise(duration_s: float = 2.0) -> np.ndarray:
    """Generate white noise for testing."""
    rng = np.random.RandomState(42)
    return 0.3 * rng.randn(int(SAMPLE_RATE * duration_s))


def _make_speech_like(duration_s: float = 3.0) -> np.ndarray:
    """Generate a multi-frequency signal that loosely resembles speech energy distribution."""
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s), endpoint=False)
    signal = np.zeros_like(t)
    # Fundamental + harmonics typical of voiced speech
    for f, amp in [(150, 0.3), (300, 0.2), (600, 0.15), (1200, 0.1), (2400, 0.05)]:
        signal += amp * np.sin(2 * np.pi * f * t)
    return signal


class TestChipGeneration:
    """PN chip sequence generation."""

    def test_deterministic(self) -> None:
        c1 = _generate_chips(0, SEED, CHIP_RATE, 512)
        c2 = _generate_chips(0, SEED, CHIP_RATE, 512)
        np.testing.assert_array_equal(c1, c2)

    def test_different_bits_produce_different_chips(self) -> None:
        c0 = _generate_chips(0, SEED, CHIP_RATE, 512)
        c1 = _generate_chips(1, SEED, CHIP_RATE, 512)
        assert not np.array_equal(c0, c1)

    def test_chip_values_are_plus_minus_one(self) -> None:
        chips = _generate_chips(0, SEED, CHIP_RATE, 512)
        unique = set(chips.tolist())
        assert unique == {-1.0, 1.0}

    def test_output_length_matches_n_bins(self) -> None:
        for n_bins in (128, 512, 1024):
            chips = _generate_chips(0, SEED, CHIP_RATE, n_bins)
            assert len(chips) == n_bins


class TestEmbedDetectRoundtrip:
    """Core embed -> detect roundtrip on synthetic audio."""

    def test_sine_wave_roundtrip(self) -> None:
        samples = _make_sine_wave(duration_s=3.0)
        watermarked, conf = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert watermarked.shape == samples.shape
        assert conf > 0.0

        detected, extracted, det_conf = detect(
            watermarked,
            SAMPLE_RATE,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is True
        assert extracted == PAYLOAD
        assert det_conf > 0.0

    def test_speech_like_roundtrip(self) -> None:
        samples = _make_speech_like(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        detected, extracted, _ = detect(
            watermarked,
            SAMPLE_RATE,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is True
        assert extracted == PAYLOAD

    def test_white_noise_roundtrip(self) -> None:
        samples = _make_white_noise(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-15.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        detected, extracted, _ = detect(
            watermarked,
            SAMPLE_RATE,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is True
        assert extracted == PAYLOAD

    def test_different_payloads(self) -> None:
        samples = _make_sine_wave(duration_s=3.0)
        for payload in ["0000000000000000", "ffffffffffffffff", "1234567890abcdef"]:  # pragma: allowlist secret
            watermarked, _ = embed(
                samples,
                SAMPLE_RATE,
                payload,
                SEED,
                snr_db=-20.0,
                chip_rate=CHIP_RATE,
                payload_bits=PAYLOAD_BITS,
            )
            detected, extracted, _ = detect(
                watermarked,
                SAMPLE_RATE,
                SEED,
                chip_rate=CHIP_RATE,
                payload_bits=PAYLOAD_BITS,
            )
            assert detected is True
            assert extracted == payload


class TestImperceptibility:
    """Watermark should not significantly alter the audio signal."""

    def test_snr_within_tolerance(self) -> None:
        samples = _make_speech_like(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        noise = watermarked - samples[: len(watermarked)]
        signal_power = np.mean(samples**2) + 1e-10
        noise_power = np.mean(noise**2) + 1e-10
        actual_snr = 10 * np.log10(signal_power / noise_power)
        # SNR should be at least 15 dB (watermark is quiet)
        assert actual_snr > 15.0, f"SNR too low: {actual_snr:.1f} dB"

    def test_output_range(self) -> None:
        samples = _make_sine_wave(duration_s=2.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert np.all(watermarked >= -1.0)
        assert np.all(watermarked <= 1.0)


class TestRobustness:
    """Watermark survives common audio processing."""

    def test_survives_pcm16_quantization(self) -> None:
        """Embed, encode to WAV PCM_16, decode, detect -- the full pipeline roundtrip."""
        samples = _make_speech_like(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        wav_bytes = encode_audio(watermarked, SAMPLE_RATE)
        decoded, sr = decode_audio(wav_bytes)

        detected, extracted, confidence = detect(
            decoded,
            sr,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is True
        assert extracted == PAYLOAD

    def test_survives_amplitude_scaling(self) -> None:
        """Watermark survives loudness normalization (amplitude scaling)."""
        samples = _make_speech_like(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        # Simulate loudness normalization: scale amplitude by 0.5 (-6 dB)
        scaled = watermarked * 0.5

        detected, extracted, _ = detect(
            scaled,
            SAMPLE_RATE,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is True
        assert extracted == PAYLOAD

    def test_survives_additive_noise(self) -> None:
        """Watermark survives low-level additive noise."""
        samples = _make_speech_like(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-15.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        # Add noise at -30 dB relative to signal
        rng = np.random.RandomState(99)
        signal_power = np.mean(watermarked**2)
        noise_power = signal_power * 1e-3  # -30 dB
        noise = rng.randn(len(watermarked)) * np.sqrt(noise_power)
        noisy = np.clip(watermarked + noise, -1.0, 1.0)

        detected, extracted, _ = detect(
            noisy,
            SAMPLE_RATE,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is True
        assert extracted == PAYLOAD

    def test_no_false_positive_on_clean_audio(self) -> None:
        """Unwatermarked audio should not produce a false detection."""
        samples = _make_speech_like(duration_s=3.0)
        detected, _, confidence = detect(
            samples,
            SAMPLE_RATE,
            SEED,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        assert detected is False
        assert confidence < 0.05

    def test_wrong_seed_fails_detection(self) -> None:
        """Detection with the wrong seed should not extract the correct payload."""
        samples = _make_speech_like(duration_s=3.0)
        watermarked, _ = embed(
            samples,
            SAMPLE_RATE,
            PAYLOAD,
            SEED,
            snr_db=-20.0,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        wrong_seed = b"wrong-seed-for-audio-watermark"
        detected, extracted, _ = detect(
            watermarked,
            SAMPLE_RATE,
            wrong_seed,
            chip_rate=CHIP_RATE,
            payload_bits=PAYLOAD_BITS,
        )
        # With wrong seed, the extracted payload should not match
        if detected:
            assert extracted != PAYLOAD


class TestAudioIO:
    """Audio encode/decode helpers."""

    def test_wav_roundtrip(self) -> None:
        samples = _make_sine_wave(duration_s=1.0)
        wav_bytes = encode_audio(samples, SAMPLE_RATE)
        decoded, sr = decode_audio(wav_bytes)
        assert sr == SAMPLE_RATE
        # PCM_16 quantization introduces small errors
        np.testing.assert_allclose(decoded, samples, atol=1e-4)

    def test_stereo_to_mono(self) -> None:
        """Stereo input should be averaged to mono."""
        import io
        import soundfile as sf

        mono = _make_sine_wave(duration_s=0.5)
        stereo = np.column_stack([mono, mono * 0.8])
        buf = io.BytesIO()
        sf.write(buf, stereo, SAMPLE_RATE, format="WAV")
        decoded, sr = decode_audio(buf.getvalue())
        assert decoded.ndim == 1
        assert sr == SAMPLE_RATE
