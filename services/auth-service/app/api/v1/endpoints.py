"""
API endpoints for Auth Service v1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
import httpx
from sqlalchemy.orm import Session
from typing import Optional

from ...db.session import get_db
from ...models.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    RefreshTokenRequest,
    OAuthExchangeRequest,
    EmailVerifyRequest,
    ResendVerificationRequest,
)
from ...services.auth_service import AuthService
from ...core.config import settings
from ...deps.rate_limit import rate_limiter

router = APIRouter()


# Standard Response Format used; returning UserResponse inside data
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("auth_signup", limit=5, window_sec=60)),
):
    """
    Create a new user account.
    Sends verification email to the user.

    - **email**: User's email address
    - **password**: User's password (min 8 characters)
    - **name**: User's full name (optional)
    """
    try:
        user = AuthService.create_user(db, user_data)
        
        # Send verification email for new users
        if not user.email_verified:
            token = AuthService.create_verification_token(db, user)
            AuthService.send_verification_email(user, token)

        # Wrap in standard response format
        return {
            "success": True,
            "data": {
                **UserResponse.model_validate(user).model_dump(),
                "verification_email_sent": not user.email_verified,
            },
            "error": None,
        }
    except ValueError as e:
        # Idempotent fallback: if a ValueError occurred, try returning existing user by email
        existing = AuthService.get_user_by_email(db, user_data.email)
        if existing:
            return {
                "success": True,
                "data": {
                    **UserResponse.model_validate(existing).model_dump(),
                    "verification_email_sent": False,
                },
                "error": None,
            }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Standard Response Format; includes tokens and user
@router.post("/login")
async def login(
    credentials: UserLogin,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("auth_login", limit=5, window_sec=60)),
):
    """
    Authenticate user and return access and refresh tokens
    
    - **email**: User's email address
    - **password**: User's password
    """
    user = AuthService.authenticate_user(db, credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox for the verification email.",
        )
    
    # Create tokens
    access_token, refresh_token = AuthService.create_tokens(user)
    
    # Store refresh token
    AuthService.store_refresh_token(
        db,
        user.id,
        refresh_token,
        user_agent=user_agent,
        ip_address=x_forwarded_for,
    )
    
    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        },
        "error": None,
    }


# ==========================================
# Email Verification Endpoints
# ==========================================

@router.post("/verify-email")
async def verify_email(
    request: EmailVerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Verify a user's email address using a verification token.
    
    - **token**: Verification token from email
    """
    user = AuthService.verify_email(db, request.token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    return {
        "success": True,
        "data": {
            "message": "Email verified successfully",
            "user": UserResponse.model_validate(user).model_dump(),
        },
        "error": None,
    }


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("auth_resend_verification", limit=3, window_sec=300)),
):
    """
    Resend verification email to a user.
    
    - **email**: User's email address
    """
    # Always return success to prevent email enumeration
    AuthService.resend_verification_email(db, request.email)
    
    return {
        "success": True,
        "data": {
            "message": "If an account exists with this email, a verification email has been sent.",
        },
        "error": None,
    }


# ==========================================
# Token Refresh Endpoint
# ==========================================

@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh an access token using a refresh token
    
    - **refresh_token**: Valid refresh token
    """
    result = AuthService.refresh_access_token(db, request.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    new_access_token, user = result
    
    return {
        "success": True,
        "data": {
            "access_token": new_access_token,
            "refresh_token": request.refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        },
        "error": None,
    }


@router.post("/oauth/exchange")
async def oauth_exchange(
    payload: OAuthExchangeRequest,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("auth_oauth_exchange", limit=10, window_sec=60)),
):
    """Exchange provider tokens for backend session tokens (Google/GitHub)."""
    provider = payload.provider.lower()

    async with httpx.AsyncClient(timeout=10.0) as client:
        if provider == "google":
            # Prefer id_token validation
            if payload.id_token:
                # Validate id_token with Google tokeninfo
                resp = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": payload.id_token},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=401, detail="Invalid Google id_token")
                data = resp.json()
                provider_id = data.get("sub")
                email = data.get("email")
                name = data.get("name")
            elif payload.access_token:
                # Fetch userinfo with access_token
                resp = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {payload.access_token}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=401, detail="Invalid Google access_token")
                info = resp.json()
                provider_id = str(info.get("id"))
                email = info.get("email")
                name = info.get("name")
            else:
                raise HTTPException(status_code=400, detail="Google requires id_token or access_token")
        elif provider == "github":
            if not payload.access_token:
                raise HTTPException(status_code=400, detail="GitHub requires access_token")
            # Get GitHub user
            resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {payload.access_token}", "Accept": "application/vnd.github+json"},
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid GitHub access_token")
            info = resp.json()
            provider_id = str(info.get("id"))
            name = info.get("name") or info.get("login")
            email = info.get("email")
            if not email:
                # Fallback to primary email
                emails = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {payload.access_token}", "Accept": "application/vnd.github+json"},
                )
                if emails.status_code == 200:
                    items = emails.json()
                    primary = next((e for e in items if e.get("primary")), None)
                    email = (primary or (items[0] if items else {})).get("email")
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")

    # Upsert user and issue tokens
    user = AuthService.upsert_oauth_user(
        db,
        provider=provider,
        provider_id=provider_id,
        email=email,
        name=name,
    )
    access_token, refresh_token = AuthService.create_tokens(user)
    AuthService.store_refresh_token(
        db,
        user.id,
        refresh_token,
        user_agent=user_agent,
        ip_address=x_forwarded_for,
    )
    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        },
        "error": None,
    }


@router.post("/logout")
async def logout(
    request: Optional[RefreshTokenRequest] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Logout user by revoking tokens.
    
    Provide either:
    - refresh_token in the request body, or
    - Authorization: Bearer <access_token> header
    """
    # Case 1: explicit refresh token in body
    if request and getattr(request, "refresh_token", None):
        success = AuthService.revoke_refresh_token(db, request.refresh_token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found",
            )
        return {"success": True, "data": {"message": "Successfully logged out"}, "error": None}

    # Case 2: Authorization header with access token – revoke all user's refresh tokens
    if authorization:
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = AuthService.verify_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        AuthService.revoke_all_refresh_tokens_for_user(db, payload["sub"])
        return {"success": True, "data": {"message": "Successfully logged out"}, "error": None}

    # Neither provided
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Must provide refresh_token in body or Authorization header",
    )


@router.post("/verify")
async def verify_token(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Verify an access token and return user information
    
    Used by other services to validate tokens
    
    - **Authorization**: Bearer token in header
    """
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    payload = AuthService.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = AuthService.get_user_by_id(db, payload["sub"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {"success": True, "data": UserResponse.model_validate(user).model_dump(), "error": None}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}
