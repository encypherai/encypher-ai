#!/usr/bin/env python3
"""
Create a test user in the local database for dashboard testing.
"""

import base64
import hashlib
import uuid
from datetime import datetime

import bcrypt
import psycopg2


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with SHA-256 pre-hash."""
    sha256_hash = hashlib.sha256(password.encode("utf-8")).digest()
    prehashed = base64.b64encode(sha256_hash)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prehashed, salt)
    return hashed.decode("utf-8")


def create_test_user():
    """Create a test user in the database."""
    # Test user credentials
    email = "test@encypher.com"
    password = "TestPassword123!"
    name = "Test User"
    user_id = str(uuid.uuid4())

    # Hash the password
    password_hash = get_password_hash(password)

    # Connect to database
    conn = psycopg2.connect(host="localhost", port=5432, database="encypher_core", user="encypher", password="encypher_dev_password")

    try:
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = cur.fetchone()

        if existing:
            print(f"User already exists with id: {existing[0]}")
            print("\nTest credentials:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            return

        # Create the user
        cur.execute(
            """
            INSERT INTO users (id, email, password_hash, name, email_verified, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                user_id,
                email,
                password_hash,
                name,
                True,  # email_verified
                True,  # is_active
                datetime.utcnow(),
                datetime.utcnow(),
            ),
        )

        conn.commit()

        print("✅ Test user created successfully!")
        print("\nTest credentials:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  User ID: {user_id}")

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    create_test_user()
