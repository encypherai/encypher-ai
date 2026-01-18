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


def upgrade() -> None:
    # Create team_members table
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
    op.create_unique_constraint("uq_team_members_org_user", "team_members", ["organization_id", "user_id"])

    # Create indexes
    op.create_index("ix_team_members_org", "team_members", ["organization_id"])
    op.create_index("ix_team_members_user", "team_members", ["user_id"])
    op.create_index("ix_team_members_email", "team_members", ["email"])

    # Create team_invites table for pending invitations
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
    op.create_index("ix_team_invites_org", "team_invites", ["organization_id"])
    op.create_index("ix_team_invites_email", "team_invites", ["email"])
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
