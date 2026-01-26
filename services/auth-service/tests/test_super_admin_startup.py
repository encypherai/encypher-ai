"""Tests for enforcing super admin account at startup."""

from unittest.mock import MagicMock

from app.db.models import User
from app.services.super_admin_service import SUPER_ADMIN_EMAIL, ensure_super_admin_user


def _build_session():
    return MagicMock()


def test_ensure_super_admin_user_sets_flag():
    db = _build_session()
    user = User(email=SUPER_ADMIN_EMAIL, password_hash="hash", is_super_admin=False)
    db.query.return_value.filter.return_value.first.return_value = user

    updated = ensure_super_admin_user(db)

    assert updated is True
    assert user.is_super_admin is True
    db.commit.assert_called_once()


def test_ensure_super_admin_user_noop_when_missing():
    db = _build_session()

    db.query.return_value.filter.return_value.first.return_value = None

    updated = ensure_super_admin_user(db)

    assert updated is False
    db.commit.assert_not_called()
