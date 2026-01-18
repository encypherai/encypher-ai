"""
Licensing API Key Authentication Middleware.

Provides authentication for AI companies using API keys.
"""

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.licensing import AICompany
from app.services.licensing_service import LicensingService
from app.utils.api_key import is_valid_api_key_format

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def verify_licensing_api_key(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)) -> AICompany:
    """
    Verify AI company API key and return the company.

    This dependency can be used in routes that require AI company authentication.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        AICompany object if authentication succeeds

    Raises:
        HTTPException: If authentication fails

    Usage:
        @app.get("/api/v1/licensing/content")
        async def get_content(
            ai_company: AICompany = Depends(verify_licensing_api_key)
        ):
            ...
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing API key", headers={"WWW-Authenticate": "Bearer"})

    api_key = credentials.credentials

    # Validate API key format
    if not is_valid_api_key_format(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key format", headers={"WWW-Authenticate": "Bearer"})

    # Verify API key
    ai_company = await LicensingService.verify_ai_company_access(db, api_key)

    if not ai_company:
        raise HTTPException(status_code=401, detail="Invalid or expired API key", headers={"WWW-Authenticate": "Bearer"})

    return ai_company


async def get_optional_licensing_api_key(
    credentials: HTTPAuthorizationCredentials = Security(optional_security), db: AsyncSession = Depends(get_db)
) -> AICompany | None:
    """
    Optional AI company API key verification.

    Returns AICompany if valid credentials provided, None otherwise.
    Does not raise exceptions.

    Usage:
        @app.get("/api/v1/licensing/content")
        async def get_content(
            ai_company: AICompany | None = Depends(get_optional_licensing_api_key)
        ):
            if ai_company:
                # Authenticated access
            else:
                # Public access
    """
    if not credentials or not credentials.credentials:
        return None

    api_key = credentials.credentials

    if not is_valid_api_key_format(api_key):
        return None

    return await LicensingService.verify_ai_company_access(db, api_key)
