"""Tests for signup input validation and normalization."""

import pytest

from app.models.schemas import UserCreate, UserLogin


def test_user_create_strips_html_tags_in_name() -> None:
    user = UserCreate(
        email="user@example.com",
        password="SecurePass123!",
        name="<b>Jane Doe</b>",
    )

    assert user.name == "Jane Doe"


def test_user_create_rejects_url_like_name() -> None:
    with pytest.raises(ValueError):
        UserCreate(
            email="user@example.com",
            password="SecurePass123!",
            name="Visit https://evil.test now",
        )


def test_user_create_canonicalizes_plus_address() -> None:
    user = UserCreate(
        email="Example+tag@company.com",
        password="SecurePass123!",
        name="Jane Doe",
    )

    assert user.email == "example@company.com"


def test_user_create_canonicalizes_gmail_dot_and_plus() -> None:
    user = UserCreate(
        email="First.Last+tag@Gmail.com",
        password="SecurePass123!",
        name="Jane Doe",
    )

    assert user.email == "firstlast@gmail.com"


def test_user_login_canonicalizes_email() -> None:
    login = UserLogin(email="First.Last+tag@Gmail.com", password="SecurePass123!")

    assert login.email == "firstlast@gmail.com"
