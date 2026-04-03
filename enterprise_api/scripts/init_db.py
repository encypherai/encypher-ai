#!/usr/bin/env python3
"""
Database initialization script for Encypher Enterprise API.

This script:
1. Creates all database tables from init_db.sql
2. Creates a test organization
3. Generates test API keys
4. (Optional) Generates test keypair for the organization
"""

import asyncio
import os
import secrets
from pathlib import Path

import asyncpg
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


async def init_database():
    """Initialize database schema and test data."""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("L DATABASE_URL environment variable not set")
        return

    # Read SQL file
    sql_file = Path(__file__).parent / "init_db.sql"
    if not sql_file.exists():
        print(f"L SQL file not found: {sql_file}")
        return

    schema_sql = sql_file.read_text()

    # Connect to database
    print("= Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Execute schema
        print("=Ë Creating database schema...")
        await conn.execute(schema_sql)
        print(" Database schema initialized")

        # Check if test organization exists
        existing = await conn.fetchval("SELECT organization_id FROM organizations WHERE organization_id = 'test_org_001'")

        if existing:
            print("9  Test organization already exists")
        else:
            # Create test organization
            print("=e Creating test organization...")
            await conn.execute("""
                INSERT INTO organizations
                (organization_id, organization_name, organization_type, email, tier)
                VALUES ('test_org_001', 'Encypher Test Publisher', 'publisher', 'test@encypher.com', 'enterprise')
            """)
            print(" Test organization created")

        # Generate test keypair (Ed25519)
        print("= Generating Ed25519 keypair for test organization...")
        private_key = ed25519.Ed25519PrivateKey.generate()

        # Encrypt private key
        key_encryption_key = os.getenv("KEY_ENCRYPTION_KEY")
        encryption_nonce = os.getenv("ENCRYPTION_NONCE")

        if key_encryption_key and encryption_nonce:
            from cryptography.hazmat.primitives import serialization

            # Serialize private key
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw, encryption_algorithm=serialization.NoEncryption()
            )

            # Encrypt
            aesgcm = AESGCM(bytes.fromhex(key_encryption_key))
            encrypted_key = aesgcm.encrypt(bytes.fromhex(encryption_nonce), private_bytes, None)

            # Store encrypted key
            await conn.execute(
                """
                UPDATE organizations
                SET private_key_encrypted = $1
                WHERE organization_id = 'test_org_001'
            """,
                encrypted_key,
            )
            print(" Keypair generated and stored (encrypted)")
        else:
            print("   Encryption keys not set - skipping keypair storage")

        # Check if test API key exists
        existing_key = await conn.fetchval("SELECT api_key FROM api_keys WHERE organization_id = 'test_org_001'")

        if existing_key:
            print(f"9  Test API key already exists: {existing_key}")
        else:
            # Generate test API key
            test_api_key = f"encypher_test_{secrets.token_urlsafe(32)}"
            await conn.execute(
                """
                INSERT INTO api_keys (api_key, organization_id, key_name)
                VALUES ($1, 'test_org_001', 'Test API Key')
            """,
                test_api_key,
            )
            print(f" Test API key created: {test_api_key}")
            print("\n=Ë Save this API key for testing:")
            print(f"   {test_api_key}\n")

        print(" Database initialization complete!")

    except Exception as e:
        print(f"L Error during initialization: {e}")
        raise
    finally:
        await conn.close()
        print("=K Database connection closed")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    asyncio.run(init_database())
