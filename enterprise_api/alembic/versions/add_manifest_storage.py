"""add manifest storage for ingredient references

Revision ID: add_manifest_storage
Revises: add_prev_manifest
Create Date: 2025-11-03

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_manifest_storage"
down_revision = "add_prev_manifest"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to store full C2PA manifest and instance_id for ingredient references
    op.add_column("content_references", sa.Column("instance_id", sa.String(), nullable=True))
    op.add_column("content_references", sa.Column("manifest_data", postgresql.JSONB(), nullable=True))

    # Add index for instance_id lookups
    op.create_index("ix_content_references_instance_id", "content_references", ["instance_id"])


def downgrade() -> None:
    op.drop_index("ix_content_references_instance_id", table_name="content_references")
    op.drop_column("content_references", "manifest_data")
    op.drop_column("content_references", "instance_id")
