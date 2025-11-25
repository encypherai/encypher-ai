"""
Organization model for tier-based access control and certificate metadata.

Keeps track of usage quotas, feature flags, and signing certificate state.
"""
from enum import Enum
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    TIMESTAMP,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import synonym

from app.database import Base


class OrganizationTier(str, Enum):
    """Organization tier levels matching pricing strategy."""

    STARTER = "starter"  # Free tier - C2PA only, 65/35 rev share
    PROFESSIONAL = "professional"  # $99/mo - Sentence tracking, 70/30 rev share
    BUSINESS = "business"  # $499/mo - Merkle + plagiarism, 75/25 rev share
    ENTERPRISE = "enterprise"  # Custom - Full platform, 80/20 rev share
    STRATEGIC_PARTNER = "strategic_partner"  # Invite only - 85/15 rev share
    
    # Legacy alias for backward compatibility
    FREE = "starter"


class OrganizationCertificateStatus(str, Enum):
    """Certificate lifecycle state for an organization."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class Organization(Base):
    """
    Organization model with tier, quota tracking, and certificate metadata.
    """

    __tablename__ = "organizations"
    __table_args__ = {"extend_existing": True}

    # Primary key
    organization_id = Column(String(255), primary_key=True)

    # Organization details
    organization_name = Column(String(255), nullable=False)
    # Preserve historical attribute name for backward compatibility
    name = synonym("organization_name")
    organization_type = Column(String(50), nullable=False, default="enterprise")
    email = Column(String(255), nullable=False)
    tier = Column(SQLEnum(OrganizationTier), nullable=False, default=OrganizationTier.FREE)

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
        default=OrganizationCertificateStatus.ACTIVE,
    )
    certificate_rotated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    certificate_expiry = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # AWS KMS Support (Enterprise Tier)
    kms_key_id = Column(String(255), nullable=True)
    kms_region = Column(String(50), nullable=True)

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

    # Coalition settings
    coalition_member = Column(Boolean, default=True)  # Auto-join on free tier
    coalition_rev_share_publisher = Column(Integer, default=65)  # Publisher's share (65-85%)
    coalition_rev_share_encypher = Column(Integer, default=35)  # Encypher's share (15-35%)
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
    batch_operations_this_month = Column(Integer, default=0)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<Organization(id={self.organization_id}, "
            f"name={self.organization_name}, tier={self.tier.value})>"
        )

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

        from app.utils.quota import QuotaType, TIER_QUOTAS

        quota_map = {
            "api_calls": (QuotaType.API_CALLS, self.api_calls_this_month),
            "merkle_encoding": (QuotaType.MERKLE_ENCODING, self.merkle_encoding_calls_this_month),
            "merkle_attribution": (QuotaType.MERKLE_ATTRIBUTION, self.merkle_attribution_calls_this_month),
            "merkle_plagiarism": (QuotaType.MERKLE_PLAGIARISM, self.merkle_plagiarism_calls_this_month),
        }

        if quota_type not in quota_map:
            return 0

        quota_enum, current_usage = quota_map[quota_type]
        limit = TIER_QUOTAS.get(self.tier, {}).get(quota_enum, 0)

        return max(0, limit - current_usage)

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
