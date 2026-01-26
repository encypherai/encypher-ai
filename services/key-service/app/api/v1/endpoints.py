"""
API endpoints for Key Service v1
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx

from ...db.session import get_db
from ...models.schemas import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyInfo,
    ApiKeyUpdate,
    ApiKeyVerify,
    ApiKeyVerifyResponse,
    KeyRotationRequest,
    KeyRotationResponse,
    MessageResponse,
    KeyUsageStats,
    RevokeKeysByUserRequest,
    RevokeKeysByUserResponse,
)
from ...services.key_service import KeyService
from ...core.config import settings

router = APIRouter()

ROLE_CAN_MANAGE_KEYS = {"owner", "admin", "manager"}


async def _emit_audit_log(
    authorization: str,
    organization_id: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    if not organization_id:
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/{organization_id}/audit-logs",
                headers={"Authorization": authorization},
                json={
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": details,
                },
            )
    except httpx.RequestError:
        return


async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Verify user token with auth service and return user data.
    Expects response format: {"success": true, "data": {...user fields...}, "error": null}
    """
    try:
        # Call auth service to verify token
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify", headers={"Authorization": authorization})

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            payload = response.json()
            # Extract user data from standard response format
            if isinstance(payload, dict) and payload.get("success") and isinstance(payload.get("data"), dict):
                return payload["data"]
            # Fallback for legacy direct user payloads
            if isinstance(payload, dict) and "id" in payload:
                return payload
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from auth service",
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )


async def _fetch_org_role(authorization: str, org_id: str, user_id: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/{org_id}/members",
                headers={"Authorization": authorization},
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )

    if response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}:
        raise HTTPException(status_code=response.status_code, detail="Access denied")
    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from auth service",
        )

    payload = response.json()
    members = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(members, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from auth service",
        )

    for member in members:
        if isinstance(member, dict) and member.get("user_id") == user_id:
            return member.get("role")

    return None


async def _require_org_key_permission(authorization: str, org_id: str, user_id: str) -> None:
    role = await _fetch_org_role(authorization, org_id, user_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if role not in ROLE_CAN_MANAGE_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to manage API keys",
        )


