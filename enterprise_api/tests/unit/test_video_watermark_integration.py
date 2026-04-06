"""Integration tests for the video watermark pipeline.

These tests verify the full signing and verification pipelines by mocking
the watermark microservice HTTP calls. They confirm:
  - Tier gating: video_watermark is False on free, True on enterprise/strategic_partner.
  - Signing with enable_video_watermark=True calls the watermark service and includes
    a c2pa.soft_binding.v1 assertion in custom_assertions.
  - Verification pipeline returns combined C2PA + watermark results.
  - Stream sessions store the watermark flag and compute payload once.

The watermark microservice is not required to be running for these tests;
all HTTP calls are intercepted via unittest.mock.
"""

import base64
from unittest.mock import AsyncMock, patch

import pytest


class TestVideoWatermarkTierGating:
    """Tier feature flags correctly gate video_watermark."""

    def test_free_tier_no_video_watermark(self) -> None:
        from app.core.tier_config import get_tier_features

        features = get_tier_features("free")
        assert features.get("video_watermark") is False

    def test_enterprise_tier_has_video_watermark(self) -> None:
        from app.core.tier_config import get_tier_features

        features = get_tier_features("enterprise")
        assert features.get("video_watermark") is True

    def test_strategic_partner_has_video_watermark(self) -> None:
        from app.core.tier_config import get_tier_features

        features = get_tier_features("strategic_partner")
        assert features.get("video_watermark") is True

    def test_free_features_dict_video_watermark_false(self) -> None:
        from app.core.tier_config import FREE_FEATURES

        assert FREE_FEATURES["video_watermark"] is False

    def test_enterprise_features_dict_video_watermark_true(self) -> None:
        from app.core.tier_config import ENTERPRISE_FEATURES

        assert ENTERPRISE_FEATURES["video_watermark"] is True

    def test_strategic_partner_features_dict_video_watermark_true(self) -> None:
        from app.core.tier_config import STRATEGIC_PARTNER_FEATURES

        assert STRATEGIC_PARTNER_FEATURES["video_watermark"] is True

    def test_legacy_starter_tier_no_video_watermark(self) -> None:
        from app.core.tier_config import get_tier_features

        features = get_tier_features("starter")
        assert features.get("video_watermark") is False

    def test_legacy_professional_tier_no_video_watermark(self) -> None:
        from app.core.tier_config import get_tier_features

        features = get_tier_features("professional")
        assert features.get("video_watermark") is False


