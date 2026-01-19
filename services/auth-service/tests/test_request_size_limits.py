import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.organizations import AcceptInvitationNewUser
from app.core.config import settings
from app.models.schemas import PasswordResetConfirm, UserCreate, UserLogin
from app.middleware.request_size_limit import RequestSizeLimitMiddleware


def _build_app(max_body_size: int) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestSizeLimitMiddleware, max_body_size=max_body_size, exclude_paths=set())

    @app.post("/signup")
    async def signup(payload: dict) -> dict:
        return {"ok": True, "payload": payload}

    return app


def test_user_create_rejects_long_password():
    long_password = "a" * (settings.AUTH_MAX_PASSWORD_LENGTH + 1)
    with pytest.raises(ValidationError):
        UserCreate(email="user@example.com", password=long_password)


def test_user_login_rejects_long_password():
    long_password = "a" * (settings.AUTH_MAX_PASSWORD_LENGTH + 1)
    with pytest.raises(ValidationError):
        UserLogin(email="user@example.com", password=long_password)


def test_password_reset_rejects_long_password():
    long_password = "a" * (settings.AUTH_MAX_PASSWORD_LENGTH + 1)
    with pytest.raises(ValidationError):
        PasswordResetConfirm(token="token", new_password=long_password)


def test_accept_invitation_rejects_long_password():
    long_password = "a" * (settings.AUTH_MAX_PASSWORD_LENGTH + 1)
    with pytest.raises(ValidationError):
        AcceptInvitationNewUser(name="Test User", password=long_password)


def test_request_size_limit_allows_small_body():
    client = TestClient(_build_app(max_body_size=128))
    response = client.post("/signup", json={"password": "short"})
    assert response.status_code == 200


def test_request_size_limit_blocks_large_body():
    client = TestClient(_build_app(max_body_size=128))
    response = client.post("/signup", json={"password": "a" * 256})
    assert response.status_code == 413
    assert response.json()["detail"] == "Request body too large"
