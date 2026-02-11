"""
Authentication endpoints for the Encypher Dashboard API.
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

logger = logging.getLogger(__name__)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.blacklisted_token import BlacklistedToken
from app.models.user import User as UserModel
from app.schemas.user import (
    PasswordReset,
    PasswordResetRequest,
    Token,
    TokenRefresh,
    User,
    UserProfileUpdate,
)
from app.services.email import send_password_reset_email
from app.services.user import (
    authenticate_user,
    get_current_user,
    get_user_by_email,
    get_user_by_username,
    update_user,
)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends(), remember_me: bool = False) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    The remember_me parameter is passed via form field or query parameter.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # If remember_me is True, set a longer expiration time (30 days)
    if remember_me:
        access_token_expires = timedelta(days=30)
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {"access_token": create_access_token(user.id, expires_delta=access_token_expires), "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user information.
    """
    return current_user


@router.patch("/profile", response_model=User)
async def update_profile(
    profile_update: UserProfileUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user profile information.

    Users can update their username, full name, email, and password.
    When updating password, current password must be provided and verified.
    """
    # Check if username already exists (if trying to change it)
    if profile_update.username and profile_update.username != current_user.username:
        existing_user = await get_user_by_username(db, profile_update.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Check if email already exists (if trying to change it)
    if profile_update.email and profile_update.email != current_user.email:
        existing_user = await get_user_by_email(db, profile_update.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Handle password update if requested
    update_data = profile_update.dict(exclude_unset=True)

    if profile_update.new_password:
        # Verify current password
        if not verify_password(profile_update.current_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

        # Remove current_password from update data
        if "current_password" in update_data:
            del update_data["current_password"]

        # Replace new_password with hashed_password
        update_data["password"] = profile_update.new_password
        del update_data["new_password"]
    elif "current_password" in update_data:
        # Remove current_password if it was provided but no new password
        del update_data["current_password"]

    # Update user profile
    updated_user = await update_user(db, current_user.id, update_data)
    return updated_user


@router.post("/logout")
async def logout(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """
    Logout the current user by blacklisting their token.
    """
    # Get the token from the Authorization header
    token = current_user.token if hasattr(current_user, "token") else None

    if token:
        # Add token to blacklist
        blacklisted_token = BlacklistedToken(token=token)
        db.add(blacklisted_token)
        await db.commit()

    return {"message": "Successfully logged out"}


@router.post("/password-reset-request")
async def request_password_reset(
    background_tasks: BackgroundTasks, reset_request: PasswordResetRequest, db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Request a password reset. Sends an email with a reset token if the email exists.
    """
    # Always return success to prevent email enumeration attacks
    response = {"message": "If the email exists, a password reset link has been sent."}

    # Check if user exists
    user = await get_user_by_email(db, reset_request.email)
    if not user:
        return response

    # Generate a secure random token
    reset_token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    # Set token expiration (24 hours)
    token_expires = datetime.utcnow() + timedelta(hours=24)

    # Update user with reset token and expiration
    stmt = select(UserModel).where(UserModel.email == reset_request.email)
    result = await db.execute(stmt)
    db_user = result.scalars().first()

    if db_user:
        db_user.reset_token = reset_token
        db_user.reset_token_expires = token_expires
        await db.commit()

        # Send email with reset link in background
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        background_tasks.add_task(send_password_reset_email, email=reset_request.email, reset_url=reset_url)

    return response


@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """
    Reset a user's password using a valid reset token.
    """
    # Find user with the given reset token
    stmt = select(UserModel).where(UserModel.reset_token == reset_data.token)
    result = await db.execute(stmt)
    user = result.scalars().first()

    # Validate token and expiration
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()

    return {"message": "Password has been reset successfully"}


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Refresh an access token using a valid existing token.
    This endpoint allows extending the session without requiring re-authentication.
    """
    try:
        # Validate the current token and get the user ID
        user = await get_current_user(db=db, token=token_data.token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token is blacklisted
        stmt = select(BlacklistedToken).where(BlacklistedToken.token == token_data.token)
        result = await db.execute(stmt)
        blacklisted = result.scalars().first()

        if blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create a new token with the same expiration policy
        # If remember_me was true originally, we'll keep the long expiration
        if token_data.remember_me:
            access_token_expires = timedelta(days=30)
        else:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Blacklist the old token
        blacklisted_token = BlacklistedToken(token=token_data.token)
        db.add(blacklisted_token)
        await db.commit()

        # Generate new token
        return {"access_token": create_access_token(user.id, expires_delta=access_token_expires), "token_type": "bearer"}

    except Exception as e:
        logger.exception("Token refresh failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
