"""
Organization model for tier-based access control and certificate metadata.

Keeps track of usage quotas, feature flags, and signing certificate state.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import synonym

from app.core.pricing_constants import COALITION_ENCYPHER_SHARE, COALITION_PUBLISHER_SHARE
from app.database import Base


class OrganizationTier(str, Enum):
    """Organization tier levels matching pricing strategy (Feb 2026).

    Only three tiers: free, enterprise, strategic_partner.
    Add-ons are tracked separately on the Organization.add_ons JSON column.
    """

    FREE = "free"  # Free tier - signing, verification, coalition
    ENTERPRISE = "enterprise"  # Custom - unlimited everything, all features
    STRATEGIC_PARTNER = "strategic_partner"  # Invite only

    # Legacy aliases — coerce old tier strings to FREE
    STARTER = "free"
    PROFESSIONAL = "free"
    BUSINESS = "free"


class OrganizationStatus(str, Enum):
    """Organization account status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


class OrganizationCertificateStatus(str, Enum):
    """Certificate lifecycle state for an organization."""

    NONE = "none"  # No certificate yet
    PENDING = "pending"  # Certificate requested
    ACTIVE = "active"  # Certificate valid
    EXPIRED = "expired"  # Certificate expired
    REVOKED = "revoked"  # Certificate revoked


