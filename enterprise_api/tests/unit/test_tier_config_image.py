"""Unit tests for image signing feature flags in tier_config.

Verifies that:
- image_signing is True for all tiers (free and enterprise)
- trustmark_watermark is enterprise-only (False for free, True for enterprise)
- image_fuzzy_search is enterprise-only (False for free, True for enterprise)
- strategic_partner inherits enterprise image features
"""

import os
import sys
from pathlib import Path

# Ensure enterprise_api root is on the path before app imports
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])

from app.core.tier_config import (
    ENTERPRISE_FEATURES,
    FREE_FEATURES,
    STRATEGIC_PARTNER_FEATURES,
    get_tier_features,
)


class TestImageSigningFeatureFlag:
    """image_signing is enabled for all tiers."""

    def test_image_signing_true_for_free(self) -> None:
        assert FREE_FEATURES["image_signing"] is True

    def test_image_signing_true_for_enterprise(self) -> None:
        assert ENTERPRISE_FEATURES["image_signing"] is True

    def test_image_signing_true_via_get_tier_features_free(self) -> None:
        features = get_tier_features("free")
        assert features["image_signing"] is True

    def test_image_signing_true_via_get_tier_features_enterprise(self) -> None:
        features = get_tier_features("enterprise")
        assert features["image_signing"] is True

    def test_image_signing_true_for_strategic_partner(self) -> None:
        assert STRATEGIC_PARTNER_FEATURES["image_signing"] is True


class TestTrustmarkWatermarkFeatureFlag:
    """trustmark_watermark is Enterprise-only."""

    def test_trustmark_watermark_false_for_free(self) -> None:
        assert FREE_FEATURES["trustmark_watermark"] is False

    def test_trustmark_watermark_true_for_enterprise(self) -> None:
        assert ENTERPRISE_FEATURES["trustmark_watermark"] is True

    def test_trustmark_watermark_false_via_get_tier_features_free(self) -> None:
        features = get_tier_features("free")
        assert features["trustmark_watermark"] is False

    def test_trustmark_watermark_true_via_get_tier_features_enterprise(self) -> None:
        features = get_tier_features("enterprise")
        assert features["trustmark_watermark"] is True

    def test_trustmark_watermark_true_for_strategic_partner(self) -> None:
        assert STRATEGIC_PARTNER_FEATURES["trustmark_watermark"] is True

    def test_trustmark_watermark_false_for_legacy_starter(self) -> None:
        """Legacy tier names (starter/professional/business) map to free."""
        for legacy in ("starter", "professional", "business"):
            features = get_tier_features(legacy)
            assert features["trustmark_watermark"] is False, f"Failed for tier={legacy!r}"


class TestImageFuzzySearchFeatureFlag:
    """image_fuzzy_search is Enterprise-only."""

    def test_image_fuzzy_search_false_for_free(self) -> None:
        assert FREE_FEATURES["image_fuzzy_search"] is False

    def test_image_fuzzy_search_true_for_enterprise(self) -> None:
        assert ENTERPRISE_FEATURES["image_fuzzy_search"] is True

    def test_image_fuzzy_search_false_via_get_tier_features_free(self) -> None:
        features = get_tier_features("free")
        assert features["image_fuzzy_search"] is False

    def test_image_fuzzy_search_true_via_get_tier_features_enterprise(self) -> None:
        features = get_tier_features("enterprise")
        assert features["image_fuzzy_search"] is True

    def test_image_fuzzy_search_true_for_strategic_partner(self) -> None:
        assert STRATEGIC_PARTNER_FEATURES["image_fuzzy_search"] is True

    def test_image_fuzzy_search_false_for_legacy_business(self) -> None:
        features = get_tier_features("business")
        assert features["image_fuzzy_search"] is False


class TestStrategicPartnerInheritsEnterpriseImageFeatures:
    """strategic_partner should have all enterprise image features via dict spread."""

    def test_strategic_partner_has_all_enterprise_image_keys(self) -> None:
        image_keys = {"image_signing", "image_fuzzy_search", "trustmark_watermark"}
        for key in image_keys:
            assert key in STRATEGIC_PARTNER_FEATURES, f"Missing key: {key!r}"
            assert STRATEGIC_PARTNER_FEATURES[key] == ENTERPRISE_FEATURES[key], f"strategic_partner[{key!r}] != enterprise[{key!r}]"
