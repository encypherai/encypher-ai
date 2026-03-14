"""
Organization API endpoints for team management
"""

import logging
import html

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from ...db.models import User, OrganizationDomainClaim
from ...db.session import get_db
from ...core.config import settings
from ...core.auth import get_email_config as _get_email_config
from ...core.responses import ok
from ...services.organization_service import OrganizationService
from ...models.schemas import UserTier
import dns.resolver
from ...services.auth_service import AuthService
from .endpoints import require_super_admin
from ...deps.rate_limit import rate_limiter
from encypher_commercial_shared.email import EmailConfig

router = APIRouter(prefix="/organizations", tags=["organizations"])
logger = logging.getLogger(__name__)
SIGNING_IDENTITY_MODE_ORGANIZATION_NAME = "organization_name"
SIGNING_IDENTITY_MODE_ORGANIZATION_AND_AUTHOR = "organization_and_author"
SIGNING_IDENTITY_MODE_CUSTOM = "custom"
ALLOWED_SIGNING_IDENTITY_MODES = {
    SIGNING_IDENTITY_MODE_ORGANIZATION_NAME,
    SIGNING_IDENTITY_MODE_ORGANIZATION_AND_AUTHOR,
    SIGNING_IDENTITY_MODE_CUSTOM,
}


# _get_email_config is imported from core.auth as _get_email_config


def _build_invitation_email(
    *,
    config: EmailConfig,
    recipient_name: Optional[str],
    inviter_name: Optional[str],
    inviter_email: str,
    organization_name: str,
    role: str,
    invitation_token: str,
    message: Optional[str],
    expires_at: Optional[datetime],
    tier: Optional[str],
    trial_months: Optional[int],
) -> tuple[str, str, str]:
    base_url = config.dashboard_url or config.frontend_url
    invitation_url = f"{base_url}/invitations/accept?token={invitation_token}"

    safe_inviter_name = html.escape(inviter_name, quote=True) if inviter_name else None
    safe_inviter_email = html.escape(inviter_email, quote=True)
    safe_org_name = html.escape(organization_name, quote=True)
    safe_role = html.escape(role, quote=True)
    safe_message = html.escape(message, quote=True) if message else None
    safe_recipient_name = html.escape(recipient_name, quote=True) if recipient_name else None

    subject = f"You're invited to join {organization_name} on Encypher"
    html_lines: list[str] = [
        f"<p>{'Hi ' + safe_recipient_name + ',' if safe_recipient_name else 'Hello,'}</p>",
        f"<p>You have been invited to join <strong>{safe_org_name}</strong>.</p>",
        f"<p>Role: <strong>{safe_role}</strong></p>",
    ]
    if tier:
        html_lines.append(f"<p>Tier: <strong>{html.escape(tier, quote=True)}</strong></p>")
    if trial_months:
        html_lines.append(f"<p>Trial: <strong>{trial_months} month(s)</strong></p>")
    if safe_inviter_name:
        html_lines.append(f"<p>Invited by: {safe_inviter_name} ({safe_inviter_email})</p>")
    else:
        html_lines.append(f"<p>Invited by: {safe_inviter_email}</p>")
    if safe_message:
        html_lines.append(f"<p>Message: {safe_message}</p>")
    html_lines.append(f'<p><a href="{invitation_url}">Accept invitation</a></p>')
    if expires_at:
        html_lines.append(f"<p>Expires at: {expires_at.isoformat()} UTC</p>")
    html_content = "\n".join(html_lines)

    plain_lines: list[str] = [
        f"{f'Hi {recipient_name},' if recipient_name else 'Hello,'}",
        f"You have been invited to join {organization_name}.",
        f"Role: {role}",
        f"Invited by: {inviter_name + ' ' if inviter_name else ''}<{inviter_email}>",
    ]
    if tier:
        plain_lines.append(f"Tier: {tier}")
    if trial_months:
        plain_lines.append(f"Trial: {trial_months} month(s)")
    if message:
        plain_lines.append(f"Message: {message}")
    plain_lines.append(f"Accept invitation: {invitation_url}")
    if expires_at:
        plain_lines.append(f"Expires at: {expires_at.isoformat()} UTC")
    plain_content = "\n".join(plain_lines)

    return subject, html_content, plain_content


