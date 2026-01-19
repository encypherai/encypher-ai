import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.services.user import create_user

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


async def test_login_for_access_token_success(client: AsyncClient, db: AsyncSession) -> None:
    """Test successful login and token retrieval."""
    # 1. Create a user directly in the database for testing
    test_username = "logintestuser"
    test_password = "testloginpass123"
    user_in = UserCreate(username=test_username, email="login@example.com", password=test_password, full_name="Login Test User")
    await create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser if hasattr(user_in, "is_superuser") else False,
    )

    # 2. Attempt to login
    login_data = {"username": test_username, "password": test_password}
    response = await client.post("/api/v1/auth/login", data=login_data)

    # 3. Assertions
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


async def test_login_for_access_token_incorrect_password(client: AsyncClient, db: AsyncSession) -> None:
    """Test login attempt with incorrect password."""
    test_username = "login_wrongpass_user"
    test_password = "correctpassword"
    user_in = UserCreate(username=test_username, email="login_wrongpass@example.com", password=test_password, full_name="Login WrongPass User")
    await create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser if hasattr(user_in, "is_superuser") else False,
    )

    login_data = {"username": test_username, "password": "incorrectpassword"}
    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_data = response.json()
    assert error_data["detail"] == "Incorrect username or password"


async def test_login_for_access_token_non_existent_user(client: AsyncClient) -> None:
    """Test login attempt for a user that does not exist."""
    login_data = {"username": "nonexistentuser", "password": "anypassword"}
    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_data = response.json()
    assert error_data["detail"] == "Incorrect username or password"


async def test_read_users_me_requires_auth(client: AsyncClient) -> None:
    """Test that /users/me endpoint requires authentication."""
    response = await client.get("/api/v1/auth/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


async def test_read_users_me_success(client: AsyncClient, db: AsyncSession) -> None:
    """Test successful retrieval of current user info after login."""
    # 1. Create user and login to get token
    test_username = "me_user"
    test_password = "me_password"
    user_in = UserCreate(username=test_username, email="me@example.com", password=test_password, full_name="Me User FullName", is_superuser=False)
    created_user = await create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser if hasattr(user_in, "is_superuser") else False,
    )

    login_data = {"username": test_username, "password": test_password}
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]

    # 2. Call /users/me with the token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/api/v1/auth/users/me", headers=headers)

    # 3. Assertions
    assert me_response.status_code == status.HTTP_200_OK
    user_data = me_response.json()
    assert user_data["username"] == test_username
    assert user_data["email"] == "me@example.com"
    assert user_data["full_name"] == "Me User FullName"
    assert user_data["id"] == created_user.id
    assert user_data["is_active"] is True
    assert user_data["is_superuser"] is False
