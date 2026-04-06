"""Tests for video C2PA signing and verification.

Unit tests for:
- video_utils: validation, format detection, MIME canonicalization
- video_signing_service: passthrough mode signing
- video_verification_service: error handling for unsigned video
- video_signing_executor: credential loading pattern

Integration tests (sign + verify round-trip) require valid signing certificates
and are skipped when certs are not available (same as image signing tests).
"""

import struct
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.utils.hashing import compute_sha256
from app.utils.video_utils import (
    SUPPORTED_VIDEO_MIME_TYPES,
    canonicalize_mime_type,
    detect_video_format,
    validate_video,
)


# ---------------------------------------------------------------------------
# Helpers: generate minimal video files
# ---------------------------------------------------------------------------


def make_fake_mp4() -> bytes:
    """Generate bytes that look like an MP4 (ftyp box)."""
    ftyp_data = b"mp42\x00\x00\x00\x00mp42isom"
    box_size = 8 + len(ftyp_data)
    return struct.pack(">I", box_size) + b"ftyp" + ftyp_data + b"\x00" * 256


def make_fake_mov() -> bytes:
    """Generate bytes that look like a MOV (ftyp box with qt brand)."""
    ftyp_data = b"qt  \x00\x00\x00\x00qt  "
    box_size = 8 + len(ftyp_data)
    return struct.pack(">I", box_size) + b"ftyp" + ftyp_data + b"\x00" * 256


def make_fake_avi() -> bytes:
    """Generate bytes that look like an AVI (RIFF + AVI header)."""
    return b"RIFF" + struct.pack("<I", 1000) + b"AVI " + b"\x00" * 256


def make_fake_webm() -> bytes:
    """Generate bytes with EBML magic (WebM/MKV -- should be rejected)."""
    return b"\x1a\x45\xdf\xa3" + b"\x00" * 256


# ===========================================================================
# video_utils: canonicalize_mime_type
# ===========================================================================


class TestCanonicalizeMimeType:
    def test_mp4(self):
        assert canonicalize_mime_type("video/mp4") == "video/mp4"

    def test_quicktime(self):
        assert canonicalize_mime_type("video/quicktime") == "video/quicktime"

    def test_m4v(self):
        assert canonicalize_mime_type("video/x-m4v") == "video/x-m4v"

    def test_avi_variants(self):
        assert canonicalize_mime_type("video/x-msvideo") == "video/x-msvideo"
        assert canonicalize_mime_type("video/avi") == "video/x-msvideo"
        assert canonicalize_mime_type("video/msvideo") == "video/x-msvideo"

    def test_unknown_passthrough(self):
        assert canonicalize_mime_type("video/webm") == "video/webm"

    def test_case_insensitive(self):
        assert canonicalize_mime_type("Video/MP4") == "video/mp4"


# ===========================================================================
# video_utils: detect_video_format
# ===========================================================================


class TestDetectVideoFormat:
    def test_ftyp_mp4(self):
        assert detect_video_format(make_fake_mp4()) == "video/mp4"

    def test_ftyp_mov(self):
        assert detect_video_format(make_fake_mov()) == "video/mp4"

    def test_riff_avi(self):
        assert detect_video_format(make_fake_avi()) == "video/x-msvideo"

    def test_ebml_webm(self):
        assert detect_video_format(make_fake_webm()) == "video/webm"

    def test_too_short(self):
        assert detect_video_format(b"\x00" * 5) is None

    def test_unknown(self):
        assert detect_video_format(b"\x00" * 100) is None


# ===========================================================================
# video_utils: validate_video
# ===========================================================================


