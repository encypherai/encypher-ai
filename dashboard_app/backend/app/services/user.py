"""
User service for authentication and user management.
"""

from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token, get_password_hash, verify_password
from app.models.blacklisted_token import BlacklistedToken
from app.models.user import User

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user.

    Args:
        db: Database session
        username: Username or email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = await get_user_by_username(db, username)
    if not user:
        # Try email instead
        user = await get_user_by_email(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Get the current user from the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Check if token is blacklisted
        stmt = select(BlacklistedToken).where(BlacklistedToken.token == token)
        result = await db.execute(stmt)
        blacklisted = result.scalars().first()

        if blacklisted:
            raise credentials_exception

        payload = decode_access_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user(db, user_id)
    if user is None:
        raise credentials_exception

    # Attach the token to the user object for logout functionality
    user.token = token

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current authenticated superuser.

    Args:
        current_user: Current authenticated user

    Returns:
        User object

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return current_user


async def create_user(
    db: AsyncSession, username: str, email: str, password: str, full_name: Optional[str] = None, is_superuser: bool = False
) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        username: Username
        email: Email
        password: Plain text password
        full_name: Full name
        is_superuser: Whether the user is a superuser

    Returns:
        Created user object
    """
    from app.core.security import get_password_hash

    user = User(username=username, email=email, hashed_password=get_password_hash(password), full_name=full_name, is_superuser=is_superuser)

    db.add(user)  # db.add is synchronous
    await db.commit()
    await db.refresh(user)

    return user


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get a list of users with pagination.

    Args:
        db: Database session
        skip: Number of users to skip
        limit: Maximum number of users to return

    Returns:
        List of User objects
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID. Alias for get_user for consistent naming.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    return await get_user(db, user_id)


async def update_user(db: AsyncSession, db_user_id: int, user_in: Any) -> User:
    """
    Update a user.

    Args:
        db: Database session
        db_user_id: User ID to update
        user_in: User update data

    Returns:
        Updated User object

    Raises:
        HTTPException: If user not found
    """
    user = await get_user(db, db_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Convert to dict if it's a Pydantic model
    update_data = user_in if isinstance(user_in, dict) else user_in.dict(exclude_unset=True)

    # Handle password update separately if it exists
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    # Update user attributes
    for field, value in update_data.items():
        if hasattr(user, field) and field != "id":  # Protect the ID field
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user
