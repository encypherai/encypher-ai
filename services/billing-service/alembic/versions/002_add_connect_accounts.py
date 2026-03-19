"""Add connect_accounts table for Stripe Connect account lookup

Revision ID: 002
Revises: 001
Create Date: 2026-03-19

Tables: connect_accounts
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "connect_accounts",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("stripe_account_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("charges_enabled", sa.Boolean, server_default="false"),
        sa.Column("payouts_enabled", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_connect_accounts_organization_id",
        "connect_accounts",
        ["organization_id"],
        unique=True,
    )
    op.create_index(
        "ix_connect_accounts_stripe_account_id",
        "connect_accounts",
        ["stripe_account_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("connect_accounts")
