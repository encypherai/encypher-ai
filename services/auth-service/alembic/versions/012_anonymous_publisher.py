"""Add anonymous_publisher flag to organizations.

Revision ID: 012
Revises: 011
Create Date: 2026-02-14

TEAM_191: Allow orgs to hide their name on verification, showing org ID instead.
"""

from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("anonymous_publisher", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("organizations", "anonymous_publisher")
