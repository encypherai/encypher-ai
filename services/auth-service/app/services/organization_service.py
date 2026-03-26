"""
Organization Service - Business logic for team management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging

import httpx
from sqlalchemy.orm import Session, load_only
from sqlalchemy import and_, inspect

from encypher_commercial_shared.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT

from ..db.models import (
    Organization,
    OrganizationMember,
    OrganizationInvitation,
    OrganizationAuditLog,
    OrganizationDomainClaim,
    User,
)
from ..core.config import settings
import secrets
import re


# Role hierarchy for permission checks
ROLE_HIERARCHY = {"owner": 5, "admin": 4, "manager": 3, "member": 2, "viewer": 1}

# What roles can manage what
ROLE_CAN_INVITE = {"owner", "admin", "manager"}
ROLE_CAN_MANAGE_MEMBERS = {"owner", "admin"}
ROLE_CAN_MANAGE_BILLING = {"owner", "admin"}
ROLE_CAN_MANAGE_SETTINGS = {"owner", "admin"}
ROLE_CAN_CREATE_API_KEYS = {"owner", "admin", "manager"}

COMMON_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "aol.com",
    "proton.me",
    "protonmail.com",
    "live.com",
}

DOMAIN_LIMITS_BY_TIER = {
    "free": 1,
    "enterprise": 10,
    "strategic_partner": 10,
}

DOMAIN_REGEX = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}$")

ENTERPRISE_EVALUATION_TIER = "enterprise"
ENTERPRISE_EVALUATION_TRIAL_MONTHS = 2

logger = logging.getLogger(__name__)


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from organization name"""
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", name.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:100]


def normalize_domain(domain: str) -> str:
    """Normalize a domain for storage and comparison."""
    cleaned = domain.strip().lower()
    if cleaned.startswith("http://"):
        cleaned = cleaned[7:]
    if cleaned.startswith("https://"):
        cleaned = cleaned[8:]
    if cleaned.startswith("@"):
        cleaned = cleaned[1:]
    return cleaned.split("/")[0]


def utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


def is_expired(expires_at: Optional[datetime]) -> bool:
    """Safely compare expiration timestamps across naive and aware datetimes."""
    if expires_at is None:
        return False
    if expires_at.tzinfo is None:
        return expires_at < datetime.utcnow()
    return expires_at < utc_now()