class Organization(Base):
    """
    Organization model with tier, quota tracking, and certificate metadata.

    Updated to use unified schema with 'id' as primary key.
    """

    __tablename__ = "organizations"
    __table_args__ = {"extend_existing": True}

    # Primary key - matches unified schema: id VARCHAR(64) PRIMARY KEY
    id = Column(String(64), primary_key=True)

    # Alias for backward compatibility
    organization_id = synonym("id")

    # Organization details - matches unified schema
    name = Column(String(255), nullable=False)
    # Alias for backward compatibility
    organization_name = synonym("name")
    slug = Column(String(100), nullable=True, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    tier = Column(String(32), nullable=False, default="free")

    # Partner hierarchy
    parent_org_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Organization status (suspension/activation)
    status = Column(String(32), nullable=False, default="active", index=True)
    suspended_at = Column(TIMESTAMP(timezone=True), nullable=True)
    suspension_reason = Column(Text, nullable=True)

    # Certificate metadata
    certificate_pem = Column(Text, nullable=True)
    cert_chain_pem = Column("certificate_chain", Text, nullable=True)
    certificate_status = Column(
        SQLEnum(
            OrganizationCertificateStatus,
            name="organization_certificate_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        default=OrganizationCertificateStatus.NONE,
    )
    certificate_rotated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    certificate_expiry = Column(TIMESTAMP(timezone=True), nullable=True)

    # AWS KMS Support (Enterprise Tier)
    kms_key_id = Column(String(255), nullable=True)
    kms_region = Column(String(50), nullable=True)

    # Purchased add-ons (JSON dict of add-on ID -> config/status)
    # TEAM_145: Add-ons are independent of tier, tracked here
    add_ons = Column(JSON, nullable=False, default=dict)

    # Feature flags
    merkle_enabled = Column(Boolean, default=False)
    advanced_analytics_enabled = Column(Boolean, default=False)
    bulk_operations_enabled = Column(Boolean, default=False)
    sentence_tracking_enabled = Column(Boolean, default=False)
    streaming_enabled = Column(Boolean, default=False)
    byok_enabled = Column(Boolean, default=False)
    team_management_enabled = Column(Boolean, default=False)
    audit_logs_enabled = Column(Boolean, default=False)
    sso_enabled = Column(Boolean, default=False)
    custom_assertions_enabled = Column(Boolean, default=False)
    fuzzy_fingerprint_enabled = Column(Boolean, default=False)

    default_c2pa_template_id = Column(String(64), nullable=True)

    # Coalition settings
    coalition_member = Column(Boolean, default=True)  # Auto-join on free tier
    coalition_rev_share_publisher = Column(Integer, default=COALITION_PUBLISHER_SHARE)
    coalition_rev_share_encypher = Column(Integer, default=COALITION_ENCYPHER_SHARE)
    coalition_opted_out = Column(Boolean, default=False)
    coalition_opted_out_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Usage tracking / quotas
    monthly_quota = Column(Integer, default=1000)
    documents_signed = Column(Integer, default=0)
    sentences_signed = Column(Integer, default=0)
    sentences_tracked_this_month = Column(Integer, default=0)  # For sentence tracking quota
    api_calls_this_month = Column(Integer, default=0)
    merkle_encoding_calls_this_month = Column(Integer, default=0)
    merkle_attribution_calls_this_month = Column(Integer, default=0)
    merkle_plagiarism_calls_this_month = Column(Integer, default=0)
    fuzzy_index_calls_this_month = Column(Integer, default=0)
    fuzzy_search_calls_this_month = Column(Integer, default=0)
    batch_operations_this_month = Column(Integer, default=0)

    # CDN Provenance feature (Phase 1)
    cdn_provenance_enabled = Column(Boolean, default=False)
    cdn_image_registrations_this_month = Column(Integer, default=0)

    # Overage Billing
    has_payment_method = Column(Boolean, default=False, nullable=False)
    overage_enabled = Column(Boolean, default=False, nullable=False)
    overage_cap_cents = Column(Integer, nullable=True)  # NULL = no cap

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        tier_value = self.tier.value if isinstance(self.tier, OrganizationTier) else self.tier
        return f"<Organization(id={self.organization_id}, name={self.organization_name}, tier={tier_value})>"

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled for this organization.

        Args:
            feature: Feature name

        Returns:
            True if enabled, False otherwise
        """

        feature_map = {
            "merkle": self.merkle_enabled,
            "advanced_analytics": self.advanced_analytics_enabled,
            "bulk_operations": self.bulk_operations_enabled,
            "sentence_tracking": self.sentence_tracking_enabled,
            "streaming": self.streaming_enabled,
            "byok": self.byok_enabled,
            "team_management": self.team_management_enabled,
            "audit_logs": self.audit_logs_enabled,
            "sso": self.sso_enabled,
            "custom_assertions": self.custom_assertions_enabled,
            "fuzzy_fingerprint": self.fuzzy_fingerprint_enabled,
        }
        return feature_map.get(feature, False)

    def get_quota_remaining(self, quota_type: str) -> int:
        """
        Get remaining quota for a quota type.

        Args:
            quota_type: Type of quota

        Returns:
            Remaining quota count
        """

        from app.utils.quota import TIER_QUOTAS, QuotaType

        quota_map = {
            "api_calls": (QuotaType.API_CALLS, self.api_calls_this_month),
            "merkle_encoding": (QuotaType.MERKLE_ENCODING, self.merkle_encoding_calls_this_month),
            "merkle_attribution": (QuotaType.MERKLE_ATTRIBUTION, self.merkle_attribution_calls_this_month),
            "merkle_plagiarism": (QuotaType.MERKLE_PLAGIARISM, self.merkle_plagiarism_calls_this_month),
            "fuzzy_index": (QuotaType.FUZZY_INDEX, self.fuzzy_index_calls_this_month),
            "fuzzy_search": (QuotaType.FUZZY_SEARCH, self.fuzzy_search_calls_this_month),
        }

        if quota_type not in quota_map:
            return 0

        quota_enum, current_usage = quota_map[quota_type]
        limit = TIER_QUOTAS.get(self.tier, {}).get(quota_enum, 0)

        return max(0, limit - current_usage)

    @property
    def is_suspended(self) -> bool:
        """Return True if the organization is suspended."""
        return self.status == "suspended"

    @property
    def certificate_is_active(self) -> bool:
        """Return True if the certificate can be used for verification."""

        if self.certificate_status not in (
            OrganizationCertificateStatus.ACTIVE,
            OrganizationCertificateStatus.INACTIVE,
        ):
            return False
        if self.certificate_expiry and self.certificate_expiry < datetime.utcnow():
            return False
        return bool(self.certificate_pem)
