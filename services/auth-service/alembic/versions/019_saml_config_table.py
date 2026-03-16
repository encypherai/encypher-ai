"""Add saml_configs table for SSO

Revision ID: 019
Revises: 018
Create Date: 2026-03-16

Adds saml_configs table to store per-organization SAML IdP configuration
for SSO (Single Sign-On) support.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists."""
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = '{table_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def upgrade() -> None:
    conn = op.get_bind()

    if not table_exists(conn, "saml_configs"):
        op.create_table(
            "saml_configs",
            sa.Column("id", sa.String(64), primary_key=True),
            sa.Column(
                "organization_id",
                sa.String(64),
                sa.ForeignKey("organizations.id", ondelete="CASCADE"),
                nullable=False,
                unique=True,
                index=True,
            ),
            sa.Column("idp_entity_id", sa.String(512), nullable=False),
            sa.Column("idp_sso_url", sa.String(1024), nullable=False),
            sa.Column("idp_certificate", sa.Text(), nullable=False),
            sa.Column("attribute_mapping", sa.JSON(), nullable=True),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )


def downgrade() -> None:
    op.drop_table("saml_configs")
