"""Add custom verification domain columns to organizations

Revision ID: 018
Revises: 017
Create Date: 2026-03-15

Adds verification_domain, verification_domain_status, verification_domain_dns_token,
and verification_domain_verified_at to organizations for custom verification domain support.
"""

import sqlalchemy as sa
from alembic import op

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("verification_domain", sa.String(255), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("verification_domain_status", sa.String(32), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("verification_domain_dns_token", sa.String(255), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("verification_domain_verified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "verification_domain_verified_at")
    op.drop_column("organizations", "verification_domain_dns_token")
    op.drop_column("organizations", "verification_domain_status")
    op.drop_column("organizations", "verification_domain")
