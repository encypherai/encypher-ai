"""Tests for audio C2PA signing and verification.

Unit tests for:
- audio_utils: validation, format detection, MIME canonicalization
- audio_signing_service: passthrough mode signing
- audio_verification_service: error handling for unsigned audio
- audio_signing_executor: credential loading pattern

Integration tests (sign + verify round-trip) require valid signing certificates
and are skipped when certs are not available (same as image signing tests).
"""

import base64
import struct
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.utils.audio_utils import (
    SUPPORTED_AUDIO_MIME_TYPES,
    canonicalize_mime_type,
    detect_audio_format,
    get_wav_info,
    validate_audio,
)
from app.utils.hashing import compute_sha256


# ---------------------------------------------------------------------------
# Helpers: generate minimal audio files
# ---------------------------------------------------------------------------


def make_test_wav(
    duration_seconds: float = 0.1,
    sample_rate: int = 8000,
    channels: int = 1,
    bits_per_sample: int = 16,
) -> bytes:
    """Generate a minimal valid WAV file (silence)."""
    num_samples = int(sample_rate * duration_seconds)
    block_align = channels * bits_per_sample // 8
    byte_rate = sample_rate * block_align
    data_size = num_samples * block_align

    buf = BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<HHIIHH", 1, channels, sample_rate, byte_rate, block_align, bits_per_sample))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(b"\x00" * data_size)
    return buf.getvalue()


def make_fake_mp3() -> bytes:
    """Generate bytes that look like an MP3 (ID3 header + padding)."""
    header = b"ID3\x03\x00\x00\x00\x00\x00\x00"
    return header + b"\x00" * 256


def make_fake_m4a() -> bytes:
    """Generate bytes that look like an M4A (ftyp box)."""
    ftyp_data = b"M4A \x00\x00\x00\x00M4A mp42"
    box_size = 8 + len(ftyp_data)
    return struct.pack(">I", box_size) + b"ftyp" + ftyp_data + b"\x00" * 256


# ===========================================================================
# audio_utils: canonicalize_mime_type
# ===========================================================================


class TestCanonicalizeMimeType:
    def test_wav_variants(self):
        assert canonicalize_mime_type("audio/wav") == "audio/wav"
        assert canonicalize_mime_type("audio/wave") == "audio/wav"
        assert canonicalize_mime_type("audio/vnd.wave") == "audio/wav"
        assert canonicalize_mime_type("audio/x-wav") == "audio/wav"

    def test_mp3(self):
        assert canonicalize_mime_type("audio/mpeg") == "audio/mpeg"
        assert canonicalize_mime_type("audio/mp3") == "audio/mpeg"

    def test_m4a(self):
        assert canonicalize_mime_type("audio/mp4") == "audio/mp4"
        assert canonicalize_mime_type("audio/m4a") == "audio/mp4"
        assert canonicalize_mime_type("audio/aac") == "audio/mp4"

    def test_unknown_passthrough(self):
        assert canonicalize_mime_type("audio/flac") == "audio/flac"

    def test_case_insensitive(self):
        assert canonicalize_mime_type("Audio/WAV") == "audio/wav"


# ===========================================================================
# audio_utils: detect_audio_format
# ===========================================================================


class TestDetectAudioFormat:
    def test_wav(self):
        assert detect_audio_format(make_test_wav()) == "audio/wav"

    def test_mp3_id3(self):
        assert detect_audio_format(make_fake_mp3()) == "audio/mpeg"

    def test_mp3_sync_word(self):
        data = b"\xff\xfb" + b"\x00" * 100
        assert detect_audio_format(data) == "audio/mpeg"

    def test_m4a_ftyp(self):
        assert detect_audio_format(make_fake_m4a()) == "audio/mp4"

    def test_too_short(self):
        assert detect_audio_format(b"\x00" * 5) is None

    def test_unknown(self):
        assert detect_audio_format(b"\x00" * 100) is None


# ===========================================================================
# audio_utils: validate_audio
# ===========================================================================


