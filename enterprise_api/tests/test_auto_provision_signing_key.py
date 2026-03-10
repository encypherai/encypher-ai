import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.crypto_utils import decrypt_private_key, load_organization_private_key


@pytest.mark.asyncio
async def test_load_organization_private_key_auto_provisions_when_missing(
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "auto_provision_signing_keys", True)

    org_id = "org_auto_key_001"

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share, created_at, updated_at
            ) VALUES (
                :id, :name, :email, :tier, 10000, 0,
                TRUE, 65, NOW(), NOW()
            )
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": org_id,
            "name": "Auto Key Org",
            "email": "auto-key-org@example.com",
            "tier": "starter",
        },
    )
    await db.commit()

    private_key = await load_organization_private_key(org_id, db)
    assert isinstance(private_key, ed25519.Ed25519PrivateKey)

    row = (await db.execute(text("SELECT private_key_encrypted, public_key FROM organizations WHERE id = :org_id"), {"org_id": org_id})).fetchone()
    assert row is not None
    assert row.private_key_encrypted
    assert row.public_key

    decrypted = decrypt_private_key(bytes(row.private_key_encrypted))
    assert decrypted.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ) == bytes(row.public_key)


@pytest.mark.asyncio
async def test_load_organization_private_key_does_not_auto_provision_when_disabled(
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "auto_provision_signing_keys", False)

    org_id = "org_no_auto_key_001"

    await db.execute(
        text(
            """
            INSERT INTO organizations (
                id, name, email, tier, monthly_api_limit, monthly_api_usage,
                coalition_member, coalition_rev_share, created_at, updated_at
            ) VALUES (
                :id, :name, :email, :tier, 10000, 0,
                TRUE, 65, NOW(), NOW()
            )
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": org_id,
            "name": "No Auto Key Org",
            "email": "no-auto-key-org@example.com",
            "tier": "starter",
        },
    )
    await db.commit()

    with pytest.raises(ValueError, match="No private key found"):
        await load_organization_private_key(org_id, db)
