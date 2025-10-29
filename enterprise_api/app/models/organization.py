"""
Organization model for tier-based access control.

Defines organization tiers and tracks usage quotas.
"""
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base


class OrganizationTier(str, Enum):
    """Organization tier levels."""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """
    Organization model with tier and quota tracking.
    
    Tracks organization tier, feature access, and usage quotas.
    """
    __tablename__ = "organizations"
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    organization_id = Column(String(255), primary_key=True)
    
    # Organization details
    name = Column(String(255), nullable=False)
    tier = Column(SQLEnum(OrganizationTier), nullable=False, default=OrganizationTier.FREE)
    
    # Feature flags
    merkle_enabled = Column(Boolean, default=False)
    advanced_analytics_enabled = Column(Boolean, default=False)
    bulk_operations_enabled = Column(Boolean, default=False)
    
    # Monthly quotas
    api_calls_this_month = Column(Integer, default=0)
    merkle_encoding_calls_this_month = Column(Integer, default=0)
    merkle_attribution_calls_this_month = Column(Integer, default=0)
    merkle_plagiarism_calls_this_month = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (if needed)
    # merkle_roots = relationship("MerkleRoot", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.organization_id}, name={self.name}, tier={self.tier.value})>"
    
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
