"""add kms support to organizations

Revision ID: add_kms_support
Revises: add_org_certificate_metadata
Create Date: 2025-11-21 19:00:00

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_kms_support"
down_revision = "add_org_certificate_metadata"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(col.get("name") == column_name for col in columns)


def upgrade() -> None:
    if not _has_column("organizations", "kms_key_id"):
        op.add_column("organizations", sa.Column("kms_key_id", sa.String(255), nullable=True))
    if not _has_column("organizations", "kms_region"):
        op.add_column("organizations", sa.Column("kms_region", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("organizations", "kms_region")
    op.drop_column("organizations", "kms_key_id")
