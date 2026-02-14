"""Add MFA and passkey columns to users.

Revision ID: 013
Revises: 012
Create Date: 2026-02-14

TEAM_191: Phase 2/3 onboarding security hardening.
"""

from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("totp_secret_encrypted", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("totp_enabled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "users",
        sa.Column("totp_backup_code_hashes", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )
    op.add_column(
        "users",
        sa.Column("passkey_credentials", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )
    op.add_column("users", sa.Column("passkey_challenge", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("passkey_challenge_expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "passkey_challenge_expires_at")
    op.drop_column("users", "passkey_challenge")
    op.drop_column("users", "passkey_credentials")
    op.drop_column("users", "totp_backup_code_hashes")
    op.drop_column("users", "totp_enabled_at")
    op.drop_column("users", "totp_secret_encrypted")
    op.drop_column("users", "totp_enabled")
