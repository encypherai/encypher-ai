from datetime import datetime, timedelta, timezone

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from sqlalchemy import text

from app.config import settings
from app.services.provisioning_service import ProvisioningService
from app.utils.crypto_utils import encrypt_private_key, serialize_public_key


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = str(self._payload)

    def json(self) -> dict:
        return self._payload


class _DummyAsyncClient:
    def __init__(self, responses: list[_DummyResponse]):
        self._responses = responses
        self.requests: list[tuple[str, str, dict | None, dict | None]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str, headers: dict | None = None):
        self.requests.append(("get", url, None, headers))
        return self._responses.pop(0)

    async def patch(self, url: str, json: dict | None = None, headers: dict | None = None):
        self.requests.append(("patch", url, json, headers))
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_ensure_organization_certificate_uses_signing_key(db, monkeypatch) -> None:
    organization_id = "org_cert_test"
    organization_name = "Cert Test Org"
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    encrypted_private_key = encrypt_private_key(private_key)
    serialized_public_key = serialize_public_key(public_key)

    # Clean up any existing test data first
    await db.execute(
        text("DELETE FROM organizations WHERE id = :id"),
        {"id": organization_id},
    )
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share, private_key_encrypted, public_key,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, :tier, :monthly_api_limit, 0,
                TRUE, 65, :private_key_encrypted, :public_key,
                NOW(), NOW()
            )
            """
        ),
        {
            "id": organization_id,
            "name": organization_name,
            "email": "cert-test@encypher.com",
            "tier": "starter",
            "monthly_api_limit": 10000,
            "private_key_encrypted": encrypted_private_key,
            "public_key": serialized_public_key,
        },
    )
    await db.commit()

    monkeypatch.setattr(settings, "internal_service_token", "internal-token")
    monkeypatch.setattr(settings, "auth_service_url", "http://auth-service")

    dummy_client = _DummyAsyncClient(
        responses=[
            _DummyResponse(200, {"success": True, "data": {}}),
            _DummyResponse(200, {"success": True}),
        ]
    )

    monkeypatch.setattr(
        "app.services.provisioning_service.httpx.AsyncClient",
        lambda *args, **kwargs: dummy_client,
    )

    result = await ProvisioningService._ensure_organization_certificate(
        db=db,
        organization_id=organization_id,
        organization_name=organization_name,
        authorization=None,
    )

    assert result is True

    cert_row = await db.execute(
        text("SELECT certificate_pem, certificate_status FROM organizations WHERE id = :org_id"),
        {"org_id": organization_id},
    )
    certificate_pem, certificate_status = cert_row.fetchone()

    assert certificate_status == "active"
    cert = x509.load_pem_x509_certificate(certificate_pem.encode("utf-8"))
    cert_public_key = cert.public_key()

    assert isinstance(cert_public_key, ed25519.Ed25519PublicKey)
    assert cert_public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    patch_calls = [request for request in dummy_client.requests if request[0] == "patch"]
    assert patch_calls
    _, patch_url, patch_json, patch_headers = patch_calls[0]
    assert patch_url.endswith(f"/api/v1/organizations/internal/{organization_id}/certificate")
    assert "certificate_pem" in patch_json
    assert patch_headers["X-Internal-Token"] == "internal-token"
    assert patch_headers["X-Internal-Service"] == "enterprise_api"
    assert patch_headers["X-Internal-Audience"] == "enterprise_api.provisioning.ensure_certificate"
    assert patch_headers["X-Internal-Timestamp"]


@pytest.mark.asyncio
async def test_ensure_organization_certificate_handles_naive_expiry(db, monkeypatch) -> None:
    organization_id = "org_cert_naive"
    organization_name = "Naive Expiry Org"
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    encrypted_private_key = encrypt_private_key(private_key)
    serialized_public_key = serialize_public_key(public_key)

    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, organization_name),
                    x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, organization_id),
                ]
            )
        )
        .issuer_name(
            x509.Name(
                [
                    x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, organization_name),
                    x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, organization_id),
                ]
            )
        )
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=3650))
        .sign(private_key, algorithm=None)
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    # Clean up any existing test data first
    await db.execute(
        text("DELETE FROM organizations WHERE id = :id"),
        {"id": organization_id},
    )
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share, private_key_encrypted, public_key,
                certificate_pem, certificate_expiry, created_at, updated_at
            ) VALUES (
                :id, :name, :email, :tier, :monthly_api_limit, 0,
                TRUE, 65, :private_key_encrypted, :public_key,
                :certificate_pem, :certificate_expiry, NOW(), NOW()
            )
            """
        ),
        {
            "id": organization_id,
            "name": organization_name,
            "email": "naive-expiry@encypher.com",
            "tier": "starter",
            "monthly_api_limit": 10000,
            "private_key_encrypted": encrypted_private_key,
            "public_key": serialized_public_key,
            "certificate_pem": cert_pem,
            "certificate_expiry": now + timedelta(days=3650),
        },
    )
    await db.commit()

    monkeypatch.setattr(settings, "internal_service_token", "internal-token")
    monkeypatch.setattr(settings, "auth_service_url", "http://auth-service")

    result = await ProvisioningService._ensure_organization_certificate(
        db=db,
        organization_id=organization_id,
        organization_name=organization_name,
        authorization=None,
    )

    assert result is True

    cert_row = await db.execute(
        text("SELECT certificate_pem FROM organizations WHERE id = :org_id"),
        {"org_id": organization_id},
    )
    stored_cert = cert_row.fetchone()[0]
    assert stored_cert == cert_pem


@pytest.mark.asyncio
async def test_internal_ensure_certificate_endpoint_requires_token(async_client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "internal_service_token", "internal-token")

    response = await async_client.post(
        "/api/v1/provisioning/internal/ensure-certificate",
        json={"organization_id": "org_demo"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_internal_ensure_certificate_endpoint_returns_success(async_client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "internal_service_token", "internal-token")

    async def _fake_ensure(*args, **kwargs):
        return True

    monkeypatch.setattr(
        "app.services.provisioning_service.ProvisioningService._ensure_organization_certificate",
        _fake_ensure,
    )

    response = await async_client.post(
        "/api/v1/provisioning/internal/ensure-certificate",
        json={"organization_id": "org_demo", "organization_name": "Demo Org"},
        headers={
            "X-Internal-Token": "internal-token",
            "X-Internal-Service": "enterprise_api",
            "X-Internal-Audience": "enterprise_api.provisioning.ensure_certificate",
            "X-Internal-Timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["organization_id"] == "org_demo"


@pytest.mark.asyncio
async def test_internal_ensure_certificate_endpoint_rejects_stale_timestamp(async_client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "internal_service_token", "internal-token")

    response = await async_client.post(
        "/api/v1/provisioning/internal/ensure-certificate",
        json={"organization_id": "org_demo", "organization_name": "Demo Org"},
        headers={
            "X-Internal-Token": "internal-token",
            "X-Internal-Service": "enterprise_api",
            "X-Internal-Audience": "enterprise_api.provisioning.ensure_certificate",
            "X-Internal-Timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
        },
    )

    assert response.status_code == 401
