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
    # TEAM_006: API Access Gating
    ApiAccessRequestCreate,
    ApiAccessStatusResponse,
    ApiAccessApproval,
    ApiAccessDenial,
    PendingAccessRequestList,
)
from ...services.auth_service import AuthService
from ...services.api_access_service import ApiAccessService
from ...deps.rate_limit import rate_limiter
from ...db.models import User

router = APIRouter()


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
            detail=str(e),
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
            detail=str(e),
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
            detail=str(e),
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
            detail=str(e),
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
