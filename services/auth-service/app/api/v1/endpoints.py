"""
API endpoints for Auth Service v1
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
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
    PasswordResetRequest,
    PasswordResetConfirm,
    # TEAM_006: API Access Gating
    ApiAccessRequestCreate,
    ApiAccessStatusResponse,
    ApiAccessApproval,
    ApiAccessDenial,
    PendingAccessRequestList,
    TierUpdateRequest,
    TierUpdateResponse,
    UserStatusUpdateRequest,
    UserStatusUpdateResponse,
    RoleUpdateRequest,
    RoleUpdateResponse,
    # TEAM_164: Admin API Access Status Management
    ApiAccessStatusSetRequest,
    ApiAccessStatusSetResponse,
    # TEAM_191: Onboarding Checklist
    OnboardingStatusResponse,
    OnboardingCompleteStepRequest,
    # TEAM_191: Setup Wizard
    SetupWizardRequest,
    SetupStatusResponse,
)
from ...services.auth_service import AuthService
from ...services.api_access_service import ApiAccessService
from ...services.admin_service import AdminService
from ...services.onboarding_service import OnboardingService
from ...db.models import Organization
from ...deps.rate_limit import rate_limiter
from ...db.models import User
from pydantic import BaseModel, EmailStr

router = APIRouter()


class SuperAdminPromoteRequest(BaseModel):
    """Request to promote a user to super admin"""

    email: EmailStr


# TEAM_006: Super admin check helper
def verify_super_admin(db: Session, user_id: str) -> bool:
    """Check if a user is a super admin"""
    user = db.query(User).filter(User.id == user_id).first()
    return user is not None and user.is_super_admin


def require_super_admin(db: Session, user_id: str) -> None:
    """Raise 403 if user is not a super admin"""
    if not verify_super_admin(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )


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
        user, is_new = AuthService.create_user(db, user_data)

        # Handle existing user case
        if not is_new:
            # User already exists - return appropriate error
            if user.email_verified:
                # Verified user trying to sign up again
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists. Please sign in instead.",
                )
            else:
                # Unverified user - resend verification email
                token = AuthService.create_verification_token(db, user)
                AuthService.send_verification_email(user, token)
                return {
                    "success": True,
                    "data": {
                        **UserResponse.model_validate(user).model_dump(),
                        "verification_email_sent": True,
                        "message": "A verification email has been resent to your email address.",
                    },
                    "error": None,
                }

        # New user - send verification email
        token = AuthService.create_verification_token(db, user)
        AuthService.send_verification_email(user, token)

        # Wrap in standard response format
        return {
            "success": True,
            "data": {
                **UserResponse.model_validate(user).model_dump(),
                "verification_email_sent": True,
            },
            "error": None,
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request validation failed",
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
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Verify a user's email address using a verification token.
    Returns tokens for auto-login after successful verification.

    - **token**: Verification token from email
    """
    user = AuthService.verify_email(db, request.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    # Create tokens for auto-login after verification
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
            "message": "Email verified successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
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
# Password Reset Endpoints
# ==========================================


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter("auth_forgot_password", limit=3, window_sec=300)),
):
    """
    Request a password reset email.

    - **email**: User's email address

    Always returns success to prevent email enumeration.
    """
    AuthService.request_password_reset(db, request.email)

    return {
        "success": True,
        "data": {
            "message": "If an account exists with this email, a password reset email has been sent.",
        },
        "error": None,
    }


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Reset password using a reset token.

    - **token**: Password reset token from email
    - **new_password**: New password (min 8 characters)
    """
    user = AuthService.reset_password(db, request.token, request.new_password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {
        "success": True,
        "data": {
            "message": "Password reset successfully. You can now log in with your new password.",
        },
        "error": None,
    }


@router.get("/validate-reset-token")
async def validate_reset_token(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Validate a password reset token without using it.

    - **token**: Password reset token from email

    Returns 200 if valid, 400 if invalid or expired.
    """
    is_valid = AuthService.validate_password_reset_token(db, token)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {
        "success": True,
        "data": {
            "valid": True,
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
    user, is_new = AuthService.upsert_oauth_user(
        db,
        provider=provider,
        provider_id=provider_id,
        email=email,
        name=name,
    )

    # Send admin notification for new OAuth signups
    if is_new:
        AuthService.send_new_signup_notification(user, signup_method=provider)

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


# ============================================
# TEAM_006: API Access Gating Endpoints
# ============================================


@router.post("/request-api-access", response_model=None)
async def request_api_access(
    request: ApiAccessRequestCreate,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Request API access with a use case description.

    Users must be approved before they can generate API keys.
    This enables controlled rollout during preview/beta phases.

    - **use_case**: Description of how you plan to use the API (min 20 chars)
    """
    # Verify token and get user
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

    user_id = payload["sub"]

    try:
        service = ApiAccessService(db)
        result = await service.request_api_access(user_id=user_id, use_case=request.use_case)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request validation failed",
        )


@router.get("/api-access-status", response_model=None)
async def get_api_access_status(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Get current API access status for the authenticated user.

    Returns:
    - **status**: not_requested, pending, approved, or denied
    - **requested_at**: When access was requested
    - **decided_at**: When admin made a decision
    - **use_case**: The submitted use case
    - **denial_reason**: Reason if denied
    """
    # Verify token and get user
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

    user_id = payload["sub"]

    try:
        service = ApiAccessService(db)
        result = await service.get_api_access_status(user_id=user_id)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request validation failed",
        )


# ============================================
# Admin Endpoints for API Access Management
# ============================================


@router.get("/admin/is-super-admin", response_model=None)
async def check_is_super_admin(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Check if the current user is a super admin.

    Returns { is_super_admin: true/false }
    """
    # Verify token
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

    user_id = payload["sub"]
    is_admin = verify_super_admin(db, user_id)

    return {
        "success": True,
        "data": {
            "is_super_admin": is_admin,
        },
        "error": None,
    }


@router.get("/admin/pending-access-requests", response_model=None)
async def list_pending_access_requests(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    List all pending API access requests for admin review.

    **Super Admin only** - Requires super admin privileges

    Returns list of pending requests with user info and use cases.
    """
    # Verify token
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

    admin_user_id = payload["sub"]

    # TEAM_006: Require super admin access
    require_super_admin(db, admin_user_id)

    service = ApiAccessService(db)
    requests = await service.list_pending_requests()

    return {
        "success": True,
        "data": {
            "requests": [r.model_dump() for r in requests],
            "total": len(requests),
        },
        "error": None,
    }


@router.get("/admin/stats", response_model=None)
async def get_admin_stats(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """Return platform stats for the admin dashboard."""
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    stats = AdminService.get_platform_stats(db)
    return {
        "success": True,
        "data": stats,
        "error": None,
    }


@router.get("/admin/users", response_model=None)
async def list_admin_users(
    authorization: str = Header(...),
    search: Optional[str] = None,
    tier: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    """List users for the admin dashboard."""
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    result = AdminService.list_users(
        db=db,
        search=search,
        tier=tier,
        page=page,
        page_size=page_size,
    )
    return {
        "success": True,
        "data": result,
        "error": None,
    }


@router.get("/admin/organizations/search", response_model=None)
async def search_admin_organizations(
    authorization: str = Header(...),
    query: str = Query(..., min_length=1, description="Search by name, email, slug, or ID"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    db: Session = Depends(get_db),
):
    """Search organizations for admin typeahead."""
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    results = AdminService.search_organizations(db=db, query=query, limit=limit)
    return {
        "success": True,
        "data": results,
        "error": None,
    }


@router.post("/admin/users/update-tier", response_model=TierUpdateResponse)
async def update_admin_user_tier(
    request: TierUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """Update a user's tier (super admin only)."""
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    result = AdminService.update_user_tier(
        db=db,
        user_id=request.user_id,
        new_tier=request.new_tier.value,
        reason=request.reason,
        admin_id=admin_user_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))

    return TierUpdateResponse(success=True, data=result)


@router.post("/admin/users/update-status", response_model=UserStatusUpdateResponse)
async def update_admin_user_status(
    request: UserStatusUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """Suspend or activate a user (super admin only)."""
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    result = AdminService.update_user_status(
        db=db,
        user_id=request.user_id,
        status=request.status.value,
        reason=request.reason,
        admin_id=admin_user_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))

    return UserStatusUpdateResponse(success=True, data=result)


@router.post("/admin/users/update-role", response_model=RoleUpdateResponse)
async def update_admin_user_role(
    request: RoleUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """Update a user's role within their organization (super admin only)."""
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    result = AdminService.update_user_role(
        db=db,
        user_id=request.user_id,
        new_role=request.new_role,
        admin_id=admin_user_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))

    return RoleUpdateResponse(success=True, data=result)


@router.post("/admin/approve-api-access", response_model=None)
async def approve_api_access(
    request: ApiAccessApproval,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Approve a user's API access request.

    **Admin only** - Requires admin role (TODO: implement role check)

    - **user_id**: ID of the user to approve
    """
    # Verify token
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

    admin_user_id = payload["sub"]

    # TEAM_006: Require super admin access
    require_super_admin(db, admin_user_id)

    try:
        service = ApiAccessService(db)
        result = await service.approve_api_access(user_id=request.user_id, admin_user_id=admin_user_id)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request validation failed",
        )


@router.post("/admin/deny-api-access", response_model=None)
async def deny_api_access(
    request: ApiAccessDenial,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Deny a user's API access request.

    **Super Admin only** - Requires super admin privileges

    - **user_id**: ID of the user to deny
    - **reason**: Reason for denial (shown to user)
    """
    # Verify token
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

    admin_user_id = payload["sub"]

    # TEAM_006: Require super admin access
    require_super_admin(db, admin_user_id)

    try:
        service = ApiAccessService(db)
        result = await service.deny_api_access(user_id=request.user_id, admin_user_id=admin_user_id, reason=request.reason)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request validation failed",
        )


@router.get("/admin/check-api-access/{user_id}", response_model=None)
async def check_user_api_access(
    user_id: str,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Check if a specific user has approved API access.

    Used by key-service to gate API key generation.

    - **user_id**: ID of the user to check

    Returns:
    - **approved**: True if user can generate API keys
    """
    # Verify token
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

    service = ApiAccessService(db)
    is_approved = await service.is_api_access_approved(user_id=user_id)

    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "approved": is_approved,
        },
        "error": None,
    }


# TEAM_164: Admin endpoint to directly set a user's API access status
@router.post("/admin/set-api-access-status", response_model=ApiAccessStatusSetResponse)
async def set_api_access_status(
    request: ApiAccessStatusSetRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Directly set a user's API access status.

    **Super Admin only** - Allows setting any status: not_requested, pending, approved, denied, suspended.
    Suspended users are blocked from requesting API access and see a contact-support message.

    - **user_id**: ID of the user to update
    - **status**: New API access status (not_requested, pending, approved, denied, suspended)
    - **reason**: Optional reason for the change
    """
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

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    try:
        service = ApiAccessService(db)
        result = await service.set_api_access_status(
            user_id=request.user_id,
            new_status=request.status.value,
            admin_user_id=admin_user_id,
            reason=request.reason,
        )
        return ApiAccessStatusSetResponse(
            success=True,
            data={
                "user_id": request.user_id,
                "new_status": request.status.value,
                "message": result.message,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request validation failed",
        )


# ============================================
# SUPER ADMIN MANAGEMENT ENDPOINTS
# ============================================


@router.post("/admin/promote", response_model=None)
async def promote_to_super_admin(
    request: SuperAdminPromoteRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Promote a user to super admin.

    **Super Admin only** - Requires existing super admin privileges.
    """
    import structlog

    logger = structlog.get_logger(__name__)

    # Verify token
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

    admin_user_id = payload["sub"]

    # Require super admin access
    require_super_admin(db, admin_user_id)

    # Find target user by email
    target_user = db.query(User).filter(User.email == request.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {request.email} not found",
        )

    # Check if already super admin
    if target_user.is_super_admin:
        return {
            "success": True,
            "data": {
                "user_id": str(target_user.id),
                "email": target_user.email,
                "is_super_admin": True,
                "message": "User is already a super admin",
            },
            "error": None,
        }

    # Promote to super admin
    target_user.is_super_admin = True
    db.commit()

    logger.info(
        "promote_super_admin_success",
        admin_user_id=admin_user_id,
        target_user_id=str(target_user.id),
        target_email=request.email,
    )

    return {
        "success": True,
        "data": {
            "user_id": str(target_user.id),
            "email": target_user.email,
            "is_super_admin": True,
            "message": "User promoted to super admin",
        },
        "error": None,
    }


@router.post("/admin/demote", response_model=None)
async def demote_from_super_admin(
    request: SuperAdminPromoteRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Demote a user from super admin.

    **Super Admin only** - Requires existing super admin privileges.
    Cannot demote yourself.
    """
    import structlog

    logger = structlog.get_logger(__name__)

    # Verify token
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

    admin_user_id = payload["sub"]

    # Require super admin access
    require_super_admin(db, admin_user_id)

    # Find target user by email
    target_user = db.query(User).filter(User.email == request.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {request.email} not found",
        )

    # Cannot demote yourself
    if str(target_user.id) == admin_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself from super admin",
        )

    # Check if not a super admin
    if not target_user.is_super_admin:
        return {
            "success": True,
            "data": {
                "user_id": str(target_user.id),
                "email": target_user.email,
                "is_super_admin": False,
                "message": "User is not a super admin",
            },
            "error": None,
        }

    # Demote from super admin
    target_user.is_super_admin = False
    db.commit()

    logger.info(
        "demote_super_admin_success",
        admin_user_id=admin_user_id,
        target_user_id=str(target_user.id),
        target_email=request.email,
    )

    return {
        "success": True,
        "data": {
            "user_id": str(target_user.id),
            "email": target_user.email,
            "is_super_admin": False,
            "message": "User demoted from super admin",
        },
        "error": None,
    }


@router.get("/admin/list-super-admins", response_model=None)
async def list_super_admins(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    List all super admin users.

    **Super Admin only** - Requires existing super admin privileges.
    """
    # Verify token
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

    admin_user_id = payload["sub"]

    # Require super admin access
    require_super_admin(db, admin_user_id)

    # Get all super admins
    super_admins = db.query(User).filter(User.is_super_admin == True).all()

    return {
        "success": True,
        "data": {
            "super_admins": [
                {
                    "user_id": str(u.id),
                    "email": u.email,
                    "name": u.name,
                }
                for u in super_admins
            ],
            "total": len(super_admins),
        },
        "error": None,
    }


# ============================================
# TEAM_191: ONBOARDING CHECKLIST ENDPOINTS
# ============================================


@router.get("/onboarding-status", response_model=None)
async def get_onboarding_status(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Get the current onboarding checklist status for the authenticated user.
    """
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

    user_id = payload["sub"]

    try:
        service = OnboardingService(db)
        result = service.get_onboarding_status(user_id)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/onboarding/complete-step", response_model=None)
async def complete_onboarding_step(
    request: OnboardingCompleteStepRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Mark an onboarding step as complete for the authenticated user.
    """
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

    user_id = payload["sub"]

    try:
        service = OnboardingService(db)
        result = service.complete_step(user_id, request.step_id)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/onboarding/dismiss", response_model=None)
async def dismiss_onboarding(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Dismiss the onboarding checklist for the authenticated user.
    The checklist will no longer be shown.
    """
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

    user_id = payload["sub"]

    try:
        service = OnboardingService(db)
        result = service.dismiss_checklist(user_id)
        return {
            "success": True,
            "data": result.model_dump(),
            "error": None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================
# TEAM_191: MANDATORY SETUP WIZARD ENDPOINTS
# ============================================


@router.get("/setup-status", response_model=None)
async def get_setup_status(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Check if the authenticated user has completed the mandatory setup wizard.
    Dashboard should call this on load and block UI if setup_completed is false.
    """
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

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Look up org for account_type / display_name
    org = None
    if user.default_organization_id:
        org = db.query(Organization).filter(Organization.id == user.default_organization_id).first()

    return {
        "success": True,
        "data": {
            "setup_completed": user.setup_completed_at is not None,
            "setup_completed_at": user.setup_completed_at.isoformat() if user.setup_completed_at else None,
            "account_type": org.account_type if org else None,
            "display_name": org.display_name if org else None,
        },
        "error": None,
    }


@router.post("/setup/complete", response_model=None)
async def complete_setup(
    request: SetupWizardRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Complete the mandatory setup wizard.
    Sets the organization's account_type, display_name, and name,
    then marks the user's setup as complete.
    """
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

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.default_organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no organization",
        )

    org = db.query(Organization).filter(Organization.id == user.default_organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found",
        )

    from datetime import datetime as dt
    from datetime import timezone as tz

    # Update organization identity
    org.account_type = request.account_type.value
    org.display_name = request.display_name
    # Also set the org name if it's still blank (personal orgs start with name="")
    if not org.name:
        org.name = request.display_name

    # Mark user setup as complete
    user.setup_completed_at = dt.now(tz.utc)

    # Mark the onboarding step
    service = OnboardingService(db)
    service.complete_step(user_id, "publisher_identity_set")

    db.commit()

    return {
        "success": True,
        "data": {
            "setup_completed": True,
            "setup_completed_at": user.setup_completed_at.isoformat(),
            "account_type": org.account_type,
            "display_name": org.display_name,
        },
        "error": None,
    }
