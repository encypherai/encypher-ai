"""
Populate demo organization's public key in the database.

This script should be run after migration 015 to ensure the demo organization
has its public key stored for Trust Anchor verification.

Supports both:
- Raw Ed25519 keys (32 bytes hex)
- PEM format keys (legacy format from old backend)
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.utils.crypto_utils import get_demo_private_key, serialize_public_key


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


async def populate_demo_public_key():
    """Populate demo organization's public key in database."""
    
    # Try to load from PEM format first (legacy keys)
    if settings.demo_public_key_pem:
        print("Loading public key from PEM format (legacy)")
        try:
            demo_public_key = load_public_key_from_pem(settings.demo_public_key_pem)
            public_key_bytes = serialize_public_key(demo_public_key)
            print("✅ Successfully loaded legacy PEM public key")
        except Exception as e:
            print(f"❌ Failed to load PEM public key: {e}")
            print("Falling back to current key format...")
            demo_private_key = get_demo_private_key()
            demo_public_key = demo_private_key.public_key()
            public_key_bytes = serialize_public_key(demo_public_key)
    elif settings.demo_private_key_pem:
        print("Loading private key from PEM format (legacy) and deriving public key")
        try:
            demo_private_key = load_private_key_from_pem(settings.demo_private_key_pem)
            demo_public_key = demo_private_key.public_key()
            public_key_bytes = serialize_public_key(demo_public_key)
            print("✅ Successfully loaded legacy PEM private key and derived public key")
        except Exception as e:
            print(f"❌ Failed to load PEM private key: {e}")
            print("Falling back to current key format...")
            demo_private_key = get_demo_private_key()
            demo_public_key = demo_private_key.public_key()
            public_key_bytes = serialize_public_key(demo_public_key)
    else:
        # Use current format (raw hex or generated)
        print("Using current key format (raw hex or generated)")
        demo_private_key = get_demo_private_key()
        demo_public_key = demo_private_key.public_key()
        public_key_bytes = serialize_public_key(demo_public_key)
    
    print(f"Demo organization ID: {settings.demo_organization_id}")
    print(f"Public key bytes length: {len(public_key_bytes)}")
    print(f"Public key hex: {public_key_bytes.hex()}")
    
    # Connect to database
    database_url = settings.core_database_url_resolved
    if not database_url:
        print("ERROR: No database URL configured")
        return False
    
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if demo org exists
            result = await session.execute(
                text("SELECT id, name FROM organizations WHERE id = :org_id"),
                {"org_id": settings.demo_organization_id}
            )
            org = result.fetchone()
            
            if not org:
                print(f"WARNING: Demo organization '{settings.demo_organization_id}' not found in database")
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
                        "id": settings.demo_organization_id,
                        "name": settings.demo_organization_name,
                        "email": "demo@encypherai.com",
                        "tier": "enterprise",
                        "public_key": public_key_bytes
                    }
                )
                await session.commit()
                print("✅ Created demo organization with public key")
                return True
            
            print(f"Found demo organization: {org.name}")
            
            # Update public key
            await session.execute(
                text("UPDATE organizations SET public_key = :public_key, updated_at = CURRENT_TIMESTAMP WHERE id = :org_id"),
                {"org_id": settings.demo_organization_id, "public_key": public_key_bytes}
            )
            await session.commit()
            
            print("✅ Updated public key for demo organization")
            
            # Verify
            result = await session.execute(
                text("SELECT public_key FROM organizations WHERE id = :org_id"),
                {"org_id": settings.demo_organization_id}
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
            await session.rollback()
            return False
        finally:
            await engine.dispose()


async def populate_legacy_signer_keys():
    """
    Populate public keys for legacy signer IDs that old content might use.
    
    Old content from the website tools might use signer IDs like:
    - demo-signer-id
    - c2pa-demo-signer-001
    - org_demo
    
    All of these should map to the same demo public key.
    """
    demo_private_key = get_demo_private_key()
    demo_public_key = demo_private_key.public_key()
    public_key_bytes = serialize_public_key(demo_public_key)
    
    legacy_signer_ids = [
        "demo-signer-id",
        "c2pa-demo-signer-001",
    ]
    
    database_url = settings.core_database_url_resolved
    if not database_url:
        print("ERROR: No database URL configured")
        return False
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            for signer_id in legacy_signer_ids:
                # Check if org exists
                result = await session.execute(
                    text("SELECT id FROM organizations WHERE id = :org_id"),
                    {"org_id": signer_id}
                )
                org = result.fetchone()
                
                if not org:
                    print(f"Creating legacy signer organization: {signer_id}")
                    await session.execute(
                        text("""
                            INSERT INTO organizations (
                                id, name, email, tier, public_key,
                                monthly_quota, created_at, updated_at
                            ) VALUES (
                                :id, :name, :email, :tier, :public_key,
                                1000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            )
                        """),
                        {
                            "id": signer_id,
                            "name": f"Legacy Demo Signer ({signer_id})",
                            "email": f"{signer_id}@encypherai.com",
                            "tier": "starter",
                            "public_key": public_key_bytes
                        }
                    )
                    print(f"✅ Created {signer_id} with demo public key")
                else:
                    # Update public key
                    await session.execute(
                        text("UPDATE organizations SET public_key = :public_key WHERE id = :org_id"),
                        {"org_id": signer_id, "public_key": public_key_bytes}
                    )
                    print(f"✅ Updated {signer_id} with demo public key")
            
            await session.commit()
            return True
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            await session.rollback()
            return False
        finally:
            await engine.dispose()


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Populating Demo Organization Public Key")
    print("=" * 60)
    print()
    
    # Populate main demo org
    success = await populate_demo_public_key()
    
    if success:
        print()
        print("=" * 60)
        print("Populating Legacy Signer Public Keys")
        print("=" * 60)
        print()
        
        # Populate legacy signer IDs
        legacy_success = await populate_legacy_signer_keys()
        
        if legacy_success:
            print()
            print("=" * 60)
            print("✅ All public keys populated successfully!")
            print("=" * 60)
            return 0
    
    print()
    print("=" * 60)
    print("❌ Failed to populate public keys")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
