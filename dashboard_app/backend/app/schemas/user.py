"""
Pydantic schemas for user-related API requests and responses.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


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


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for resetting a password."""

    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class TokenRefresh(BaseModel):
    """Schema for token refresh requests"""

    token: str
    remember_me: bool = False


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile information.

    This schema is specifically for the /profile endpoint where users can update
    their own profile information, but with more limited fields than the admin UserUpdate.
    """

    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)

    @validator("new_password")
    def password_requires_current(cls, v, values):
        if v is not None and "current_password" not in values:
            raise ValueError("Current password is required to set a new password")
        return v
