"""
SQLAlchemy database models for Auth Service
"""

from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET
import uuid
import secrets

from encypher_commercial_shared.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT


# TEAM_006: API Access Gating - Status enum for user API access
class ApiAccessStatus(str, Enum):
    """Status of a user's API access request"""

    NOT_REQUESTED = "not_requested"  # Default for new users
    PENDING = "pending"  # User requested, awaiting admin review
    APPROVED = "approved"  # Admin approved - user can generate API keys
    DENIED = "denied"  # Admin denied - user cannot generate API keys
    SUSPENDED = "suspended"  # TEAM_164: Admin suspended - user cannot request or use API access


Base = declarative_base()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


def generate_prefixed_id(prefix: str):
    """Generate a prefixed ID like 'org_abc123...'"""
    return f"{prefix}_{secrets.token_hex(8)}"


class User(Base):
    """User model - matches core_db schema exactly"""

    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=generate_uuid)

    # Identity
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # NULL for OAuth-only users

    # Profile
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Auth
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)

    # OAuth Providers (separate columns per provider in core_db)
    google_id = Column(String(255), unique=True, nullable=True)
    github_id = Column(String(255), unique=True, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)  # TEAM_006: Super admin flag
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # TEAM_006: API Access Gating
    # TEAM_191: Auto-approve on signup — users get instant API access
    api_access_status = Column(String(32), default=ApiAccessStatus.APPROVED.value, nullable=False)
    api_access_requested_at = Column(DateTime(timezone=True), nullable=True)
    api_access_decided_at = Column(DateTime(timezone=True), nullable=True)
    api_access_decided_by = Column(String(64), nullable=True)  # Admin user_id who approved/denied
    api_access_use_case = Column(Text, nullable=True)  # User's stated use case for API access
    api_access_denial_reason = Column(Text, nullable=True)  # Reason if denied

    # TEAM_191: Server-side onboarding checklist
    onboarding_checklist = Column(JSON, nullable=False, default=dict)
    onboarding_completed_at = Column(DateTime(timezone=True), nullable=True)

    # TEAM_191: Mandatory setup wizard — NULL until wizard is done; dashboard blocks if NULL
    setup_completed_at = Column(DateTime(timezone=True), nullable=True)

    # Team management
    default_organization_id = Column(String(64), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class RefreshToken(Base):
    """Refresh token model for token management"""

    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    token = Column(Text, nullable=False, unique=True)

    # Token metadata
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Device/client info
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"


class PasswordResetToken(Base):
    """Password reset token model"""

    __tablename__ = "password_reset_tokens"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    user_id = Column(String(64), nullable=False, index=True)
    token = Column(String(64), nullable=False, unique=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"


class EmailVerificationToken(Base):
    """Email verification token model"""

    __tablename__ = "email_verification_tokens"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    user_id = Column(String(64), nullable=False, index=True)
    token = Column(String(64), nullable=False, unique=True, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id})>"


# ============================================
# TEAM MANAGEMENT MODELS
# ============================================


class Organization(Base):
    """Organization model - the primary billing entity"""

    __tablename__ = "organizations"

    id = Column(String(64), primary_key=True, default=lambda: generate_prefixed_id("org"))

    # Identity
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False)

    # TEAM_191: Publisher identity — individual creator vs organization
    account_type = Column(String(32), nullable=True)  # "individual" or "organization"; NULL = not yet set
    display_name = Column(String(255), nullable=True)  # Human-readable publisher name for signed content
    anonymous_publisher = Column(Boolean, default=False, nullable=False)  # If true, show org ID instead of name on verification

    # Subscription & Tier
    tier = Column(String(32), nullable=False, default="free")

    # Trial metadata
    trial_tier = Column(String(32), nullable=True)
    trial_months = Column(Integer, nullable=True)
    trial_started_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Stripe Integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(String(32), default="active")

    # Feature Flags
    features = Column(JSON, nullable=False, default=dict)

    # Purchased add-ons (JSON dict of add-on ID -> config/status)
    # TEAM_145: Add-ons are independent of tier
    add_ons = Column(JSON, nullable=False, default=dict)

    # Usage Limits
    monthly_api_limit = Column(Integer, default=10000)
    monthly_api_usage = Column(Integer, default=0)
    usage_reset_at = Column(DateTime(timezone=True), nullable=True)

    # Team Management
    max_seats = Column(Integer, default=1)  # -1 = unlimited

    # Coalition Revenue Sharing
    coalition_member = Column(Boolean, default=True)
    coalition_rev_share = Column(Integer, default=DEFAULT_COALITION_PUBLISHER_PERCENT)
    coalition_opted_out = Column(Boolean, default=False)

    # BYOK (Bring Your Own Key) Certificate Support
    certificate_pem = Column(Text, nullable=True)
    certificate_chain = Column(Text, nullable=True)
    certificate_status = Column(String(20), default="none")  # none, pending, active, expired
    certificate_rotated_at = Column(DateTime(timezone=True), nullable=True)
    certificate_expiry = Column(DateTime(timezone=True), nullable=True)
    kms_key_id = Column(String(255), nullable=True)
    kms_region = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("OrganizationInvitation", back_populates="organization", cascade="all, delete-orphan")
    domain_claims = relationship("OrganizationDomainClaim", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("OrganizationAuditLog", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, tier={self.tier})>"


class OrganizationMember(Base):
    """Organization member - links users to organizations with roles"""

    __tablename__ = "organization_members"

    id = Column(String(64), primary_key=True, default=lambda: generate_prefixed_id("mem"))
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Role & Permissions
    role = Column(String(32), nullable=False, default="member")  # owner, admin, manager, member, viewer

    # Status
    status = Column(String(32), nullable=False, default="active")  # active, invited, suspended

    # Invitation tracking
    invited_by = Column(String(64), ForeignKey("users.id"), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Activity
    last_active_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<OrganizationMember(org={self.organization_id}, user={self.user_id}, role={self.role})>"


class OrganizationInvitation(Base):
    """Pending invitation to join an organization"""

    __tablename__ = "organization_invitations"

    id = Column(String(64), primary_key=True, default=lambda: generate_prefixed_id("inv"))
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Invitation details
    email = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    organization_name = Column(String(255), nullable=True)
    tier = Column(String(32), nullable=True)
    trial_months = Column(Integer, nullable=True)
    role = Column(String(32), nullable=False, default="member")  # admin, manager, member, viewer

    # Token for accepting invitation
    token = Column(String(255), nullable=False, unique=True, default=lambda: secrets.token_urlsafe(32))

    # Tracking
    invited_by = Column(String(64), ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)  # Optional personal message

    # Status
    status = Column(String(32), nullable=False, default="pending")  # pending, accepted, expired, cancelled

    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<OrganizationInvitation(org={self.organization_id}, email={self.email}, status={self.status})>"


class OrganizationDomainClaim(Base):
    """Organization domain claim for verification and auto-join settings"""

    __tablename__ = "organization_domain_claims"

    id = Column(String(64), primary_key=True, default=lambda: generate_prefixed_id("odc"))
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(255), nullable=False)
    verification_email = Column(String(255), nullable=False)

    dns_token = Column(String(255), nullable=False)
    email_token = Column(String(255), nullable=False)

    status = Column(String(32), nullable=False, default="pending")  # pending, verified, rejected, expired
    dns_verified_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    auto_join_enabled = Column(Boolean, default=False)
    created_by = Column(String(64), ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="domain_claims")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<OrganizationDomainClaim(org={self.organization_id}, domain={self.domain}, status={self.status})>"


class OrganizationAuditLog(Base):
    """Audit log for organization actions"""

    __tablename__ = "organization_audit_log"

    id = Column(String(64), primary_key=True, default=lambda: generate_prefixed_id("aud"))
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Actor
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Preserved even if user deleted

    # Action details
    action = Column(String(100), nullable=False)  # e.g., 'member.invited', 'member.role_changed'
    resource_type = Column(String(50), nullable=True)  # e.g., 'member', 'api_key', 'settings'
    resource_id = Column(String(64), nullable=True)

    # Change details
    details = Column(JSON, nullable=True)  # { old_value: ..., new_value: ..., etc. }

    # Request metadata
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<OrganizationAuditLog(org={self.organization_id}, action={self.action})>"
