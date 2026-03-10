"""
Regression tests for TEAM_188: CERT_NOT_FOUND verification bug.

Verifies that:
1. load_organization_public_key falls back to private_key_encrypted when
   public_key column is NULL.
2. CertificateResolver loads auto-provisioned keys (orgs with
   private_key_encrypted but no certificate_pem).
"""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from sqlalchemy import text

from app.services.certificate_service import CertificateResolver
from app.utils.crypto_utils import (
    encrypt_private_key,
    load_organization_public_key,
    serialize_public_key,
)

# ---------------------------------------------------------------------------
# load_organization_public_key fallback tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_load_public_key_from_public_key_column(db) -> None:
    """Standard path: public_key column is populated."""
    org_id = "org_pubkey_standard"
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    await db.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share, public_key,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, 'free', 10000, 0,
                TRUE, 65, :public_key, NOW(), NOW()
            )
            """
        ),
        {
            "id": org_id,
            "name": "Standard PubKey Org",
            "email": f"{org_id}@test.local",
            "public_key": serialize_public_key(public_key),
        },
    )
    await db.commit()

    result = await load_organization_public_key(org_id, db)
    assert result.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


@pytest.mark.asyncio
async def test_load_public_key_fallback_to_private_key_encrypted(db) -> None:
    """TEAM_188: When public_key is NULL, derive from private_key_encrypted."""
    org_id = "org_pubkey_fallback"
    private_key = ed25519.Ed25519PrivateKey.generate()
    expected_public_key = private_key.public_key()
    encrypted = encrypt_private_key(private_key)

    await db.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share,
                private_key_encrypted, public_key,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, 'free', 10000, 0,
                TRUE, 65,
                :private_key_encrypted, NULL,
                NOW(), NOW()
            )
            """
        ),
        {
            "id": org_id,
            "name": "Fallback PubKey Org",
            "email": f"{org_id}@test.local",
            "private_key_encrypted": encrypted,
        },
    )
    await db.commit()

    result = await load_organization_public_key(org_id, db)
    assert result.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == expected_public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


@pytest.mark.asyncio
async def test_load_public_key_raises_when_org_missing(db) -> None:
    """ValueError when org doesn't exist at all."""
    with pytest.raises(ValueError, match="No public key found"):
        await load_organization_public_key("org_nonexistent_999", db)


@pytest.mark.asyncio
async def test_load_public_key_raises_when_no_keys(db) -> None:
    """ValueError when org exists but has neither public_key nor private_key_encrypted."""
    org_id = "org_pubkey_empty"

    await db.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, 'free', 10000, 0,
                TRUE, 65, NOW(), NOW()
            )
            """
        ),
        {
            "id": org_id,
            "name": "Empty Key Org",
            "email": f"{org_id}@test.local",
        },
    )
    await db.commit()

    with pytest.raises(ValueError, match="No public key found"):
        await load_organization_public_key(org_id, db)


# ---------------------------------------------------------------------------
# CertificateResolver auto-provisioned key tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_certificate_resolver_loads_auto_provisioned_key(db) -> None:
    """TEAM_188: Resolver should cache orgs with private_key_encrypted but no certificate_pem."""
    org_id = "org_resolver_auto"
    private_key = ed25519.Ed25519PrivateKey.generate()
    expected_public_key = private_key.public_key()
    encrypted = encrypt_private_key(private_key)

    await db.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share,
                private_key_encrypted, public_key, certificate_pem,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, 'free', 10000, 0,
                TRUE, 65,
                :private_key_encrypted, NULL, NULL,
                NOW(), NOW()
            )
            """
        ),
        {
            "id": org_id,
            "name": "Auto Provisioned Org",
            "email": f"{org_id}@test.local",
            "private_key_encrypted": encrypted,
        },
    )
    await db.commit()

    resolver = CertificateResolver(ttl_seconds=0)
    await resolver.refresh_cache(db)

    cert = resolver.get(org_id)
    assert cert is not None, f"Resolver should have cached org {org_id}"
    assert cert.public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == expected_public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    resolved_key = resolver.resolve_public_key(org_id)
    assert resolved_key is not None


@pytest.mark.asyncio
async def test_certificate_resolver_prefers_certificate_pem_over_auto_provisioned(db) -> None:
    """Orgs with certificate_pem should use that, not the auto-provisioned fallback."""
    from datetime import datetime, timedelta

    from cryptography import x509

    org_id = "org_resolver_cert_pem"
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    encrypted = encrypt_private_key(private_key)

    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, org_id)]))
        .issuer_name(x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, org_id)]))
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .sign(private_key, algorithm=None)
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    await db.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
    await db.commit()

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share,
                private_key_encrypted, public_key, certificate_pem,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, 'enterprise', 100000, 0,
                TRUE, 65,
                :private_key_encrypted, :public_key, :certificate_pem,
                NOW(), NOW()
            )
            """
        ),
        {
            "id": org_id,
            "name": "Cert PEM Org",
            "email": f"{org_id}@test.local",
            "private_key_encrypted": encrypted,
            "public_key": serialize_public_key(public_key),
            "certificate_pem": cert_pem,
        },
    )
    await db.commit()

    resolver = CertificateResolver(ttl_seconds=0)
    await resolver.refresh_cache(db)

    resolved = resolver.get(org_id)
    assert resolved is not None
    assert resolved.certificate_pem == cert_pem
    assert not resolved.is_byok
