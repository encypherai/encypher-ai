"""Add dashboard layout and publisher platform to organizations

Revision ID: 015
Revises: 014
Create Date: 2026-03-09
"""

from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "dashboard_layout",
            sa.String(length=32),
            nullable=False,
            server_default="publisher",
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("publisher_platform", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("publisher_platform_custom", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "publisher_platform_custom")
    op.drop_column("organizations", "publisher_platform")
    op.drop_column("organizations", "dashboard_layout")
