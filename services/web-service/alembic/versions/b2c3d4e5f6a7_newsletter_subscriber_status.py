"""Newsletter subscriber status

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-07 04:20:00.000000

"""

import sqlalchemy as sa

from alembic import op

revision = "b2c3d4e5f6a7"  # pragma: allowlist secret
down_revision = "a1b2c3d4e5f6"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "newsletter_subscribers",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
    )
    op.add_column(
        "newsletter_subscribers",
        sa.Column("status_reason", sa.Text(), nullable=True),
    )
    op.create_index(
        op.f("ix_newsletter_subscribers_status"),
        "newsletter_subscribers",
        ["status"],
        unique=False,
    )
    op.execute(sa.text("UPDATE newsletter_subscribers SET status = CASE WHEN active THEN 'active' ELSE 'unsubscribed' END"))
    op.alter_column("newsletter_subscribers", "status", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_newsletter_subscribers_status"), table_name="newsletter_subscribers")
    op.drop_column("newsletter_subscribers", "status_reason")
    op.drop_column("newsletter_subscribers", "status")
