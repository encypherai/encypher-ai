"""Tests for audio_watermark tier gating."""

from app.core.tier_config import (
    FREE_FEATURES,
    ENTERPRISE_FEATURES,
    STRATEGIC_PARTNER_FEATURES,
    get_tier_features,
)


class TestAudioWatermarkFeatureFlag:
    def test_audio_watermark_false_for_free(self):
        assert FREE_FEATURES["audio_watermark"] is False

    def test_audio_watermark_true_for_enterprise(self):
        assert ENTERPRISE_FEATURES["audio_watermark"] is True

    def test_audio_watermark_true_for_strategic_partner(self):
        assert STRATEGIC_PARTNER_FEATURES["audio_watermark"] is True

    def test_audio_watermark_false_via_get_tier_features_free(self):
        features = get_tier_features("free")
        assert features["audio_watermark"] is False

    def test_audio_watermark_true_via_get_tier_features_enterprise(self):
        features = get_tier_features("enterprise")
        assert features["audio_watermark"] is True

    def test_audio_watermark_false_for_legacy_starter(self):
        features = get_tier_features("starter")
        assert features["audio_watermark"] is False

    def test_audio_watermark_false_for_legacy_professional(self):
        features = get_tier_features("professional")
        assert features["audio_watermark"] is False
