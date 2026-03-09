"""Add workflow_category and publisher platform extras to organizations

Revision ID: 016
Revises: 015
Create Date: 2026-03-09
"""

from alembic import op
import sqlalchemy as sa


revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("workflow_category", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("publisher_platform_language", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("publisher_platform_other", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "publisher_platform_other")
    op.drop_column("organizations", "publisher_platform_language")
    op.drop_column("organizations", "workflow_category")
