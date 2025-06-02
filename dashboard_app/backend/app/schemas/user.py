"""
Pydantic schemas for user-related API requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for creating a new user, including password."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user stored in the database."""
    id: int
    hashed_password: str

    class Config:
        """Pydantic config."""
        from_attributes = True


class User(UserBase):
    """Schema for user response without sensitive data."""
    id: int

    class Config:
        """Pydantic config."""
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[int] = None
