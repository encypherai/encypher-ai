"""Tests for TOTP 2FA + passkey factor service."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pyotp
import pytest

from app.services.auth_factors_service import AuthFactorsService


@pytest.fixture
def service(mock_db):
    return AuthFactorsService(mock_db)


@pytest.fixture
def user() -> SimpleNamespace:
    return SimpleNamespace(
        id="user_123",
        email="user@example.com",
        name="Test User",
        totp_enabled=False,
        totp_secret_encrypted=None,
        totp_enabled_at=None,
        totp_backup_code_hashes=[],
        passkey_credentials=[],
        passkey_challenge=None,
        passkey_challenge_expires_at=None,
    )


def _wire_user(mock_db, user):
    mock_db.query.return_value.filter.return_value.first.return_value = user


def test_begin_totp_setup_generates_secret_and_backup_hashes(service, mock_db, user):
    _wire_user(mock_db, user)

    setup = service.begin_totp_setup(user.id)

    assert isinstance(setup["secret"], str)
    assert setup["secret"]
    assert "otpauth://" in setup["provisioning_uri"]
    assert len(setup["backup_codes"]) == 8
    assert len(user.totp_backup_code_hashes) == 8


def test_confirm_totp_setup_enables_factor(service, mock_db, user):
    _wire_user(mock_db, user)
    setup = service.begin_totp_setup(user.id)
    valid_code = pyotp.TOTP(setup["secret"]).now()

    result = service.confirm_totp_setup(user.id, valid_code)

    assert result["enabled"] is True
    assert user.totp_enabled is True
    assert user.totp_enabled_at is not None


def test_confirm_totp_setup_rejects_invalid_code(service, mock_db, user):
    _wire_user(mock_db, user)
    service.begin_totp_setup(user.id)

    with pytest.raises(ValueError, match="Invalid authentication code"):
        service.confirm_totp_setup(user.id, "000000")


def test_begin_totp_setup_requires_pyotp_dependency(service, mock_db, user):
    _wire_user(mock_db, user)

    with patch("app.services.auth_factors_service.pyotp", None):
        with pytest.raises(ValueError, match="TOTP support is unavailable"):
            service.begin_totp_setup(user.id)


def test_verify_totp_or_backup_accepts_backup_code_once(service, mock_db, user):
    _wire_user(mock_db, user)
    setup = service.begin_totp_setup(user.id)
    code = setup["backup_codes"][0]

    method = service.verify_totp_or_backup(user, code)
    assert method == "backup_code"

    method_again = service.verify_totp_or_backup(user, code)
    assert method_again is None


def test_verify_totp_or_backup_uses_backup_code_when_pyotp_missing(service, mock_db, user):
    _wire_user(mock_db, user)
    setup = service.begin_totp_setup(user.id)
    code = setup["backup_codes"][0]

    with patch("app.services.auth_factors_service.pyotp", None):
        method = service.verify_totp_or_backup(user, code)

    assert method == "backup_code"


def test_begin_passkey_registration_requires_webauthn_dependency(service, mock_db, user):
    _wire_user(mock_db, user)

    with patch("app.services.auth_factors_service.generate_registration_options", None):
        with pytest.raises(ValueError, match="Passkey support is unavailable"):
            service.begin_passkey_registration(user.id)


def test_begin_passkey_registration_sets_challenge(service, mock_db, user):
    _wire_user(mock_db, user)

    with patch("app.services.auth_factors_service.generate_registration_options") as generate_options:
        generate_options.return_value = SimpleNamespace(challenge=b"challenge")
        with patch("app.services.auth_factors_service.options_to_json", return_value='{"challenge":"x"}'):
            result = service.begin_passkey_registration(user.id)

    assert result["options_json"] == '{"challenge":"x"}'
    assert user.passkey_challenge == "Y2hhbGxlbmdl"
    assert user.passkey_challenge_expires_at is not None


def test_complete_passkey_registration_stores_credential(service, mock_db, user):
    _wire_user(mock_db, user)
    user.passkey_challenge = "Y2hhbGxlbmdl"
    user.passkey_challenge_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    verified = SimpleNamespace(
        credential_id=b"cred-id",
        credential_public_key=b"pub-key",
        sign_count=7,
        aaguid="aaguid-test",
    )
    with patch("app.services.auth_factors_service.verify_registration_response", return_value=verified):
        result = service.complete_passkey_registration(user.id, {"id": "abc"}, "Laptop")

    assert result["credential_id"] == "Y3JlZC1pZA"
    assert len(user.passkey_credentials) == 1
    assert user.passkey_credentials[0]["name"] == "Laptop"


def test_begin_passkey_authentication_uses_existing_credentials(service, mock_db, user):
    user.passkey_credentials = [
        {"credential_id": "Y3JlZC1pZA", "public_key": "cHViLWtleQ", "sign_count": 0, "name": "Laptop"}
    ]
    _wire_user(mock_db, user)

    with patch("app.services.auth_factors_service.generate_authentication_options") as generate_options:
        generate_options.return_value = SimpleNamespace(challenge=b"challenge")
        with patch("app.services.auth_factors_service.options_to_json", return_value='{"challenge":"x"}'):
            result = service.begin_passkey_authentication(user.email)

    assert result["options_json"] == '{"challenge":"x"}'
    assert user.passkey_challenge == "Y2hhbGxlbmdl"


def test_complete_passkey_authentication_updates_counter(service, mock_db, user):
    user.passkey_challenge = "Y2hhbGxlbmdl"
    user.passkey_challenge_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    user.passkey_credentials = [
        {"credential_id": "Y3JlZC1pZA", "public_key": "cHViLWtleQ", "sign_count": 1, "name": "Laptop"}
    ]
    _wire_user(mock_db, user)

    credential = {"id": "Y3JlZC1pZA", "response": {}}
    verified_auth = SimpleNamespace(new_sign_count=42)
    with patch("app.services.auth_factors_service.verify_authentication_response", return_value=verified_auth):
        returned_user = service.complete_passkey_authentication(user.email, credential)

    assert returned_user.id == user.id
    assert user.passkey_credentials[0]["sign_count"] == 42
