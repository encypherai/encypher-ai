"""
API endpoints for Auth Service v1
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
import httpx
from sqlalchemy import literal, select, update
from sqlalchemy.orm import Session
from typing import Literal, Optional

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
    TotpSetupConfirmRequest,
    TotpDisableRequest,
    MfaLoginCompleteRequest,
    PasskeyRegistrationCompleteRequest,
    PasskeyAuthenticationStartRequest,
    PasskeyAuthenticationCompleteRequest,
)
from ...services.auth_service import AuthService
from ...services.api_access_service import ApiAccessService
from ...services.admin_service import AdminService
from ...services.onboarding_service import OnboardingService
from ...services.auth_factors_service import AuthFactorsService
from ...services.turnstile_service import verify_turnstile_token
from ...core.config import settings
from ...core.security import create_typed_token, verify_token as verify_jwt_token, get_password_hash
from ...core.auth import extract_bearer_token as _extract_bearer_token
from ...core.responses import ok
from ...db.models import Organization, OrganizationMember
from ...deps.rate_limit import rate_limiter
from ...db.models import User
from pydantic import BaseModel, EmailStr

router = APIRouter()


class SuperAdminPromoteRequest(BaseModel):
    """Request to promote a user to super admin"""

    email: EmailStr


class SetDefaultOrganizationRequest(BaseModel):
    """Request to set a user's default organization"""

    user_id: str
    organization_id: str


class NewsletterSubscriberStatusUpdateRequest(BaseModel):
    status: Literal["active", "unsubscribed", "invalid"]
    reason: str | None = None


# TEAM_006: Super admin check helper
def verify_super_admin(db: Session, user_id: str) -> bool:
    """Check if a user is a super admin"""
    return AdminService.is_super_admin(db, user_id)


def require_super_admin(db: Session, user_id: str) -> None:
    """Raise 403 if user is not a super admin"""
    if not verify_super_admin(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )


# _extract_bearer_token is imported from core.auth as _extract_bearer_token


async def _enforce_turnstile_if_required(*, route: str, token: Optional[str], remote_ip: Optional[str]) -> None:
    if not settings.TURNSTILE_ENABLED:
        return

    required = (route == "signup" and settings.TURNSTILE_REQUIRE_SIGNUP) or (route == "login" and settings.TURNSTILE_REQUIRE_LOGIN)
    if not required:
        return

    is_valid = await verify_turnstile_token(token, remote_ip=remote_ip)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Turnstile validation failed",
        )


# Standard Response Format used; returning UserResponse inside data
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    x_forwarded_for: Optional[str] = Header(None),
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
    await _enforce_turnstile_if_required(
        route="signup",
        token=user_data.turnstile_token,
        remote_ip=x_forwarded_for,
    )

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
                return ok(
                    {
                        **UserResponse.model_validate(user).model_dump(),
                        "verification_email_sent": True,
                        "message": "A verification email has been resent to your email address.",
                    }
                )

        # New user - send verification email
        token = AuthService.create_verification_token(db, user)
        AuthService.send_verification_email(user, token)

        # Wrap in standard response format
        return ok(
            {
                **UserResponse.model_validate(user).model_dump(),
                "verification_email_sent": True,
            }
        )
    except HTTPException:
        raise
    except ValueError as e:
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
    await _enforce_turnstile_if_required(
        route="login",
        token=credentials.turnstile_token,
        remote_ip=x_forwarded_for,
    )

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

    # Org-level MFA enforcement: if org mandates 2FA and user has none, block login
    if getattr(user, "default_organization_id", None):
        org = db.query(Organization).filter(Organization.id == user.default_organization_id).first()
        if org and (org.features or {}).get("enforce_mfa"):
            if not user.totp_enabled:
                return {
                    "success": False,
                    "data": {
                        "mfa_setup_required": True,
                    },
                    "error": {
                        "code": "E_MFA_SETUP_REQUIRED",
                        "message": (
                            "Your organization requires two-factor authentication. Please sign in and go to Settings > Security to set up 2FA."
                        ),
                    },
                }

    mfa_method = None
    if user.totp_enabled:
        factor_service = AuthFactorsService(db)
        if not credentials.mfa_code:
            mfa_token = create_typed_token(
                {
                    "sub": user.id,
                    "email": user.email,
                },
                token_type="mfa_challenge",
                expires_delta=timedelta(minutes=settings.MFA_CHALLENGE_EXPIRE_MINUTES),
            )
            return ok(
                {
                    "mfa_required": True,
                    "mfa_token": mfa_token,
                    "available_methods": ["totp", "backup_code"],
                }
            )

        mfa_method = factor_service.verify_totp_or_backup(user, credentials.mfa_code)
        if not mfa_method:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid multi-factor authentication code",
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
    AuthService.mark_login_success(db, user)

    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "mfa_method": mfa_method,
            "user": UserResponse.model_validate(user).model_dump(),
        }
    )


