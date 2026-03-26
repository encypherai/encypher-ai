"""Team management router for Business+ tier organizations."""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import require_read_permission
from app.routers.audit import AuditAction, log_audit_event
from app.services.auth_service_client import auth_service_client

router = APIRouter(prefix="/org/members", tags=["Team Management"])
invite_router = APIRouter(prefix="/org/invites", tags=["Team Invites"])

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=select_autoescape(["html", "xml"]))


def _render_team_invite_email(
    *, subject: str, inviter_name: str, organization_name: str, role: str, invitation_url: str, expires_at: datetime
) -> str:
    template = _jinja_env.get_template("team_invitation.html")
    return template.render(
        subject=subject,
        inviter_name=inviter_name,
        organization_name=organization_name,
        role=role.capitalize(),
        invitation_url=invitation_url,
        expires_at_label=expires_at.strftime("%B %-d, %Y at %-I:%M %p UTC"),
        year=datetime.now(timezone.utc).year,
    )


class TeamRole(str, Enum):
    """Team member roles with hierarchical permissions."""

    OWNER = "owner"  # Full access, can transfer ownership
    ADMIN = "admin"  # Full access except ownership transfer
    MEMBER = "member"  # Can sign/verify, view analytics
    VIEWER = "viewer"  # Read-only access


# Role hierarchy for permission checks
ROLE_HIERARCHY = {
    TeamRole.OWNER: 4,
    TeamRole.ADMIN: 3,
    TeamRole.MEMBER: 2,
    TeamRole.VIEWER: 1,
}


class TeamMember(BaseModel):
    """Team member details."""

    id: str
    user_id: str
    email: str
    name: Optional[str] = None
    role: TeamRole
    status: str
    invited_at: Optional[str] = None
    accepted_at: Optional[str] = None
    last_active_at: Optional[str] = None


class TeamMemberListResponse(BaseModel):
    """List of team members."""

    organization_id: str
    members: List[TeamMember]
    total: int
    max_members: int  # Based on tier


class InviteRequest(BaseModel):
    """Request to invite a new team member."""

    email: EmailStr
    role: TeamRole = TeamRole.MEMBER
    name: Optional[str] = None


class InviteResponse(BaseModel):
    """Response after sending an invite."""

    success: bool
    invite_id: str
    email: str
    role: str
    expires_at: str
    message: str


class PendingInvite(BaseModel):
    """Pending team invitation."""

    id: str
    email: str
    role: str
    invited_by: str
    status: str
    expires_at: str
    created_at: str


class UpdateRoleRequest(BaseModel):
    """Request to update a member's role."""

    role: TeamRole


from app.core.tier_config import get_team_member_limit, is_enterprise_tier


