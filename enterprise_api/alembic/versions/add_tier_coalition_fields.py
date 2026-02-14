"""Add tier and coalition fields to organizations

Revision ID: add_tier_coalition
Revises: add_licensing_mgmt
Create Date: 2025-11-25

This migration adds:
- New tier values (starter, business, strategic_partner)
- Coalition membership and revenue share fields
- New feature flags for tier-based access control
- Additional usage tracking fields
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "add_tier_coalition"
down_revision = "add_licensing_mgmt"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(col["name"] == column_name for col in columns)


def _has_pg_type(type_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = :type_name LIMIT 1"),
        {"type_name": type_name},
    )
    return result.scalar() is not None


def upgrade() -> None:
    # Add new columns to organizations table

    # New feature flags
    if not _has_column("organizations", "sentence_tracking_enabled"):
        op.add_column("organizations", sa.Column("sentence_tracking_enabled", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "streaming_enabled"):
        op.add_column("organizations", sa.Column("streaming_enabled", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "byok_enabled"):
        op.add_column("organizations", sa.Column("byok_enabled", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "team_management_enabled"):
        op.add_column("organizations", sa.Column("team_management_enabled", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "audit_logs_enabled"):
        op.add_column("organizations", sa.Column("audit_logs_enabled", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "sso_enabled"):
        op.add_column("organizations", sa.Column("sso_enabled", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "custom_assertions_enabled"):
        op.add_column("organizations", sa.Column("custom_assertions_enabled", sa.Boolean(), nullable=False, server_default="false"))

    # Coalition settings
    if not _has_column("organizations", "coalition_member"):
        op.add_column("organizations", sa.Column("coalition_member", sa.Boolean(), nullable=False, server_default="true"))
    if not _has_column("organizations", "coalition_rev_share_publisher"):
        op.add_column("organizations", sa.Column("coalition_rev_share_publisher", sa.Integer(), nullable=False, server_default="65"))
    if not _has_column("organizations", "coalition_rev_share_encypher"):
        op.add_column("organizations", sa.Column("coalition_rev_share_encypher", sa.Integer(), nullable=False, server_default="35"))
    if not _has_column("organizations", "coalition_opted_out"):
        op.add_column("organizations", sa.Column("coalition_opted_out", sa.Boolean(), nullable=False, server_default="false"))
    if not _has_column("organizations", "coalition_opted_out_at"):
        op.add_column("organizations", sa.Column("coalition_opted_out_at", sa.TIMESTAMP(timezone=True), nullable=True))

    # Additional usage tracking
    if not _has_column("organizations", "sentences_tracked_this_month"):
        op.add_column("organizations", sa.Column("sentences_tracked_this_month", sa.Integer(), nullable=False, server_default="0"))
    if not _has_column("organizations", "batch_operations_this_month"):
        op.add_column("organizations", sa.Column("batch_operations_this_month", sa.Integer(), nullable=False, server_default="0"))

    # Update legacy tier enum only when that PG type exists.
    # Some environments use VARCHAR for organizations.tier, so ALTER TYPE
    # would fail with UndefinedObject unless we guard it.
    if _has_pg_type("organizationtier"):
        op.execute("ALTER TYPE organizationtier ADD VALUE IF NOT EXISTS 'starter'")
        op.execute("ALTER TYPE organizationtier ADD VALUE IF NOT EXISTS 'business'")
        op.execute("ALTER TYPE organizationtier ADD VALUE IF NOT EXISTS 'strategic_partner'")

        # Migrate existing 'free' tier to 'starter' for legacy enum-based schema.
        op.execute("UPDATE organizations SET tier = 'starter' WHERE tier = 'free'")


def downgrade() -> None:
    # Remove columns
    op.drop_column("organizations", "batch_operations_this_month")
    op.drop_column("organizations", "sentences_tracked_this_month")
    op.drop_column("organizations", "coalition_opted_out_at")
    op.drop_column("organizations", "coalition_opted_out")
    op.drop_column("organizations", "coalition_rev_share_encypher")
    op.drop_column("organizations", "coalition_rev_share_publisher")
    op.drop_column("organizations", "coalition_member")
    op.drop_column("organizations", "custom_assertions_enabled")
    op.drop_column("organizations", "sso_enabled")
    op.drop_column("organizations", "audit_logs_enabled")
    op.drop_column("organizations", "team_management_enabled")
    op.drop_column("organizations", "byok_enabled")
    op.drop_column("organizations", "streaming_enabled")
    op.drop_column("organizations", "sentence_tracking_enabled")

    # Note: Cannot easily remove enum values in PostgreSQL
    # Migrate 'starter' back to 'free' if needed
    op.execute("UPDATE organizations SET tier = 'free' WHERE tier = 'starter'")