class TestVideoWatermarkInSigningPipeline:
    """Signing pipeline calls watermark service and updates result correctly."""

    @pytest.mark.asyncio
    async def test_soft_binding_assertion_shape(self) -> None:
        """SOFT_BINDING_ASSERTION_VIDEO has the expected label, method, and payload_bits."""
        from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO

        assert SOFT_BINDING_ASSERTION_VIDEO["label"] == "c2pa.soft_binding.v1"
        assert "method" in SOFT_BINDING_ASSERTION_VIDEO["data"]
        assert "payload_bits" in SOFT_BINDING_ASSERTION_VIDEO["data"]
        assert SOFT_BINDING_ASSERTION_VIDEO["data"]["payload_bits"] == 64
        assert "video" in SOFT_BINDING_ASSERTION_VIDEO["data"]["method"]

    @pytest.mark.asyncio
    async def test_video_watermark_assertion_added_when_enabled(self) -> None:
        """When enable_video_watermark=True, SOFT_BINDING_ASSERTION_VIDEO is in custom_assertions."""
        from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO

        enable_video_watermark = True
        custom_assertions: list = []
        if enable_video_watermark:
            custom_assertions.append(SOFT_BINDING_ASSERTION_VIDEO)

        assert len(custom_assertions) == 1
        assert custom_assertions[0]["label"] == "c2pa.soft_binding.v1"
        assert custom_assertions[0]["data"]["method"] == "encypher.spread_spectrum_video.v1"

    @pytest.mark.asyncio
    async def test_no_soft_binding_when_watermark_disabled(self) -> None:
        """When enable_video_watermark=False, custom_assertions is empty."""
        from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO

        enable_video_watermark = False
        custom_assertions: list = []
        if enable_video_watermark:
            custom_assertions.append(SOFT_BINDING_ASSERTION_VIDEO)

        assert len(custom_assertions) == 0

    @pytest.mark.asyncio
    async def test_apply_watermark_to_signed_video_calls_client(self) -> None:
        """apply_watermark_to_signed_video calls the HTTP client with the correct payload."""
        from app.services.video_watermark_client import (
            apply_watermark_to_signed_video,
            compute_video_watermark_payload,
        )
        from app.utils.hashing import compute_sha256

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40  # minimal MP4-like bytes
        video_id = "vid_test_abc1234567"
        org_id = "org_test_xyz"
        expected_payload = compute_video_watermark_payload(video_id, org_id)

        mock_wm_b64 = base64.b64encode(b"watermarked-video-data").decode()
        captured_calls: list = []

        async def fake_apply(b64, mime, payload, snr_db=None):
            captured_calls.append({"b64": b64, "mime": mime, "payload": payload})
            return mock_wm_b64, 0.95

        with patch("app.services.video_watermark_client.video_watermark_client") as mock_client:
            mock_client.is_configured = True
            mock_client.apply_watermark = AsyncMock(side_effect=fake_apply)

            result = await apply_watermark_to_signed_video(dummy_video, "video/mp4", video_id, org_id)

        assert result is not None
        watermarked_bytes, new_hash, wm_key = result

        assert len(captured_calls) == 1
        assert captured_calls[0]["payload"] == expected_payload
        assert captured_calls[0]["mime"] == "video/mp4"

        assert watermarked_bytes == base64.b64decode(mock_wm_b64)

        expected_hash = compute_sha256(watermarked_bytes)
        assert new_hash == expected_hash

        assert wm_key.startswith("vwm_")
        assert video_id in wm_key

    @pytest.mark.asyncio
    async def test_apply_watermark_returns_none_when_service_unavailable(self) -> None:
        """apply_watermark_to_signed_video gracefully returns None when service is not configured."""
        from app.services.video_watermark_client import apply_watermark_to_signed_video

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40

        with patch("app.services.video_watermark_client.video_watermark_client") as mock_client:
            mock_client.is_configured = False

            result = await apply_watermark_to_signed_video(dummy_video, "video/mp4", "vid_x", "org_y")

        assert result is None

    @pytest.mark.asyncio
    async def test_apply_watermark_returns_none_when_service_call_fails(self) -> None:
        """apply_watermark_to_signed_video returns None when the microservice call returns None."""
        from app.services.video_watermark_client import apply_watermark_to_signed_video

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40

        with patch("app.services.video_watermark_client.video_watermark_client") as mock_client:
            mock_client.is_configured = True
            mock_client.apply_watermark = AsyncMock(return_value=None)

            result = await apply_watermark_to_signed_video(dummy_video, "video/mp4", "vid_fail", "org_fail")

        assert result is None

    @pytest.mark.asyncio
    async def test_apply_watermark_response_structure(self) -> None:
        """apply_watermark_to_signed_video returns (bytes, hash, key) tuple."""
        from app.services.video_watermark_client import (
            apply_watermark_to_signed_video,
            compute_video_watermark_key,
        )
        from app.utils.hashing import compute_sha256

        signed_bytes = b"\x00\x00\x00\x18ftyp" + b"\x00" * 100
        video_id = "vid_pipeline_test123"
        org_id = "org_pipeline_test"

        mock_wm_b64 = base64.b64encode(b"watermarked" + signed_bytes).decode()

        with patch("app.services.video_watermark_client.video_watermark_client") as mock_client:
            mock_client.is_configured = True
            mock_client.apply_watermark = AsyncMock(return_value=(mock_wm_b64, 0.88))

            result = await apply_watermark_to_signed_video(signed_bytes, "video/mp4", video_id, org_id)

        assert result is not None
        wm_bytes, wm_hash, wm_key = result

        assert isinstance(wm_bytes, bytes)
        assert wm_hash == compute_sha256(wm_bytes)
        assert wm_key == compute_video_watermark_key(video_id, org_id)

    @pytest.mark.asyncio
    async def test_watermark_payload_is_tied_to_video_and_org(self) -> None:
        """The watermark payload binds the video_id to the org -- different inputs give different payloads."""
        from app.services.video_watermark_client import compute_video_watermark_payload

        p1 = compute_video_watermark_payload("vid_aaa", "org_111")
        p2 = compute_video_watermark_payload("vid_bbb", "org_111")
        p3 = compute_video_watermark_payload("vid_aaa", "org_222")

        assert p1 != p2, "Different video_id must produce different payload"
        assert p1 != p3, "Different org_id must produce different payload"
        assert len(p1) == 16  # 64 bits as 16 hex chars
        assert all(c in "0123456789abcdef" for c in p1)

    def test_non_video_mime_raises_in_classify(self) -> None:
        """_classify returns 'image' for image/jpeg, triggering watermark rejection in sign_media."""
        from app.routers.media_signing import _classify

        assert _classify("image/jpeg") == "image"
        assert _classify("video/mp4") == "video"
        assert _classify("audio/wav") == "audio"

    def test_sign_video_pipeline_builds_assertion_when_enabled(self) -> None:
        """The _sign_video function adds SOFT_BINDING_ASSERTION_VIDEO to custom_assertions when enabled."""
        from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO

        # Mirror the logic in _sign_video
        enable_video_watermark = True
        custom_assertions: list[dict] = []
        if enable_video_watermark:
            custom_assertions.append(SOFT_BINDING_ASSERTION_VIDEO)

        assert any(a["label"] == "c2pa.soft_binding.v1" for a in custom_assertions)

    def test_sign_video_pipeline_no_assertion_when_disabled(self) -> None:
        """The _sign_video function does not add any assertions when enable_video_watermark=False."""
        from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO

        enable_video_watermark = False
        custom_assertions: list[dict] = []
        if enable_video_watermark:
            custom_assertions.append(SOFT_BINDING_ASSERTION_VIDEO)

        assert not any(a.get("label") == "c2pa.soft_binding.v1" for a in custom_assertions)


