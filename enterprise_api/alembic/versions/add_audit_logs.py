"""Add audit_logs table for Business+ tier

Revision ID: add_audit_logs
Revises: add_tier_coalition
Create Date: 2025-11-25

This migration adds:
- audit_logs table for tracking all auditable actions
- Indexes for efficient querying by organization, action, and date
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers
revision = "add_audit_logs"
down_revision = "add_tier_coalition"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(idx.get("name") == index_name for idx in indexes)


def upgrade() -> None:
    # Create audit_logs table
    if not _has_table("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.String(32), primary_key=True),
            sa.Column("organization_id", sa.String(64), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("action", sa.String(64), nullable=False),
            sa.Column("actor_id", sa.String(64), nullable=False),
            sa.Column("actor_type", sa.String(32), nullable=False),  # user, api_key, system
            sa.Column("resource_type", sa.String(64), nullable=False),
            sa.Column("resource_id", sa.String(64), nullable=True),
            sa.Column("details", JSONB, nullable=True),
            sa.Column("ip_address", sa.String(45), nullable=True),  # IPv6 max length
            sa.Column("user_agent", sa.String(512), nullable=True),
        )

    # Create indexes for efficient querying
    if not _has_index("audit_logs", "ix_audit_logs_org_created"):
        op.create_index(
            "ix_audit_logs_org_created",
            "audit_logs",
            ["organization_id", "created_at"],
        )
    if not _has_index("audit_logs", "ix_audit_logs_org_action"):
        op.create_index(
            "ix_audit_logs_org_action",
            "audit_logs",
            ["organization_id", "action"],
        )
    if not _has_index("audit_logs", "ix_audit_logs_actor"):
        op.create_index(
            "ix_audit_logs_actor",
            "audit_logs",
            ["organization_id", "actor_id"],
        )
    if not _has_index("audit_logs", "ix_audit_logs_resource"):
        op.create_index(
            "ix_audit_logs_resource",
            "audit_logs",
            ["organization_id", "resource_type", "resource_id"],
        )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource")
    op.drop_index("ix_audit_logs_actor")
    op.drop_index("ix_audit_logs_org_action")
    op.drop_index("ix_audit_logs_org_created")
    op.drop_table("audit_logs")
