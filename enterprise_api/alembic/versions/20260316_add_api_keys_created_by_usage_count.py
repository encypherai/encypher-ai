"""Add created_by and usage_count columns to api_keys

Revision ID: 20260316_120000
Revises: 20260316_110000
Create Date: 2026-03-16

Adds created_by (tracks which user created a key) and usage_count
(per-key call counter) to support team key management and usage stats.
"""

import sqlalchemy as sa
from alembic import op

revision = "20260316_120000"
down_revision = "20260316_110000"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    return column_name in columns


def upgrade() -> None:
    if not _has_column("api_keys", "created_by"):
        op.add_column(
            "api_keys",
            sa.Column("created_by", sa.String(255), nullable=True),
        )
        op.create_index("ix_api_keys_created_by", "api_keys", ["created_by"])
    if not _has_column("api_keys", "usage_count"):
        op.add_column(
            "api_keys",
            sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    if _has_column("api_keys", "usage_count"):
        op.drop_column("api_keys", "usage_count")
    if _has_column("api_keys", "created_by"):
        op.drop_index("ix_api_keys_created_by", table_name="api_keys")
        op.drop_column("api_keys", "created_by")
