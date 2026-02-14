"""Add team_members table for Business+ tier

Revision ID: add_team_members
Revises: add_audit_logs
Create Date: 2025-11-25

This migration adds:
- team_members table for organization team management
- team_invites table for pending invitations
- Indexes for efficient querying
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers
revision = "add_team_members"
down_revision = "add_audit_logs"
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


def _has_unique_constraint(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_unique_constraints(table_name)
    return any(constraint.get("name") == constraint_name for constraint in constraints)


def upgrade() -> None:
    # Create team_members table
    if not _has_table("team_members"):
        op.create_table(
            "team_members",
            sa.Column("id", sa.String(32), primary_key=True),
            sa.Column("organization_id", sa.String(64), nullable=False),
            sa.Column("user_id", sa.String(64), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("name", sa.String(255), nullable=True),
            sa.Column("role", sa.String(32), nullable=False),  # owner, admin, member, viewer
            sa.Column("status", sa.String(32), nullable=False, server_default="active"),  # active, suspended
            sa.Column("invited_by", sa.String(64), nullable=True),
            sa.Column("invited_at", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("accepted_at", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("last_active_at", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("permissions", JSONB, nullable=True),  # Custom permission overrides
            sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        )

    # Create unique constraint on org + user
    if not _has_unique_constraint("team_members", "uq_team_members_org_user"):
        op.create_unique_constraint("uq_team_members_org_user", "team_members", ["organization_id", "user_id"])

    # Create indexes
    if not _has_index("team_members", "ix_team_members_org"):
        op.create_index("ix_team_members_org", "team_members", ["organization_id"])
    if not _has_index("team_members", "ix_team_members_user"):
        op.create_index("ix_team_members_user", "team_members", ["user_id"])
    if not _has_index("team_members", "ix_team_members_email"):
        op.create_index("ix_team_members_email", "team_members", ["email"])

    # Create team_invites table for pending invitations
    if not _has_table("team_invites"):
        op.create_table(
            "team_invites",
            sa.Column("id", sa.String(32), primary_key=True),
            sa.Column("organization_id", sa.String(64), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("role", sa.String(32), nullable=False),
            sa.Column("invited_by", sa.String(64), nullable=False),
            sa.Column("invite_token", sa.String(64), nullable=False, unique=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),  # pending, accepted, expired, revoked
            sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
            sa.Column("accepted_at", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    # Create indexes for invites
    if not _has_index("team_invites", "ix_team_invites_org"):
        op.create_index("ix_team_invites_org", "team_invites", ["organization_id"])
    if not _has_index("team_invites", "ix_team_invites_email"):
        op.create_index("ix_team_invites_email", "team_invites", ["email"])
    if not _has_index("team_invites", "ix_team_invites_token"):
        op.create_index("ix_team_invites_token", "team_invites", ["invite_token"])


def downgrade() -> None:
    op.drop_index("ix_team_invites_token")
    op.drop_index("ix_team_invites_email")
    op.drop_index("ix_team_invites_org")
    op.drop_table("team_invites")

    op.drop_index("ix_team_members_email")
    op.drop_index("ix_team_members_user")
    op.drop_index("ix_team_members_org")
    op.drop_constraint("uq_team_members_org_user", "team_members")
    op.drop_table("team_members")