@router.get("/mfa/status", response_model=None)
async def get_mfa_status(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return ok(
        {
            "totp_enabled": bool(user.totp_enabled),
            "backup_codes_remaining": len(user.totp_backup_code_hashes or []),
            "passkeys_count": len(user.passkey_credentials or []),
            "passkeys": user.passkey_credentials or [],
        }
    )


@router.post("/mfa/totp/setup", response_model=None)
async def setup_totp(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    setup = AuthFactorsService(db).begin_totp_setup(payload["sub"])
    return ok(setup)


@router.post("/mfa/totp/confirm", response_model=None)
async def confirm_totp(
    request: TotpSetupConfirmRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        result = AuthFactorsService(db).confirm_totp_setup(payload["sub"], request.code)
        return ok(result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login/mfa/complete", response_model=None)
async def complete_mfa_login(
    request: MfaLoginCompleteRequest,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    payload = verify_jwt_token(request.mfa_token, token_type="mfa_challenge")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired MFA challenge")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.totp_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for user")

    method = AuthFactorsService(db).verify_totp_or_backup(user, request.mfa_code)
    if not method:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid multi-factor authentication code")

    access_token, refresh_token = AuthService.create_tokens(user)
    AuthService.store_refresh_token(
        db,
        user.id,
        refresh_token,
        user_agent=user_agent,
        ip_address=x_forwarded_for,
    )
    AuthService.mark_login_success(db, user)

    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "mfa_method": method,
            "user": UserResponse.model_validate(user).model_dump(),
        }
    )


@router.post("/mfa/totp/disable", response_model=None)
async def disable_totp(
    request: TotpDisableRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        AuthFactorsService(db).disable_totp(payload["sub"], request.code)
        return ok({"totp_enabled": False})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/passkeys/register/options", response_model=None)
async def start_passkey_registration(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not settings.PASSKEY_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passkeys disabled")
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    result = AuthFactorsService(db).begin_passkey_registration(payload["sub"])
    return ok(result)


@router.post("/passkeys/register/complete", response_model=None)
async def complete_passkey_registration(
    request: PasskeyRegistrationCompleteRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not settings.PASSKEY_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passkeys disabled")
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        result = AuthFactorsService(db).complete_passkey_registration(payload["sub"], request.credential, request.name)
        return ok(result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/passkeys/authenticate/options", response_model=None)
async def start_passkey_authentication(
    request: PasskeyAuthenticationStartRequest,
    db: Session = Depends(get_db),
):
    if not settings.PASSKEY_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passkeys disabled")
    try:
        result = AuthFactorsService(db).begin_passkey_authentication(request.email)
        return ok(result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/passkeys/authenticate/complete", response_model=None)
async def complete_passkey_authentication(
    request: PasskeyAuthenticationCompleteRequest,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if not settings.PASSKEY_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passkeys disabled")

    try:
        user = AuthFactorsService(db).complete_passkey_authentication(request.email, request.credential)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    access_token, refresh_token = AuthService.create_tokens(user)
    AuthService.store_refresh_token(
        db,
        user.id,
        refresh_token,
        user_agent=user_agent,
        ip_address=x_forwarded_for,
    )
    AuthService.mark_login_success(db, user)

    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        }
    )


@router.delete("/passkeys/{credential_id}", response_model=None)
async def delete_passkey(
    credential_id: str,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    try:
        AuthFactorsService(db).delete_passkey(payload["sub"], credential_id)
        return ok({"deleted": True})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


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

    return ok(
        {
            "message": "Email verified successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        }
    )


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

    return ok(
        {
            "message": "If an account exists with this email, a verification email has been sent.",
        }
    )


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

    return ok(
        {
            "message": "If an account exists with this email, a password reset email has been sent.",
        }
    )


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

    return ok(
        {
            "message": "Password reset successfully. You can now log in with your new password.",
        }
    )


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

    return ok(
        {
            "valid": True,
        }
    )


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

    new_access_token, new_refresh_token, user = result

    return ok(
        {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        }
    )


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

    # Send welcome email and admin notification for new OAuth signups
    if is_new:
        AuthService.send_welcome_email(user)
        AuthService.send_new_signup_notification(user, signup_method=provider)

    access_token, refresh_token = AuthService.create_tokens(user)
    AuthService.store_refresh_token(
        db,
        user.id,
        refresh_token,
        user_agent=user_agent,
        ip_address=x_forwarded_for,
    )
    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        }
    )


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
        return ok({"message": "Successfully logged out"})

    # Case 2: Authorization header with access token -- revoke all user's refresh tokens
    if authorization:
        token = _extract_bearer_token(authorization)
        payload = AuthService.verify_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        AuthService.revoke_all_refresh_tokens_for_user(db, payload["sub"])
        return ok({"message": "Successfully logged out"})

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
    token = _extract_bearer_token(authorization)

    # Verify token
    payload = AuthService.verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = AdminService.get_basic_user_profile(db, payload["sub"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return ok(user)


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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    is_admin = verify_super_admin(db, user_id)

    return ok(
        {
            "is_super_admin": is_admin,
        }
    )


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
    token = _extract_bearer_token(authorization)

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

    return ok(
        {
            "requests": [r.model_dump() for r in requests],
            "total": len(requests),
        }
    )


@router.get("/admin/stats", response_model=None)
async def get_admin_stats(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """Return platform stats for the admin dashboard."""
    token = _extract_bearer_token(authorization)

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
    return ok(stats)


@router.get("/admin/users", response_model=None)
async def list_admin_users(
    authorization: str = Header(...),
    search: Optional[str] = None,
    tier: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List users for the admin dashboard."""
    token = _extract_bearer_token(authorization)

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
    return ok(result)


@router.get("/admin/newsletter-subscribers", response_model=None)
async def list_newsletter_subscribers(
    authorization: str = Header(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List newsletter subscribers for the admin dashboard (super admin only)."""
    token = _extract_bearer_token(authorization)

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
        result = await AdminService.get_newsletter_subscribers(
            page=page,
            page_size=page_size,
            active_only=active_only,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Newsletter service unavailable",
        ) from exc

    return ok(result)


@router.post("/admin/newsletter-subscribers/{subscriber_id}/status", response_model=None)
async def update_newsletter_subscriber_status(
    subscriber_id: int,
    payload: NewsletterSubscriberStatusUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)

    verified = AuthService.verify_access_token(token)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    require_super_admin(db, verified["sub"])

    try:
        result = await AdminService.update_newsletter_subscriber_status(
            subscriber_id=subscriber_id,
            status_value=payload.status,
            reason=payload.reason,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Newsletter service unavailable",
        ) from exc

    return ok(result)


@router.delete("/admin/newsletter-subscribers/{subscriber_id}", response_model=None)
async def delete_newsletter_subscriber(
    subscriber_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)

    verified = AuthService.verify_access_token(token)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    require_super_admin(db, verified["sub"])

    try:
        result = await AdminService.delete_newsletter_subscriber(subscriber_id=subscriber_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Newsletter service unavailable",
        ) from exc

    return ok(result)


@router.get("/admin/organizations/search", response_model=None)
async def search_admin_organizations(
    authorization: str = Header(...),
    query: str = Query(..., min_length=1, description="Search by name, email, slug, or ID"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    db: Session = Depends(get_db),
):
    """Search organizations for admin typeahead."""
    token = _extract_bearer_token(authorization)

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
    return ok(results)


@router.post("/admin/users/update-tier", response_model=TierUpdateResponse)
async def update_admin_user_tier(
    request: TierUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """Update a user's tier (super admin only)."""
    token = _extract_bearer_token(authorization)

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
    token = _extract_bearer_token(authorization)

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
    token = _extract_bearer_token(authorization)

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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    service = ApiAccessService(db)
    is_approved = await service.is_api_access_approved(user_id=user_id)

    return ok(
        {
            "user_id": user_id,
            "approved": is_approved,
        }
    )


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
    token = _extract_bearer_token(authorization)

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
            detail=str(e),
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
    token = _extract_bearer_token(authorization)

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
        return ok(
            {
                "user_id": str(target_user.id),
                "email": target_user.email,
                "is_super_admin": True,
                "message": "User is already a super admin",
            }
        )

    # Promote to super admin
    target_user.is_super_admin = True
    db.commit()

    logger.info(
        "promote_super_admin_success",
        admin_user_id=admin_user_id,
        target_user_id=str(target_user.id),
        target_email=request.email,
    )

    return ok(
        {
            "user_id": str(target_user.id),
            "email": target_user.email,
            "is_super_admin": True,
            "message": "User promoted to super admin",
        }
    )


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
    token = _extract_bearer_token(authorization)

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
        return ok(
            {
                "user_id": str(target_user.id),
                "email": target_user.email,
                "is_super_admin": False,
                "message": "User is not a super admin",
            }
        )

    # Demote from super admin
    target_user.is_super_admin = False
    db.commit()

    logger.info(
        "demote_super_admin_success",
        admin_user_id=admin_user_id,
        target_user_id=str(target_user.id),
        target_email=request.email,
    )

    return ok(
        {
            "user_id": str(target_user.id),
            "email": target_user.email,
            "is_super_admin": False,
            "message": "User demoted from super admin",
        }
    )


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
    token = _extract_bearer_token(authorization)

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

    return ok(
        {
            "super_admins": [
                {
                    "user_id": str(u.id),
                    "email": u.email,
                    "name": u.name,
                }
                for u in super_admins
            ],
            "total": len(super_admins),
        }
    )


@router.post("/admin/users/set-default-organization", response_model=None)
async def set_user_default_organization(
    request: SetDefaultOrganizationRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Set a user's default organization.

    Useful for fixing users stuck in the setup wizard after accepting an
    invite that did not automatically assign a default organization.

    **Super Admin only** - Requires existing super admin privileges.
    """
    import structlog

    logger = structlog.get_logger(__name__)

    token = _extract_bearer_token(authorization)
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin_user_id = payload["sub"]
    require_super_admin(db, admin_user_id)

    # Validate user exists
    target_user = db.query(User).filter(User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Validate organization exists
    org = db.query(Organization).filter(Organization.id == request.organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Validate user is a member of the organization
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == request.user_id,
            OrganizationMember.organization_id == request.organization_id,
            OrganizationMember.status == "active",
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an active member of this organization",
        )

    previous_org_id = target_user.default_organization_id
    target_user.default_organization_id = request.organization_id
    db.commit()

    logger.info(
        "set_default_organization",
        admin_user_id=admin_user_id,
        target_user_id=request.user_id,
        target_email=target_user.email,
        organization_id=request.organization_id,
        organization_name=org.name,
        previous_organization_id=previous_org_id,
    )

    return ok(
        {
            "user_id": request.user_id,
            "email": target_user.email,
            "organization_id": request.organization_id,
            "organization_name": org.name,
            "previous_organization_id": previous_org_id,
            "message": "Default organization updated",
        }
    )


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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

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
        return ok(result.model_dump())
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
    token = _extract_bearer_token(authorization)

    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    result = AdminService.get_setup_status(db=db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return ok(result)


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
    token = _extract_bearer_token(authorization)

    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    try:
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

        org.account_type = request.account_type.value
        org.display_name = request.display_name
        org.dashboard_layout = request.dashboard_layout.value
        org.workflow_category = request.workflow_category.value
        org.publisher_platform = request.publisher_platform
        org.publisher_platform_custom = request.publisher_platform_custom
        if not org.name:
            org.name = request.display_name

        user.setup_completed_at = dt.now(tz.utc)

        service = OnboardingService(db)
        service.complete_step(user_id, "publisher_identity_set")

        db.commit()

        return ok(
            {
                "setup_completed": True,
                "setup_completed_at": user.setup_completed_at.isoformat(),
                "account_type": org.account_type,
                "display_name": org.display_name,
                "workflow_category": org.workflow_category,
                "dashboard_layout": org.dashboard_layout,
                "publisher_platform": org.publisher_platform,
                "publisher_platform_custom": org.publisher_platform_custom,
            }
        )
    except HTTPException:
        raise
    except Exception:
        user_columns = AdminService._table_columns(db, User.__tablename__)
        org_columns = AdminService._table_columns(db, Organization.__tablename__)

        user_query = select(
            User.id.label("id"),
            (User.default_organization_id if "default_organization_id" in user_columns else literal(None)).label("default_organization_id"),
        ).where(User.id == user_id)
        user_row = db.execute(user_query).mappings().first()
        if not user_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user_row["default_organization_id"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization")

        org_query = select(
            Organization.id.label("id"),
            (Organization.name if "name" in org_columns else literal(None)).label("name"),
        ).where(Organization.id == user_row["default_organization_id"])
        org_row = db.execute(org_query).mappings().first()
        if not org_row:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not found")

        org_update_values = {}
        if "account_type" in org_columns:
            org_update_values["account_type"] = request.account_type.value
        if "display_name" in org_columns:
            org_update_values["display_name"] = request.display_name
        if "dashboard_layout" in org_columns:
            org_update_values["dashboard_layout"] = request.dashboard_layout.value
        if "workflow_category" in org_columns:
            org_update_values["workflow_category"] = request.workflow_category.value
        if "publisher_platform" in org_columns:
            org_update_values["publisher_platform"] = request.publisher_platform
        if "publisher_platform_custom" in org_columns:
            org_update_values["publisher_platform_custom"] = request.publisher_platform_custom
        if "name" in org_columns and not org_row["name"]:
            org_update_values["name"] = request.display_name
        if org_update_values:
            db.execute(update(Organization).where(Organization.id == user_row["default_organization_id"]).values(**org_update_values))

        from datetime import datetime as dt
        from datetime import timezone as tz

        setup_completed_at = dt.now(tz.utc)
        if "setup_completed_at" in user_columns:
            db.execute(update(User).where(User.id == user_id).values(setup_completed_at=setup_completed_at))

        service = OnboardingService(db)
        service.complete_step(user_id, "publisher_identity_set")
        db.commit()

        return ok(
            {
                "setup_completed": True,
                "setup_completed_at": setup_completed_at.isoformat(),
                "account_type": request.account_type.value if "account_type" in org_columns else None,
                "display_name": request.display_name if "display_name" in org_columns else None,
                "workflow_category": request.workflow_category.value if "workflow_category" in org_columns else None,
                "dashboard_layout": request.dashboard_layout.value if "dashboard_layout" in org_columns else None,
                "publisher_platform": request.publisher_platform if "publisher_platform" in org_columns else None,
                "publisher_platform_custom": request.publisher_platform_custom if "publisher_platform_custom" in org_columns else None,
            }
        )


# ============================================================
# INTERNAL: User creation for invite flow (TEAM_224)
# ============================================================


class InternalCreateUserRequest(BaseModel):
    """Payload for internal user creation (team invite accept-new flow)."""

    email: EmailStr
    name: str
    password: str


@router.post("/internal/users/create", include_in_schema=False)
async def create_user_internal(
    payload: InternalCreateUserRequest,
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    db: Session = Depends(get_db),
):
    """
    Create a new user account for an invite-based signup.

    Internal-only endpoint (X-Internal-Token required).
    The user's email is auto-verified and API access pre-approved so they
    can start using the platform immediately after accepting the invite.

    Returns 409 if the email is already registered.
    """
    if not settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Internal service token not configured")
    if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    from datetime import datetime as _dt
    from ...db.models import ApiAccessStatus as _ApiAccessStatus

    password_hash = get_password_hash(payload.password)

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=password_hash,
        email_verified=True,
        email_verified_at=_dt.utcnow(),
        api_access_status=_ApiAccessStatus.APPROVED.value,
        totp_enabled=False,
        totp_secret_encrypted=None,
        totp_enabled_at=None,
        totp_backup_code_hashes=[],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token, refresh_token = AuthService.create_tokens(user)
    AuthService.store_refresh_token(db, user.id, refresh_token)

    return ok(
        {
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@router.post("/internal/users/set-default-org", include_in_schema=False)
async def set_default_org_internal(
    payload: SetDefaultOrganizationRequest,
    internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
    db: Session = Depends(get_db),
):
    """
    Set a user's default organization (internal service-to-service call).

    Used by the enterprise_api team invite flow to link a newly created
    user to their invited organization so the setup wizard can complete.
    """
    if not settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Internal service token not configured")
    if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    user.default_organization_id = payload.organization_id
    db.commit()

    return ok(
        {
            "user_id": payload.user_id,
            "organization_id": payload.organization_id,
            "message": "Default organization set",
        }
    )
