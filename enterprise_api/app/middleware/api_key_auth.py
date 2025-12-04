"""
API Key Authentication Middleware for HTTP Endpoints.

Provides authentication for enterprise API endpoints using API keys.
"""
import logging
from datetime import datetime
from typing import Dict, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)


async def get_api_key_from_header(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Extract API key from Authorization header.
    
    Supports formats:
    - Bearer <api_key>
    - <api_key>
    
    Args:
        authorization: Authorization header value
    
    Returns:
        API key or None
    """
    if not authorization:
        return None
    
    # Handle "Bearer <token>" format
    if authorization.startswith("Bearer "):
        return authorization[7:]
    
    # Handle raw API key
    return authorization


async def authenticate_api_key(
    api_key: Optional[str] = Depends(get_api_key_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Authenticate API key and return organization details.
    
    Args:
        api_key: API key from header
        db: Database session
    
    Returns:
        Organization details dictionary
    
    Raises:
        HTTPException: If authentication fails
    """
    if not api_key:
        logger.warning("API request attempted without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Demo key bypass for local testing
    if settings.demo_api_key and api_key == settings.demo_api_key:
        logger.info("Request authenticated with demo key")
        return {
            "api_key": api_key,
            "organization_id": settings.demo_organization_id,
            "organization_name": settings.demo_organization_name,
            "organization_type": "demo",
            "tier": "demo",
            "can_sign": True,
            "can_verify": True,
            "can_lookup": True,
            "monthly_quota": 10_000,
            "api_calls_this_month": 0,
            "is_demo": True,
            "private_key_encrypted": settings.demo_private_key_bytes or b""
        }
    
    # Query database for API key
    try:
        result = await db.execute(
            text(
                """
                SELECT
                    ak.api_key, ak.organization_id, ak.revoked, ak.expires_at,
                    ak.can_sign, ak.can_verify, ak.can_lookup,
                    o.organization_name, o.organization_type, o.tier,
                    o.monthly_quota, o.api_calls_this_month, o.private_key_encrypted
                FROM api_keys ak
                JOIN organizations o ON ak.organization_id = o.organization_id
                WHERE ak.api_key = :api_key
                """
            ),
            {"api_key": api_key},
        )
        row = result.fetchone()
        
        if not row:
            logger.warning("Authentication failed: Invalid API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if revoked
        if row.revoked:
            logger.warning(f"Authentication failed: Revoked API key for org {row.organization_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has been revoked",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if expired
        if row.expires_at and row.expires_at < datetime.utcnow():
            logger.warning(f"Authentication failed: Expired API key for org {row.organization_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check quota (if not on unlimited plan)
        if row.tier != "enterprise" and row.api_calls_this_month >= row.monthly_quota:
            logger.warning(f"Authentication failed: Quota exceeded for org {row.organization_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Monthly API quota exceeded. Please upgrade your plan or wait until next month."
            )
        
        # Update last_used_at timestamp and increment API call count
        await db.execute(
            text(
                """
                UPDATE api_keys SET last_used_at = :last_used_at WHERE api_key = :api_key;
                UPDATE organizations SET api_calls_this_month = api_calls_this_month + 1 
                WHERE organization_id = :organization_id;
                """
            ),
            {
                "api_key": api_key,
                "last_used_at": datetime.utcnow(),
                "organization_id": row.organization_id
            },
        )
        await db.commit()
        
        logger.info(f"Request authenticated for org {row.organization_id}")
        
        # Return organization details
        return {
            "api_key": row.api_key,
            "organization_id": row.organization_id,
            "organization_name": row.organization_name,
            "organization_type": row.organization_type,
            "tier": row.tier,
            "can_sign": row.can_sign,
            "can_verify": row.can_verify,
            "can_lookup": row.can_lookup,
            "monthly_quota": row.monthly_quota,
            "api_calls_this_month": row.api_calls_this_month + 1,  # Include current call
            "is_demo": False,
            "private_key_encrypted": row.private_key_encrypted
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )


async def require_embedding_permission(
    organization: Dict = Depends(authenticate_api_key)
) -> Dict:
    """
    Verify organization has permission to create embeddings.
    
    Args:
        organization: Organization details from authentication
    
    Returns:
        Organization details
    
    Raises:
        HTTPException: If organization lacks embedding permission
    """
    # Check tier - embeddings require Professional or Enterprise
    if organization["tier"] not in ("professional", "enterprise", "demo"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Embeddings require Professional or Enterprise tier. Please upgrade your plan."
        )
    
    # Check sign permission
    if not organization["can_sign"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have permission to sign content"
        )
    
    return organization


async def require_verification_permission(
    organization: Dict = Depends(authenticate_api_key)
) -> Dict:
    """
    Verify organization has permission to verify content.
    
    Args:
        organization: Organization details from authentication
    
    Returns:
        Organization details
    
    Raises:
        HTTPException: If organization lacks verification permission
    """
    # Check verify permission
    if not organization["can_verify"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have permission to verify content"
        )
    
    return organization


# Convenience dependency for endpoints that need any authenticated organization
get_current_organization = authenticate_api_key
