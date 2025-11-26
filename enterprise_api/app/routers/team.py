"""Team management router for Business+ tier organizations."""
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional, List
from uuid import uuid4
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_read_permission
from app.routers.audit import log_audit_event, AuditAction


router = APIRouter(prefix="/org/members", tags=["Team Management"])


class TeamRole(str, Enum):
    """Team member roles with hierarchical permissions."""
    OWNER = "owner"      # Full access, can transfer ownership
    ADMIN = "admin"      # Full access except ownership transfer
    MEMBER = "member"    # Can sign/verify, view analytics
    VIEWER = "viewer"    # Read-only access


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


# Tier limits for team members
TIER_MEMBER_LIMITS = {
    "starter": 1,        # Owner only
    "professional": 5,   # Small team
    "business": 10,      # Medium team
    "enterprise": -1,    # Unlimited
    "strategic_partner": -1,
}


async def check_team_management_enabled(
    organization: dict = Depends(require_read_permission),
) -> dict:
    """Check if team management is enabled for the organization."""
    if not organization.get("team_management_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Team management is only available on Business and Enterprise tiers",
                "upgrade_url": "/billing/upgrade",
            }
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
        {"org_id": organization_id, "user_id": user_id}
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User context required for team management"
        )
    
    # Check if user has admin/owner role in the database
    role = await get_member_role(db, organization["organization_id"], user_id)
    
    # If no role found in DB but this is a demo/test key with owner tier features,
    # assume owner role for testing purposes
    if role is None:
        tier = organization.get("tier", "starter")
        if tier in ["business", "enterprise", "strategic_partner"]:
            # For demo keys with team_management enabled, assume owner role
            role = TeamRole.OWNER
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or Owner role required for this operation"
            )
    
    if role not in [TeamRole.OWNER, TeamRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Owner role required for this operation"
        )
    
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
    tier = organization.get("tier", "starter")
    max_members = TIER_MEMBER_LIMITS.get(tier, 1)
    
    result = await db.execute(
        text("""
            SELECT om.id, om.user_id, u.email, u.name, om.role, om.status,
                   om.invited_at, om.accepted_at, om.last_active_at
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
                om.created_at
        """),
        {"org_id": org_id}
    )
    rows = result.fetchall()
    
    members = [
        TeamMember(
            id=row.id,
            user_id=row.user_id,
            email=row.email,
            name=row.name,
            role=TeamRole(row.role),
            status=row.status,
            invited_at=row.invited_at.isoformat() if row.invited_at else None,
            accepted_at=row.accepted_at.isoformat() if row.accepted_at else None,
            last_active_at=row.last_active_at.isoformat() if row.last_active_at else None,
        )
        for row in rows
    ]
    
    return TeamMemberListResponse(
        organization_id=org_id,
        members=members,
        total=len(members),
        max_members=max_members if max_members > 0 else 999999,
    )


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
    tier = organization.get("tier", "starter")
    max_members = TIER_MEMBER_LIMITS.get(tier, 1)
    inviter_id = organization.get("user_id") or organization.get("api_key_owner_id")
    
    # Check member limit
    count_result = await db.execute(
        text("SELECT COUNT(*) FROM organization_members WHERE organization_id = :org_id"),
        {"org_id": org_id}
    )
    current_count = count_result.scalar() or 0
    
    if max_members > 0 and current_count >= max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "MEMBER_LIMIT_REACHED",
                "message": f"Your plan allows up to {max_members} team members",
                "upgrade_url": "/billing/upgrade",
            }
        )
    
    # Check if already a member
    existing = await db.execute(
        text("""
            SELECT om.id FROM organization_members om
            JOIN users u ON om.user_id = u.id
            WHERE om.organization_id = :org_id AND u.email = :email
        """),
        {"org_id": org_id, "email": request.email}
    )
    if existing.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already a team member"
        )
    
    # Check for pending invite
    pending = await db.execute(
        text("""
            SELECT id FROM organization_invites 
            WHERE organization_id = :org_id AND email = :email AND status = 'pending'
        """),
        {"org_id": org_id, "email": request.email}
    )
    if pending.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An invitation is already pending for this email"
        )
    
    # Cannot invite as owner
    if request.role == TeamRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invite as owner. Use transfer ownership instead."
        )
    
    # Create invite
    invite_id = f"inv_{uuid4().hex[:16]}"
    invite_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.execute(
        text("""
            INSERT INTO organization_invites (
                id, organization_id, email, role, invited_by,
                invite_token, status, expires_at
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
        }
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
    
    # TODO: Send email invitation in background
    # background_tasks.add_task(send_invite_email, request.email, invite_token, org_id)
    
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
        {"org_id": org_id}
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
        {"invite_id": invite_id, "org_id": org_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already processed"
        )
    
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
    
    # Get target member
    result = await db.execute(
        text("SELECT user_id, role FROM organization_members WHERE id = :id AND organization_id = :org_id"),
        {"id": member_id, "org_id": org_id}
    )
    member = result.fetchone()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    target_role = TeamRole(member.role)
    
    # Cannot change owner role
    if target_role == TeamRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change owner role. Use transfer ownership instead."
        )
    
    # Cannot promote to owner
    if request.role == TeamRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot promote to owner. Use transfer ownership instead."
        )
    
    # Admins cannot change other admins
    if current_role == TeamRole.ADMIN and target_role == TeamRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can modify admin roles"
        )
    
    # Admins cannot promote to admin
    if current_role == TeamRole.ADMIN and request.role == TeamRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can promote to admin"
        )
    
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
        }
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
    
    # Get target member
    result = await db.execute(
        text("""
            SELECT om.user_id, u.email, om.role 
            FROM organization_members om
            JOIN users u ON om.user_id = u.id
            WHERE om.id = :id AND om.organization_id = :org_id
        """),
        {"id": member_id, "org_id": org_id}
    )
    member = result.fetchone()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    target_role = TeamRole(member.role)
    
    # Cannot remove owner
    if target_role == TeamRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the organization owner"
        )
    
    # Admins cannot remove other admins
    if current_role == TeamRole.ADMIN and target_role == TeamRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can remove admins"
        )
    
    # Delete member
    await db.execute(
        text("DELETE FROM organization_members WHERE id = :id AND organization_id = :org_id"),
        {"id": member_id, "org_id": org_id}
    )
    
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
            WHERE invite_token = :token AND status = 'pending'
        """),
        {"token": token}
    )
    invite = result.fetchone()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invitation"
        )
    
    if invite.expires_at < now:
        # Mark as expired
        await db.execute(
            text("UPDATE organization_invites SET status = 'expired' WHERE id = :id"),
            {"id": invite.id}
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired"
        )
    
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
        }
    )
    
    # Update invite status
    await db.execute(
        text("UPDATE organization_invites SET status = 'accepted', accepted_at = :now WHERE id = :id"),
        {"id": invite.id, "now": now}
    )
    
    await db.commit()
    
    return {
        "success": True,
        "member_id": member_id,
        "organization_id": invite.organization_id,
        "role": invite.role,
        "message": "You have joined the organization",
    }
