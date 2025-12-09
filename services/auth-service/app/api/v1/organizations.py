"""
Organization API endpoints for team management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ...db.session import get_db
from ...services.organization_service import OrganizationService
from ...services.auth_service import AuthService
from ...deps.rate_limit import rate_limiter

router = APIRouter(prefix="/organizations", tags=["organizations"])


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

        # TODO: Send invitation email via notification service

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

        # TODO: Send invitation email via notification service

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
