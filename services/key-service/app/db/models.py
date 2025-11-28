"""
SQLAlchemy database models for Key Service

Uses the unified schema from services/migrations/001_core_schema.sql
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


class Organization(Base):
    """Organization model - the billing entity"""
    __tablename__ = "organizations"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True)
    email = Column(String(255), nullable=False, unique=True)

    # Subscription
    tier = Column(String(32), nullable=False, default='starter')
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255))
    subscription_status = Column(String(32), default='active')

    # Features (JSONB)
    features = Column(JSONB, nullable=False, default={})

    # Usage
    monthly_api_limit = Column(Integer, default=10000)
    monthly_api_usage = Column(Integer, default=0)

    # Coalition
    coalition_member = Column(Boolean, default=True)
    coalition_rev_share = Column(Integer, default=65)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ApiKey(Base):
    """API Key model - unified schema"""
    __tablename__ = "api_keys"

    id = Column(String(64), primary_key=True, default=lambda: f"key_{uuid.uuid4().hex[:16]}")

    # Owner - can be organization_id OR user_id depending on context
    # For dashboard users without orgs, we use user_id
    organization_id = Column(String(64), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True)
    user_id = Column(String(64), nullable=True, index=True)  # For users without orgs

    # Key information
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)  # SHA-256 hash
    key_prefix = Column(String(20), nullable=False)  # First chars for display
    fingerprint = Column(String(64), nullable=True)  # Key fingerprint for identification

    # Permissions (JSONB array)
    permissions = Column(JSONB, nullable=False, default=["sign", "verify", "lookup"])

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)

    # Lifecycle
    created_by = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ApiKey(id={self.id}, name={self.name}, user={self.user_id}, org={self.organization_id})>"


class KeyUsage(Base):
    """API Key usage tracking"""
    __tablename__ = "key_usage"

    id = Column(String(64), primary_key=True, default=lambda: f"ku_{uuid.uuid4().hex[:12]}")
    key_id = Column(String(64), ForeignKey('api_keys.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(String(64), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)

    # Request information
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)

    # Client information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<KeyUsage(id={self.id}, key_id={self.key_id})>"


class KeyRotation(Base):
    """API Key rotation history"""
    __tablename__ = "key_rotations"

    id = Column(String(64), primary_key=True, default=lambda: f"kr_{uuid.uuid4().hex[:12]}")
    old_key_id = Column(String(64), nullable=False, index=True)
    new_key_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)

    # Rotation information
    reason = Column(String(255), nullable=True)
    rotated_by = Column(String(64), nullable=True)  # user_id or "system"

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<KeyRotation(id={self.id}, old_key_id={self.old_key_id}, new_key_id={self.new_key_id})>"
