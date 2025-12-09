"""Team management - organizations, members, invitations, audit logs

Revision ID: 002
Revises: 001
Create Date: 2025-11-28

Adds team management tables:
- organizations
- organization_members
- organization_invitations
- organization_audit_log
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import INET, JSONB

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def index_exists(conn, index_name: str) -> bool:
    """Check if an index exists."""
    sql = f"""
        SELECT EXISTS (
            SELECT FROM pg_indexes WHERE indexname = '{index_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def upgrade() -> None:
    conn = op.get_bind()

    # =========================================
    # ORGANIZATIONS TABLE
    # =========================================
    if not table_exists(conn, "organizations"):
        op.create_table(
            "organizations",
            sa.Column("id", sa.String(64), primary_key=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("slug", sa.String(100), unique=True, nullable=True),
            sa.Column("email", sa.String(255), unique=True, nullable=False),
            # Subscription & Tier
            sa.Column("tier", sa.String(32), nullable=False, server_default="starter"),
            # Stripe Integration
            sa.Column("stripe_customer_id", sa.String(255), unique=True, nullable=True),
            sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
            sa.Column("subscription_status", sa.String(32), server_default="active"),
            # Feature Flags
            sa.Column("features", JSONB, nullable=False, server_default="{}"),
            # Usage Limits
            sa.Column("monthly_api_limit", sa.Integer(), server_default="10000"),
            sa.Column("monthly_api_usage", sa.Integer(), server_default="0"),
            sa.Column("usage_reset_at", sa.DateTime(timezone=True), nullable=True),
            # Team Management
            sa.Column("max_seats", sa.Integer(), server_default="1"),
            # Coalition Revenue Sharing
            sa.Column("coalition_member", sa.Boolean(), server_default="true"),
            sa.Column("coalition_rev_share", sa.Integer(), server_default="65"),
            sa.Column("coalition_opted_out", sa.Boolean(), server_default="false"),
            # Timestamps
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not index_exists(conn, "ix_organizations_slug"):
        op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    if not index_exists(conn, "ix_organizations_tier"):
        op.create_index("ix_organizations_tier", "organizations", ["tier"])

    # =========================================
    # ORGANIZATION MEMBERS TABLE
    # =========================================
    if not table_exists(conn, "organization_members"):
        op.create_table(
            "organization_members",
            sa.Column("id", sa.String(64), primary_key=True),
            sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            # Role & Permissions
            sa.Column("role", sa.String(32), nullable=False, server_default="member"),
            # Status
            sa.Column("status", sa.String(32), nullable=False, server_default="active"),
            # Invitation tracking
            sa.Column("invited_by", sa.String(64), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
            # Activity
            sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
            # Timestamps
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            # Unique constraint
            sa.UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
        )

    if not index_exists(conn, "ix_org_members_org"):
        op.create_index("ix_org_members_org", "organization_members", ["organization_id"])
    if not index_exists(conn, "ix_org_members_user"):
        op.create_index("ix_org_members_user", "organization_members", ["user_id"])

    # =========================================
    # ORGANIZATION INVITATIONS TABLE
    # =========================================
    if not table_exists(conn, "organization_invitations"):
        op.create_table(
            "organization_invitations",
            sa.Column("id", sa.String(64), primary_key=True),
            sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            # Invitation details
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("role", sa.String(32), nullable=False, server_default="member"),
            # Token for accepting invitation
            sa.Column("token", sa.String(255), nullable=False, unique=True),
            # Tracking
            sa.Column("invited_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("message", sa.Text(), nullable=True),
            # Status
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            # Lifecycle
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not index_exists(conn, "ix_org_invitations_org"):
        op.create_index("ix_org_invitations_org", "organization_invitations", ["organization_id"])
    if not index_exists(conn, "ix_org_invitations_email"):
        op.create_index("ix_org_invitations_email", "organization_invitations", ["email"])
    if not index_exists(conn, "ix_org_invitations_token"):
        op.create_index("ix_org_invitations_token", "organization_invitations", ["token"], unique=True)

    # =========================================
    # ORGANIZATION AUDIT LOG TABLE
    # =========================================
    if not table_exists(conn, "organization_audit_log"):
        op.create_table(
            "organization_audit_log",
            sa.Column("id", sa.String(64), primary_key=True),
            sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            # Actor
            sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("user_email", sa.String(255), nullable=True),
            # Action details
            sa.Column("action", sa.String(100), nullable=False),
            sa.Column("resource_type", sa.String(50), nullable=True),
            sa.Column("resource_id", sa.String(64), nullable=True),
            # Change details
            sa.Column("details", JSONB, nullable=True),
            # Request metadata
            sa.Column("ip_address", INET, nullable=True),
            sa.Column("user_agent", sa.Text(), nullable=True),
            # Timestamp
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not index_exists(conn, "ix_audit_log_org"):
        op.create_index("ix_audit_log_org", "organization_audit_log", ["organization_id"])
    if not index_exists(conn, "ix_audit_log_user"):
        op.create_index("ix_audit_log_user", "organization_audit_log", ["user_id"])
    if not index_exists(conn, "ix_audit_log_action"):
        op.create_index("ix_audit_log_action", "organization_audit_log", ["action"])

    # =========================================
    # ADD default_organization_id TO USERS
    # =========================================
    if not column_exists(conn, "users", "default_organization_id"):
        op.add_column("users", sa.Column("default_organization_id", sa.String(64), nullable=True))


def downgrade() -> None:
    # Remove column from users
    op.drop_column("users", "default_organization_id")

    # Drop tables in reverse order
    op.drop_table("organization_audit_log")
    op.drop_table("organization_invitations")
    op.drop_table("organization_members")
    op.drop_table("organizations")
