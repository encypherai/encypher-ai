"""Add is_super_admin field and set default super admin

Revision ID: 004_add_super_admin
Revises: 003_api_access_gating
Create Date: 2025-12-09

TEAM_006: Add super admin functionality for API access approval
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None

# Default super admin email
DEFAULT_SUPER_ADMIN_EMAIL = "erik.svilich@encypher.com"


def upgrade() -> None:
    # Add is_super_admin column with default False
    op.add_column("users", sa.Column("is_super_admin", sa.Boolean(), nullable=False, server_default="false"))

    # Set erik.svilich@encypher.com as super admin if they exist
    op.execute(f"""
        UPDATE users
        SET is_super_admin = true
        WHERE email = '{DEFAULT_SUPER_ADMIN_EMAIL}'
    """)


def downgrade() -> None:
    op.drop_column("users", "is_super_admin")
