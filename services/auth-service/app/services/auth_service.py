"""
Authentication service business logic
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..db.models import User, RefreshToken, EmailVerificationToken
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
from encypher_commercial_shared.email import (
    EmailConfig,
    generate_token,
    send_verification_email as _send_verification_email,
    send_welcome_email as _send_welcome_email,
)


# Create email config from settings
def _get_email_config() -> EmailConfig:
    return EmailConfig(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_pass=settings.SMTP_PASS,
        smtp_tls=settings.SMTP_TLS,
        email_from=settings.EMAIL_FROM,
        email_from_name=settings.EMAIL_FROM_NAME,
        frontend_url=settings.FRONTEND_URL,
        dashboard_url=settings.DASHBOARD_URL,
    )


class AuthService:
    """Authentication service"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Idempotent: if user already exists, return it
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            return existing

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=hashed_password,
        )

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                return existing_user
            raise ValueError("User with this email already exists")

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

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        return user

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
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[Tuple[str, User]]:
        """Refresh an access token using a refresh token"""
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

        # Create new access token
        token_data = {
            "sub": user.id,
            "email": user.email,
        }
        new_access_token = create_access_token(token_data)

        return new_access_token, user

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
    ) -> User:
        """
        Create or update a user from an OAuth provider.
        Uses google_id/github_id columns per core_db schema.
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
            return user

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
                return user

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
        db.commit()
        db.refresh(user)
        return user

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
        config = _get_email_config()
        _send_welcome_email(config=config, to_email=user.email, user_name=user.name)

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
