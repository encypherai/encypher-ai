"""
Organization API endpoints for team management
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ...db.models import User
from ...db.session import get_db
from ...core.config import settings
from ...services.organization_service import OrganizationService
import dns.resolver
from ...services.auth_service import AuthService
from ...deps.rate_limit import rate_limiter
from encypher_commercial_shared.email import EmailConfig, build_invitation_email

router = APIRouter(prefix="/organizations", tags=["organizations"])
logger = logging.getLogger(__name__)


def _get_email_config() -> EmailConfig:
    return EmailConfig(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_pass=settings.SMTP_PASS,
        smtp_tls=settings.SMTP_TLS,
        email_from=settings.EMAIL_FROM,
        email_from_name=settings.EMAIL_FROM_NAME,
        frontend_url=settings.FRONTEND_URL,
        dashboard_url=settings.DASHBOARD_URL,
        support_email=settings.SUPPORT_EMAIL,
    )


async def _send_invitation_email(
    *,
    authorization: str,
    recipient_email: str,
    inviter_name: Optional[str],
    inviter_email: str,
    organization_name: str,
    role: str,
    invitation_token: str,
    message: Optional[str],
    expires_at: Optional[datetime],
) -> None:
    config = _get_email_config()
    subject, html_content, plain_content = build_invitation_email(
        config=config,
        inviter_name=inviter_name,
        inviter_email=inviter_email,
        organization_name=organization_name,
        role=role,
        invitation_token=invitation_token,
        message=message,
        expires_at=expires_at,
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
                logger.warning(
                    "invitation_email_failed",
                    status=response.status_code,
                    response=response.text,
                )
    except httpx.RequestError as exc:
        logger.warning("invitation_email_request_failed", error=str(exc))


async def _send_domain_claim_email(
    *,
    authorization: str,
    recipient_email: str,
    organization_name: str,
    domain: str,
    email_token: str,
) -> None:
    config = _get_email_config()
    base_url = config.dashboard_url or config.frontend_url
    verification_url = f"{base_url}/verify-domain?token={email_token}"
    subject = f"Verify {domain} for {organization_name}"
    html_content = (
        f"<p>Confirm domain ownership for <strong>{organization_name}</strong>.</p>"
        f"<p>Verify <strong>{domain}</strong> by clicking the link below:</p>"
        f"<p><a href=\"{verification_url}\">Verify domain</a></p>"
        "<p>If you did not request this, you can ignore this email.</p>"
    )
    plain_content = (
        f"Verify {domain} for {organization_name}\n\n"
        f"Verify domain: {verification_url}\n\n"
        "If you did not request this, you can ignore this email."
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
                logger.warning(
                    "domain_claim_email_failed",
                    status=response.status_code,
                    response=response.text,
                )
    except httpx.RequestError as exc:
        logger.warning("domain_claim_email_request_failed", error=str(exc))


# ==========================================
# SCHEMAS
# ==========================================


class OrganizationCreate(BaseModel):
    name: str
    email: EmailStr


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: Optional[str]
    email: str
    tier: str
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
    role: str = "member"
    message: Optional[str] = None


class InvitationResponse(BaseModel):
    id: str
    email: str
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
    user_id = await get_current_user_id(request, db)

    try:
        org_service = OrganizationService(db)
        org = org_service.create_organization(name=org_data.name, email=org_data.email, owner_user_id=user_id)

        return {"success": True, "data": OrganizationResponse.model_validate(org).model_dump(), "error": None}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
        return {
            "success": True,
            "data": [DomainClaimResponse.model_validate(claim).model_dump() for claim in claims],
            "error": None,
        }
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
            await _send_domain_claim_email(
                authorization=request.headers.get("Authorization", ""),
                recipient_email=claim.verification_email,
                organization_name=org.name,
                domain=claim.domain,
                email_token=claim.email_token,
            )

        response = DomainClaimResponse.model_validate(claim).model_dump()
        response["dns_txt_record"] = f"encypher-domain-claim={claim.dns_token}"
        return {
            "success": True,
            "data": response,
            "error": None,
        }
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
        return {
            "success": True,
            "data": DomainClaimResponse.model_validate(verified).model_dump(),
            "error": None,
        }
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
        return {
            "success": True,
            "data": DomainClaimResponse.model_validate(claim).model_dump(),
            "error": None,
        }
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
        return {
            "success": True,
            "data": DomainClaimResponse.model_validate(claim).model_dump(),
            "error": None,
        }
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

    return {"success": True, "data": [OrganizationResponse.model_validate(org).model_dump() for org in orgs], "error": None}


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get organization details"""
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access
    if not org_service.can_user_access_org(org_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    org = org_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return {"success": True, "data": OrganizationResponse.model_validate(org).model_dump(), "error": None}


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

        return {"success": True, "data": OrganizationResponse.model_validate(org).model_dump(), "error": None}
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
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access
    if not org_service.can_user_access_org(org_id, user_id):
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

    return {"success": True, "data": result, "error": None}


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

        return {
            "success": True,
            "data": {
                "id": member.id,
                "user_id": member.user_id,
                "role": member.role,
                "status": member.status,
            },
            "error": None,
        }
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

        return {"success": True, "data": {"removed": True}, "error": None}
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

    return {"success": True, "data": seat_info, "error": None}


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
        org_service = OrganizationService(db)
        invitation = org_service.create_invitation(
            org_id=org_id, email=invitation_data.email, role=invitation_data.role, inviter_user_id=user_id, message=invitation_data.message
        )

        inviter = db.query(User).filter(User.id == user_id).first()
        org = org_service.get_organization(org_id)
        if inviter and org:
            await _send_invitation_email(
                authorization=request.headers.get("Authorization", ""),
                recipient_email=invitation.email,
                inviter_name=inviter.name,
                inviter_email=inviter.email,
                organization_name=org.name,
                role=invitation.role,
                invitation_token=invitation.token,
                message=invitation.message,
                expires_at=invitation.expires_at,
            )

        return {"success": True, "data": InvitationResponse.model_validate(invitation).model_dump(), "error": None}
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

    return {"success": True, "data": [InvitationResponse.model_validate(inv).model_dump() for inv in invitations], "error": None}


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

        return {"success": True, "data": {"cancelled": True}, "error": None}
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
        if inviter and org:
            await _send_invitation_email(
                authorization=request.headers.get("Authorization", ""),
                recipient_email=invitation.email,
                inviter_name=inviter.name,
                inviter_email=inviter.email,
                organization_name=org.name,
                role=invitation.role,
                invitation_token=invitation.token,
                message=invitation.message,
                expires_at=invitation.expires_at,
            )

        return {"success": True, "data": InvitationResponse.model_validate(invitation).model_dump(), "error": None}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# INVITATION ACCEPTANCE (Public endpoints)
# ==========================================


class AcceptInvitationNewUser(BaseModel):
    """Schema for accepting invitation with new account"""

    name: str
    password: str


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

    return {"success": True, "data": details, "error": None}


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

        return {
            "success": True,
            "data": {"organization_id": member.organization_id, "role": member.role, "message": "Successfully joined the organization"},
            "error": None,
        }
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

    # Validate password
    if len(data.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

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

        return {
            "success": True,
            "data": {
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
            },
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# AUDIT LOG ENDPOINTS
# ==========================================


@router.get("/{org_id}/audit-logs")
async def get_audit_logs(
    org_id: str,
    request: Request,
    limit: int = 50,
    offset: int = 0,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get organization audit logs"""
    user_id = await get_current_user_id(request, db)

    org_service = OrganizationService(db)

    # Check access (any member can view audit logs)
    if not org_service.can_user_access_org(org_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    logs = org_service.get_audit_logs(
        org_id=org_id,
        limit=min(limit, 100),  # Cap at 100
        offset=offset,
        action_filter=action,
    )

    return {"success": True, "data": [AuditLogResponse.model_validate(log).model_dump() for log in logs], "error": None}
