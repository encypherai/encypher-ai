"""Add owned_domains table for org domain allowlist

Revision ID: 003
Revises: 002
Create Date: 2026-02-14

Tables: owned_domains
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "owned_domains",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(255), nullable=False, index=True),
        sa.Column("domain_pattern", sa.String(255), nullable=False),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Unique constraint: one pattern per org
    op.create_index(
        "idx_owned_domain_org_pattern",
        "owned_domains",
        ["organization_id", "domain_pattern"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("idx_owned_domain_org_pattern")
    op.drop_table("owned_domains")
