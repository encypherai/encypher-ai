"""add original_text column to attestations

Revision ID: 20260302_100000
Revises: 20260228_200000_add_attestation_policies
Create Date: 2026-03-02 10:00:00
"""

import sqlalchemy as sa

from alembic import op

revision = "20260302_100000"
down_revision = "20260228_200000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "attestations",
        sa.Column("original_text", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("attestations", "original_text")
