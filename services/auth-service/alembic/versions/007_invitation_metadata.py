"""Add invitation metadata fields

Revision ID: 007
Revises: 006
Create Date: 2026-01-29
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organization_invitations",
        sa.Column("first_name", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "organization_invitations",
        sa.Column("last_name", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "organization_invitations",
        sa.Column("organization_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "organization_invitations",
        sa.Column("tier", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "organization_invitations",
        sa.Column("trial_months", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organization_invitations", "trial_months")
    op.drop_column("organization_invitations", "tier")
    op.drop_column("organization_invitations", "organization_name")
    op.drop_column("organization_invitations", "last_name")
    op.drop_column("organization_invitations", "first_name")
