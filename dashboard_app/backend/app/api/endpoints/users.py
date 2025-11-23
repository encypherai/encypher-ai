"""
API endpoints for user management.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_password_hash
from app.schemas.user import User, UserUpdate
from app.services.user import (
    get_current_user,
    get_user_by_id,
    get_users,
    update_user
)

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve users.
    """
    # Only superusers can access all users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    users = await get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user.
    """
    # If password is provided, hash it
    if user_in.password:
        user_in_dict = user_in.dict(exclude_unset=True)
        user_in_dict["hashed_password"] = get_password_hash(user_in.password)
        del user_in_dict["password"]
        user_in = UserUpdate(**user_in_dict)
    
    updated_user = await update_user(db, db_user_id=current_user.id, user_in=user_in)
    return updated_user

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get user by ID.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Only allow superusers or the user themselves to access their data
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

@router.put("/{user_id}", response_model=User)
async def update_user_by_id(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update user by ID.
    """
    # Only superusers can update other users
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If password is provided, hash it
    if user_in.password:
        user_in_dict = user_in.dict(exclude_unset=True)
        user_in_dict["hashed_password"] = get_password_hash(user_in.password)
        del user_in_dict["password"]
        user_in = UserUpdate(**user_in_dict)
    
    updated_user = await update_user(db, db_user_id=user_id, user_in=user_in)
    return updated_user
