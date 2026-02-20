"""2FA (TOTP) and passkey factor orchestration."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import pyotp
except ModuleNotFoundError:
    pyotp = None
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
try:
    from webauthn import (
        generate_authentication_options,
        generate_registration_options,
        options_to_json,
        verify_authentication_response,
        verify_registration_response,
    )
    from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
    from webauthn.helpers.structs import PublicKeyCredentialDescriptor
except ModuleNotFoundError:
    generate_authentication_options = None
    generate_registration_options = None
    options_to_json = None
    verify_authentication_response = None
    verify_registration_response = None
    base64url_to_bytes = None
    bytes_to_base64url = None
    PublicKeyCredentialDescriptor = None

from app.core.config import settings
from app.db.models import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_factor_code(code: str) -> str:
    return code.replace(" ", "").replace("-", "").strip()


def _fernet() -> Fernet:
    key_seed = hashlib.sha256(settings.JWT_SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(key_seed))


def _require_pyotp() -> None:
    if pyotp is None:
        raise ValueError("TOTP support is unavailable because dependency 'pyotp' is not installed")


def _require_webauthn() -> None:
    if (
        generate_authentication_options is None
        or generate_registration_options is None
        or options_to_json is None
        or verify_authentication_response is None
        or verify_registration_response is None
        or base64url_to_bytes is None
        or bytes_to_base64url is None
        or PublicKeyCredentialDescriptor is None
    ):
        raise ValueError("Passkey support is unavailable because dependency 'webauthn' is not installed")


class AuthFactorsService:
    def __init__(self, db: Session):
        self.db = db

    def _get_user(self, user_id: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user

    def _get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found")
        return user

    def begin_totp_setup(self, user_id: str) -> dict[str, Any]:
        _require_pyotp()
        user = self._get_user(user_id)
        secret = pyotp.random_base32()
        user.totp_secret_encrypted = _fernet().encrypt(secret.encode("utf-8")).decode("utf-8")
        backup_codes = [secrets.token_hex(4) for _ in range(settings.MFA_BACKUP_CODES_COUNT)]
        user.totp_backup_code_hashes = [_hash_value(code) for code in backup_codes]
        self.db.commit()

        issuer = settings.MFA_ISSUER
        username = user.email
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)
        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "backup_codes": backup_codes,
        }

    def confirm_totp_setup(self, user_id: str, code: str) -> dict[str, Any]:
        _require_pyotp()
        user = self._get_user(user_id)
        if not user.totp_secret_encrypted:
            raise ValueError("TOTP setup has not been initialized")

        secret = _fernet().decrypt(user.totp_secret_encrypted.encode("utf-8")).decode("utf-8")
        normalized_code = _normalize_factor_code(code)
        if not pyotp.TOTP(secret).verify(normalized_code, valid_window=1):
            raise ValueError("Invalid authentication code")

        user.totp_enabled = True
        user.totp_enabled_at = _utcnow()
        self.db.commit()
        return {"enabled": True, "recovery_codes_remaining": len(user.totp_backup_code_hashes or [])}

    def verify_totp_or_backup(self, user: User, code: str) -> str | None:
        normalized_code = _normalize_factor_code(code)
        if pyotp is not None and user.totp_secret_encrypted:
            secret = _fernet().decrypt(user.totp_secret_encrypted.encode("utf-8")).decode("utf-8")
            if pyotp.TOTP(secret).verify(normalized_code, valid_window=1):
                return "totp"

        hashed = _hash_value(normalized_code)
        backup_hashes = list(user.totp_backup_code_hashes or [])
        if hashed in backup_hashes:
            backup_hashes.remove(hashed)
            user.totp_backup_code_hashes = backup_hashes
            self.db.commit()
            return "backup_code"

        return None

    def disable_totp(self, user_id: str, code: str) -> None:
        user = self._get_user(user_id)
        if not user.totp_enabled:
            return
        if self.verify_totp_or_backup(user, code) is None:
            raise ValueError("Invalid authentication code")
        user.totp_enabled = False
        user.totp_secret_encrypted = None
        user.totp_enabled_at = None
        user.totp_backup_code_hashes = []
        self.db.commit()

    def begin_passkey_registration(self, user_id: str) -> dict[str, str]:
        _require_webauthn()
        user = self._get_user(user_id)
        existing = []
        for cred in user.passkey_credentials or []:
            cred_id = cred.get("credential_id")
            if cred_id:
                existing.append(PublicKeyCredentialDescriptor(id=base64url_to_bytes(cred_id)))

        options = generate_registration_options(
            rp_id=settings.PASSKEY_RP_ID,
            rp_name=settings.PASSKEY_RP_NAME,
            user_id=user.id.encode("utf-8"),
            user_name=user.email,
            user_display_name=user.name or user.email,
            exclude_credentials=existing or None,
        )

        user.passkey_challenge = bytes_to_base64url(options.challenge)
        user.passkey_challenge_expires_at = _utcnow() + timedelta(minutes=10)
        self.db.commit()

        return {"options_json": options_to_json(options)}

    def complete_passkey_registration(self, user_id: str, credential: dict[str, Any], name: str | None = None) -> dict[str, Any]:
        _require_webauthn()
        user = self._get_user(user_id)
        if not user.passkey_challenge:
            raise ValueError("No passkey registration in progress")
        if not user.passkey_challenge_expires_at or _utcnow() > user.passkey_challenge_expires_at:
            user.passkey_challenge = None
            user.passkey_challenge_expires_at = None
            self.db.commit()
            raise ValueError("Passkey challenge has expired")

        verified = verify_registration_response(
            credential=credential,
            expected_challenge=base64url_to_bytes(user.passkey_challenge),
            expected_rp_id=settings.PASSKEY_RP_ID,
            expected_origin=settings.PASSKEY_EXPECTED_ORIGIN,
            require_user_verification=True,
        )

        credential_info = {
            "credential_id": bytes_to_base64url(verified.credential_id),
            "public_key": bytes_to_base64url(verified.credential_public_key),
            "sign_count": int(verified.sign_count),
            "aaguid": str(verified.aaguid),
            "name": (name or "Passkey").strip() or "Passkey",
            "created_at": _utcnow().isoformat(),
        }

        current = list(user.passkey_credentials or [])
        current.append(credential_info)
        user.passkey_credentials = current
        user.passkey_challenge = None
        user.passkey_challenge_expires_at = None
        self.db.commit()
        return credential_info

    def begin_passkey_authentication(self, email: str) -> dict[str, str]:
        _require_webauthn()
        user = self._get_user_by_email(email)
        credentials = list(user.passkey_credentials or [])
        if not credentials:
            raise ValueError("No passkeys registered")

        allow_creds = [
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(cred["credential_id"]))
            for cred in credentials
            if cred.get("credential_id")
        ]

        options = generate_authentication_options(
            rp_id=settings.PASSKEY_RP_ID,
            allow_credentials=allow_creds,
            user_verification="required",
        )
        user.passkey_challenge = bytes_to_base64url(options.challenge)
        user.passkey_challenge_expires_at = _utcnow() + timedelta(minutes=10)
        self.db.commit()

        return {"options_json": options_to_json(options)}

    def complete_passkey_authentication(self, email: str, credential: dict[str, Any]) -> User:
        _require_webauthn()
        user = self._get_user_by_email(email)
        if not user.passkey_challenge:
            raise ValueError("No passkey authentication in progress")
        if not user.passkey_challenge_expires_at or _utcnow() > user.passkey_challenge_expires_at:
            user.passkey_challenge = None
            user.passkey_challenge_expires_at = None
            self.db.commit()
            raise ValueError("Passkey challenge has expired")

        credential_id = credential.get("id")
        if not credential_id:
            raise ValueError("Credential ID missing")

        credentials = list(user.passkey_credentials or [])
        matched = next((c for c in credentials if c.get("credential_id") == credential_id), None)
        if not matched:
            raise ValueError("Unknown passkey")

        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=base64url_to_bytes(user.passkey_challenge),
            expected_rp_id=settings.PASSKEY_RP_ID,
            expected_origin=settings.PASSKEY_EXPECTED_ORIGIN,
            credential_public_key=base64url_to_bytes(matched["public_key"]),
            credential_current_sign_count=int(matched.get("sign_count", 0)),
            require_user_verification=True,
        )

        matched["sign_count"] = int(verified.new_sign_count)
        user.passkey_credentials = credentials
        user.passkey_challenge = None
        user.passkey_challenge_expires_at = None
        self.db.commit()
        return user

    def list_passkeys(self, user_id: str) -> list[dict[str, Any]]:
        user = self._get_user(user_id)
        return list(user.passkey_credentials or [])

    def delete_passkey(self, user_id: str, credential_id: str) -> None:
        user = self._get_user(user_id)
        credentials = list(user.passkey_credentials or [])
        filtered = [item for item in credentials if item.get("credential_id") != credential_id]
        if len(filtered) == len(credentials):
            raise ValueError("Passkey not found")
        user.passkey_credentials = filtered
        self.db.commit()
