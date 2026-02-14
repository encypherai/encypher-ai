from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509.oid import NameOID

from app.config import settings
from app.models.request_models import SignRequest
from app.services.certificate_service import CertificateResolver
from app.services.signing_executor import execute_signing


class _FakeScalarResult:
    def scalar_one_or_none(self):
        return None


class _FakeSessionCtx:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


def _ed25519_private_key_pem(private_key: ed25519.Ed25519PrivateKey) -> str:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def _self_signed_cert_pem(private_key: ed25519.Ed25519PrivateKey, *, common_name: str) -> str:
    now = datetime.now(timezone.utc)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=365))
        .sign(private_key=private_key, algorithm=None)
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")


@pytest.mark.asyncio
async def test_execute_signing_uses_managed_signer_when_mode_is_managed(monkeypatch: pytest.MonkeyPatch) -> None:
    managed_private_key = ed25519.Ed25519PrivateKey.generate()
    monkeypatch.setattr(settings, "managed_signer_private_key_pem", _ed25519_private_key_pem(managed_private_key))
    monkeypatch.setattr(settings, "managed_signer_id", "encypher_managed")

    request = SignRequest(text="Hello world.", document_type="article")
    organization = {
        "organization_id": "org_managed_signing",
        "organization_name": "Managed Signing Org",
        "tier": "enterprise",
        "is_demo": False,
        "features": {},
        "signing_mode": "managed",
    }

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_FakeScalarResult())

    content_db = AsyncMock()
    core_db = AsyncMock()
    allocate_mock = AsyncMock(return_value=(0, 7, "https://verify.encypherai.com/status/v1/org/list/0"))
    ensure_cert_mock = AsyncMock(return_value=True)

    with (
        patch("app.services.signing_executor.ensure_organization_exists", new=AsyncMock(return_value=None)),
        patch("app.services.signing_executor.ProvisioningService._ensure_organization_certificate", new=ensure_cert_mock),
        patch("app.services.signing_executor.status_service.allocate_status_index", new=allocate_mock),
        patch("app.services.signing_executor._index_in_coalition", new=AsyncMock(return_value=None)),
        patch("app.services.signing_executor.content_session_factory", new=lambda: _FakeSessionCtx(content_db)),
        patch("app.services.signing_executor.core_session_factory", new=lambda: _FakeSessionCtx(core_db)),
        patch("app.services.signing_executor.UnicodeMetadata.embed_metadata", return_value="signed") as mock_embed,
    ):
        result = await execute_signing(request=request, organization=organization, db=db)

    assert result.success is True
    assert result.signed_text == "signed"
    ensure_cert_mock.assert_not_awaited()
    assert mock_embed.call_args.kwargs["signer_id"] == "encypher_managed"
    private_key = mock_embed.call_args.kwargs["private_key"]
    assert isinstance(private_key, ed25519.Ed25519PrivateKey)


@pytest.mark.asyncio
async def test_certificate_resolver_loads_managed_signer_from_settings(
    db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    managed_private_key = ed25519.Ed25519PrivateKey.generate()
    managed_cert_pem = _self_signed_cert_pem(managed_private_key, common_name="Encypher Managed Signer")

    monkeypatch.setattr(settings, "managed_signer_id", "encypher_managed")
    monkeypatch.setattr(settings, "managed_signer_certificate_pem", managed_cert_pem)

    resolver = CertificateResolver(ttl_seconds=0)
    await resolver.refresh_cache(db)

    managed = resolver.get("encypher_managed")
    assert managed is not None
    assert managed.certificate_pem == managed_cert_pem
    assert resolver.resolve_public_key("encypher_managed") is not None