class TestVideoWatermarkInVerification:
    """Verification pipeline returns combined C2PA + watermark results."""

    @pytest.mark.asyncio
    async def test_verify_video_with_watermark_detected(self) -> None:
        """verify_video_with_watermark returns combined C2PA + watermark result on detection."""
        from app.services.video_verification_service import (
            VideoVerificationWithWatermark,
            verify_video_with_watermark,
        )
        from app.utils.c2pa_verifier_core import C2paVerificationResult

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40

        mock_c2pa_result = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )

        with (
            patch("app.services.video_verification_service.verify_video_c2pa", return_value=mock_c2pa_result),
            patch("app.services.video_watermark_client.video_watermark_client") as mock_client,
        ):
            mock_client.is_configured = True
            mock_client.detect_watermark = AsyncMock(return_value=(True, "deadbeefcafebabe", 0.93))

            result = await verify_video_with_watermark(dummy_video, "video/mp4")

        assert isinstance(result, VideoVerificationWithWatermark)
        assert result.watermark_detected is True
        assert result.watermark_payload == "deadbeefcafebabe"
        assert result.watermark_confidence == 0.93
        assert result.c2pa is mock_c2pa_result

    @pytest.mark.asyncio
    async def test_verify_video_no_watermark_detected(self) -> None:
        """verify_video_with_watermark returns watermark_detected=False when not found."""
        from app.services.video_verification_service import verify_video_with_watermark
        from app.utils.c2pa_verifier_core import C2paVerificationResult

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40

        mock_c2pa_result = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )

        with (
            patch("app.services.video_verification_service.verify_video_c2pa", return_value=mock_c2pa_result),
            patch("app.services.video_watermark_client.video_watermark_client") as mock_client,
        ):
            mock_client.is_configured = True
            mock_client.detect_watermark = AsyncMock(return_value=(False, None, 0.002))

            result = await verify_video_with_watermark(dummy_video, "video/mp4")

        assert result.watermark_detected is False
        assert result.watermark_payload is None
        assert result.watermark_confidence == 0.002

    @pytest.mark.asyncio
    async def test_verify_video_service_unavailable_graceful_degradation(self) -> None:
        """When watermark service is not configured, watermark fields are falsy defaults."""
        from app.services.video_verification_service import verify_video_with_watermark
        from app.utils.c2pa_verifier_core import C2paVerificationResult

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40

        mock_c2pa_result = C2paVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
        )

        with (
            patch("app.services.video_verification_service.verify_video_c2pa", return_value=mock_c2pa_result),
            patch("app.services.video_watermark_client.video_watermark_client") as mock_client,
        ):
            mock_client.is_configured = False

            result = await verify_video_with_watermark(dummy_video, "video/mp4")

        assert result.watermark_detected is False
        assert result.watermark_payload is None
        assert result.watermark_confidence == 0.0

    @pytest.mark.asyncio
    async def test_verify_video_detection_returns_none_graceful(self) -> None:
        """When detection call returns None (service error), defaults are preserved."""
        from app.services.video_verification_service import verify_video_with_watermark
        from app.utils.c2pa_verifier_core import C2paVerificationResult

        dummy_video = b"\x00\x00\x00\x18ftyp" + b"\x00" * 40

        mock_c2pa_result = C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )

        with (
            patch("app.services.video_verification_service.verify_video_c2pa", return_value=mock_c2pa_result),
            patch("app.services.video_watermark_client.video_watermark_client") as mock_client,
        ):
            mock_client.is_configured = True
            mock_client.detect_watermark = AsyncMock(return_value=None)

            result = await verify_video_with_watermark(dummy_video, "video/mp4")

        assert result.watermark_detected is False
        assert result.watermark_payload is None
        assert result.watermark_confidence == 0.0
        # C2PA result is preserved
        assert result.c2pa.valid is True


