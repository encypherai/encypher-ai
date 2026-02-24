"""Newsletter subscribers

Revision ID: a1b2c3d4e5f6
Revises: f6191c441090
Create Date: 2026-02-23 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f6191c441090"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "newsletter_subscribers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("subscribed_at", sa.DateTime(), nullable=False),
        sa.Column("unsubscribe_token", sa.String(length=64), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("unsubscribe_token"),
    )
    op.create_index(
        op.f("ix_newsletter_subscribers_id"),
        "newsletter_subscribers",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_newsletter_subscribers_email"),
        "newsletter_subscribers",
        ["email"],
        unique=True,
    )
    op.create_index(
        op.f("ix_newsletter_subscribers_active"),
        "newsletter_subscribers",
        ["active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_newsletter_subscribers_active"),
        table_name="newsletter_subscribers",
    )
    op.drop_index(
        op.f("ix_newsletter_subscribers_email"),
        table_name="newsletter_subscribers",
    )
    op.drop_index(
        op.f("ix_newsletter_subscribers_id"),
        table_name="newsletter_subscribers",
    )
    op.drop_table("newsletter_subscribers")
