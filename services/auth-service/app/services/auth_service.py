"""
Authentication service business logic
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..db.models import User, RefreshToken, PasswordResetToken
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
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            tier=user_data.tier or "free",
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    
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
            RefreshToken.revoked == False,
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