async def _send_invitation_email(
    *,
    authorization: str,
    recipient_email: str,
    recipient_name: Optional[str],
    inviter_name: Optional[str],
    inviter_email: str,
    organization_name: str,
    role: str,
    invitation_token: str,
    message: Optional[str],
    expires_at: Optional[datetime],
    tier: Optional[str],
    trial_months: Optional[int],
) -> None:
    config = _get_email_config()
    subject, html_content, plain_content = _build_invitation_email(
        config=config,
        recipient_name=recipient_name,
        inviter_name=inviter_name,
        inviter_email=inviter_email,
        organization_name=organization_name,
        role=role,
        invitation_token=invitation_token,
        message=message,
        expires_at=expires_at,
        tier=tier,
        trial_months=trial_months,
    )

    payload = {
        "notification_type": "email",
        "recipient": recipient_email,
        "subject": subject,
        "content": html_content,
        "metadata": {
            "plain_content": plain_content,
            "organization_name": organization_name,
            "role": role,
            "tier": tier,
            "trial_months": trial_months,
            "recipient_name": recipient_name,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/send",
                json=payload,
                headers={"Authorization": authorization},
            )
            if response.status_code >= 400:
                logger.warning("invitation_email_failed status=%s response=%s", response.status_code, response.text)
    except httpx.RequestError as exc:
        logger.warning("invitation_email_request_failed error=%s", str(exc))
    except Exception as exc:
        logger.exception("invitation_email_unexpected_error error=%s", str(exc))


async def _send_domain_claim_email(
    *,
    authorization: str,
    recipient_email: str,
    organization_name: str,
    domain: str,
    email_token: str,
    dns_token: str,
) -> None:
    config = _get_email_config()
    base_url = config.dashboard_url or config.frontend_url
    audit_url = f"{base_url}/verify-domain?token={email_token}"
    settings_url = f"{base_url}/settings?tab=organization"
    dns_record = f"encypher-domain-claim={dns_token}"
    subject = f"Set up DNS verification for {domain}"
    html_content = (
        f"<p>You've initiated domain verification for <strong>{domain}</strong> "
        f"on behalf of <strong>{organization_name}</strong>.</p>"
        "<p>To verify ownership, add the following TXT record to your DNS provider "
        f"under the <strong>{domain}</strong> zone:</p>"
        f'<pre style="background:#f4f4f4;padding:12px;border-radius:4px;font-family:monospace">'
        f"{dns_record}</pre>"
        "<p>Once the record is live (propagation may take a few minutes), open your "
        f"dashboard settings and click <strong>Verify DNS</strong>:</p>"
        f'<p><a href="{settings_url}">Go to Settings</a></p>'
        '<hr style="margin:24px 0;border:none;border-top:1px solid #eee">'
        f'<p style="font-size:12px;color:#888">If you did not request this, you can ignore '
        f'this email. <a href="{audit_url}">Confirm this request</a> (optional audit trail).</p>'
    )
    plain_content = (
        f"Set up DNS verification for {domain}\n\n"
        f"You've initiated domain verification for {domain} ({organization_name}).\n\n"
        "Add this TXT record to your DNS provider under the domain zone:\n\n"
        f"  {dns_record}\n\n"
        "Once the record is live, go to Settings > Organization and click Verify DNS:\n"
        f"  {settings_url}\n\n"
        "If you did not request this, ignore this email.\n"
        f"Optional audit confirmation: {audit_url}"
    )

    payload = {
        "notification_type": "email",
        "recipient": recipient_email,
        "subject": subject,
        "content": html_content,
        "metadata": {
            "plain_content": plain_content,
            "organization_name": organization_name,
            "domain": domain,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/send",
                json=payload,
                headers={"Authorization": authorization},
            )
            if response.status_code >= 400:
                logger.warning("domain_claim_email_failed status=%s response=%s", response.status_code, response.text)
    except httpx.RequestError as exc:
        logger.warning("domain_claim_email_request_failed error=%s", str(exc))
    except Exception as exc:
        logger.exception("domain_claim_email_unexpected_error error=%s", str(exc))


# ==========================================
# SCHEMAS
# ==========================================


class OrganizationCreate(BaseModel):
    name: str
    email: EmailStr


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class InternalTierUpdateRequest(BaseModel):
    tier: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None


class InternalTierUpdateResponse(BaseModel):
    success: bool = True
    data: dict = Field(default_factory=dict)


class InternalOrgContextResponse(BaseModel):
    success: bool = True
    data: dict = Field(default_factory=dict)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: Optional[str]
    email: str
    account_type: Optional[str] = None
    display_name: Optional[str] = None
    dashboard_layout: Optional[str] = None
    publisher_platform: Optional[str] = None
    publisher_platform_custom: Optional[str] = None
    signing_identity_mode: Optional[str] = None
    signing_identity_custom_label: Optional[str] = None
    anonymous_publisher: bool = False
    add_ons: Optional[dict] = None
    tier: str
    trial_tier: Optional[str] = None
    trial_months: Optional[int] = None
    trial_started_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    max_seats: int
    subscription_status: str
    coalition_rev_share: int
    created_at: datetime

    class Config:
        from_attributes = True


class DomainClaimCreate(BaseModel):
    domain: str
    verification_email: EmailStr


class DomainClaimAutoJoinUpdate(BaseModel):
    enabled: bool


class DomainClaimResponse(BaseModel):
    id: str
    organization_id: str
    domain: str
    verification_email: str
    status: str
    dns_token: str
    dns_verified_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    auto_join_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    id: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    role: str
    status: str
    invited_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization_name: Optional[str] = None
    tier: Optional[UserTier] = None
    trial_months: Optional[int] = Field(default=None, ge=1, le=24)
    role: str = "member"
    message: Optional[str] = None


class TrialInvitationCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    organization_name: str
    tier: UserTier
    trial_months: int = Field(..., ge=1, le=24)


class InvitationResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization_name: Optional[str] = None
    tier: Optional[str] = None
    trial_months: Optional[int] = None
    role: str
    status: str
    message: Optional[str] = None
    invited_by: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    role: str


class SeatInfo(BaseModel):
    used: int
    active: int
    pending: int
    max: int
    available: int
    unlimited: bool


class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# HELPER: Get current user from token
# ==========================================


async def get_current_user_id(request: Request, db: Session = Depends(get_db)) -> str:
    """Extract user ID from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")

    token = auth_header.split(" ")[1]
    payload = AuthService.verify_access_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return payload["sub"]


# ==========================================
# ORGANIZATION ENDPOINTS
# ==========================================


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("org_create", limit=5, window_sec=60)),
):
    """Create a new organization with the current user as owner"""
    actor_user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        org = org_service.create_organization(name=org_data.name, email=org_data.email, owner_user_id=actor_user_id)

        return ok(OrganizationResponse.model_validate(org).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/invitations/trial")
async def create_trial_invitation_for_new_org(
    invitation_data: TrialInvitationCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("org_invite", limit=20, window_sec=60)),
):
    """Send a trial invitation for a new organization."""
    user_id = await get_current_user_id(request, db)

    try:
        require_super_admin(db, user_id)

        org_service = OrganizationService(db)
        invitation = org_service.create_trial_invitation_for_new_org(
            organization_name=invitation_data.organization_name,
            email=invitation_data.email,
            first_name=invitation_data.first_name,
            last_name=invitation_data.last_name,
            tier=invitation_data.tier.value,
            trial_months=invitation_data.trial_months,
            inviter_user_id=user_id,
        )

        inviter = db.query(User).filter(User.id == user_id).first()
        recipient_name = " ".join([invitation_data.first_name, invitation_data.last_name]).strip()
        if inviter:
            await _send_invitation_email(
                authorization=request.headers.get("Authorization", ""),
                recipient_email=invitation.email,
                recipient_name=recipient_name,
                inviter_name=inviter.name,
                inviter_email=inviter.email,
                organization_name=invitation.organization_name or invitation_data.organization_name,
                role=invitation.role,
                invitation_token=invitation.token,
                message=invitation.message,
                expires_at=invitation.expires_at,
                tier=invitation.tier,
                trial_months=invitation.trial_months,
            )

        return ok(InvitationResponse.model_validate(invitation).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/internal/{org_id}/context", response_model=InternalOrgContextResponse, include_in_schema=False)
async def get_organization_context_internal(
    org_id: str,
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    db: Session = Depends(get_db),
):
    if settings.INTERNAL_SERVICE_TOKEN:
        if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
    else:
        logger.warning("internal_service_token_missing")

    org_service = OrganizationService(db)
    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return InternalOrgContextResponse(
        success=True,
        data={
            "id": org.id,
            "name": org.name,
            "tier": org.tier,
            "features": org.features or {},
            "monthly_api_limit": org.monthly_api_limit,
            "monthly_api_usage": org.monthly_api_usage,
            "coalition_member": org.coalition_member,
            "coalition_rev_share": org.coalition_rev_share,
            "certificate_pem": org.certificate_pem,
            # TEAM_191: Publisher identity for attribution
            "account_type": org.account_type,
            "display_name": org.display_name,
            "anonymous_publisher": org.anonymous_publisher,
        },
    )


@router.post("/internal/{org_id}/tier", response_model=InternalTierUpdateResponse, include_in_schema=False)
async def update_organization_tier_internal(
    org_id: str,
    payload: InternalTierUpdateRequest,
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    db: Session = Depends(get_db),
):
    if settings.INTERNAL_SERVICE_TOKEN:
        if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
    else:
        logger.warning("internal_service_token_missing")

    org_service = OrganizationService(db)
    try:
        org = org_service.update_tier_internal(
            org_id=org_id,
            tier=payload.tier,
            stripe_customer_id=payload.stripe_customer_id,
            stripe_subscription_id=payload.stripe_subscription_id,
            subscription_status=payload.subscription_status,
        )
        return InternalTierUpdateResponse(success=True, data=OrganizationResponse.model_validate(org).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# BULK PROVISION SCHEMAS (TEAM_222)
# ==========================================


class BulkPublisherSpec(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    contact_email: EmailStr
    domain: Optional[str] = None
    display_name: Optional[str] = None


class BulkProvisionRequest(BaseModel):
    publishers: List[BulkPublisherSpec] = Field(min_length=1, max_length=1000)
    partner_org_id: str
    partner_name: str
    send_claim_email: bool = True


class BulkProvisionedResult(BaseModel):
    org_id: Optional[str] = None
    org_name: str
    contact_email: str
    invitation_token: Optional[str] = None
    domain: Optional[str] = None
    error: Optional[str] = None


class CertificateUpdateRequest(BaseModel):
    certificate_pem: str = Field(..., description="PEM-encoded certificate")


@router.patch("/internal/{org_id}/certificate", include_in_schema=False)
async def update_organization_certificate_internal(
    org_id: str,
    payload: CertificateUpdateRequest,
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    db: Session = Depends(get_db),
):
    if settings.INTERNAL_SERVICE_TOKEN:
        if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
    else:
        logger.warning("internal_service_token_missing")

    org_service = OrganizationService(db)
    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    org.certificate_pem = payload.certificate_pem
    org.certificate_status = "active"
    db.commit()
    db.refresh(org)

    logger.info(f"Updated certificate for organization {org_id}")
    return ok({"organization_id": org_id, "certificate_updated": True})


@router.post("/internal/bulk-provision", include_in_schema=False)
async def bulk_provision_publishers(
    payload: BulkProvisionRequest,
    db: Session = Depends(get_db),
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Bulk-provision publisher organizations for a platform partner (TEAM_222).

    Creates org + invitation for each publisher. Domain claims are attempted but
    failures do not fail the overall provisioning.
    """
    if settings.INTERNAL_SERVICE_TOKEN:
        if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    org_service = OrganizationService(db)
    provisioned: list[BulkProvisionedResult] = []
    failed: list[BulkProvisionedResult] = []

    for pub in payload.publishers:
        try:
            # 1. Create org without owner
            org = org_service.create_organization_without_owner(
                name=pub.name,
                email=str(pub.contact_email),
                tier="free",
                created_by=payload.partner_org_id,
            )

            # 2. Create invitation (owner role so publisher can manage their org)
            inv = org_service.create_invitation(
                org_id=org.id,
                email=str(pub.contact_email),
                role="owner",
                inviter_user_id=payload.partner_org_id,
                message=f"Provisioned by {payload.partner_name}",
                allow_owner=True,
                skip_permission=True,
                skip_seat_check=True,
            )

            # 3. Optional domain claim (failure does not fail provisioning)
            if pub.domain:
                try:
                    org_service.create_domain_claim(
                        org_id=org.id,
                        domain=pub.domain,
                        verification_email=str(pub.contact_email),
                        actor_user_id=payload.partner_org_id,
                    )
                except Exception as domain_exc:
                    logger.warning(
                        "bulk_provision_domain_claim_failed org=%s domain=%s error=%s",
                        org.id,
                        pub.domain,
                        str(domain_exc),
                    )

            provisioned.append(
                BulkProvisionedResult(
                    org_id=org.id,
                    org_name=pub.name,
                    contact_email=str(pub.contact_email),
                    invitation_token=inv.token,
                    domain=pub.domain,
                )
            )
        except Exception as exc:
            logger.warning(
                "bulk_provision_publisher_failed name=%s error=%s",
                pub.name,
                str(exc),
            )
            failed.append(
                BulkProvisionedResult(
                    org_name=pub.name,
                    contact_email=str(pub.contact_email),
                    domain=pub.domain,
                    error=str(exc),
                )
            )

    return ok(
        {
            "provisioned": [p.model_dump() for p in provisioned],
            "failed": [f.model_dump() for f in failed],
            "total": len(payload.publishers),
            "success_count": len(provisioned),
            "failure_count": len(failed),
        }
    )


# ==========================================
# DOMAIN CLAIM ENDPOINTS
# ==========================================


@router.get("/{org_id}/domain-claims")
async def list_domain_claims(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List domain claims for an organization"""
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)
    try:
        claims = org_service.list_domain_claims(org_id, user_id)
        return ok([DomainClaimResponse.model_validate(claim).model_dump() for claim in claims])
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{org_id}/domain-claims", status_code=status.HTTP_201_CREATED)
async def create_domain_claim(
    org_id: str,
    payload: DomainClaimCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("domain_claim_create", limit=5, window_sec=300)),
):
    """Create a domain claim for verification."""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        claim = org_service.create_domain_claim(
            org_id=org_id,
            domain=payload.domain,
            verification_email=payload.verification_email,
            actor_user_id=user_id,
        )
        org = org_service.get_organization(org_id)
        if org:
            try:
                await _send_domain_claim_email(
                    authorization=request.headers.get("Authorization", ""),
                    recipient_email=claim.verification_email,
                    organization_name=org.name,
                    domain=claim.domain,
                    email_token=claim.email_token,
                    dns_token=claim.dns_token,
                )
            except Exception as exc:
                # Domain claims are persisted before notification dispatch; email failures
                # should not fail claim creation.
                logger.exception("domain_claim_email_dispatch_failed claim_id=%s error=%s", claim.id, str(exc))

        response = DomainClaimResponse.model_validate(claim).model_dump()
        response["dns_txt_record"] = f"encypher-domain-claim={claim.dns_token}"
        return ok(response)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{org_id}/domain-claims/{claim_id}/verify-dns")
async def verify_domain_dns(
    org_id: str,
    claim_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Verify a domain claim via DNS TXT records."""
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    try:
        claim = org_service.get_domain_claim(org_id, claim_id)
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain claim not found")

        records = dns.resolver.resolve(claim.domain, "TXT")
        txt_records = ["".join(part.decode("utf-8") for part in record.strings) for record in records]
        verified = org_service.verify_domain_dns(org_id, claim_id, user_id, txt_records)
        return ok(DomainClaimResponse.model_validate(verified).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ValueError, dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{org_id}/domain-claims/{claim_id}/auto-join")
async def update_domain_auto_join(
    org_id: str,
    claim_id: str,
    payload: DomainClaimAutoJoinUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Enable or disable auto-join for a verified domain claim."""
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    try:
        claim = org_service.set_domain_auto_join(org_id, claim_id, user_id, payload.enabled)
        return ok(DomainClaimResponse.model_validate(claim).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{org_id}/domain-claims/{claim_id}")
async def delete_domain_claim(
    org_id: str,
    claim_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Delete a domain claim for an organization."""
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    try:
        claim = org_service.delete_domain_claim(org_id, claim_id, user_id)
        return ok(DomainClaimResponse.model_validate(claim).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/domain-claims/verify-email")
async def verify_domain_email(token: str, db: Session = Depends(get_db)):
    """Verify a domain claim via email token (public endpoint)."""
    org_service = OrganizationService(db)
    try:
        claim = org_service.verify_domain_email(token)
        return ok(DomainClaimResponse.model_validate(claim).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
async def list_organizations(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all organizations the current user belongs to"""
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)
    orgs = org_service.get_user_organizations(user_id)

    return ok([OrganizationResponse.model_validate(org).model_dump() for org in orgs])


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get organization details"""
    actor_user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access
    if not org_service.can_user_access_org(org_id, actor_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return ok(OrganizationResponse.model_validate(org).model_dump())


@router.patch("/{org_id}")
async def update_organization(
    org_id: str,
    updates: OrganizationUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Update organization settings"""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        org = org_service.update_organization(org_id=org_id, user_id=user_id, **updates.model_dump(exclude_unset=True))

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        return ok(OrganizationResponse.model_validate(org).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# MEMBER ENDPOINTS
# ==========================================


@router.get("/{org_id}/members")
async def list_members(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List all members of an organization"""
    actor_user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access
    if not org_service.can_user_access_org(org_id, actor_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    members = org_service.get_members(org_id)

    # Enrich with user info
    result = []
    for member in members:
        member_data = {
            "id": member.id,
            "user_id": member.user_id,
            "user_email": member.user.email if member.user else None,
            "user_name": member.user.name if member.user else None,
            "role": member.role,
            "status": member.status,
            "invited_at": member.invited_at,
            "accepted_at": member.accepted_at,
            "last_active_at": member.last_active_at,
        }
        result.append(member_data)

    return ok(result)


@router.patch("/{org_id}/members/{target_user_id}")
async def update_member_role(
    org_id: str,
    target_user_id: str,
    role_update: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Update a member's role"""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        member = org_service.update_member_role(org_id=org_id, target_user_id=target_user_id, new_role=role_update.role, actor_user_id=user_id)

        return ok(
            {
                "id": member.id,
                "user_id": member.user_id,
                "role": member.role,
                "status": member.status,
            }
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{org_id}/members/{target_user_id}")
async def remove_member(
    org_id: str,
    target_user_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Remove a member from the organization"""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        org_service.remove_member(org_id=org_id, target_user_id=target_user_id, actor_user_id=user_id)

        return ok({"removed": True})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{org_id}/seats")
async def get_seat_info(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get seat usage information"""
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access
    if not org_service.can_user_access_org(org_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    seat_info = org_service.get_seat_count(org_id)

    return ok(seat_info)


# ==========================================
# INVITATION ENDPOINTS
# ==========================================


@router.post("/{org_id}/invitations")
async def create_invitation(
    org_id: str,
    invitation_data: InvitationCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("org_invite", limit=20, window_sec=60)),
):
    """Send an invitation to join the organization"""
    user_id = await get_current_user_id(request, db)

    try:
        if invitation_data.trial_months:
            require_super_admin(db, user_id)

        org_service = OrganizationService(db)
        invitation = org_service.create_invitation(
            org_id=org_id,
            email=invitation_data.email,
            role=invitation_data.role,
            inviter_user_id=user_id,
            message=invitation_data.message,
            first_name=invitation_data.first_name,
            last_name=invitation_data.last_name,
            organization_name=invitation_data.organization_name,
            tier=invitation_data.tier.value if invitation_data.tier else None,
            trial_months=invitation_data.trial_months,
        )

        inviter = db.query(User).filter(User.id == user_id).first()
        org = org_service.get_organization(org_id)
        organization_name = invitation.organization_name or (org.name if org else "")
        if inviter and organization_name:
            recipient_name = " ".join(part for part in [invitation.first_name, invitation.last_name] if part).strip()
            await _send_invitation_email(
                authorization=request.headers.get("Authorization", ""),
                recipient_email=invitation.email,
                recipient_name=recipient_name or None,
                inviter_name=inviter.name,
                inviter_email=inviter.email,
                organization_name=organization_name,
                role=invitation.role,
                invitation_token=invitation.token,
                message=invitation.message,
                expires_at=invitation.expires_at,
                tier=invitation.tier,
                trial_months=invitation.trial_months,
            )

        return ok(InvitationResponse.model_validate(invitation).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{org_id}/invitations")
async def list_invitations(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List pending invitations"""
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check permission
    if not org_service.can_user_invite(org_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    invitations = org_service.get_pending_invitations(org_id)

    return ok([InvitationResponse.model_validate(inv).model_dump() for inv in invitations])


@router.delete("/{org_id}/invitations/{invitation_id}")
async def cancel_invitation(
    org_id: str,
    invitation_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Cancel a pending invitation"""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        org_service.cancel_invitation(org_id=org_id, invitation_id=invitation_id, actor_user_id=user_id)

        return ok({"cancelled": True})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{org_id}/invitations/{invitation_id}/resend")
async def resend_invitation(
    org_id: str,
    invitation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("org_invite", limit=20, window_sec=60)),
):
    """Resend an invitation"""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        invitation = org_service.resend_invitation(org_id=org_id, invitation_id=invitation_id, actor_user_id=user_id)

        inviter = db.query(User).filter(User.id == user_id).first()
        org = org_service.get_organization(org_id)
        organization_name = invitation.organization_name or (org.name if org else "")
        if inviter and organization_name:
            recipient_name = " ".join(part for part in [invitation.first_name, invitation.last_name] if part).strip()
            await _send_invitation_email(
                authorization=request.headers.get("Authorization", ""),
                recipient_email=invitation.email,
                recipient_name=recipient_name or None,
                inviter_name=inviter.name,
                inviter_email=inviter.email,
                organization_name=organization_name,
                role=invitation.role,
                invitation_token=invitation.token,
                message=invitation.message,
                expires_at=invitation.expires_at,
                tier=invitation.tier,
                trial_months=invitation.trial_months,
            )

        return ok(InvitationResponse.model_validate(invitation).model_dump())
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# INVITATION ACCEPTANCE (Public endpoints)
# ==========================================


class AcceptInvitationNewUser(BaseModel):
    """Schema for accepting invitation with new account"""

    name: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=settings.AUTH_MAX_PASSWORD_LENGTH)


@router.get("/invitations/{token}")
async def get_invitation_details(
    token: str,
    db: Session = Depends(get_db),
):
    """Get invitation details (public endpoint for invitation page)"""
    org_service = OrganizationService(db)
    details = org_service.get_invitation_details(token)

    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    return ok(details)


@router.post("/invitations/{token}/accept")
async def accept_invitation(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Accept an invitation and join the organization (for logged-in users)"""
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        member = org_service.accept_invitation(token=token, user_id=user_id)

        return ok({"organization_id": member.organization_id, "role": member.role, "message": "Successfully joined the organization"})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/invitations/{token}/accept-new")
async def accept_invitation_new_user(
    token: str,
    data: AcceptInvitationNewUser,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("signup", limit=5, window_sec=60)),
):
    """Accept an invitation and create a new account"""
    from passlib.context import CryptContext

    # Hash password
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(data.password)

    try:
        org_service = OrganizationService(db)
        user, member = org_service.accept_invitation_new_user(token=token, name=data.name, password_hash=password_hash)

        # Generate tokens for auto-login
        from ...services.auth_service import AuthService

        access_token = AuthService.create_access_token(user)
        refresh_token_obj = AuthService.create_refresh_token(db, user)

        return ok(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                },
                "organization_id": member.organization_id,
                "role": member.role,
                "access_token": access_token,
                "refresh_token": refresh_token_obj.token,
                "message": "Account created and joined the organization",
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# AUDIT LOG ENDPOINTS
# ==========================================


@router.get("/{org_id}/audit-logs")
async def get_audit_logs(
    org_id: str,
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = None,
    user_id_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get organization audit logs"""
    actor_user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access (any member can view audit logs)
    if not org_service.can_user_access_org(org_id, actor_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    logs = org_service.get_audit_logs(
        org_id=org_id,
        limit=min(limit, 100),  # Cap at 100
        offset=offset,
        action_filter=action,
        user_id_filter=user_id_filter,
    )

    return ok([AuditLogResponse.model_validate(log).model_dump() for log in logs])


class AuditLogCreate(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[dict] = None


@router.post("/{org_id}/audit-logs")
async def create_audit_log(
    org_id: str,
    payload: AuditLogCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create an audit log entry"""
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    if not org_service.can_user_access_org(org_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    org_service._log_action(
        org_id=org_id,
        user_id=user_id,
        action=payload.action,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        details=payload.details,
    )
    db.commit()

    logs = org_service.get_audit_logs(org_id=org_id, limit=1, offset=0)
    created_log = logs[0] if logs else None

    return ok(AuditLogResponse.model_validate(created_log).model_dump() if created_log else None)


# ============================================
# TEAM_191: PUBLISHER SETTINGS
# ============================================


class PublisherSettingsUpdate(BaseModel):
    """Request to update publisher identity settings"""

    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    dashboard_layout: Optional[str] = Field(None, min_length=1, max_length=32)
    publisher_platform: Optional[str] = Field(None, min_length=1, max_length=64)
    publisher_platform_custom: Optional[str] = Field(None, min_length=1, max_length=255)
    signing_identity_mode: Optional[str] = Field(None, min_length=1, max_length=64)
    anonymous_publisher: Optional[bool] = None


@router.patch("/{org_id}/publisher-settings")
async def update_publisher_settings(
    org_id: str,
    payload: PublisherSettingsUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Update publisher identity settings for an organization.
    Allows toggling anonymous mode and updating display name.
    """
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    if not org_service._has_permission(org_id, user_id, {"owner", "admin"}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners and admins can update publisher settings")

    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    changes = {}
    requested_layout = payload.dashboard_layout.strip().lower() if payload.dashboard_layout is not None else None
    requested_platform = payload.publisher_platform.strip().lower() if payload.publisher_platform is not None else None
    requested_platform_custom = payload.publisher_platform_custom.strip() if payload.publisher_platform_custom is not None else None

    if requested_layout is not None and requested_layout not in {"publisher", "enterprise"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dashboard layout")

    if requested_platform is not None and requested_platform not in {"wordpress", "ghost", "substack", "medium", "custom"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid publisher platform")

    resolved_layout = requested_layout or org.dashboard_layout or "publisher"
    resolved_platform = requested_platform if requested_platform is not None else org.publisher_platform
    resolved_platform_custom = requested_platform_custom if payload.publisher_platform_custom is not None else org.publisher_platform_custom
    updating_layout_preferences = any(
        value is not None for value in (payload.dashboard_layout, payload.publisher_platform, payload.publisher_platform_custom)
    )

    if updating_layout_preferences and resolved_layout == "publisher":
        if not resolved_platform:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Publisher platform is required for publisher layout")
        if resolved_platform == "custom" and not resolved_platform_custom:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Custom publisher platform is required when platform is custom")
    elif updating_layout_preferences:
        resolved_platform = None
        resolved_platform_custom = None

    if payload.signing_identity_mode is not None:
        requested_mode = payload.signing_identity_mode.strip().lower()
        if requested_mode not in ALLOWED_SIGNING_IDENTITY_MODES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signing identity mode")
    else:
        requested_mode = None

    if org.account_type == "organization" and (payload.display_name is not None or requested_mode is not None):
        verified_claim = (
            db.query(OrganizationDomainClaim)
            .filter(
                OrganizationDomainClaim.organization_id == org_id,
                OrganizationDomainClaim.status == "verified",
            )
            .first()
        )
        if not verified_claim:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verify at least one organization domain before setting publisher display name.",
            )

    if requested_mode is not None:
        is_custom_mode = requested_mode == SIGNING_IDENTITY_MODE_CUSTOM
        has_custom_add_on = bool((org.add_ons or {}).get("custom-signing-identity"))
        has_custom_entitlement = org.tier in {"enterprise", "strategic_partner"} or has_custom_add_on
        if is_custom_mode and not has_custom_entitlement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom signing identity requires the Custom Signing Identity add-on.",
            )

        org.signing_identity_mode = requested_mode
        changes["signing_identity_mode"] = org.signing_identity_mode
        if requested_mode != SIGNING_IDENTITY_MODE_CUSTOM:
            org.signing_identity_custom_label = None
            changes["signing_identity_custom_label"] = None

    if payload.display_name is not None:
        cleaned_display_name = payload.display_name.strip()
        if not cleaned_display_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Display name cannot be empty")

        resolved_mode = requested_mode or org.signing_identity_mode or SIGNING_IDENTITY_MODE_ORGANIZATION_NAME
        if resolved_mode == SIGNING_IDENTITY_MODE_CUSTOM:
            has_custom_add_on = bool((org.add_ons or {}).get("custom-signing-identity"))
            has_custom_entitlement = org.tier in {"enterprise", "strategic_partner"} or has_custom_add_on
            if not has_custom_entitlement:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom signing identity requires the Custom Signing Identity add-on.",
                )
            org.signing_identity_custom_label = cleaned_display_name
            changes["signing_identity_custom_label"] = org.signing_identity_custom_label

        org.display_name = cleaned_display_name
        if not org.name:
            org.name = org.display_name
        changes["display_name"] = org.display_name

    if requested_layout is not None:
        org.dashboard_layout = requested_layout
        changes["dashboard_layout"] = org.dashboard_layout

    if resolved_layout == "publisher":
        if requested_platform is not None:
            org.publisher_platform = requested_platform
            changes["publisher_platform"] = org.publisher_platform
        if requested_platform is not None and requested_platform != "custom":
            org.publisher_platform_custom = None
            changes["publisher_platform_custom"] = None
        elif payload.publisher_platform_custom is not None or org.publisher_platform == "custom":
            org.publisher_platform_custom = resolved_platform_custom
            changes["publisher_platform_custom"] = org.publisher_platform_custom
    elif requested_layout is not None or payload.publisher_platform is not None or payload.publisher_platform_custom is not None:
        org.publisher_platform = None
        org.publisher_platform_custom = None
        changes["publisher_platform"] = None
        changes["publisher_platform_custom"] = None

    if payload.anonymous_publisher is not None:
        org.anonymous_publisher = payload.anonymous_publisher
        changes["anonymous_publisher"] = org.anonymous_publisher

    if changes:
        org_service._log_action(
            org_id=org_id,
            user_id=user_id,
            action="publisher_settings.updated",
            resource_type="organization",
            resource_id=org_id,
            details=changes,
        )
        db.commit()

    return ok(
        {
            "display_name": org.display_name,
            "account_type": org.account_type,
            "dashboard_layout": org.dashboard_layout,
            "publisher_platform": org.publisher_platform,
            "publisher_platform_custom": org.publisher_platform_custom,
            "signing_identity_mode": org.signing_identity_mode,
            "signing_identity_custom_label": org.signing_identity_custom_label,
            "custom_signing_identity_enabled": bool((org.add_ons or {}).get("custom-signing-identity"))
            or org.tier in {"enterprise", "strategic_partner"},
            "anonymous_publisher": org.anonymous_publisher,
        }
    )


# ============================================================
# ORG SECURITY SETTINGS (TEAM_224)
# ============================================================


class OrgSecuritySettingsUpdate(BaseModel):
    enforce_mfa: Optional[bool] = None


@router.get("/{org_id}/security")
async def get_org_security_settings(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get security settings for an organization (admin/owner only)."""
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    if not org_service._has_permission(org_id, user_id, {"owner", "admin"}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or owner role required")

    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return ok(
        {
            "enforce_mfa": bool((org.features or {}).get("enforce_mfa", False)),
        }
    )


@router.patch("/{org_id}/security")
async def update_org_security_settings(
    org_id: str,
    payload: OrgSecuritySettingsUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Update security settings for an organization (admin/owner only)."""
    user_id = await get_current_user_id(request, db)
    org_service = OrganizationService(db)

    if not org_service._has_permission(org_id, user_id, {"owner", "admin"}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or owner role required")

    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    features = dict(org.features or {})
    if payload.enforce_mfa is not None:
        features["enforce_mfa"] = payload.enforce_mfa
    org.features = features
    db.commit()

    return ok(
        {
            "enforce_mfa": bool(features.get("enforce_mfa", False)),
        }
    )
