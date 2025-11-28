"""
API endpoints for Key Service v1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
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
)
from ...services.key_service import KeyService
from ...core.config import settings

router = APIRouter()


async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Verify user token with auth service and return user data.
    Expects response format: {"success": true, "data": {...user fields...}, "error": null}
    """
    try:
        # Call auth service to verify token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )

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


@router.post("/generate", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_key(
    key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
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
        db_key, api_key = KeyService.create_key(db, current_user["id"], key_data)

        return ApiKeyResponse(
            id=db_key.id,
            name=db_key.name,
            key=api_key,  # Only time the actual key is returned!
            fingerprint=db_key.fingerprint,
            permissions=db_key.permissions,
            created_at=db_key.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate key: {str(e)}",
        )


@router.get("", response_model=List[ApiKeyInfo])
async def list_keys(
    include_revoked: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all API keys for the current user
    
    - **include_revoked**: Include revoked keys in the list
    """
    keys = KeyService.get_user_keys(db, current_user["id"], include_revoked)
    return keys


@router.get("/{key_id}", response_model=ApiKeyInfo)
async def get_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get details of a specific API key
    
    - **key_id**: ID of the key to retrieve
    """
    db_key = KeyService.get_key_by_id(db, key_id, current_user["id"])

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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update an API key
    
    - **key_id**: ID of the key to update
    - **name**: New name (optional)
    - **description**: New description (optional)
    - **permissions**: New permissions (optional)
    """
    db_key = KeyService.update_key(db, key_id, current_user["id"], update_data)

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return db_key


@router.delete("/{key_id}", response_model=MessageResponse)
async def revoke_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Revoke an API key
    
    **Warning:** This action cannot be undone!
    
    - **key_id**: ID of the key to revoke
    """
    success = KeyService.revoke_key(db, key_id, current_user["id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return {"message": "API key revoked successfully"}


@router.post("/{key_id}/rotate", response_model=KeyRotationResponse)
async def rotate_key(
    key_id: str,
    rotation_data: KeyRotationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Rotate an API key
    
    Creates a new key with the same properties and revokes the old one.
    
    **Important:** The new key is only returned once. Save it securely!
    
    - **key_id**: ID of the key to rotate
    - **reason**: Optional reason for rotation
    """
    result = KeyService.rotate_key(db, key_id, current_user["id"], rotation_data.reason)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    new_db_key, new_api_key = result

    return KeyRotationResponse(
        old_key_id=key_id,
        new_key=ApiKeyResponse(
            id=new_db_key.id,
            name=new_db_key.name,
            key=new_api_key,
            fingerprint=new_db_key.fingerprint,
            permissions=new_db_key.permissions,
            created_at=new_db_key.created_at,
        ),
        message="Key rotated successfully. Old key has been revoked.",
    )


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

    return {
        "success": True,
        "data": org_context,
    }


@router.get("/{key_id}/usage", response_model=KeyUsageStats)
async def get_key_usage(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get usage statistics for an API key
    
    - **key_id**: ID of the key
    """
    stats = KeyService.get_key_usage_stats(db, key_id, current_user["id"])

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
