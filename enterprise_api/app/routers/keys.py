"""
API Keys router for key management.

Provides endpoints for creating, listing, rotating, and revoking API keys.
"""

import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.services.provisioning_service import ProvisioningService

router = APIRouter(prefix="/keys", tags=["API Keys"])
logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class KeyPermission(BaseModel):
    """API key permission."""

    name: str
    description: Optional[str] = None


class KeySummary(BaseModel):
    """Summary of an API key (masked)."""

    id: str = Field(..., description="Key ID")
    name: Optional[str] = Field(None, description="Key name")
    prefix: str = Field(..., description="Key prefix (first 12 chars)")
    permissions: List[str] = Field(default_factory=list, description="Key permissions")
    created_at: str = Field(..., description="Creation timestamp")
    last_used_at: Optional[str] = Field(None, description="Last usage timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    is_active: bool = Field(True, description="Whether key is active")
    usage_count: int = Field(0, description="Total usage count")


class KeyCreateRequest(BaseModel):
    """Request to create a new API key."""

    name: Optional[str] = Field(None, description="Friendly name for the key", max_length=255)
    permissions: List[str] = Field(
        default=["sign", "verify"],
        description="Permissions: sign, verify, read, admin",
    )
    expires_in_days: Optional[int] = Field(
        None,
        description="Days until expiration (null for no expiration)",
        ge=1,
        le=365,
    )


class KeyCreateResponse(BaseModel):
    """Response after creating a key (includes full key - only shown once)."""

    success: bool = True
    data: dict
    warning: str = "Store this key securely. It will not be shown again."


class KeyListResponse(BaseModel):
    """Response for key listing."""

    success: bool = True
    data: dict


class KeyUpdateRequest(BaseModel):
    """Request to update a key."""

    name: Optional[str] = Field(None, description="New name for the key")
    permissions: Optional[List[str]] = Field(None, description="New permissions")


class KeyUpdateResponse(BaseModel):
    """Response after updating a key."""

    success: bool = True
    data: dict


class KeyRevokeResponse(BaseModel):
    """Response after revoking a key."""

    success: bool = True
    data: dict


class KeyRotateResponse(BaseModel):
    """Response after rotating a key (includes new key)."""

    success: bool = True
    data: dict
    warning: str = "Store this key securely. It will not be shown again."


# =============================================================================
# Helper Functions
# =============================================================================


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key.

    Returns:
        Tuple of (full_key, key_hash)
    """
    # Generate 32 random bytes = 256 bits of entropy
    random_bytes = secrets.token_bytes(32)
    key_suffix = secrets.token_urlsafe(32)

    # Create key with prefix for easy identification
    full_key = f"ek_live_{key_suffix}"

    # Hash for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    return full_key, key_hash


def get_key_prefix(full_key: str) -> str:
    """Get the prefix of a key for display."""
    return full_key[:12] + "..."


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=KeyListResponse)
async def list_keys(
    include_revoked: bool = Query(False, description="Include revoked keys"),
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> KeyListResponse:
    """
    List API keys for the organization.

    Keys are masked - only the prefix is shown for security.
    """
    org_id = organization.get("organization_id")

    # Handle user-level keys
    if org_id and org_id.startswith("user_"):
        return KeyListResponse(
            data={
                "keys": [],
                "total": 0,
                "message": "User-level keys cannot manage other keys",
            }
        )

    where_clause = "organization_id = :org_id"
    if not include_revoked:
        where_clause += " AND revoked_at IS NULL"

    result = await db.execute(
        text(f"""
            SELECT 
                id, name, key_prefix, scopes,
                created_at, last_used_at, expires_at,
                is_active, revoked_at
            FROM api_keys
            WHERE {where_clause}
            ORDER BY created_at DESC
        """),
        {"org_id": org_id},
    )
    rows = result.fetchall()

    keys = []
    for row in rows:
        # scopes is JSONB, parse it
        scopes = row.scopes if row.scopes else ["sign", "verify"]
        if isinstance(scopes, str):
            import json

            scopes = json.loads(scopes)
        keys.append(
            KeySummary(
                id=row.id,
                name=row.name,
                prefix=row.key_prefix or "ek_...",
                permissions=scopes,
                created_at=row.created_at.isoformat() if row.created_at else "",
                last_used_at=row.last_used_at.isoformat() if row.last_used_at else None,
                expires_at=row.expires_at.isoformat() if row.expires_at else None,
                is_active=row.is_active and row.revoked_at is None,
                usage_count=0,
            ).model_dump()
        )

    return KeyListResponse(
        data={
            "keys": keys,
            "total": len(keys),
        }
    )


@router.post("", response_model=KeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
    request: KeyCreateRequest,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> KeyCreateResponse:
    """
    Create a new API key.

    The full key is only returned once - store it securely.
    """
    org_id = organization.get("organization_id")

    # Check if user-level key
    if org_id and org_id.startswith("user_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User-level keys cannot create organization keys",
        )

    # Auto-provision certificate if needed (before creating key)
    org_name = organization.get("organization_name", org_id)
    await ProvisioningService._ensure_organization_certificate(
        db=db,
        organization_id=org_id,
        organization_name=org_name,
        authorization=None,  # No auth header in this context
    )

    # Check key limit based on tier
    tier = organization.get("tier", "starter")
    tier_limits = {
        "starter": 2,
        "professional": 10,
        "business": 50,
        "enterprise": -1,
        "strategic_partner": -1,
    }
    limit = tier_limits.get(tier, 2)

    if limit != -1:
        count_result = await db.execute(
            text("SELECT COUNT(*) FROM api_keys WHERE organization_id = :org_id AND revoked_at IS NULL"),
            {"org_id": org_id},
        )
        current_count = count_result.scalar() or 0

        if current_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "KEY_LIMIT_REACHED",
                    "message": f"API key limit ({limit}) reached for {tier} tier",
                    "upgrade_url": "/billing/upgrade",
                },
            )

    # Generate key
    full_key, key_hash = generate_api_key()
    key_prefix = full_key[:12]
    key_id = f"key_{secrets.token_hex(8)}"

    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)

    # Validate permissions
    valid_permissions = {"sign", "verify", "read", "admin", "merkle"}
    permissions = [p for p in request.permissions if p in valid_permissions]
    if not permissions:
        permissions = ["sign", "verify"]

    # Insert key - use scopes column (JSONB)
    await db.execute(
        text("""
            INSERT INTO api_keys (
                id, organization_id, name, key_hash, key_prefix,
                scopes, created_at, expires_at, is_active
            ) VALUES (
                :id, :org_id, :name, :key_hash, :key_prefix,
                CAST(:scopes AS jsonb), :created_at, :expires_at, true
            )
        """),
        {
            "id": key_id,
            "org_id": org_id,
            "name": request.name or "API Key",
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "scopes": json.dumps(permissions),
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at,
        },
    )
    await db.commit()

    logger.info(f"Created API key {key_id} for organization {org_id}")

    return KeyCreateResponse(
        data={
            "id": key_id,
            "name": request.name,
            "key": full_key,
            "prefix": key_prefix,
            "permissions": permissions,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
    )


@router.patch("/{key_id}", response_model=KeyUpdateResponse)
async def update_key(
    key_id: str,
    request: KeyUpdateRequest,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> KeyUpdateResponse:
    """
    Update an API key's name or permissions.
    """
    org_id = organization.get("organization_id")

    # Verify key exists and belongs to org
    result = await db.execute(
        text("SELECT id, name, scopes FROM api_keys WHERE id = :key_id AND organization_id = :org_id"),
        {"key_id": key_id, "org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "KEY_NOT_FOUND", "message": "API key not found"},
        )

    # Build update
    updates = []
    params = {"key_id": key_id, "org_id": org_id}

    if request.name is not None:
        updates.append("name = :name")
        params["name"] = request.name

    if request.permissions is not None:
        valid_permissions = {"sign", "verify", "read", "admin", "merkle"}
        permissions = [p for p in request.permissions if p in valid_permissions]
        updates.append("scopes = CAST(:scopes AS jsonb)")
        params["scopes"] = json.dumps(permissions)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )

    updates.append("updated_at = :updated_at")
    params["updated_at"] = datetime.now(timezone.utc)

    await db.execute(
        text(f"UPDATE api_keys SET {', '.join(updates)} WHERE id = :key_id AND organization_id = :org_id"),
        params,
    )
    await db.commit()

    return KeyUpdateResponse(
        data={
            "id": key_id,
            "updated": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.delete("/{key_id}", response_model=KeyRevokeResponse)
async def revoke_key(
    key_id: str,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> KeyRevokeResponse:
    """
    Revoke an API key.

    The key will immediately stop working. This action cannot be undone.
    """
    org_id = organization.get("organization_id")

    # Verify key exists
    result = await db.execute(
        text("SELECT id, revoked_at FROM api_keys WHERE id = :key_id AND organization_id = :org_id"),
        {"key_id": key_id, "org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "KEY_NOT_FOUND", "message": "API key not found"},
        )

    if row.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "KEY_ALREADY_REVOKED", "message": "Key is already revoked"},
        )

    # Revoke
    await db.execute(
        text("""
            UPDATE api_keys 
            SET is_active = false, revoked_at = :revoked_at
            WHERE id = :key_id AND organization_id = :org_id
        """),
        {"key_id": key_id, "org_id": org_id, "revoked_at": datetime.now(timezone.utc)},
    )
    await db.commit()

    logger.info(f"Revoked API key {key_id} for organization {org_id}")

    return KeyRevokeResponse(
        data={
            "id": key_id,
            "revoked": True,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.post("/{key_id}/rotate", response_model=KeyRotateResponse)
async def rotate_key(
    key_id: str,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> KeyRotateResponse:
    """
    Rotate an API key.

    Creates a new key with the same permissions and revokes the old one.
    The new key is only returned once - store it securely.
    """
    org_id = organization.get("organization_id")

    # Get existing key
    result = await db.execute(
        text("""
            SELECT id, name, scopes, expires_at, revoked_at
            FROM api_keys 
            WHERE id = :key_id AND organization_id = :org_id
        """),
        {"key_id": key_id, "org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "KEY_NOT_FOUND", "message": "API key not found"},
        )

    if row.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "KEY_ALREADY_REVOKED", "message": "Cannot rotate a revoked key"},
        )

    # Generate new key
    full_key, key_hash = generate_api_key()
    key_prefix = full_key[:12]
    new_key_id = f"key_{secrets.token_hex(8)}"

    # Parse scopes from JSONB
    scopes = row.scopes if row.scopes else ["sign", "verify"]
    if isinstance(scopes, str):
        scopes = json.loads(scopes)
    now = datetime.now(timezone.utc)

    # Create new key
    await db.execute(
        text("""
            INSERT INTO api_keys (
                id, organization_id, name, key_hash, key_prefix,
                scopes, created_at, expires_at, is_active
            ) VALUES (
                :id, :org_id, :name, :key_hash, :key_prefix,
                CAST(:scopes AS jsonb), :created_at, :expires_at, true
            )
        """),
        {
            "id": new_key_id,
            "org_id": org_id,
            "name": f"{row.name} (rotated)" if row.name else "Rotated Key",
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "scopes": json.dumps(scopes),
            "created_at": now,
            "expires_at": row.expires_at,
        },
    )

    # Revoke old key
    await db.execute(
        text("""
            UPDATE api_keys 
            SET is_active = false, revoked_at = :revoked_at
            WHERE id = :key_id AND organization_id = :org_id
        """),
        {"key_id": key_id, "org_id": org_id, "revoked_at": now},
    )

    await db.commit()

    logger.info(f"Rotated API key {key_id} -> {new_key_id} for organization {org_id}")

    return KeyRotateResponse(
        data={
            "old_key_id": key_id,
            "new_key_id": new_key_id,
            "key": full_key,
            "prefix": key_prefix,
            "permissions": scopes,
            "created_at": now.isoformat(),
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        }
    )