async def check_team_management_enabled(
    organization: dict = Depends(require_read_permission),
) -> dict:
    """Check if team management is enabled for the organization."""
    if not organization.get("team_management_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Team management requires Enterprise tier",
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


async def get_member_role(
    db: AsyncSession,
    organization_id: str,
    user_id: str,
) -> Optional[TeamRole]:
    """Get the role of a user in an organization."""
    result = await db.execute(
        text("SELECT role FROM organization_members WHERE organization_id = :org_id AND user_id = :user_id"),
        {"org_id": organization_id, "user_id": user_id},
    )
    row = result.fetchone()
    return TeamRole(row.role) if row else None


async def require_admin_role(
    organization: dict = Depends(check_team_management_enabled),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Require admin or owner role for team management operations."""
    user_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User context required for team management")

    # Check if user has admin/owner role in the database
    role = await get_member_role(db, organization["organization_id"], user_id)

    # If no role found in DB but this is a demo/test key with owner tier features,
    # assume owner role for testing purposes
    if role is None:
        tier = organization.get("tier", "free")
        if is_enterprise_tier(tier):
            # For demo keys with team_management enabled, assume owner role
            role = TeamRole.OWNER
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Owner role required for this operation")

    if role not in [TeamRole.OWNER, TeamRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Owner role required for this operation")

    organization["current_user_role"] = role
    return organization


@router.get("", response_model=TeamMemberListResponse)
async def list_team_members(
    organization: dict = Depends(check_team_management_enabled),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberListResponse:
    """
    List all team members in the organization.
    """
    org_id = organization["organization_id"]
    tier = organization.get("tier", "free")
    max_members = get_team_member_limit(tier)

    result = await db.execute(
        text("""
            SELECT om.id, om.user_id, u.email, u.name, om.role, om.joined_at
            FROM organization_members om
            LEFT JOIN users u ON om.user_id = u.id
            WHERE om.organization_id = :org_id
            ORDER BY
                CASE om.role
                    WHEN 'owner' THEN 1
                    WHEN 'admin' THEN 2
                    WHEN 'member' THEN 3
                    WHEN 'viewer' THEN 4
                END,
                om.joined_at
        """),
        {"org_id": org_id},
    )
    rows = result.fetchall()

    members = [
        TeamMember(
            id=row.id,
            user_id=row.user_id,
            email=row.email,
            name=row.name,
            role=TeamRole(row.role),
            status="active",  # All members in this table are active
            invited_at=None,  # Invites are in organization_invites table
            accepted_at=row.joined_at.isoformat() if row.joined_at else None,
            last_active_at=None,  # Not tracked in current schema
        )
        for row in rows
    ]


@router.post("/invites/{invite_id}/resend")
async def resend_invite(
    invite_id: str,
    background_tasks: BackgroundTasks,
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    """Resend a pending invitation and refresh its token and expiry."""
    org_id = organization["organization_id"]
    inviter_name = organization.get("user_name") or organization.get("organization_name") or "Your team admin"
    org_name = organization.get("organization_name", org_id)
    refreshed_token = secrets.token_urlsafe(32)
    refreshed_expiry = datetime.now(timezone.utc) + timedelta(days=7)

    result = await db.execute(
        text("""
            UPDATE organization_invites
            SET token = :token, expires_at = :expires_at
            WHERE id = :invite_id AND organization_id = :org_id AND status = 'pending'
            RETURNING email, role, token, expires_at
        """),
        {
            "invite_id": invite_id,
            "org_id": org_id,
            "token": refreshed_token,
            "expires_at": refreshed_expiry,
        },
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or already processed")

    actor_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if actor_id:
        await log_audit_event(
            db=db,
            organization_id=org_id,
            action=AuditAction.ORG_MEMBER_ADDED,
            actor_id=actor_id,
            actor_type="user",
            resource_type="team_invite",
            resource_id=invite_id,
            details={"email": row.email, "role": row.role, "event": "resent"},
        )

    await db.commit()

    background_tasks.add_task(
        _send_team_invite_email,
        recipient_email=row.email,
        inviter_name=inviter_name,
        org_name=org_name,
        role=row.role,
        invite_token=row.token,
        expires_at=row.expires_at,
    )

    return {
        "success": True,
        "message": f"Invitation resent to {row.email}",
        "invite_id": invite_id,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
    }


async def _send_team_invite_email(
    *,
    recipient_email: str,
    inviter_name: str,
    org_name: str,
    role: str,
    invite_token: str,
    expires_at: Optional[datetime] = None,
) -> None:
    """Send team invitation email via notification service. Non-fatal on failure."""
    claim_url = f"{settings.dashboard_url}/invite/team/{invite_token}"
    subject = f"You've been invited to join {org_name} on Encypher"
    html_body = _render_team_invite_email(
        subject=subject,
        inviter_name=inviter_name,
        organization_name=org_name,
        role=role,
        invitation_url=claim_url,
        expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(days=7)),
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{settings.notification_service_url}/api/v1/notifications/send",
                json={
                    "notification_type": "email",
                    "recipient_email": recipient_email,
                    "subject": subject,
                    "html_body": html_body,
                },
            )
    except Exception as exc:
        logging.getLogger(__name__).warning("team_invite_email_failed email=%s error=%s", recipient_email, exc)


@router.post("/invite", response_model=InviteResponse)
async def invite_member(
    request: InviteRequest,
    background_tasks: BackgroundTasks,
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    """
    Invite a new member to the organization.

    Sends an email invitation that expires in 7 days.
    """
    org_id = organization["organization_id"]
    tier = organization.get("tier", "free")
    max_members = get_team_member_limit(tier)
    inviter_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if not inviter_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inviter ID missing")

    # Check member limit
    count_result = await db.execute(text("SELECT COUNT(*) FROM organization_members WHERE organization_id = :org_id"), {"org_id": org_id})
    current_count = count_result.scalar() or 0

    if max_members > 0 and current_count >= max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "MEMBER_LIMIT_REACHED",
                "message": f"Your plan allows up to {max_members} team members",
                "upgrade_url": "/billing/upgrade",
            },
        )

    # Check if already a member
    existing = await db.execute(
        text("""
            SELECT om.id FROM organization_members om
            JOIN users u ON om.user_id = u.id
            WHERE om.organization_id = :org_id AND u.email = :email
        """),
        {"org_id": org_id, "email": request.email},
    )
    if existing.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email is already a team member")

    # Check for pending invite
    pending = await db.execute(
        text("""
            SELECT id FROM organization_invites
            WHERE organization_id = :org_id AND email = :email AND status = 'pending'
        """),
        {"org_id": org_id, "email": request.email},
    )
    if pending.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An invitation is already pending for this email")

    # Cannot invite as owner
    if request.role == TeamRole.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot invite as owner. Use transfer ownership instead.")

    # Create invite
    invite_id = f"inv_{uuid4().hex[:16]}"
    invite_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    await db.execute(
        text("""
            INSERT INTO organization_invites (
                id, organization_id, email, role, invited_by,
                token, status, expires_at
            )
            VALUES (
                :id, :org_id, :email, :role, :invited_by,
                :token, 'pending', :expires_at
            )
        """),
        {
            "id": invite_id,
            "org_id": org_id,
            "email": request.email,
            "role": request.role.value,
            "invited_by": inviter_id,
            "token": invite_token,
            "expires_at": expires_at,
        },
    )

    # Log audit event
    await log_audit_event(
        db=db,
        organization_id=org_id,
        action=AuditAction.ORG_MEMBER_ADDED,
        actor_id=inviter_id,
        actor_type="user",
        resource_type="team_invite",
        resource_id=invite_id,
        details={"email": request.email, "role": request.role.value},
    )

    await db.commit()

    org_name = organization.get("organization_name", org_id)
    inviter_name = organization.get("user_name") or organization.get("organization_name") or "Your team admin"
    background_tasks.add_task(
        _send_team_invite_email,
        recipient_email=request.email,
        inviter_name=inviter_name,
        org_name=org_name,
        role=request.role.value,
        invite_token=invite_token,
        expires_at=expires_at,
    )

    return InviteResponse(
        success=True,
        invite_id=invite_id,
        email=request.email,
        role=request.role.value,
        expires_at=expires_at.isoformat(),
        message=f"Invitation sent to {request.email}",
    )


@router.get("/invites", response_model=List[PendingInvite])
async def list_pending_invites(
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
) -> List[PendingInvite]:
    """
    List all pending invitations.
    """
    org_id = organization["organization_id"]

    result = await db.execute(
        text("""
            SELECT id, email, role, invited_by, status, expires_at, created_at
            FROM organization_invites
            WHERE organization_id = :org_id AND status = 'pending'
            ORDER BY created_at DESC
        """),
        {"org_id": org_id},
    )
    rows = result.fetchall()

    return [
        PendingInvite(
            id=row.id,
            email=row.email,
            role=row.role,
            invited_by=row.invited_by,
            status=row.status,
            expires_at=row.expires_at.isoformat() if row.expires_at else "",
            created_at=row.created_at.isoformat() if row.created_at else "",
        )
        for row in rows
    ]


@router.delete("/invites/{invite_id}")
async def revoke_invite(
    invite_id: str,
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a pending invitation.
    """
    org_id = organization["organization_id"]

    result = await db.execute(
        text("""
            UPDATE organization_invites
            SET status = 'revoked'
            WHERE id = :invite_id AND organization_id = :org_id AND status = 'pending'
            RETURNING email
        """),
        {"invite_id": invite_id, "org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or already processed")

    await db.commit()

    return {"success": True, "message": f"Invitation to {row.email} revoked"}


@router.patch("/{member_id}/role")
async def update_member_role(
    member_id: str,
    request: UpdateRoleRequest,
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a team member's role.

    Admins can change roles of members and viewers.
    Only owners can change admin roles.
    """
    org_id = organization["organization_id"]
    current_role = organization.get("current_user_role")
    actor_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if not actor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Actor ID missing")

    # Get target member
    result = await db.execute(
        text("SELECT user_id, role FROM organization_members WHERE id = :id AND organization_id = :org_id"), {"id": member_id, "org_id": org_id}
    )
    member = result.fetchone()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")

    target_role = TeamRole(member.role)

    # Cannot change owner role
    if target_role == TeamRole.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change owner role. Use transfer ownership instead.")

    # Cannot promote to owner
    if request.role == TeamRole.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot promote to owner. Use transfer ownership instead.")

    # Admins cannot change other admins
    if current_role == TeamRole.ADMIN and target_role == TeamRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can modify admin roles")

    # Admins cannot promote to admin
    if current_role == TeamRole.ADMIN and request.role == TeamRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can promote to admin")

    # Update role
    await db.execute(
        text("""
            UPDATE organization_members
            SET role = :role, updated_at = :updated_at
            WHERE id = :id AND organization_id = :org_id
        """),
        {
            "id": member_id,
            "org_id": org_id,
            "role": request.role.value,
            "updated_at": datetime.now(timezone.utc),
        },
    )

    # Log audit event
    await log_audit_event(
        db=db,
        organization_id=org_id,
        action=AuditAction.ORG_MEMBER_ROLE_CHANGED,
        actor_id=actor_id,
        actor_type="user",
        resource_type="team_member",
        resource_id=member_id,
        details={"old_role": target_role.value, "new_role": request.role.value},
    )

    await db.commit()

    return {
        "success": True,
        "member_id": member_id,
        "old_role": target_role.value,
        "new_role": request.role.value,
    }


@router.delete("/{member_id}")
async def remove_member(
    member_id: str,
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a team member from the organization.

    Cannot remove the owner.
    """
    org_id = organization["organization_id"]
    current_role = organization.get("current_user_role")
    actor_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if not actor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Actor ID missing")

    # Get target member
    result = await db.execute(
        text("""
            SELECT om.user_id, u.email, om.role
            FROM organization_members om
            JOIN users u ON om.user_id = u.id
            WHERE om.id = :id AND om.organization_id = :org_id
        """),
        {"id": member_id, "org_id": org_id},
    )
    member = result.fetchone()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")

    target_role = TeamRole(member.role)

    # Cannot remove owner
    if target_role == TeamRole.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the organization owner")

    # Admins cannot remove other admins
    if current_role == TeamRole.ADMIN and target_role == TeamRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can remove admins")

    # Delete member
    await db.execute(text("DELETE FROM organization_members WHERE id = :id AND organization_id = :org_id"), {"id": member_id, "org_id": org_id})

    # Log audit event
    await log_audit_event(
        db=db,
        organization_id=org_id,
        action=AuditAction.ORG_MEMBER_REMOVED,
        actor_id=actor_id,
        actor_type="user",
        resource_type="team_member",
        resource_id=member_id,
        details={"email": member.email, "role": target_role.value},
    )

    await db.commit()

    return {
        "success": True,
        "message": f"Removed {member.email} from the organization",
    }


@router.post("/accept-invite")
async def accept_invite(
    token: str = Query(..., description="Invitation token"),
    user_id: str = Query(..., description="User ID of the accepting user"),
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a team invitation.

    This endpoint is called after the user authenticates.
    """
    now = datetime.now(timezone.utc)

    # Find and validate invite
    result = await db.execute(
        text("""
            SELECT id, organization_id, email, role, expires_at
            FROM organization_invites
            WHERE token = :token AND status = 'pending'
        """),
        {"token": token},
    )
    invite = result.fetchone()

    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired invitation")

    if invite.expires_at < now:
        # Mark as expired
        await db.execute(text("UPDATE organization_invites SET status = 'expired' WHERE id = :id"), {"id": invite.id})
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invitation has expired")

    # Create team member
    member_id = f"mem_{uuid4().hex[:16]}"

    await db.execute(
        text("""
            INSERT INTO organization_members (
                id, organization_id, user_id, role,
                status, invited_at, accepted_at
            )
            VALUES (
                :id, :org_id, :user_id, :role,
                'active', :invited_at, :accepted_at
            )
        """),
        {
            "id": member_id,
            "org_id": invite.organization_id,
            "user_id": user_id,
            "role": invite.role,
            "invited_at": now,
            "accepted_at": now,
        },
    )

    # Update invite status
    await db.execute(text("UPDATE organization_invites SET status = 'accepted', accepted_at = :now WHERE id = :id"), {"id": invite.id, "now": now})

    await db.commit()

    # Set default org in auth-service so setup wizard can complete (best-effort)
    await auth_service_client.set_default_organization(
        user_id=user_id,
        organization_id=str(invite.organization_id),
    )

    return {
        "success": True,
        "member_id": member_id,
        "organization_id": invite.organization_id,
        "role": invite.role,
        "message": "You have joined the organization",
    }


# ============================================================
# PUBLIC INVITE ENDPOINTS (no auth required)
# ============================================================


class AcceptInviteNewUserRequest(BaseModel):
    """Payload for accepting a team invite as a brand-new user."""

    name: str
    password: str


@invite_router.get("/public/{token}", response_model=None)
async def get_public_invite(token: str, db: AsyncSession = Depends(get_db)):
    """
    Return invite metadata for a pending team invitation (no auth required).

    Used by the /invite/team/[token] dashboard page to render invite details
    before the user is logged in.
    """
    result = await db.execute(
        text("""
            SELECT oi.id, oi.organization_id, oi.email, oi.role,
                   oi.expires_at, oi.status, oi.created_at,
                   o.name AS org_name
            FROM organization_invites oi
            LEFT JOIN organizations o ON o.id = oi.organization_id
            WHERE oi.token = :token AND oi.status = 'pending'
        """),
        {"token": token},
    )
    invite = result.fetchone()

    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or expired")

    now = datetime.now(timezone.utc)
    if invite.expires_at and invite.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invitation expired")

    return {
        "success": True,
        "data": {
            "email": invite.email,
            "org_name": invite.org_name or invite.organization_id,
            "role": invite.role,
            "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
            "status": invite.status,
        },
    }


@invite_router.post("/public/{token}/accept-new", response_model=None)
async def accept_invite_new_user(
    token: str,
    payload: AcceptInviteNewUserRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a team invitation and create a new user account in one step.

    - Validates the invite token
    - Creates a new user account via auth-service internal endpoint (email auto-verified)
    - Creates the org member record
    - Marks the invite as accepted
    - Returns access + refresh tokens so the dashboard can auto-login

    Returns 409 if the email is already registered (frontend shows 'sign in instead').
    Returns 404/410 if the invite is missing or expired.
    """
    result = await db.execute(
        text("""
            SELECT id, organization_id, email, role, expires_at, created_at
            FROM organization_invites
            WHERE token = :token AND status = 'pending'
        """),
        {"token": token},
    )
    invite = result.fetchone()

    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or expired")

    now = datetime.now(timezone.utc)
    if invite.expires_at and invite.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invitation expired")

    # Create user via auth-service
    try:
        user_result = await auth_service_client.create_user_internal(
            email=invite.email,
            name=payload.name,
            password=payload.password,
        )
    except RuntimeError as exc:
        if "409" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered. Please sign in to accept this invitation.",
            )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="User creation failed")

    user_id = user_result["user_id"]

    # Sync minimal user record to enterprise_api DB to satisfy org_members FK
    await db.execute(
        text("""
            INSERT INTO users (id, email, name, email_verified)
            VALUES (:id, :email, :name, TRUE)
            ON CONFLICT DO NOTHING
        """),
        {"id": user_id, "email": invite.email, "name": payload.name},
    )

    # Create org member record
    member_id = f"mem_{uuid4().hex[:16]}"
    await db.execute(
        text("""
            INSERT INTO organization_members (
                id, organization_id, user_id, role, joined_at
            )
            VALUES (
                :id, :org_id, :user_id, :role, :joined_at
            )
            ON CONFLICT (organization_id, user_id) DO NOTHING
        """),
        {
            "id": member_id,
            "org_id": invite.organization_id,
            "user_id": user_id,
            "role": invite.role,
            "joined_at": now,
        },
    )

    # Mark invite accepted
    await db.execute(
        text("UPDATE organization_invites SET status = 'accepted', accepted_at = :now WHERE id = :id"),
        {"id": invite.id, "now": now},
    )
    await db.commit()

    # Set default org in auth-service so setup wizard can complete (best-effort)
    await auth_service_client.set_default_organization(
        user_id=user_id,
        organization_id=str(invite.organization_id),
    )

    return {
        "success": True,
        "data": {
            "access_token": user_result["access_token"],
            "refresh_token": user_result["refresh_token"],
            "organization_id": str(invite.organization_id),
            "role": invite.role,
        },
    }


# ============================================================
# BULK INVITE ENDPOINT
# ============================================================


class BulkInviteItem(BaseModel):
    """Single invitation in a bulk invite request."""

    email: EmailStr
    role: str = "member"


class BulkInviteRequest(BaseModel):
    """Request body for bulk invite."""

    invitations: List[BulkInviteItem]


class BulkInviteResultItem(BaseModel):
    """Result for a single invitation in the bulk response."""

    email: str
    success: bool
    invite_id: Optional[str] = None
    error: Optional[str] = None


@router.post("/invite/bulk")
async def bulk_invite_members(
    request: BulkInviteRequest,
    background_tasks: BackgroundTasks,
    organization: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite multiple members to the organization in one request.

    - Limited to 50 invitations per request
    - Enterprise tier gated (via require_admin_role -> check_team_management_enabled)
    - Partial success: each invitation is processed individually
    - Returns per-item results with total/succeeded/failed counts
    """
    if not request.invitations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one invitation is required",
        )

    if len(request.invitations) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 invitations per request",
        )

    org_id = organization["organization_id"]
    inviter_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if not inviter_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inviter ID missing")

    org_name = organization.get("organization_name", org_id)
    inviter_name = organization.get("user_name") or organization.get("organization_name") or "Your team admin"

    # Pre-fetch existing member emails for efficiency
    existing_members_result = await db.execute(
        text("""
            SELECT u.email FROM organization_members om
            JOIN users u ON om.user_id = u.id
            WHERE om.organization_id = :org_id
        """),
        {"org_id": org_id},
    )
    existing_member_emails = {row.email.lower() for row in existing_members_result.fetchall()}

    # Pre-fetch pending invite emails for efficiency
    pending_invites_result = await db.execute(
        text("""
            SELECT email FROM organization_invites
            WHERE organization_id = :org_id AND status = 'pending'
        """),
        {"org_id": org_id},
    )
    pending_invite_emails = {row.email.lower() for row in pending_invites_result.fetchall()}

    results: List[BulkInviteResultItem] = []
    succeeded = 0
    failed = 0

    # Track emails already invited in this batch to catch duplicates
    batch_emails: set = set()

    for item in request.invitations:
        email_lower = item.email.lower()

        # Reject owner role
        if item.role == TeamRole.OWNER or item.role == "owner":
            results.append(
                BulkInviteResultItem(
                    email=item.email,
                    success=False,
                    error="Cannot invite as owner. Use transfer ownership instead.",
                )
            )
            failed += 1
            continue

        # Check duplicate within this batch
        if email_lower in batch_emails:
            results.append(
                BulkInviteResultItem(
                    email=item.email,
                    success=False,
                    error="Duplicate email in this batch",
                )
            )
            failed += 1
            continue

        # Check existing member
        if email_lower in existing_member_emails:
            results.append(
                BulkInviteResultItem(
                    email=item.email,
                    success=False,
                    error="This email is already a team member",
                )
            )
            failed += 1
            continue

        # Check pending invite
        if email_lower in pending_invite_emails:
            results.append(
                BulkInviteResultItem(
                    email=item.email,
                    success=False,
                    error="An invitation is already pending for this email",
                )
            )
            failed += 1
            continue

        # Create invite
        invite_id = f"inv_{uuid4().hex[:16]}"
        invite_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        try:
            role_value = TeamRole(item.role).value
        except ValueError:
            role_value = TeamRole.MEMBER.value

        await db.execute(
            text("""
                INSERT INTO organization_invites (
                    id, organization_id, email, role, invited_by,
                    token, status, expires_at
                )
                VALUES (
                    :id, :org_id, :email, :role, :invited_by,
                    :token, 'pending', :expires_at
                )
            """),
            {
                "id": invite_id,
                "org_id": org_id,
                "email": item.email,
                "role": role_value,
                "invited_by": inviter_id,
                "token": invite_token,
                "expires_at": expires_at,
            },
        )

        batch_emails.add(email_lower)
        pending_invite_emails.add(email_lower)

        # Queue invitation email as background task
        background_tasks.add_task(
            _send_team_invite_email,
            recipient_email=item.email,
            inviter_name=inviter_name,
            org_name=org_name,
            role=role_value,
            invite_token=invite_token,
            expires_at=expires_at,
        )

        results.append(
            BulkInviteResultItem(
                email=item.email,
                success=True,
                invite_id=invite_id,
            )
        )
        succeeded += 1

    await db.commit()

    return {
        "total": len(request.invitations),
        "succeeded": succeeded,
        "failed": failed,
        "results": [r.model_dump() for r in results],
    }