@router.post("/generate", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_key(
    key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
    request: Request = None,
):
    """
    Generate a new API key

    **Important:** The actual key is only returned once. Save it securely!

    - **name**: Descriptive name for the key
    - **description**: Optional description
    - **permissions**: List of permissions (sign, verify, read)
    - **expires_at**: Optional expiration date
    """
    try:
        organization_id = key_data.organization_id

        if organization_id and not current_user.get("is_super_admin"):
            await _require_org_key_permission(authorization, organization_id, current_user["id"])

        # If user is a superadmin, ensure the key has super_admin permission
        if current_user.get("is_super_admin"):
            if key_data.permissions is None:
                key_data.permissions = ["sign", "verify", "super_admin"]
            elif "super_admin" not in key_data.permissions:
                key_data.permissions = list(key_data.permissions) + ["super_admin"]

        db_key, api_key = KeyService.create_key(db, current_user["id"], key_data, organization_id=organization_id)

        if request is not None:
            request.state.organization_id = organization_id
            request.state.user_id = current_user["id"]
            request.state.api_key_id = db_key.id

        response = ApiKeyResponse(
            id=db_key.id,
            name=db_key.name,
            key=api_key,  # Only time the actual key is returned!
            fingerprint=db_key.fingerprint,
            permissions=db_key.permissions,
            created_at=db_key.created_at,
            organization_id=db_key.organization_id,
            user_id=db_key.user_id,
            created_by=db_key.created_by,
        )
        await _emit_audit_log(
            authorization,
            organization_id,
            "api_key.created",
            resource_type="api_key",
            resource_id=db_key.id,
            details={"key_name": db_key.name},
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate key: {str(e)}",
        )


@router.get("", response_model=List[ApiKeyInfo])
async def list_keys(
    include_revoked: bool = False,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """
    List all API keys for the current user

    - **include_revoked**: Include revoked keys in the list
    """
    if organization_id:
        if not current_user.get("is_super_admin"):
            await _require_org_key_permission(authorization, organization_id, current_user["id"])
        keys = KeyService.get_org_keys(db, organization_id, include_revoked)
        return keys

    return KeyService.get_user_keys(db, current_user["id"], include_revoked)


@router.get("/{key_id}", response_model=ApiKeyInfo)
async def get_key(
    key_id: str,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Get details of a specific API key

    - **key_id**: ID of the key to retrieve
    """
    if organization_id and not current_user.get("is_super_admin"):
        await _require_org_key_permission(authorization, organization_id, current_user["id"])

    db_key = KeyService.get_key_by_id(db, key_id, user_id=current_user["id"], organization_id=organization_id)

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return db_key


@router.put("/{key_id}", response_model=ApiKeyInfo)
async def update_key(
    key_id: str,
    update_data: ApiKeyUpdate,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Update an API key

    - **key_id**: ID of the key to update
    - **name**: New name (optional)
    - **description**: New description (optional)
    - **permissions**: New permissions (optional)
    """
    if organization_id and not current_user.get("is_super_admin"):
        await _require_org_key_permission(authorization, organization_id, current_user["id"])

    db_key = KeyService.update_key(db, key_id, current_user["id"], update_data, organization_id=organization_id)

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return db_key


@router.delete("/{key_id}", response_model=MessageResponse)
async def revoke_key(
    key_id: str,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Revoke an API key

    **Warning:** This action cannot be undone!

    - **key_id**: ID of the key to revoke
    """
    if organization_id and not current_user.get("is_super_admin"):
        await _require_org_key_permission(authorization, organization_id, current_user["id"])

    success = KeyService.revoke_key(db, key_id, current_user["id"], organization_id=organization_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await _emit_audit_log(
        authorization,
        organization_id,
        "api_key.revoked",
        resource_type="api_key",
        resource_id=key_id,
    )

    return {"message": "API key revoked successfully"}


@router.post("/{key_id}/rotate", response_model=KeyRotationResponse)
async def rotate_key(
    key_id: str,
    rotation_data: KeyRotationRequest,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Rotate an API key

    Creates a new key with the same properties and revokes the old one.

    **Important:** The new key is only returned once. Save it securely!

    - **key_id**: ID of the key to rotate
    - **reason**: Optional reason for rotation
    """
    if organization_id and not current_user.get("is_super_admin"):
        await _require_org_key_permission(authorization, organization_id, current_user["id"])

    result = KeyService.rotate_key(db, key_id, current_user["id"], rotation_data.reason, organization_id=organization_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    new_db_key, new_api_key = result

    response = KeyRotationResponse(
        old_key_id=key_id,
        new_key=ApiKeyResponse(
            id=new_db_key.id,
            name=new_db_key.name,
            key=new_api_key,
            fingerprint=new_db_key.fingerprint,
            permissions=new_db_key.permissions,
            created_at=new_db_key.created_at,
            organization_id=new_db_key.organization_id,
            user_id=new_db_key.user_id,
            created_by=new_db_key.created_by,
        ),
        message="Key rotated successfully. Old key has been revoked.",
    )

    await _emit_audit_log(
        authorization,
        organization_id,
        "api_key.rotated",
        resource_type="api_key",
        resource_id=key_id,
        details={"new_key_id": new_db_key.id, "reason": rotation_data.reason},
    )

    return response


@router.post("/revoke-by-user", response_model=RevokeKeysByUserResponse)
async def revoke_keys_by_user(
    payload: RevokeKeysByUserRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """Revoke all API keys created by a specific user within an organization"""
    if not current_user.get("is_super_admin"):
        await _require_org_key_permission(authorization, payload.organization_id, current_user["id"])

    revoked_count = KeyService.revoke_keys_by_user(
        db,
        organization_id=payload.organization_id,
        target_user_id=payload.user_id,
        actor_user_id=current_user["id"],
    )

    await _emit_audit_log(
        authorization,
        payload.organization_id,
        "api_key.bulk_revoked",
        resource_type="api_key",
        details={"target_user_id": payload.user_id, "revoked_count": revoked_count},
    )

    return {"revoked_count": revoked_count}


@router.post("/verify", response_model=ApiKeyVerifyResponse)
async def verify_key(
    verify_data: ApiKeyVerify,
    db: Session = Depends(get_db),
):
    """
    Verify an API key

    **Public endpoint** - Used by other services to validate API keys

    - **key**: The API key to verify
    """
    db_key = KeyService.verify_key(db, verify_data.key)

    if not db_key:
        return ApiKeyVerifyResponse(
            valid=False,
            message="Invalid or expired API key",
        )

    return ApiKeyVerifyResponse(
        valid=True,
        key_id=db_key.id,
        user_id=db_key.user_id,
        permissions=db_key.permissions,
        message="API key is valid",
    )


@router.post("/validate")
async def validate_key_with_org(
    verify_data: ApiKeyVerify,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Validate an API key and return full organization context.

    **Public endpoint** - The unified auth method for all services.
    Returns organization details, tier, and feature flags.

    - **key**: The API key to validate

    Returns:
        - organization_id, organization_name
        - tier (starter, professional, business, enterprise)
        - features (dict of enabled features)
        - permissions (list of key permissions)
        - usage limits
    """
    org_context = KeyService.verify_key_with_org(db, verify_data.key)

    if not org_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )

    if request is not None:
        request.state.organization_id = org_context.get("organization_id")
        request.state.user_id = org_context.get("user_id")
        request.state.api_key_id = org_context.get("key_id")

    return {
        "success": True,
        "data": org_context,
    }


@router.get("/{key_id}/usage", response_model=KeyUsageStats)
async def get_key_usage(
    key_id: str,
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Get usage statistics for an API key

    - **key_id**: ID of the key
    """
    if organization_id and not current_user.get("is_super_admin"):
        await _require_org_key_permission(authorization, organization_id, current_user["id"])

    stats = KeyService.get_key_usage_stats(db, key_id, current_user["id"], organization_id=organization_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return KeyUsageStats(**stats, requests_by_day={})


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "key-service"}
