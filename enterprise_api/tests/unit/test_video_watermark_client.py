"""Unit tests for the video watermark client module.

Tests cover configuration detection, deterministic payload/key computation,
and the shape of the soft-binding assertion constant. No live service required.
"""

import pytest

from app.services.video_watermark_client import (
    SOFT_BINDING_ASSERTION_VIDEO,
    VideoWatermarkClient,
    compute_video_watermark_key,
    compute_video_watermark_payload,
)


class TestVideoWatermarkClientConfigured:
    """is_configured reflects the presence of video_watermark_service_url."""

    def test_is_configured_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app import config as cfg

        monkeypatch.setattr(cfg.settings, "video_watermark_service_url", "http://localhost:8012")
        client = VideoWatermarkClient()
        assert client.is_configured is True

    def test_is_configured_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app import config as cfg

        monkeypatch.setattr(cfg.settings, "video_watermark_service_url", "")
        client = VideoWatermarkClient()
        assert client.is_configured is False


class TestComputeVideoWatermarkPayload:
    """compute_video_watermark_payload produces stable, correctly-shaped output."""

    def test_payload_deterministic(self) -> None:
        first = compute_video_watermark_payload("vid_abc123", "org_xyz")
        second = compute_video_watermark_payload("vid_abc123", "org_xyz")
        assert first == second

    def test_payload_length(self) -> None:
        payload = compute_video_watermark_payload("vid_abc123", "org_xyz")
        assert len(payload) == 16

    def test_payload_is_hex(self) -> None:
        payload = compute_video_watermark_payload("vid_abc123", "org_xyz")
        int(payload, 16)  # raises ValueError if not valid hex

    def test_payload_differs_by_video_id(self) -> None:
        p1 = compute_video_watermark_payload("vid_aaa", "org_xyz")
        p2 = compute_video_watermark_payload("vid_bbb", "org_xyz")
        assert p1 != p2

    def test_payload_differs_by_org(self) -> None:
        p1 = compute_video_watermark_payload("vid_abc123", "org_111")
        p2 = compute_video_watermark_payload("vid_abc123", "org_222")
        assert p1 != p2


class TestComputeVideoWatermarkKey:
    """compute_video_watermark_key produces a stable, readable key."""

    def test_key_starts_with_vwm(self) -> None:
        key = compute_video_watermark_key("vid_abc123", "org_xyz")
        assert key.startswith("vwm_")

    def test_key_contains_video_id(self) -> None:
        key = compute_video_watermark_key("vid_abc123", "org_xyz")
        assert "vid_abc123" in key

    def test_key_deterministic(self) -> None:
        k1 = compute_video_watermark_key("vid_abc123", "org_xyz")
        k2 = compute_video_watermark_key("vid_abc123", "org_xyz")
        assert k1 == k2

    def test_key_differs_by_org(self) -> None:
        k1 = compute_video_watermark_key("vid_abc123", "org_111")
        k2 = compute_video_watermark_key("vid_abc123", "org_222")
        assert k1 != k2


class TestSoftBindingAssertion:
    """SOFT_BINDING_ASSERTION_VIDEO has the expected shape and values."""

    def test_assertion_label(self) -> None:
        assert SOFT_BINDING_ASSERTION_VIDEO["label"] == "c2pa.soft_binding.v1"

    def test_assertion_method_contains_video(self) -> None:
        method = SOFT_BINDING_ASSERTION_VIDEO["data"]["method"]
        assert "video" in method

    def test_assertion_payload_bits(self) -> None:
        assert SOFT_BINDING_ASSERTION_VIDEO["data"]["payload_bits"] == 64

    def test_assertion_has_description(self) -> None:
        assert "description" in SOFT_BINDING_ASSERTION_VIDEO["data"]
