"""Add organization trial metadata fields.

Revision ID: 008
Revises: 007
Create Date: 2026-01-29
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("trial_tier", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("trial_months", sa.Integer(), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "trial_ends_at")
    op.drop_column("organizations", "trial_started_at")
    op.drop_column("organizations", "trial_months")
    op.drop_column("organizations", "trial_tier")