class TestValidateVideo:
    def test_valid_mp4(self):
        mime, size = validate_video(make_fake_mp4(), "video/mp4")
        assert mime == "video/mp4"
        assert size > 0

    def test_valid_mov_ftyp(self):
        """ftyp-detected video with declared video/quicktime should pass (ISO BMFF family)."""
        mime, size = validate_video(make_fake_mov(), "video/quicktime")
        assert mime == "video/quicktime"
        assert size > 0

    def test_valid_m4v_ftyp(self):
        """ftyp-detected video with declared video/x-m4v should pass (ISO BMFF family)."""
        mime, size = validate_video(make_fake_mov(), "video/x-m4v")
        assert mime == "video/x-m4v"
        assert size > 0

    def test_valid_avi(self):
        mime, size = validate_video(make_fake_avi(), "video/x-msvideo")
        assert mime == "video/x-msvideo"
        assert size > 0

    def test_empty_data(self):
        with pytest.raises(ValueError, match="empty"):
            validate_video(b"", "video/mp4")

    def test_too_large(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            validate_video(b"\x00" * 100, "video/mp4", max_size_bytes=50)

    def test_unsupported_mime(self):
        with pytest.raises(ValueError, match="Unsupported"):
            validate_video(b"\x00" * 100, "video/webm")

    def test_mime_mismatch(self):
        """ftyp-detected MP4/ISO BMFF with declared AVI -> mismatch error."""
        mp4_bytes = make_fake_mp4()
        with pytest.raises(ValueError, match="mismatch"):
            validate_video(mp4_bytes, "video/x-msvideo")

    def test_webm_rejected(self):
        """WebM magic bytes are not in supported set."""
        with pytest.raises(ValueError, match="Unsupported"):
            validate_video(make_fake_webm(), "video/webm")

    def test_ftyp_with_quicktime_declared(self):
        """ftyp box with video/quicktime declared should pass -- ISO BMFF family."""
        mime, size = validate_video(make_fake_mp4(), "video/quicktime")
        assert mime == "video/quicktime"


# ===========================================================================
# video_verification_service: error handling
# ===========================================================================


class TestVideoVerificationService:
    def test_unsigned_mp4(self):
        """Unsigned MP4 should return valid=False with 'no manifest' error."""
        from app.services.video_verification_service import verify_video_c2pa

        result = verify_video_c2pa(make_fake_mp4(), "video/mp4")
        assert result.valid is False
        assert result.error is not None

    def test_empty_video(self):
        """Empty bytes should return error."""
        from app.services.video_verification_service import verify_video_c2pa

        result = verify_video_c2pa(b"", "video/mp4")
        assert result.valid is False

    def test_canonicalizes_mime(self):
        """Should canonicalize 'video/avi' to 'video/x-msvideo'."""
        from app.services.video_verification_service import verify_video_c2pa

        result = verify_video_c2pa(make_fake_avi(), "video/avi")
        assert result.valid is False
        # Should not error on MIME -- error should be about missing manifest


# ===========================================================================
# video_signing_service: passthrough mode
# ===========================================================================


class TestVideoSigningPassthrough:
    @pytest.mark.asyncio
    async def test_passthrough_no_keys(self):
        """With no signing keys, should return passthrough result."""
        from app.services.video_signing_service import sign_video

        result = await sign_video(
            video_data=make_fake_mp4(),
            mime_type="video/mp4",
            title="test.mp4",
            org_id="org_test",
            document_id="doc_test",
            video_id="vid_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )
        assert result.c2pa_signed is False
        assert result.video_id == "vid_test"
        assert result.mime_type == "video/mp4"
        assert result.original_hash.startswith("sha256:")
        # Passthrough now injects Encypher metadata (uuid box), so bytes differ
        assert len(result.signed_bytes) >= len(make_fake_mp4())

    @pytest.mark.asyncio
    async def test_passthrough_has_correct_hashes(self):
        """Passthrough mode should still compute hashes."""
        from app.services.video_signing_service import sign_video

        mp4_data = make_fake_mp4()
        result = await sign_video(
            video_data=mp4_data,
            mime_type="video/mp4",
            title="test.mp4",
            org_id="org_test",
            document_id="doc_test",
            video_id="vid_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )

        expected_hash = compute_sha256(mp4_data)
        assert result.original_hash == expected_hash
        # signed_hash is of the metadata-injected bytes, not the original
        assert result.signed_hash == compute_sha256(result.signed_bytes)
        assert result.signed_hash != result.original_hash

    @pytest.mark.asyncio
    async def test_passthrough_instance_id_format(self):
        """Passthrough mode should generate a valid URN UUID."""
        from app.services.video_signing_service import sign_video

        result = await sign_video(
            video_data=make_fake_mp4(),
            mime_type="video/mp4",
            title="test.mp4",
            org_id="org_test",
            document_id="doc_test",
            video_id="vid_test",
            custom_assertions=[],
            rights_data={},
            signer_private_key_pem="",
            signer_cert_chain_pem="",
        )
        assert result.c2pa_instance_id.startswith("urn:uuid:")

    @pytest.mark.asyncio
    async def test_validation_rejects_bad_mime(self):
        """Should raise ValueError for unsupported MIME type."""
        from app.services.video_signing_service import sign_video

        with pytest.raises(ValueError, match="Unsupported"):
            await sign_video(
                video_data=make_fake_mp4(),
                mime_type="video/webm",
                title="test.webm",
                org_id="org_test",
                document_id="doc_test",
                video_id="vid_test",
                custom_assertions=[],
                rights_data={},
                signer_private_key_pem="",
                signer_cert_chain_pem="",
            )

    @pytest.mark.asyncio
    async def test_validation_rejects_empty_data(self):
        """Should raise ValueError for empty video data."""
        from app.services.video_signing_service import sign_video

        with pytest.raises(ValueError, match="empty"):
            await sign_video(
                video_data=b"",
                mime_type="video/mp4",
                title="test.mp4",
                org_id="org_test",
                document_id="doc_test",
                video_id="vid_test",
                custom_assertions=[],
                rights_data={},
                signer_private_key_pem="",
                signer_cert_chain_pem="",
            )


# ===========================================================================
# video_signing_executor: credential loading
# ===========================================================================


class TestVideoSigningExecutor:
    @pytest.mark.asyncio
    async def test_passthrough_when_no_org_keys(self):
        """Executor should fall through to passthrough when org has no keys."""
        from app.services.video_signing_executor import execute_video_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        result = await execute_video_signing(
            video_bytes=make_fake_mp4(),
            mime_type="video/mp4",
            title="test.mp4",
            org=mock_org,
            db=mock_db,
        )

        assert result.c2pa_signed is False
        assert result.video_id.startswith("vid_")
        assert result.mime_type == "video/mp4"
        assert result.original_hash.startswith("sha256:")

    @pytest.mark.asyncio
    async def test_executor_rejects_bad_data(self):
        """Executor should raise HTTPException for invalid video."""
        from fastapi import HTTPException

        from app.services.video_signing_executor import execute_video_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await execute_video_signing(
                video_bytes=b"",
                mime_type="video/mp4",
                title="test.mp4",
                org=mock_org,
                db=mock_db,
            )

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_executor_custom_document_id(self):
        """Executor should use provided document_id."""
        from app.services.video_signing_executor import execute_video_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        result = await execute_video_signing(
            video_bytes=make_fake_mp4(),
            mime_type="video/mp4",
            title="test.mp4",
            org=mock_org,
            db=mock_db,
            document_id="doc_custom_123",
        )

        # document_id is passed through to sign_video but not on SignedVideoResult;
        # we verify the call didn't error and returned a valid result
        assert result.c2pa_signed is False

    @pytest.mark.asyncio
    async def test_executor_custom_action(self):
        """Executor should pass through the action parameter."""
        from app.services.video_signing_executor import execute_video_signing

        mock_org = MagicMock()
        mock_org.id = "org_test"
        mock_org.cert_chain_pem = None

        mock_db = AsyncMock()

        result = await execute_video_signing(
            video_bytes=make_fake_mp4(),
            mime_type="video/mp4",
            title="test.mp4",
            org=mock_org,
            db=mock_db,
            action="c2pa.transcoded",
        )

        assert result.c2pa_signed is False  # passthrough, but no error
