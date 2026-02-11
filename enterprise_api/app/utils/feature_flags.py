"""
Feature flag system for tier-based feature access.

Manages which features are available to which tiers.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set

from app.models.organization import OrganizationTier


class Feature(str, Enum):
    """Available features in the system."""

    # Merkle Tree Features
    MERKLE_ENCODING = "merkle_encoding"
    MERKLE_ATTRIBUTION = "merkle_attribution"
    MERKLE_PLAGIARISM = "merkle_plagiarism"
    MERKLE_PROOF_VERIFICATION = "merkle_proof_verification"
    FUZZY_FINGERPRINTING = "fuzzy_fingerprinting"

    # Advanced Features
    BULK_OPERATIONS = "bulk_operations"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_SEGMENTATION = "custom_segmentation"
    API_WEBHOOKS = "api_webhooks"

    # Performance Features
    PRIORITY_PROCESSING = "priority_processing"
    DEDICATED_RESOURCES = "dedicated_resources"
    CUSTOM_RATE_LIMITS = "custom_rate_limits"

    # Support Features
    PREMIUM_SUPPORT = "premium_support"
    SLA_GUARANTEE = "sla_guarantee"


@dataclass
class FeatureConfig:
    """Configuration for a feature."""

    name: str
    description: str
    required_tier: OrganizationTier
    enabled: bool = True
    beta: bool = False


class FeatureFlagManager:
    """
    Manages feature flags and tier-based access.

    This class defines which features are available to which tiers
    and provides methods to check feature access.
    """

    # Feature configuration mapping
    FEATURE_CONFIG: Dict[Feature, FeatureConfig] = {
        # Merkle Tree Features - Free tier gets basic, Enterprise gets advanced
        Feature.MERKLE_ENCODING: FeatureConfig(
            name="Sentence-Level Merkle Roots",
            description="Encode documents into Merkle trees with sentence-level granularity",
            required_tier=OrganizationTier.FREE,
        ),
        Feature.MERKLE_ATTRIBUTION: FeatureConfig(
            name="Source Attribution", description="Find source documents for text segments", required_tier=OrganizationTier.FREE
        ),
        Feature.MERKLE_PLAGIARISM: FeatureConfig(
            name="Plagiarism Detection",
            description="Detect plagiarism and generate reports",
            required_tier=OrganizationTier.ENTERPRISE,
        ),
        Feature.MERKLE_PROOF_VERIFICATION: FeatureConfig(
            name="Proof Verification", description="Verify Merkle proofs", required_tier=OrganizationTier.FREE
        ),
        Feature.FUZZY_FINGERPRINTING: FeatureConfig(
            name="Fuzzy Fingerprinting",
            description="Locality-sensitive fingerprints for fuzzy attribution",
            required_tier=OrganizationTier.ENTERPRISE,
        ),
        # Advanced Features - Enterprise only
        Feature.BULK_OPERATIONS: FeatureConfig(
            name="Bulk Operations", description="Batch process multiple documents", required_tier=OrganizationTier.ENTERPRISE
        ),
        Feature.ADVANCED_ANALYTICS: FeatureConfig(
            name="Advanced Analytics", description="Detailed usage analytics and insights", required_tier=OrganizationTier.ENTERPRISE
        ),
        Feature.CUSTOM_SEGMENTATION: FeatureConfig(
            name="Custom Segmentation", description="Define custom segmentation rules", required_tier=OrganizationTier.ENTERPRISE
        ),
        Feature.API_WEBHOOKS: FeatureConfig(
            name="API Webhooks", description="Receive webhooks for events", required_tier=OrganizationTier.ENTERPRISE
        ),
        # Performance Features - Enterprise Only
        Feature.PRIORITY_PROCESSING: FeatureConfig(
            name="Priority Processing", description="Priority queue for requests", required_tier=OrganizationTier.ENTERPRISE
        ),
        Feature.DEDICATED_RESOURCES: FeatureConfig(
            name="Dedicated Resources", description="Dedicated compute resources", required_tier=OrganizationTier.ENTERPRISE
        ),
        Feature.CUSTOM_RATE_LIMITS: FeatureConfig(
            name="Custom Rate Limits", description="Customizable rate limits", required_tier=OrganizationTier.ENTERPRISE
        ),
        # Support Features
        Feature.PREMIUM_SUPPORT: FeatureConfig(
            name="Premium Support", description="24/7 premium support", required_tier=OrganizationTier.ENTERPRISE
        ),
        Feature.SLA_GUARANTEE: FeatureConfig(name="SLA Guarantee", description="99.9% uptime SLA", required_tier=OrganizationTier.ENTERPRISE),
    }

    @classmethod
    def has_feature_access(cls, tier: OrganizationTier, feature: Feature) -> bool:
        """
        Check if a tier has access to a feature.

        Args:
            tier: Organization tier
            feature: Feature to check

        Returns:
            True if tier has access, False otherwise
        """
        config = cls.FEATURE_CONFIG.get(feature)
        if not config:
            return False

        if not config.enabled:
            return False

        # Tier hierarchy
        tier_levels = {
            OrganizationTier.FREE: 0,
            OrganizationTier.ENTERPRISE: 1,
            OrganizationTier.STRATEGIC_PARTNER: 2,
        }

        current_level = tier_levels.get(tier, -1)
        required_level = tier_levels.get(config.required_tier, 999)

        return current_level >= required_level

    @classmethod
    def get_available_features(cls, tier: OrganizationTier) -> List[FeatureConfig]:
        """
        Get all features available to a tier.

        Args:
            tier: Organization tier

        Returns:
            List of available feature configurations
        """
        return [config for feature, config in cls.FEATURE_CONFIG.items() if cls.has_feature_access(tier, feature)]

    @classmethod
    def get_feature_config(cls, feature: Feature) -> FeatureConfig:
        """
        Get configuration for a feature.

        Args:
            feature: Feature to get config for

        Returns:
            Feature configuration

        Raises:
            KeyError: If feature not found
        """
        return cls.FEATURE_CONFIG[feature]

    @classmethod
    def is_feature_enabled(cls, feature: Feature) -> bool:
        """
        Check if a feature is globally enabled.

        Args:
            feature: Feature to check

        Returns:
            True if enabled, False otherwise
        """
        config = cls.FEATURE_CONFIG.get(feature)
        return config.enabled if config else False

    @classmethod
    def get_required_tier(cls, feature: Feature) -> OrganizationTier:
        """
        Get the required tier for a feature.

        Args:
            feature: Feature to check

        Returns:
            Required organization tier

        Raises:
            KeyError: If feature not found
        """
        return cls.FEATURE_CONFIG[feature].required_tier


# Convenience function for checking feature access
def check_feature_access(tier: OrganizationTier, feature: Feature) -> bool:
    """
    Check if a tier has access to a feature.

    Args:
        tier: Organization tier
        feature: Feature to check

    Returns:
        True if tier has access, False otherwise
    """
    return FeatureFlagManager.has_feature_access(tier, feature)


# Tier feature matrix for documentation
# TEAM_145: Consolidated to free/enterprise/strategic_partner
TIER_FEATURES: Dict[OrganizationTier, Set[Feature]] = {
    OrganizationTier.FREE: {
        Feature.MERKLE_ENCODING,
        Feature.MERKLE_ATTRIBUTION,
        Feature.MERKLE_PROOF_VERIFICATION,
    },
    OrganizationTier.ENTERPRISE: {
        Feature.MERKLE_ENCODING,
        Feature.MERKLE_ATTRIBUTION,
        Feature.MERKLE_PROOF_VERIFICATION,
        Feature.MERKLE_PLAGIARISM,
        Feature.FUZZY_FINGERPRINTING,
        Feature.BULK_OPERATIONS,
        Feature.ADVANCED_ANALYTICS,
        Feature.CUSTOM_SEGMENTATION,
        Feature.API_WEBHOOKS,
        Feature.PRIORITY_PROCESSING,
        Feature.DEDICATED_RESOURCES,
        Feature.CUSTOM_RATE_LIMITS,
        Feature.PREMIUM_SUPPORT,
        Feature.SLA_GUARANTEE,
    },
    OrganizationTier.STRATEGIC_PARTNER: {
        Feature.MERKLE_ENCODING,
        Feature.MERKLE_ATTRIBUTION,
        Feature.MERKLE_PROOF_VERIFICATION,
        Feature.MERKLE_PLAGIARISM,
        Feature.FUZZY_FINGERPRINTING,
        Feature.BULK_OPERATIONS,
        Feature.ADVANCED_ANALYTICS,
        Feature.CUSTOM_SEGMENTATION,
        Feature.API_WEBHOOKS,
        Feature.PRIORITY_PROCESSING,
        Feature.DEDICATED_RESOURCES,
        Feature.CUSTOM_RATE_LIMITS,
        Feature.PREMIUM_SUPPORT,
        Feature.SLA_GUARANTEE,
    },
}
