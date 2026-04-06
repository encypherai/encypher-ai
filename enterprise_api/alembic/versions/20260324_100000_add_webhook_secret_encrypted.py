"""Add secret_encrypted column to webhooks

Revision ID: 20260324_100000
Revises: 20260316_120000
Create Date: 2026-03-24

Adds secret_encrypted BYTEA column to webhooks table for encrypted
webhook shared secret storage. Corresponds to raw SQL migration 023.
"""

import sqlalchemy as sa
from alembic import op

revision = "20260324_100000"
down_revision = "20260316_120000"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT 1 FROM information_schema.columns WHERE table_name = :table AND column_name = :col"),
        {"table": table_name, "col": column_name},
    )
    return result.fetchone() is not None


def upgrade() -> None:
    if not _has_column("webhooks", "secret_encrypted"):
        op.add_column(
            "webhooks",
            sa.Column("secret_encrypted", sa.LargeBinary(), nullable=True, comment="Encrypted webhook shared secret for outbound signing"),
        )


def downgrade() -> None:
    if _has_column("webhooks", "secret_encrypted"):
        op.drop_column("webhooks", "secret_encrypted")