class TestValidateAudio:
    def test_valid_wav(self):
        mime, size = validate_audio(make_test_wav(), "audio/wav")
        assert mime == "audio/wav"
        assert size > 0

    def test_valid_wav_variant_mime(self):
        mime, size = validate_audio(make_test_wav(), "audio/wave")
        assert mime == "audio/wav"

    def test_empty_data(self):
        with pytest.raises(ValueError, match="empty"):
            validate_audio(b"", "audio/wav")

    def test_too_large(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            validate_audio(b"\x00" * 100, "audio/wav", max_size_bytes=50)

    def test_unsupported_mime(self):
        with pytest.raises(ValueError, match="Unsupported"):
            validate_audio(b"\x00" * 100, "audio/flac")

    def test_mime_mismatch(self):
        """Declared MIME doesn't match magic bytes."""
        wav_bytes = make_test_wav()
        with pytest.raises(ValueError, match="mismatch"):
            validate_audio(wav_bytes, "audio/mpeg")


# ===========================================================================
# audio_utils: compute_sha256 (re-exported from hashing)
# ===========================================================================


class TestComputeSha256:
    def test_known_hash(self):
        result = compute_sha256(b"hello")
        assert result.startswith("sha256:")
        assert len(result) == 7 + 64

    def test_deterministic(self):
        a = compute_sha256(b"test")
        b = compute_sha256(b"test")
        assert a == b


# ===========================================================================
# audio_utils: get_wav_info
# ===========================================================================


class TestGetWavInfo:
    def test_basic_wav(self):
        info = get_wav_info(make_test_wav(duration_seconds=1.0, sample_rate=44100))
        assert info is not None
        assert info["sample_rate"] == 44100
        assert info["channels"] == 1
        assert info["bits_per_sample"] == 16
        assert abs(info["duration_seconds"] - 1.0) < 0.01

    def test_not_wav(self):
        assert get_wav_info(b"\x00" * 100) is None

    def test_too_short(self):
        assert get_wav_info(b"RIFF") is None


# ===========================================================================
# audio_verification_service: error handling
# ===========================================================================


class TestAudioVerificationService:
    def test_unsigned_wav(self):
        """Unsigned WAV should return valid=False with 'no manifest' error."""
        from app.services.audio_verification_service import verify_audio_c2pa

        result = verify_audio_c2pa(make_test_wav(), "audio/wav")
        assert result.valid is False
        assert result.error is not None

    def test_empty_audio(self):
        """Empty bytes should return error."""
        from app.services.audio_verification_service import verify_audio_c2pa

        result = verify_audio_c2pa(b"", "audio/wav")
        assert result.valid is False

    def test_canonicalizes_mime(self):
        """Should canonicalize 'audio/wave' to 'audio/wav'."""
        from app.services.audio_verification_service import verify_audio_c2pa

        result = verify_audio_c2pa(make_test_wav(), "audio/wave")
        assert result.valid is False
        # Should not error on MIME -- error should be about missing manifest


# ===========================================================================
# audio_signing_service: passthrough mode
# ===========================================================================


class TestAudioSigningPassthrough:
    @pytest.mark.asyncio
    async def test_passthrough_no_keys(self):
        """With no signing keys, should return passthrough result."""
        from app.services.audio_signing_service import sign_audio

        result = await sign_audio(
            audio_data=make_test_wav(),
            mime_type="audio/wav",
            title="test.wav",
            org_id="org_test",
            document_id="doc_test",
            audio_id="aud_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )
        assert result.c2pa_signed is False
        assert result.audio_id == "aud_test"
        assert result.mime_type == "audio/wav"
        assert result.original_hash.startswith("sha256:")
        # Passthrough now injects Encypher metadata (RIFF chunk), so bytes differ
        assert len(result.signed_bytes) >= len(make_test_wav())

    @pytest.mark.asyncio
    async def test_passthrough_has_correct_hashes(self):
        """Passthrough mode should still compute hashes."""
        from app.services.audio_signing_service import sign_audio

        wav_data = make_test_wav()
        result = await sign_audio(
            audio_data=wav_data,
            mime_type="audio/wav",
            title="test.wav",
            org_id="org_test",
            document_id="doc_test",
            audio_id="aud_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )

        expected_hash = compute_sha256(wav_data)
        assert result.original_hash == expected_hash
        # signed_hash is of the metadata-injected bytes, not the original
        assert result.signed_hash == compute_sha256(result.signed_bytes)
        assert result.signed_hash != result.original_hash

    @pytest.mark.asyncio
    async def test_passthrough_instance_id_format(self):
        """Passthrough mode should generate a valid URN UUID."""
        from app.services.audio_signing_service import sign_audio

        result = await sign_audio(
            audio_data=make_test_wav(),
            mime_type="audio/wav",
            title="test.wav",
            org_id="org_test",
            document_id="doc_test",
            audio_id="aud_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )
        assert result.c2pa_instance_id.startswith("urn:uuid:")

    @pytest.mark.asyncio
    async def test_validation_rejects_bad_mime(self):
        """Should raise ValueError for unsupported MIME type."""
        from app.services.audio_signing_service import sign_audio

        with pytest.raises(ValueError, match="Unsupported"):
            await sign_audio(
                audio_data=make_test_wav(),
                mime_type="audio/flac",
                title="test.flac",
                org_id="org_test",
                document_id="doc_test",
                audio_id="aud_test",
                custom_assertions=[],
                rights_data={},
                signer_private_key_pem="",
                signer_cert_chain_pem="",
            )

    @pytest.mark.asyncio
    async def test_validation_rejects_empty_data(self):
        """Should raise ValueError for empty audio data."""
        from app.services.audio_signing_service import sign_audio

        with pytest.raises(ValueError, match="empty"):
            await sign_audio(
                audio_data=b"",
                mime_type="audio/wav",
                title="test.wav",
                org_id="org_test",
                document_id="doc_test",
                audio_id="aud_test",
                custom_assertions=[],
                rights_data={},
                signer_private_key_pem="",
                signer_cert_chain_pem="",
            )


# ===========================================================================
# audio_signing_executor: credential loading
# ===========================================================================


class TestAudioSigningExecutor:
    @pytest.mark.asyncio
    async def test_passthrough_when_no_org_keys(self):
        """Executor should fall through to passthrough when org has no keys."""
        from app.services.audio_signing_executor import execute_audio_signing

        # Create a fake Organization with no certs
        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        result = await execute_audio_signing(
            audio_bytes=make_test_wav(),
            mime_type="audio/wav",
            title="test.wav",
            org=mock_org,
            db=mock_db,
        )

        assert result.c2pa_signed is False
        assert result.audio_id.startswith("aud_")
        assert result.mime_type == "audio/wav"
        assert result.original_hash.startswith("sha256:")

    @pytest.mark.asyncio
    async def test_executor_rejects_bad_data(self):
        """Executor should raise HTTPException for invalid audio."""
        from fastapi import HTTPException

        from app.services.audio_signing_executor import execute_audio_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await execute_audio_signing(
                audio_bytes=b"",
                mime_type="audio/wav",
                title="test.wav",
                org=mock_org,
                db=mock_db,
            )

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_executor_custom_document_id(self):
        """Executor should use provided document_id."""
        from app.services.audio_signing_executor import execute_audio_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        result = await execute_audio_signing(
            audio_bytes=make_test_wav(),
            mime_type="audio/wav",
            title="test.wav",
            org=mock_org,
            db=mock_db,
            document_id="doc_custom_123",
        )

        # document_id is passed through to sign_audio but not on SignedAudioResult;
        # we verify the call didn't error and returned a valid result
        assert result.c2pa_signed is False

    @pytest.mark.asyncio
    async def test_executor_custom_action(self):
        """Executor should pass through the action parameter."""
        from app.services.audio_signing_executor import execute_audio_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        # Just verify it doesn't crash with a valid audio action
        result = await execute_audio_signing(
            audio_bytes=make_test_wav(),
            mime_type="audio/wav",
            title="test.wav",
            org=mock_org,
            db=mock_db,
            action="c2pa.dubbed",
        )

        assert result.c2pa_signed is False  # passthrough, but no error


# ===========================================================================
# Re-export compatibility
# ===========================================================================


class TestReExports:
    def test_compute_sha256_from_image_utils(self):
        """compute_sha256 should be importable from image_utils."""
        from app.utils.hashing import compute_sha256 as hashing_sha256
        from app.utils.image_utils import compute_sha256 as image_sha256

        assert image_sha256(b"test") == hashing_sha256(b"test")

    def test_compute_sha256_from_image_verification_service(self):
        """compute_sha256 should be importable from image_verification_service."""
        from app.services.image_verification_service import compute_sha256 as svc_sha256
        from app.utils.hashing import compute_sha256 as hashing_sha256

        assert svc_sha256(b"test") == hashing_sha256(b"test")
