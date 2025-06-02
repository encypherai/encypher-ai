import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user import get_user_by_username, create_user, authenticate_user
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

async def test_create_user(db: AsyncSession) -> None:
    """Test creating a new user."""
    user_in = UserCreate(
        username="testuser_create", 
        email="test_create@example.com", 
        password="testpassword123",
        full_name="Test User Create"
    )
    created_user = await create_user(
        db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )
    assert created_user is not None
    assert created_user.username == user_in.username
    assert created_user.email == user_in.email
    assert created_user.full_name == user_in.full_name
    assert hasattr(created_user, 'hashed_password')
    assert verify_password("testpassword123", created_user.hashed_password)

    # Check if user is in DB
    db_user = await db.get(User, created_user.id)
    assert db_user is not None
    assert db_user.username == user_in.username

async def test_get_user_by_username_existing(db: AsyncSession) -> None:
    """Test retrieving an existing user by username."""
    user_in = UserCreate(
        username="testuser_get", 
        email="test_get@example.com", 
        password="securepassword",
        full_name="Test User Get"
    )
    await create_user(
        db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    ) # Create user first

    found_user = await get_user_by_username(db, "testuser_get")
    assert found_user is not None
    assert found_user.username == "testuser_get"
    assert found_user.email == "test_get@example.com"

async def test_get_user_by_username_non_existing(db: AsyncSession) -> None:
    """Test retrieving a non-existing user by username."""
    found_user = await get_user_by_username(db, "nonexistentuser")
    assert found_user is None

async def test_authenticate_user_correct_credentials(db: AsyncSession) -> None:
    """Test authenticating a user with correct credentials."""
    user_in = UserCreate(
        username="auth_user_correct", 
        email="auth_correct@example.com", 
        password="authpass123",
        full_name="Auth User Correct"
    )
    await create_user(
        db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )

    authenticated_user = await authenticate_user(db, "auth_user_correct", "authpass123")
    assert authenticated_user is not None
    assert authenticated_user.username == "auth_user_correct"

async def test_authenticate_user_incorrect_password(db: AsyncSession) -> None:
    """Test authenticating a user with an incorrect password."""
    user_in = UserCreate(
        username="auth_user_incorrect_pass", 
        email="auth_incorrect_pass@example.com", 
        password="correctpass",
        full_name="Auth User Incorrect Pass"
    )
    await create_user(
        db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )

    authenticated_user = await authenticate_user(db, "auth_user_incorrect_pass", "wrongpassword")
    assert authenticated_user is None

async def test_authenticate_user_non_existing_user(db: AsyncSession) -> None:
    """Test authenticating a non-existing user."""
    authenticated_user = await authenticate_user(db, "no_such_user_auth", "anypassword")
    assert authenticated_user is None
