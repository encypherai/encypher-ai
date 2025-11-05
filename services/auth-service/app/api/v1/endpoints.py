"""
API endpoints for Auth Service v1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from ...db.session import get_db
from ...models.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    MessageResponse,
)
from ...services.auth_service import AuthService
from ...utils.coalition_client import CoalitionClient
from ...core.config import settings

router = APIRouter()

# Initialize coalition client
coalition_client = CoalitionClient(settings.COALITION_SERVICE_URL)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user account

    - **email**: User's email address
    - **password**: User's password (min 8 characters)
    - **name**: User's full name (optional)
    - **tier**: User tier (free, pro, enterprise) - defaults to free
    """
    try:
        user = AuthService.create_user(db, user_data)

        # Auto-enroll in coalition if free tier
        if user.tier == "free":
            # Run coalition enrollment asynchronously (don't block on failure)
            try:
                await coalition_client.auto_enroll_member(
                    user_id=user.id,
                    tier=user.tier,
                )
            except Exception as e:
                # Log error but don't fail signup
                import structlog
                logger = structlog.get_logger()
                logger.warning(
                    "coalition_enrollment_failed_but_user_created",
                    user_id=user.id,
                    error=str(e),
                )

        return user
    except ValueError as e:
        # Idempotent fallback: if a ValueError occurred, try returning existing user by email
        existing = AuthService.get_user_by_email(db, user_data.email)
        if existing:
            return existing
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    db: Session = Depends(get_db),
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
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
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
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,  # Keep the same refresh token
        "token_type": "bearer",
    }


@router.post("/logout", response_model=MessageResponse)
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
        return {"message": "Successfully logged out"}

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
        return {"message": "Successfully logged out"}

    # Neither provided
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Must provide refresh_token in body or Authorization header",
    )


@router.post("/verify", response_model=UserResponse)
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
    
    return user


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}