class OrganizationService:
    """Service for organization management"""

    def __init__(self, db: Session):
        self.db = db
        self._organization_columns: Optional[set[str]] = None

    def _table_columns(self, table_name: str) -> set[str]:
        return {column["name"] for column in inspect(self.db.get_bind()).get_columns(table_name)}

    def _organization_columns_in_db(self) -> set[str]:
        if self._organization_columns is None:
            self._organization_columns = self._table_columns(Organization.__tablename__)
        return self._organization_columns

    def _organization_query(self):
        query = self.db.query(Organization)
        organization_columns = self._organization_columns_in_db()
        loadable_columns = [getattr(Organization, column.name) for column in Organization.__table__.columns if column.name in organization_columns]
        if loadable_columns:
            query = query.options(load_only(*loadable_columns))
        return query

    def _organization_slug_exists(self, slug: str) -> bool:
        return self.db.query(Organization.id).filter(Organization.slug == slug).first() is not None

    def _organization_email_exists(self, email: str) -> bool:
        return self.db.query(Organization.id).filter(Organization.email == email).first() is not None

    # ==========================================
    # ORGANIZATION CRUD
    # ==========================================

    def create_organization(self, name: str, email: str, owner_user_id: str, tier: str = "free") -> Organization:
        """Create a new organization with the user as owner"""

        org = self._create_organization_record(name=name, email=email, tier=tier)

        # Add owner as first member
        owner_member = OrganizationMember(organization_id=org.id, user_id=owner_user_id, role="owner", status="active", accepted_at=datetime.utcnow())
        self.db.add(owner_member)

        # Log the creation
        self._log_action(org.id, owner_user_id, "organization.created", "organization", org.id, {"name": name, "tier": tier})

        self.db.commit()
        return org

    def create_organization_without_owner(self, name: str, email: str, tier: str, created_by: str) -> Organization:
        """Create an organization without assigning a member yet."""
        org = self._create_organization_record(name=name, email=email, tier=tier)
        self._log_action(org.id, created_by, "organization.created", "organization", org.id, {"name": name, "tier": tier})
        self.db.commit()
        return org

    def _create_organization_record(self, *, name: str, email: str, tier: str) -> Organization:
        name = name.strip()
        email = email.strip().lower()

        # Generate unique slug
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 1
        while self._organization_slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        if self._organization_email_exists(email):
            raise ValueError("An organization with this email already exists")

        # Set max_seats based on tier
        max_seats = {
            "free": 1,
            "enterprise": -1,  # unlimited
            "strategic_partner": -1,  # unlimited
        }.get(tier, 1)

        # Create organization
        org = Organization(name=name, slug=slug, email=email, tier=tier, max_seats=max_seats)
        self.db.add(org)
        self.db.flush()  # Get the org.id
        return org

    def _get_tier_config(self, tier: str) -> Optional[dict]:
        # TEAM_145: Map legacy tier names
        legacy_map = {"starter": "free", "professional": "free", "business": "free"}
        tier = legacy_map.get(tier, tier)

        tier_config = {
            "free": {
                "max_seats": 1,
                "monthly_api_limit": 10000,
                "coalition_rev_share": DEFAULT_COALITION_PUBLISHER_PERCENT,
                "features": {
                    "team_management": False,
                    "audit_logs": False,
                    "merkle_enabled": True,
                    "bulk_operations": False,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": False,
                    "sso": False,
                    "custom_assertions": False,
                    "whitelabel": False,
                },
            },
            "enterprise": {
                "max_seats": -1,
                "monthly_api_limit": -1,
                "coalition_rev_share": DEFAULT_COALITION_PUBLISHER_PERCENT,
                "features": {
                    "team_management": True,
                    "audit_logs": True,
                    "merkle_enabled": True,
                    "bulk_operations": True,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": True,
                    "sso": True,
                    "fuzzy_fingerprint": True,
                    "custom_assertions": True,
                    "whitelabel": True,
                },
            },
            "strategic_partner": {
                "max_seats": -1,
                "monthly_api_limit": -1,
                "coalition_rev_share": DEFAULT_COALITION_PUBLISHER_PERCENT,
                "features": {
                    "team_management": True,
                    "audit_logs": True,
                    "merkle_enabled": True,
                    "bulk_operations": True,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": True,
                    "sso": True,
                    "fuzzy_fingerprint": True,
                    "custom_assertions": True,
                    "whitelabel": True,
                },
            },
        }
        return tier_config.get(tier)

    def update_tier_internal(
        self,
        *,
        org_id: str,
        tier: str,
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
        subscription_status: Optional[str] = None,
    ) -> Organization:
        org = self.get_organization(org_id)
        if not org:
            raise ValueError("Organization not found")

        config = self._get_tier_config(tier)
        if not config:
            raise ValueError(f"Invalid tier: {tier}")

        previous_tier = org.tier
        org.tier = tier
        org.max_seats = config["max_seats"]
        org.monthly_api_limit = config["monthly_api_limit"]
        org.features = config["features"]
        org.coalition_rev_share = config["coalition_rev_share"]

        if stripe_customer_id:
            org.stripe_customer_id = stripe_customer_id
        if stripe_subscription_id:
            org.stripe_subscription_id = stripe_subscription_id
        if subscription_status:
            org.subscription_status = subscription_status

        self._log_action(
            org_id=org_id,
            user_id=None,
            action="subscription.tier_updated",
            resource_type="organization",
            resource_id=org_id,
            details={"previous_tier": previous_tier, "new_tier": tier, "subscription_status": subscription_status},
        )

        self.db.commit()
        return org

    def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        org = self._organization_query().filter(Organization.id == org_id).first()
        return self.refresh_trial_state(org)

    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        return self._organization_query().filter(Organization.slug == slug).first()

    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """Get all organizations a user belongs to"""
        memberships = (
            self.db.query(OrganizationMember).filter(and_(OrganizationMember.user_id == user_id, OrganizationMember.status == "active")).all()
        )

        org_ids = [m.organization_id for m in memberships]
        if not org_ids:
            return []

        orgs = self._organization_query().filter(Organization.id.in_(org_ids)).all()
        return [self.refresh_trial_state(org) for org in orgs]

    def refresh_trial_state(self, org: Optional[Organization]) -> Optional[Organization]:
        """Downgrade expired evaluation trials to free when org state is read."""
        if not org:
            return None

        if not self._should_expire_trial(org):
            return org

        return self._expire_trial_to_free(org)

    def _should_expire_trial(self, org: Organization) -> bool:
        if org.subscription_status != "trialing":
            return False
        trial_ends_at = org.trial_ends_at
        if not trial_ends_at:
            return False
        comparison_now = datetime.now(timezone.utc) if trial_ends_at.tzinfo else datetime.utcnow()
        if trial_ends_at > comparison_now:
            return False
        if not org.trial_tier:
            return False
        if org.tier != org.trial_tier:
            return False
        return True

    def _expire_trial_to_free(self, org: Organization) -> Organization:
        config = self._get_tier_config("free")
        if not config:
            raise ValueError("Invalid tier: free")

        previous_tier = org.tier
        org.tier = "free"
        org.max_seats = config["max_seats"]
        org.monthly_api_limit = config["monthly_api_limit"]
        org.features = config["features"]
        org.coalition_rev_share = config["coalition_rev_share"]
        org.subscription_status = "expired"

        self._log_action(
            org_id=org.id,
            user_id=None,
            action="subscription.trial_expired_downgraded",
            resource_type="organization",
            resource_id=org.id,
            details={
                "previous_tier": previous_tier,
                "new_tier": "free",
                "trial_tier": org.trial_tier,
                "trial_ends_at": org.trial_ends_at.isoformat() if org.trial_ends_at else None,
            },
        )

        self.db.commit()
        self.db.refresh(org)
        return org

    def update_organization(self, org_id: str, user_id: str, **updates) -> Optional[Organization]:
        """Update organization settings"""
        org = self.get_organization(org_id)
        if not org:
            return None

        # Check permission
        if not self._has_permission(org_id, user_id, ROLE_CAN_MANAGE_SETTINGS):
            raise PermissionError("You don't have permission to update organization settings")

        old_values = {}
        for key, value in updates.items():
            if hasattr(org, key):
                old_values[key] = getattr(org, key)
                setattr(org, key, value)

        # Log the update
        self._log_action(org_id, user_id, "organization.updated", "organization", org_id, {"old": old_values, "new": updates})

        self.db.commit()
        return org

    # ==========================================
    # MEMBER MANAGEMENT
    # ==========================================

    def get_members(self, org_id: str) -> List[OrganizationMember]:
        """Get all members of an organization"""
        return self.db.query(OrganizationMember).filter(OrganizationMember.organization_id == org_id).all()

    def get_active_members(self, org_id: str) -> List[OrganizationMember]:
        """Get active members of an organization"""
        return (
            self.db.query(OrganizationMember).filter(and_(OrganizationMember.organization_id == org_id, OrganizationMember.status == "active")).all()
        )

    def get_member(self, org_id: str, user_id: str) -> Optional[OrganizationMember]:
        """Get a specific member"""
        return (
            self.db.query(OrganizationMember)
            .filter(and_(OrganizationMember.organization_id == org_id, OrganizationMember.user_id == user_id))
            .first()
        )

    def get_user_role(self, org_id: str, user_id: str) -> Optional[str]:
        """Get user's role in an organization"""
        member = self.get_member(org_id, user_id)
        return member.role if member and member.status == "active" else None

    def update_member_role(self, org_id: str, target_user_id: str, new_role: str, actor_user_id: str) -> OrganizationMember:
        """Update a member's role"""
        # Validate role
        if new_role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {new_role}")

        # Check permission
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_MANAGE_MEMBERS):
            raise PermissionError("You don't have permission to manage members")

        member = self.get_member(org_id, target_user_id)
        if not member:
            raise ValueError("Member not found")

        # Cannot change owner role
        if member.role == "owner":
            raise ValueError("Cannot change the owner's role")

        # Cannot promote to owner
        if new_role == "owner":
            raise ValueError("Cannot promote to owner. Transfer ownership instead.")

        old_role = member.role
        member.role = new_role

        # Log the change
        self._log_action(
            org_id,
            actor_user_id,
            "member.role_changed",
            "member",
            member.id,
            {"old_role": old_role, "new_role": new_role, "target_user_id": target_user_id},
        )

        self.db.commit()
        return member

    def remove_member(self, org_id: str, target_user_id: str, actor_user_id: str) -> bool:
        """Remove a member from the organization"""
        # Check permission
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_MANAGE_MEMBERS):
            raise PermissionError("You don't have permission to remove members")

        member = self.get_member(org_id, target_user_id)
        if not member:
            raise ValueError("Member not found")

        # Cannot remove owner
        if member.role == "owner":
            raise ValueError("Cannot remove the owner. Transfer ownership first.")

        # Get user email for audit log
        user = self.db.query(User).filter(User.id == target_user_id).first()
        user_email = user.email if user else None

        self.db.delete(member)

        # Log the removal
        self._log_action(
            org_id, actor_user_id, "member.removed", "member", member.id, {"removed_user_id": target_user_id, "removed_user_email": user_email}
        )

        self.db.commit()
        return True

    def get_seat_count(self, org_id: str) -> dict:
        """Get current seat usage"""
        org = self.get_organization(org_id)
        if not org:
            return {"used": 0, "max": 0, "available": 0}

        active_count = (
            self.db.query(OrganizationMember)
            .filter(and_(OrganizationMember.organization_id == org_id, OrganizationMember.status == "active"))
            .count()
        )

        pending_count = (
            self.db.query(OrganizationInvitation)
            .filter(and_(OrganizationInvitation.organization_id == org_id, OrganizationInvitation.status == "pending"))
            .count()
        )

        used = active_count + pending_count
        max_seats = org.max_seats

        return {
            "used": used,
            "active": active_count,
            "pending": pending_count,
            "max": max_seats,
            "available": -1 if max_seats == -1 else max(0, max_seats - used),
            "unlimited": max_seats == -1,
        }

    # ==========================================
    # DOMAIN CLAIMS
    # ==========================================

    def list_domain_claims(self, org_id: str, user_id: str) -> List[OrganizationDomainClaim]:
        """List domain claims for an organization"""
        if not self.can_user_access_org(org_id, user_id):
            raise PermissionError("You don't have permission to view domain claims")

        return (
            self.db.query(OrganizationDomainClaim)
            .filter(OrganizationDomainClaim.organization_id == org_id)
            .order_by(OrganizationDomainClaim.created_at.desc())
            .all()
        )

    def get_domain_claim(self, org_id: str, claim_id: str) -> Optional[OrganizationDomainClaim]:
        """Fetch a specific domain claim for an organization."""
        return (
            self.db.query(OrganizationDomainClaim)
            .filter(
                OrganizationDomainClaim.id == claim_id,
                OrganizationDomainClaim.organization_id == org_id,
            )
            .first()
        )

    def create_domain_claim(
        self,
        org_id: str,
        domain: str,
        verification_email: str,
        actor_user_id: str,
    ) -> OrganizationDomainClaim:
        """Create a domain claim for verification."""
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_MANAGE_SETTINGS):
            raise PermissionError("You don't have permission to manage domain claims")

        org = self.get_organization(org_id)
        if not org:
            raise ValueError("Organization not found")

        normalized_domain = normalize_domain(domain)
        if not DOMAIN_REGEX.match(normalized_domain):
            raise ValueError("Invalid domain format")
        if normalized_domain in COMMON_EMAIL_DOMAINS:
            raise ValueError("Common email domains cannot be claimed")

        email_domain = normalize_domain(verification_email.split("@")[-1]) if "@" in verification_email else ""
        if email_domain != normalized_domain:
            raise ValueError("Verification email must match the domain being claimed")

        limit = DOMAIN_LIMITS_BY_TIER.get(org.tier, 1)
        active_claims = (
            self.db.query(OrganizationDomainClaim)
            .filter(
                OrganizationDomainClaim.organization_id == org_id,
                OrganizationDomainClaim.status.in_(["pending", "verified"]),
            )
            .count()
        )
        if active_claims >= limit:
            raise ValueError("Domain claim limit reached for this organization tier")

        existing_domain = (
            self.db.query(OrganizationDomainClaim)
            .filter(
                OrganizationDomainClaim.domain == normalized_domain,
                OrganizationDomainClaim.status.in_(["pending", "verified"]),
            )
            .first()
        )
        if existing_domain:
            if existing_domain.organization_id == org_id:
                raise ValueError("This organization already has a pending or verified claim for this domain")
            raise ValueError("Domain is already claimed by another organization")

        dns_token = secrets.token_urlsafe(24)
        email_token = secrets.token_urlsafe(24)

        claim = OrganizationDomainClaim(
            organization_id=org_id,
            domain=normalized_domain,
            verification_email=verification_email.lower(),
            dns_token=dns_token,
            email_token=email_token,
            created_by=actor_user_id,
            status="pending",
        )
        self.db.add(claim)

        self._log_action(
            org_id,
            actor_user_id,
            "domain_claim.created",
            "domain_claim",
            claim.id,
            {"domain": normalized_domain, "verification_email": verification_email},
        )

        self.db.commit()
        return claim

    def verify_domain_email(self, token: str) -> OrganizationDomainClaim:
        """Verify a domain claim via email token."""
        claim = self.db.query(OrganizationDomainClaim).filter(OrganizationDomainClaim.email_token == token).first()
        if not claim:
            raise ValueError("Domain claim not found")

        if claim.status == "rejected":
            raise ValueError("Domain claim has been rejected")

        claim.email_verified_at = datetime.utcnow()
        self._refresh_domain_claim_status(claim)
        self.db.commit()
        return claim

    def verify_domain_dns(self, org_id: str, claim_id: str, actor_user_id: str, txt_records: List[str]) -> OrganizationDomainClaim:
        """Verify a domain claim via DNS TXT lookup."""
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_MANAGE_SETTINGS):
            raise PermissionError("You don't have permission to verify domain claims")

        claim = self.get_domain_claim(org_id, claim_id)
        if not claim:
            raise ValueError("Domain claim not found")

        if claim.status == "rejected":
            raise ValueError("Domain claim has been rejected")

        expected_marker = f"encypher-domain-claim={claim.dns_token}"
        if not any(expected_marker in record for record in txt_records):
            raise ValueError("DNS verification record not found")

        claim.dns_verified_at = datetime.utcnow()
        self._refresh_domain_claim_status(claim)
        self.db.commit()
        return claim

    def set_domain_auto_join(
        self,
        org_id: str,
        claim_id: str,
        actor_user_id: str,
        enabled: bool,
    ) -> OrganizationDomainClaim:
        """Enable/disable auto-join for a verified domain claim."""
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_MANAGE_SETTINGS):
            raise PermissionError("You don't have permission to manage domain claims")

        claim = (
            self.db.query(OrganizationDomainClaim)
            .filter(
                OrganizationDomainClaim.id == claim_id,
                OrganizationDomainClaim.organization_id == org_id,
            )
            .first()
        )
        if not claim:
            raise ValueError("Domain claim not found")

        if claim.status != "verified":
            raise ValueError("Domain must be verified before enabling auto-join")

        claim.auto_join_enabled = enabled
        self._log_action(
            org_id,
            actor_user_id,
            "domain_claim.auto_join_updated",
            "domain_claim",
            claim.id,
            {"auto_join_enabled": enabled},
        )
        self.db.commit()
        return claim

    def delete_domain_claim(self, org_id: str, claim_id: str, actor_user_id: str) -> OrganizationDomainClaim:
        """Delete a domain claim from an organization."""
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_MANAGE_SETTINGS):
            raise PermissionError("You don't have permission to manage domain claims")

        claim = self.get_domain_claim(org_id, claim_id)
        if not claim:
            raise ValueError("Domain claim not found")

        self._log_action(
            org_id,
            actor_user_id,
            "domain_claim.deleted",
            "domain_claim",
            claim.id,
            {
                "domain": claim.domain,
                "status": claim.status,
            },
        )
        self.db.delete(claim)
        self.db.commit()
        return claim

    def get_auto_join_org_for_email(self, email: str) -> Optional[str]:
        """Return org_id for a verified domain with auto-join enabled."""
        if "@" not in email:
            return None
        domain = normalize_domain(email.split("@")[-1])
        claim = (
            self.db.query(OrganizationDomainClaim)
            .filter(
                OrganizationDomainClaim.domain == domain,
                OrganizationDomainClaim.status == "verified",
                OrganizationDomainClaim.auto_join_enabled == True,
            )
            .first()
        )
        return claim.organization_id if claim else None

    def _refresh_domain_claim_status(self, claim: OrganizationDomainClaim) -> None:
        if claim.dns_verified_at:
            claim.status = "verified"
            if not claim.verified_at:
                claim.verified_at = datetime.utcnow()

    # ==========================================
    # INVITATIONS
    # ==========================================

    def create_invitation(
        self,
        org_id: str,
        email: str,
        role: str,
        inviter_user_id: str,
        message: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization_name: Optional[str] = None,
        tier: Optional[str] = None,
        trial_months: Optional[int] = None,
        allow_owner: bool = False,
        skip_permission: bool = False,
        skip_seat_check: bool = False,
    ) -> OrganizationInvitation:
        """Create an invitation to join the organization"""
        # Validate role
        if role not in ROLE_HIERARCHY or (role == "owner" and not allow_owner):
            raise ValueError(f"Invalid role for invitation: {role}")

        # Check permission
        if not skip_permission and not self._has_permission(org_id, inviter_user_id, ROLE_CAN_INVITE):
            raise PermissionError("You don't have permission to invite members")

        # Check seat limit
        if not skip_seat_check:
            seat_info = self.get_seat_count(org_id)
            if not seat_info["unlimited"] and seat_info["available"] <= 0:
                raise ValueError("No seats available. Upgrade your plan to add more team members.")

        if tier:
            config = self._get_tier_config(tier)
            if not config:
                raise ValueError(f"Invalid tier: {tier}")

        if trial_months is not None and trial_months < 1:
            raise ValueError("Trial months must be at least 1")

        if bool(tier) ^ bool(trial_months):
            raise ValueError("Trial invitations require both tier and trial months")

        if tier and trial_months:
            if not (first_name or "").strip() or not (last_name or "").strip():
                raise ValueError("Trial invitations require first and last name")

        # Check if user is already a member
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            existing_member = self.get_member(org_id, existing_user.id)
            if existing_member and existing_member.status == "active":
                raise ValueError("This user is already a member of the organization")

        # Check for existing pending invitation
        existing_invite = (
            self.db.query(OrganizationInvitation)
            .filter(
                and_(
                    OrganizationInvitation.organization_id == org_id,
                    OrganizationInvitation.email == email,
                    OrganizationInvitation.status == "pending",
                )
            )
            .first()
        )

        if existing_invite:
            raise ValueError("An invitation is already pending for this email")

        # Create invitation
        invitation = OrganizationInvitation(
            organization_id=org_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name,
            tier=tier,
            trial_months=trial_months,
            role=role,
            invited_by=inviter_user_id,
            message=message,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        self.db.add(invitation)

        # Log the invitation
        self._log_action(
            org_id,
            inviter_user_id,
            "member.invited",
            "invitation",
            invitation.id,
            {"email": email, "role": role, "tier": tier, "trial_months": trial_months},
        )

        self.db.commit()
        return invitation

    def create_trial_invitation_for_new_org(
        self,
        *,
        organization_name: Optional[str],
        email: str,
        first_name: Optional[str],
        last_name: Optional[str],
        tier: str,
        trial_months: int,
        inviter_user_id: str,
    ) -> OrganizationInvitation:
        if not organization_name or not organization_name.strip():
            raise ValueError("Organization name is required")

        if not (first_name or "").strip() or not (last_name or "").strip():
            raise ValueError("Trial invitations require first and last name")

        org = self.create_organization_without_owner(
            name=organization_name.strip(),
            email=email,
            tier="starter",
            created_by=inviter_user_id,
        )

        return self.create_invitation(
            org_id=org.id,
            email=email,
            role="owner",
            inviter_user_id=inviter_user_id,
            message=None,
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name.strip(),
            tier=tier,
            trial_months=trial_months,
            allow_owner=True,
            skip_permission=True,
            skip_seat_check=True,
        )

    def create_enterprise_evaluation_invitation(
        self,
        *,
        organization_name: Optional[str],
        email: str,
        first_name: Optional[str],
        last_name: Optional[str],
        inviter_user_id: str,
    ) -> OrganizationInvitation:
        return self.create_trial_invitation_for_new_org(
            organization_name=organization_name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            tier=ENTERPRISE_EVALUATION_TIER,
            trial_months=ENTERPRISE_EVALUATION_TRIAL_MONTHS,
            inviter_user_id=inviter_user_id,
        )

    def get_pending_invitations(self, org_id: str) -> List[OrganizationInvitation]:
        """Get all pending invitations for an organization"""
        return (
            self.db.query(OrganizationInvitation)
            .filter(
                and_(
                    OrganizationInvitation.organization_id == org_id,
                    OrganizationInvitation.status == "pending",
                    OrganizationInvitation.expires_at > datetime.utcnow(),
                )
            )
            .all()
        )

    def get_invitation_by_token(self, token: str) -> Optional[OrganizationInvitation]:
        """Get invitation by token"""
        return self.db.query(OrganizationInvitation).filter(OrganizationInvitation.token == token).first()

    def get_invitation_details(self, token: str) -> Optional[dict]:
        """Get invitation details for display (public endpoint)"""
        invitation = self.get_invitation_by_token(token)

        if not invitation:
            return None

        if invitation.status != "pending":
            return {"status": invitation.status, "valid": False}

        if is_expired(invitation.expires_at):
            return {"status": "expired", "valid": False}

        # Get organization name
        org = self.get_organization(invitation.organization_id)
        organization_name = invitation.organization_name or (org.name if org else "Unknown")

        # Get inviter name
        inviter = self.db.query(User).filter(User.id == invitation.invited_by).first()

        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == invitation.email).first()

        return {
            "valid": True,
            "status": invitation.status,
            "email": invitation.email,
            "first_name": invitation.first_name,
            "last_name": invitation.last_name,
            "role": invitation.role,
            "organization_name": organization_name,
            "organization_id": invitation.organization_id,
            "inviter_name": inviter.name or inviter.email if inviter else "Unknown",
            "message": invitation.message,
            "tier": invitation.tier,
            "trial_months": invitation.trial_months,
            "expires_at": invitation.expires_at.isoformat(),
            "user_exists": existing_user is not None,
        }

    def _seed_enterprise_invite_onboarding(self, invitation: OrganizationInvitation, user: User) -> None:
        if invitation.tier != "enterprise":
            return
        if invitation.role != "owner":
            return

        org = self.db.query(Organization).filter(Organization.id == invitation.organization_id).first()
        if not org:
            return

        user.default_organization_id = invitation.organization_id
        if not user.setup_completed_at:
            user.setup_completed_at = datetime.utcnow()

        org.account_type = org.account_type or "organization"
        org.display_name = org.display_name or invitation.organization_name or org.name
        org.dashboard_layout = "enterprise"
        org.workflow_category = org.workflow_category or "enterprise"

    def accept_invitation(self, token: str, user_id: str) -> OrganizationMember:
        """Accept an invitation and become a member (for existing users)"""
        invitation = self.get_invitation_by_token(token)

        if not invitation:
            raise ValueError("Invitation not found")

        if invitation.status != "pending":
            raise ValueError(f"Invitation is {invitation.status}")

        if is_expired(invitation.expires_at):
            invitation.status = "expired"
            self.db.commit()
            raise ValueError("Invitation has expired")

        # Verify user email matches invitation
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.email.lower() != invitation.email.lower():
            raise ValueError("This invitation was sent to a different email address")

        # Check if already a member
        existing_member = self.get_member(invitation.organization_id, user_id)
        if existing_member:
            raise ValueError("You are already a member of this organization")

        # Create membership
        member = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=user_id,
            role=invitation.role,
            status="active",
            invited_by=invitation.invited_by,
            invited_at=invitation.created_at,
            accepted_at=datetime.utcnow(),
        )
        self.db.add(member)

        # Update invitation status
        invitation.status = "accepted"
        invitation.accepted_at = datetime.utcnow()

        # Ensure user has a default org so the setup wizard can complete
        if not user.default_organization_id:
            user.default_organization_id = invitation.organization_id

        self._seed_enterprise_invite_onboarding(invitation, user)

        if invitation.tier:
            subscription_status = "trialing" if invitation.trial_months else None
            org = self.update_tier_internal(
                org_id=invitation.organization_id,
                tier=invitation.tier,
                subscription_status=subscription_status,
            )
            if invitation.trial_months:
                self._apply_trial_metadata(
                    org=org,
                    tier=invitation.tier,
                    trial_months=invitation.trial_months,
                )
                self._sync_trial_to_billing(
                    organization_id=invitation.organization_id,
                    user_id=user.id,
                    tier=invitation.tier,
                    trial_months=invitation.trial_months,
                )

        # Log the acceptance
        self._log_action(
            invitation.organization_id, user_id, "member.joined", "member", member.id, {"role": invitation.role, "invitation_id": invitation.id}
        )

        self.db.commit()
        return member

    def accept_invitation_new_user(self, token: str, name: Optional[str], password_hash: str) -> tuple:
        """Accept an invitation and create a new user account

        Returns: (user, member) tuple
        """
        invitation = self.get_invitation_by_token(token)

        if not invitation:
            raise ValueError("Invitation not found")

        if invitation.status != "pending":
            raise ValueError(f"Invitation is {invitation.status}")

        if is_expired(invitation.expires_at):
            invitation.status = "expired"
            self.db.commit()
            raise ValueError("Invitation has expired")

        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == invitation.email).first()
        if existing_user:
            raise ValueError("An account with this email already exists. Please log in to accept the invitation.")

        resolved_name = name
        if not resolved_name:
            name_parts = [invitation.first_name, invitation.last_name]
            resolved_name = " ".join(part for part in name_parts if part).strip() or None

        # Create new user
        user = User(
            email=invitation.email,
            password_hash=password_hash,
            name=resolved_name,
            email_verified=True,  # Email is verified via invitation
            email_verified_at=datetime.utcnow(),
            is_active=True,
            totp_enabled=False,
            totp_secret_encrypted=None,
            totp_enabled_at=None,
            totp_backup_code_hashes=[],
        )
        self.db.add(user)
        self.db.flush()  # Get user.id

        # Create membership
        member = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=user.id,
            role=invitation.role,
            status="active",
            invited_by=invitation.invited_by,
            invited_at=invitation.created_at,
            accepted_at=datetime.utcnow(),
        )
        self.db.add(member)

        # Update invitation status
        invitation.status = "accepted"
        invitation.accepted_at = datetime.utcnow()

        # Ensure user has a default org so the setup wizard can complete
        if not user.default_organization_id:
            user.default_organization_id = invitation.organization_id

        self._seed_enterprise_invite_onboarding(invitation, user)

        if invitation.tier:
            subscription_status = "trialing" if invitation.trial_months else None
            org = self.update_tier_internal(
                org_id=invitation.organization_id,
                tier=invitation.tier,
                subscription_status=subscription_status,
            )
            if invitation.trial_months:
                self._apply_trial_metadata(
                    org=org,
                    tier=invitation.tier,
                    trial_months=invitation.trial_months,
                )
                self._sync_trial_to_billing(
                    organization_id=invitation.organization_id,
                    user_id=user.id,
                    tier=invitation.tier,
                    trial_months=invitation.trial_months,
                )

        # Log the acceptance
        self._log_action(
            invitation.organization_id,
            user.id,
            "member.joined",
            "member",
            member.id,
            {"role": invitation.role, "invitation_id": invitation.id, "new_account": True},
        )

        self.db.commit()
        return user, member

    def _sync_trial_to_billing(
        self,
        *,
        organization_id: str,
        user_id: str,
        tier: str,
        trial_months: int,
    ) -> None:
        if not settings.BILLING_SERVICE_URL:
            logger.warning("billing_service_url_missing")
            return

        payload = {
            "organization_id": organization_id,
            "user_id": user_id,
            "tier": tier,
            "trial_months": trial_months,
        }
        headers = {}
        if settings.INTERNAL_SERVICE_TOKEN:
            headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN

        try:
            with httpx.Client(timeout=10) as client:
                response = client.post(
                    f"{settings.BILLING_SERVICE_URL}/api/v1/billing/internal/trials",
                    json=payload,
                    headers=headers,
                )
                if response.status_code >= 400:
                    logger.warning(
                        "billing_trial_sync_failed status=%s response=%s",
                        response.status_code,
                        response.text,
                    )
        except httpx.RequestError as exc:
            logger.warning("billing_trial_sync_request_failed error=%s", exc)

    def _apply_trial_metadata(self, *, org: Organization, tier: str, trial_months: int) -> None:
        now = datetime.utcnow()
        org.trial_tier = tier
        org.trial_months = trial_months
        org.trial_started_at = now
        org.trial_ends_at = now + timedelta(days=trial_months * 30)

    def cancel_invitation(self, org_id: str, invitation_id: str, actor_user_id: str) -> bool:
        """Cancel a pending invitation"""
        # Check permission
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_INVITE):
            raise PermissionError("You don't have permission to cancel invitations")

        invitation = (
            self.db.query(OrganizationInvitation)
            .filter(and_(OrganizationInvitation.id == invitation_id, OrganizationInvitation.organization_id == org_id))
            .first()
        )

        if not invitation:
            raise ValueError("Invitation not found")

        if invitation.status != "pending":
            raise ValueError(f"Cannot cancel invitation with status: {invitation.status}")

        invitation.status = "cancelled"
        invitation.cancelled_at = datetime.utcnow()

        # Log the cancellation
        self._log_action(org_id, actor_user_id, "invitation.cancelled", "invitation", invitation_id, {"email": invitation.email})

        self.db.commit()
        return True

    def resend_invitation(self, org_id: str, invitation_id: str, actor_user_id: str) -> OrganizationInvitation:
        """Resend an invitation (generate new token and extend expiry)"""
        # Check permission
        if not self._has_permission(org_id, actor_user_id, ROLE_CAN_INVITE):
            raise PermissionError("You don't have permission to resend invitations")

        invitation = (
            self.db.query(OrganizationInvitation)
            .filter(and_(OrganizationInvitation.id == invitation_id, OrganizationInvitation.organization_id == org_id))
            .first()
        )

        if not invitation:
            raise ValueError("Invitation not found")

        if invitation.status != "pending":
            raise ValueError(f"Cannot resend invitation with status: {invitation.status}")

        # Generate new token and extend expiry
        invitation.token = secrets.token_urlsafe(32)
        invitation.expires_at = datetime.utcnow() + timedelta(days=7)

        # Log the resend
        self._log_action(org_id, actor_user_id, "invitation.resent", "invitation", invitation_id, {"email": invitation.email})

        self.db.commit()
        return invitation

    # ==========================================
    # AUDIT LOGS
    # ==========================================

    def get_audit_logs(
        self,
        org_id: str,
        limit: int = 50,
        offset: int = 0,
        action_filter: Optional[str] = None,
        user_id_filter: Optional[str] = None,
    ) -> List[OrganizationAuditLog]:
        """Get audit logs for an organization"""
        query = self.db.query(OrganizationAuditLog).filter(OrganizationAuditLog.organization_id == org_id)

        if action_filter:
            query = query.filter(OrganizationAuditLog.action.like(f"{action_filter}%"))

        if user_id_filter:
            query = query.filter(OrganizationAuditLog.user_id == user_id_filter)

        return query.order_by(OrganizationAuditLog.created_at.desc()).offset(offset).limit(limit).all()

    def _log_action(
        self,
        org_id: str,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log an action to the audit log"""
        # Get user email
        user = None
        user_email = None
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            user_email = user.email if user else None

        log = OrganizationAuditLog(
            organization_id=org_id,
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)

    # ==========================================
    # PERMISSION HELPERS
    # ==========================================

    def is_super_admin(self, user_id: str) -> bool:
        """Check if the actor has global super admin privileges."""
        user_columns = self._table_columns(User.__tablename__)
        if "is_super_admin" not in user_columns:
            return False

        return bool(
            self.db.query(User.id)
            .filter(
                User.id == user_id,
                User.is_super_admin == True,
            )
            .first()
        )

    def _has_permission(self, org_id: str, user_id: str, allowed_roles: set) -> bool:
        """Check if user has one of the allowed roles"""
        if self.is_super_admin(user_id):
            return True
        role = self.get_user_role(org_id, user_id)
        return role in allowed_roles if role else False

    def can_user_access_org(self, org_id: str, user_id: str) -> bool:
        """Check if user can access the organization"""
        if self.is_super_admin(user_id):
            return True
        member = self.get_member(org_id, user_id)
        return member is not None and member.status == "active"

    def can_user_invite(self, org_id: str, user_id: str) -> bool:
        """Check if user can invite members"""
        return self._has_permission(org_id, user_id, ROLE_CAN_INVITE)

    def can_user_manage_members(self, org_id: str, user_id: str) -> bool:
        """Check if user can manage members"""
        return self._has_permission(org_id, user_id, ROLE_CAN_MANAGE_MEMBERS)

    def can_user_manage_billing(self, org_id: str, user_id: str) -> bool:
        """Check if user can manage billing"""
        return self._has_permission(org_id, user_id, ROLE_CAN_MANAGE_BILLING)

    def can_user_create_api_keys(self, org_id: str, user_id: str) -> bool:
        """Check if user can create API keys"""
        return self._has_permission(org_id, user_id, ROLE_CAN_CREATE_API_KEYS)