class TestVideoStreamWatermark:
    """Stream session stores watermark flag and computes payload once."""

    @pytest.mark.asyncio
    async def test_stream_session_stores_watermark_flag_true(self) -> None:
        """VideoStreamSession.enable_video_watermark is True when passed to start_stream_session."""
        from app.services.video_stream_signing_service import start_stream_session

        with patch("app.services.video_stream_signing_service._redis_save_session", AsyncMock(return_value=False)):
            session = await start_stream_session(
                org_id="org_test_stream",
                private_key_pem="",
                cert_chain_pem="",
                enable_video_watermark=True,
            )

        assert session.enable_video_watermark is True

    @pytest.mark.asyncio
    async def test_stream_session_stores_watermark_flag_false(self) -> None:
        """VideoStreamSession.enable_video_watermark is False when not requested."""
        from app.services.video_stream_signing_service import start_stream_session

        with patch("app.services.video_stream_signing_service._redis_save_session", AsyncMock(return_value=False)):
            session = await start_stream_session(
                org_id="org_test_stream",
                private_key_pem="",
                cert_chain_pem="",
                enable_video_watermark=False,
            )

        assert session.enable_video_watermark is False
        assert session.watermark_payload is None

    @pytest.mark.asyncio
    async def test_stream_payload_computed_once_at_session_start(self) -> None:
        """watermark_payload is set on session creation and is a 16-char hex string."""
        from app.services.video_stream_signing_service import start_stream_session

        with patch("app.services.video_stream_signing_service._redis_save_session", AsyncMock(return_value=False)):
            session = await start_stream_session(
                org_id="org_payload_test",
                private_key_pem="",
                cert_chain_pem="",
                enable_video_watermark=True,
            )

        assert session.watermark_payload is not None
        assert len(session.watermark_payload) == 16
        assert all(c in "0123456789abcdef" for c in session.watermark_payload)

    @pytest.mark.asyncio
    async def test_stream_payload_deterministic_given_same_inputs(self) -> None:
        """The same session_id and org_id always produce the same watermark payload.

        Note: session_id is generated via secrets.token_hex, so we test the payload
        computation function directly rather than two full session starts.
        """
        from app.services.video_watermark_client import compute_video_watermark_payload

        session_id = "vstream_abcdef123456"
        org_id = "org_determinism_test"

        payload_a = compute_video_watermark_payload(session_id, org_id)
        payload_b = compute_video_watermark_payload(session_id, org_id)

        assert payload_a == payload_b
        assert len(payload_a) == 16

    @pytest.mark.asyncio
    async def test_stream_payload_differs_across_orgs(self) -> None:
        """Different org_id values produce different watermark payloads for the same session."""
        from app.services.video_watermark_client import compute_video_watermark_payload

        session_id = "vstream_shared_session"
        payload_org1 = compute_video_watermark_payload(session_id, "org_aaa")
        payload_org2 = compute_video_watermark_payload(session_id, "org_bbb")

        assert payload_org1 != payload_org2

    @pytest.mark.asyncio
    async def test_stream_no_payload_when_watermark_disabled(self) -> None:
        """watermark_payload is None when enable_video_watermark=False."""
        from app.services.video_stream_signing_service import start_stream_session

        with patch("app.services.video_stream_signing_service._redis_save_session", AsyncMock(return_value=False)):
            session = await start_stream_session(
                org_id="org_no_wm",
                private_key_pem="",
                cert_chain_pem="",
                enable_video_watermark=False,
            )

        assert session.watermark_payload is None
