"""
Authentication service business logic
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..db.models import User, RefreshToken
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
            hashed_password=hashed_password,
            tier=user_data.tier or "free",
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
        
        if not user.hashed_password:
            # OAuth user trying to login with password
            return None
        
        if not verify_password(credentials.password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
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
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None
        
        # Check if token exists and is not revoked
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            not RefreshToken.revoked,
        ).first()
        
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
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            not RefreshToken.revoked,
        ).all()
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
        return verify_token(token, token_type="access")

    @staticmethod
    def upsert_oauth_user(
        db: Session,
        *,
        provider: str,
        provider_id: str,
        email: Optional[str],
        name: Optional[str] = None,
    ) -> User:
        """Create or update a user from an OAuth provider."""
        # Try match by provider id first
        user = (
            db.query(User)
            .filter(User.oauth_provider == provider, User.oauth_id == provider_id)
            .first()
        )
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
                user.oauth_provider = provider
                user.oauth_id = provider_id
                if name and not user.name:
                    user.name = name
                db.commit()
                db.refresh(user)
                return user

        # Create new OAuth user
        user = User(
            email=email or f"{provider}_{provider_id}@users.void",
            name=name,
            hashed_password=None,
            oauth_provider=provider,
            oauth_id=provider_id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
