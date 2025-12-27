#!/usr/bin/env python3
"""
Standalone script to populate demo organization public keys.
Can be run via: railway run python populate_keys.py
"""
import asyncio
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


def load_public_key_from_pem(pem_str: str) -> ed25519.Ed25519PublicKey:
    """Load Ed25519 public key from PEM format string."""
    public_key = serialization.load_pem_public_key(pem_str.encode())
    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        raise ValueError("PEM does not contain an Ed25519 public key")
    return public_key


def load_private_key_from_pem(pem_str: str) -> ed25519.Ed25519PrivateKey:
    """Load Ed25519 private key from PEM format string."""
    private_key = serialization.load_pem_private_key(pem_str.encode(), password=None)
    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("PEM does not contain an Ed25519 private key")
    return private_key


def serialize_public_key(public_key: ed25519.Ed25519PublicKey) -> bytes:
    """Serialize Ed25519 public key to raw bytes (32 bytes)."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )


def get_demo_private_key() -> ed25519.Ed25519PrivateKey:
    """Get demo private key from environment or generate ephemeral one."""
    # Try PEM format first
    demo_private_key_pem = os.getenv('DEMO_PRIVATE_KEY_PEM')
    if demo_private_key_pem:
        print("Loading private key from PEM format")
        return load_private_key_from_pem(demo_private_key_pem)
    
    # Try hex format
    demo_private_key_hex = os.getenv('DEMO_PRIVATE_KEY_HEX') or os.getenv('SECRET_KEY')
    if demo_private_key_hex:
        print("Loading private key from hex format")
        private_key_bytes = bytes.fromhex(demo_private_key_hex.strip())
        return ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    
    # Generate ephemeral key (not recommended for production)
    print("WARNING: Generating ephemeral key (not recommended for production)")
    return ed25519.Ed25519PrivateKey.generate()


async def populate_demo_public_key():
    """Populate demo organization's public key in database."""
    
    # Get demo organization details from environment
    demo_organization_id = os.getenv('DEMO_ORGANIZATION_ID', 'org_demo')
    demo_organization_name = os.getenv('DEMO_ORGANIZATION_NAME', 'Encypher Demo Organization')
    
    # Get database URL
    database_url = os.getenv('CORE_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: No database URL configured (CORE_DATABASE_URL or DATABASE_URL)")
        return False
    
    # Convert postgresql:// to postgresql+asyncpg:// for async support
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    elif database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    
    # Get public key
    demo_public_key_pem = os.getenv('DEMO_PUBLIC_KEY_PEM')
    if demo_public_key_pem:
        print("Loading public key from PEM format (legacy)")
        try:
            demo_public_key = load_public_key_from_pem(demo_public_key_pem)
            public_key_bytes = serialize_public_key(demo_public_key)
            print("✅ Successfully loaded legacy PEM public key")
        except Exception as e:
            print(f"❌ Failed to load PEM public key: {e}")
            print("Falling back to deriving from private key...")
            demo_private_key = get_demo_private_key()
            demo_public_key = demo_private_key.public_key()
            public_key_bytes = serialize_public_key(demo_public_key)
    else:
        print("Deriving public key from private key")
        demo_private_key = get_demo_private_key()
        demo_public_key = demo_private_key.public_key()
        public_key_bytes = serialize_public_key(demo_public_key)
    
    print(f"Demo organization ID: {demo_organization_id}")
    print(f"Public key bytes length: {len(public_key_bytes)}")
    print(f"Public key hex: {public_key_bytes.hex()}")
    
    # Connect to database
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if demo org exists
            result = await session.execute(
                text("SELECT id, name FROM organizations WHERE id = :org_id"),
                {"org_id": demo_organization_id}
            )
            org = result.fetchone()
            
            if not org:
                print(f"WARNING: Demo organization '{demo_organization_id}' not found in database")
                print("Creating demo organization...")
                
                # Create demo organization
                await session.execute(
                    text("""
                        INSERT INTO organizations (
                            id, name, email, tier, public_key,
                            merkle_enabled, streaming_enabled, byok_enabled,
                            monthly_quota, created_at, updated_at
                        ) VALUES (
                            :id, :name, :email, :tier, :public_key,
                            TRUE, TRUE, FALSE,
                            10000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """),
                    {
                        "id": demo_organization_id,
                        "name": demo_organization_name,
                        "email": "demo@encypherai.com",
                        "tier": "enterprise",
                        "public_key": public_key_bytes
                    }
                )
                await session.commit()
                print("✅ Created demo organization with public key")
            else:
                print(f"Found demo organization: {org.name}")
                
                # Update public key
                await session.execute(
                    text("UPDATE organizations SET public_key = :public_key, updated_at = CURRENT_TIMESTAMP WHERE id = :org_id"),
                    {"org_id": demo_organization_id, "public_key": public_key_bytes}
                )
                await session.commit()
                print("✅ Updated public key for demo organization")
            
            # Update legacy signer IDs
            legacy_signer_ids = ["demo-signer-id", "c2pa-demo-signer-001"]
            for signer_id in legacy_signer_ids:
                result = await session.execute(
                    text("SELECT id FROM organizations WHERE id = :org_id"),
                    {"org_id": signer_id}
                )
                if result.fetchone():
                    await session.execute(
                        text("UPDATE organizations SET public_key = :public_key, updated_at = CURRENT_TIMESTAMP WHERE id = :org_id"),
                        {"org_id": signer_id, "public_key": public_key_bytes}
                    )
                    await session.commit()
                    print(f"✅ Updated public key for legacy signer: {signer_id}")
                else:
                    # Create legacy signer entry
                    await session.execute(
                        text("""
                            INSERT INTO organizations (
                                id, name, email, tier, public_key,
                                merkle_enabled, streaming_enabled, byok_enabled,
                                monthly_quota, created_at, updated_at
                            ) VALUES (
                                :id, :name, :email, :tier, :public_key,
                                TRUE, TRUE, FALSE,
                                10000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            )
                        """),
                        {
                            "id": signer_id,
                            "name": f"Legacy Signer ({signer_id})",
                            "email": "demo@encypherai.com",
                            "tier": "enterprise",
                            "public_key": public_key_bytes
                        }
                    )
                    await session.commit()
                    print(f"✅ Created legacy signer with public key: {signer_id}")
            
            # Verify
            result = await session.execute(
                text("SELECT public_key FROM organizations WHERE id = :org_id"),
                {"org_id": demo_organization_id}
            )
            row = result.fetchone()
            if row and row[0]:
                stored_key = bytes(row[0])
                if stored_key == public_key_bytes:
                    print("✅ Verification successful - public key matches")
                    return True
                else:
                    print("❌ ERROR: Stored key doesn't match!")
                    print(f"   Expected: {public_key_bytes.hex()}")
                    print(f"   Got:      {stored_key.hex()}")
                    return False
            else:
                print("❌ ERROR: Public key not found after update")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return False
        finally:
            await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(populate_demo_public_key())
    sys.exit(0 if success else 1)
