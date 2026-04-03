"""
Authentication service business logic
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from encypher_commercial_shared.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT

from ..db.models import User, RefreshToken, EmailVerificationToken, PasswordResetToken, Organization, OrganizationMember
from .organization_service import OrganizationService
from sqlalchemy.exc import IntegrityError
from ..models.schemas import UserCreate, UserLogin
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from ..core.config import settings
from ..core.auth import get_email_config as _get_email_config
from encypher_commercial_shared.email import (
    EmailConfig,
    generate_token,
    send_verification_email as _send_verification_email,
    send_welcome_email as _send_welcome_email,
    send_password_reset_email as _send_password_reset_email,
    send_new_signup_admin_email as _send_new_signup_admin_email,
)
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Tuple[User, bool]:
        """
        Create a new user with an auto-created personal organization.

        Returns:
            Tuple of (user, is_new) where is_new indicates if user was just created
        """
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            return existing, False

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=hashed_password,
        )

        db.add(db_user)
        try:
            db.flush()  # Get user ID before creating org

            # Auto-join to verified org domain if enabled; otherwise create personal org
            org_service = OrganizationService(db)
            auto_join_org_id = org_service.get_auto_join_org_for_email(db_user.email)
            if auto_join_org_id:
                member = OrganizationMember(
                    organization_id=auto_join_org_id,
                    user_id=db_user.id,
                    role="member",
                    status="active",
                    accepted_at=datetime.utcnow(),
                )
                db.add(member)
                db_user.default_organization_id = auto_join_org_id
            else:
                # Auto-create personal organization for the user
                # Free tier uses Encypher's signing keys; paid tiers can BYOK
                org = AuthService._create_personal_organization(db, db_user)
                db_user.default_organization_id = org.id

            # TEAM_191: Initialize onboarding checklist for new user
            from .onboarding_service import OnboardingService

            OnboardingService(db).initialize_for_new_user(db_user.id)

            db.commit()
            db.refresh(db_user)
            return db_user, True
        except IntegrityError:
            db.rollback()
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                return existing_user, False
            raise ValueError("User with this email already exists")

    @staticmethod
    def _create_personal_organization(db: Session, user: User) -> Organization:
        """
        Create a personal organization for a new user.

        - Free/starter tier: Uses Encypher's signing keys (no certificate_pem)
        - Paid tiers: Can bring their own keys (BYOK) via certificate_pem

        The organization is created with minimal info - user fills in company name later.
        """
        import secrets

        # Generate unique org ID
        org_id = f"org_{secrets.token_hex(8)}"

        # Create organization with defaults
        # Name is empty - user will fill in later
        # Email matches user email for now
        org = Organization(
            id=org_id,
            name="",  # User fills in later
            slug=None,  # Will be set when user provides company name
            email=user.email,
            tier="free",  # TEAM_173: Default free tier
            max_seats=1,
            monthly_api_limit=10000,
            monthly_api_usage=0,
            features={
                "team_management": False,
                "audit_logs": False,
                "merkle_enabled": True,  # TEAM_173: Free tier includes Merkle
                "bulk_operations": False,
                "sentence_tracking": True,  # TEAM_173: Free tier includes sentence tracking
                "streaming": True,
                "byok": False,  # Free tier uses Encypher's keys
                "sso": False,
                "custom_assertions": False,
            },
            coalition_member=True,
            coalition_rev_share=DEFAULT_COALITION_PUBLISHER_PERCENT,  # TEAM_173: from SSOT
            # certificate_pem is NULL - free tier uses Encypher's signing keys
        )
        db.add(org)
        db.flush()

        # Add user as owner
        member_id = f"mem_{secrets.token_hex(8)}"
        member = OrganizationMember(
            id=member_id,
            organization_id=org.id,
            user_id=user.id,
            role="owner",
            status="active",
            accepted_at=datetime.utcnow(),
        )
        db.add(member)

        logger.info(f"Created personal organization {org.id} for user {user.id}")
        return org

    @staticmethod
    def authenticate_user(db: Session, credentials: UserLogin) -> Optional[User]:
        """Authenticate a user with email and password"""
        user = db.query(User).filter(User.email == credentials.email).first()

        if not user:
            return None

        if not user.password_hash:
            # OAuth user trying to login with password
            return None

        if not verify_password(credentials.password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def mark_login_success(db: Session, user: User) -> None:
        """Persist successful login timestamp once all auth factors have passed."""
        user.last_login_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def create_tokens(user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for a user"""
        token_data = {
            "sub": user.id,
            "email": user.email,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return access_token, refresh_token

    @staticmethod
    def store_refresh_token(
        db: Session,
        user_id: str,
        token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> RefreshToken:
        """Store a refresh token in the database"""
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        db.add(db_token)
        db.commit()
        db.refresh(db_token)

        return db_token

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[Tuple[str, str, User]]:
        """Refresh session tokens using a refresh token."""
        # Verify the refresh token
        payload = verify_token(refresh_token, token_type="refresh")  # noqa: S106
        if not payload:
            return None

        # Check if token exists and is not revoked
        db_token = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == refresh_token,
                not RefreshToken.revoked,
            )
            .first()
        )

        if not db_token:
            return None

        # Check if token is expired
        if db_token.expires_at < datetime.utcnow():
            return None

        # Get user
        user = db.query(User).filter(User.id == payload["sub"]).first()
        if not user or not user.is_active:
            return None

        new_access_token, new_refresh_token = AuthService.create_tokens(user)

        db_token.revoked = True
        db_token.revoked_at = datetime.utcnow()

        rotated_token = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=db_token.user_agent,
            ip_address=db_token.ip_address,
        )
        db.add(rotated_token)
        db.commit()

        return new_access_token, new_refresh_token, user

    @staticmethod
    def revoke_refresh_token(db: Session, token: str) -> bool:
        """Revoke a refresh token"""
        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()

        if not db_token:
            return False

        db_token.revoked = True
        db_token.revoked_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def revoke_all_refresh_tokens_for_user(db: Session, user_id: str) -> int:
        """Revoke all active refresh tokens for a user. Returns number revoked."""
        tokens = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                not RefreshToken.revoked,
            )
            .all()
        )
        count = 0
        for t in tokens:
            t.revoked = True
            t.revoked_at = datetime.utcnow()
            count += 1
        db.commit()
        return count

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def verify_access_token(token: str) -> Optional[dict]:
        """Verify an access token and return payload"""
        return verify_token(token, token_type="access")  # noqa: S106

    @staticmethod
    def upsert_oauth_user(
        db: Session,
        *,
        provider: str,
        provider_id: str,
        email: Optional[str],
        name: Optional[str] = None,
    ) -> Tuple[User, bool]:
        """
        Create or update a user from an OAuth provider.
        Uses google_id/github_id columns per core_db schema.

        Returns:
            Tuple of (user, is_new) where is_new indicates if user was just created
        """
        # Determine which provider column to use
        provider_column = None
        if provider == "google":
            provider_column = User.google_id
        elif provider == "github":
            provider_column = User.github_id
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        # Try match by provider id first
        user = db.query(User).filter(provider_column == provider_id).first()
        if user:
            # Update basic profile fields if provided
            if email and not user.email:
                user.email = email
            if name and not user.name:
                user.name = name
            db.commit()
            db.refresh(user)
            return user, False

        # Fallback: match by email if exists
        if email:
            user = db.query(User).filter(User.email == email).first()
            if user:
                # Link OAuth provider to existing user
                if provider == "google":
                    user.google_id = provider_id
                elif provider == "github":
                    user.github_id = provider_id
                if name and not user.name:
                    user.name = name
                db.commit()
                db.refresh(user)
                return user, False

        # Create new OAuth user
        user_kwargs = {
            "email": email or f"{provider}_{provider_id}@users.void",
            "name": name,
            "password_hash": None,
            "is_active": True,
        }
        if provider == "google":
            user_kwargs["google_id"] = provider_id
        elif provider == "github":
            user_kwargs["github_id"] = provider_id

        user = User(**user_kwargs)
        db.add(user)
        db.flush()  # Get user ID before creating org

        org_service = OrganizationService(db)
        auto_join_org_id = org_service.get_auto_join_org_for_email(user.email)
        if auto_join_org_id:
            member = OrganizationMember(
                organization_id=auto_join_org_id,
                user_id=user.id,
                role="member",
                status="active",
                accepted_at=datetime.utcnow(),
            )
            db.add(member)
            user.default_organization_id = auto_join_org_id
        else:
            # Auto-create personal organization for the user
            # Free tier uses Encypher's signing keys; paid tiers can BYOK
            org = AuthService._create_personal_organization(db, user)
            user.default_organization_id = org.id

        # TEAM_191: Initialize onboarding checklist for new OAuth user
        from .onboarding_service import OnboardingService

        OnboardingService(db).initialize_for_new_user(user.id)

        db.commit()
        db.refresh(user)
        return user, True

    # ==========================================
    # Email Verification Methods
    # ==========================================

    @staticmethod
    def create_verification_token(db: Session, user: User) -> str:
        """
        Create an email verification token for a user.
        Invalidates any existing tokens for this user.
        """
        # Invalidate existing tokens
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used == False,
        ).update({"used": True, "used_at": datetime.utcnow()})

        # Create new token
        token = generate_token(32)
        expires_at = datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)

        db_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(db_token)
        db.commit()

        return token

    @staticmethod
    def send_verification_email(user: User, token: str) -> bool:
        """Send verification email to user."""
        config = _get_email_config()
        return _send_verification_email(
            config=config,
            to_email=user.email,
            user_name=user.name,
            verification_token=token,
        )

    @staticmethod
    def verify_email(db: Session, token: str) -> Optional[User]:
        """
        Verify a user's email using a verification token.
        Returns the user if successful, None otherwise.
        """
        # Find valid token
        db_token = (
            db.query(EmailVerificationToken)
            .filter(
                EmailVerificationToken.token == token,
                EmailVerificationToken.used == False,
                EmailVerificationToken.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not db_token:
            return None

        # Get user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            return None

        # Mark token as used
        db_token.used = True
        db_token.used_at = datetime.utcnow()

        # Mark user as verified
        user.email_verified = True
        user.email_verified_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        # Send welcome email
        AuthService.send_welcome_email(user)

        return user

    @staticmethod
    def resend_verification_email(db: Session, email: str) -> bool:
        """
        Resend verification email to a user.
        Returns True if email was sent, False otherwise.
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if user exists
            return True

        if user.email_verified:
            # Already verified
            return True

        # Create new token and send email
        token = AuthService.create_verification_token(db, user)
        return AuthService.send_verification_email(user, token)

    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """Send welcome email to a newly active user (email verification or OAuth signup)."""
        config = _get_email_config()
        try:
            return _send_welcome_email(config=config, to_email=user.email, user_name=user.name, logger=logger)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False

    @staticmethod
    def send_new_signup_notification(user: User, signup_method: str = "email") -> bool:
        """
        Send admin notification about new user signup.

        Args:
            user: The newly created user
            signup_method: How they signed up (email, google, github)

        Returns:
            True if sent successfully
        """
        config = _get_email_config()
        if not config.support_email:
            logger.warning("No support_email configured, skipping signup notification")
            return False

        try:
            return _send_new_signup_admin_email(
                config=config,
                to_email=config.support_email,
                user_name=user.name,
                user_email=user.email,
                signup_method=signup_method,
                logger=logger,
            )
        except Exception as e:
            logger.error(f"Failed to send signup notification: {e}")
            return False

    # ==========================================
    # Password Reset Methods
    # ==========================================

    @staticmethod
    def create_password_reset_token(db: Session, user: User) -> str:
        """
        Create a password reset token for a user.
        Invalidates any existing tokens for this user.
        """
        # Invalidate existing tokens
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        ).update({"used": True, "used_at": datetime.utcnow()})

        # Create new token
        token = generate_token(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

        db_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(db_token)
        db.commit()

        return token

    @staticmethod
    def send_password_reset_email(user: User, token: str) -> bool:
        """Send password reset email to user."""
        config = _get_email_config()
        return _send_password_reset_email(
            config=config,
            to_email=user.email,
            user_name=user.name,
            reset_token=token,
        )

    @staticmethod
    def request_password_reset(db: Session, email: str) -> bool:
        """
        Request a password reset for a user.
        Returns True always to prevent email enumeration.
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if user exists
            return True

        if not user.password_hash:
            # OAuth user - can't reset password
            return True

        # Create token and send email
        token = AuthService.create_password_reset_token(db, user)
        AuthService.send_password_reset_email(user, token)
        return True

    @staticmethod
    def validate_password_reset_token(db: Session, token: str) -> bool:
        """
        Validate a password reset token without using it.
        Returns True if valid, False otherwise.
        """
        db_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow(),
            )
            .first()
        )
        return db_token is not None

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> Optional[User]:
        """
        Reset a user's password using a reset token.
        Returns the user if successful, None otherwise.
        """
        # Find valid token
        db_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not db_token:
            return None

        # Get user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            return None

        # Mark token as used
        db_token.used = True
        db_token.used_at = datetime.utcnow()

        # Update password
        user.password_hash = get_password_hash(new_password)

        db.commit()
        db.refresh(user)

        return user
