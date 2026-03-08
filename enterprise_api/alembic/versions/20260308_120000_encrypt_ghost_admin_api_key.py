"""Encrypt ghost_integrations.ghost_admin_api_key at rest.

Revision ID: 20260308_120000
Revises: 20260302_100000
Create Date: 2026-03-08 12:00:00.000000

Replaces the plaintext ghost_admin_api_key column with an AES-GCM encrypted
ghost_admin_api_key_encrypted column, consistent with how webhook secrets are
stored.  Existing rows are encrypted in-place during the migration.
"""

import sqlalchemy as sa

from alembic import op

revision = "20260308_120000"
down_revision = "20260302_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new encrypted column (nullable so existing rows can be backfilled)
    op.add_column(
        "ghost_integrations",
        sa.Column("ghost_admin_api_key_encrypted", sa.LargeBinary(600), nullable=True),
    )

    # 2. Encrypt all existing plaintext values
    from app.utils.crypto_utils import encrypt_sensitive_value

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, ghost_admin_api_key FROM ghost_integrations"))
    for row in rows.fetchall():
        plaintext = row[1]
        if plaintext:
            encrypted = encrypt_sensitive_value(plaintext)
            connection.execute(
                sa.text("UPDATE ghost_integrations SET ghost_admin_api_key_encrypted = :enc WHERE id = :id"),
                {"enc": encrypted, "id": row[0]},
            )

    # 3. Make the encrypted column non-nullable now that all rows are backfilled
    op.alter_column("ghost_integrations", "ghost_admin_api_key_encrypted", nullable=False)

    # 4. Drop the old plaintext column
    op.drop_column("ghost_integrations", "ghost_admin_api_key")


def downgrade() -> None:
    # 1. Re-add plaintext column (nullable for the backfill)
    op.add_column(
        "ghost_integrations",
        sa.Column("ghost_admin_api_key", sa.String(500), nullable=True),
    )

    # 2. Decrypt values back to plaintext
    from app.utils.crypto_utils import decrypt_sensitive_value

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, ghost_admin_api_key_encrypted FROM ghost_integrations"))
    for row in rows.fetchall():
        encrypted = row[1]
        if encrypted:
            plaintext = decrypt_sensitive_value(bytes(encrypted))
            connection.execute(
                sa.text("UPDATE ghost_integrations SET ghost_admin_api_key = :plain WHERE id = :id"),
                {"plain": plaintext, "id": row[0]},
            )

    # 3. Make non-nullable
    op.alter_column("ghost_integrations", "ghost_admin_api_key", nullable=False)

    # 4. Drop the encrypted column
    op.drop_column("ghost_integrations", "ghost_admin_api_key_encrypted")
