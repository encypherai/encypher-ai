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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("content_references")}
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("content_references")}

    # Add columns to store full C2PA manifest and instance_id for ingredient references
    if "instance_id" not in existing_columns:
        op.add_column("content_references", sa.Column("instance_id", sa.String(), nullable=True))
    if "manifest_data" not in existing_columns:
        op.add_column("content_references", sa.Column("manifest_data", postgresql.JSONB(), nullable=True))

    # Add index for instance_id lookups
    if "ix_content_references_instance_id" not in existing_indexes:
        op.create_index("ix_content_references_instance_id", "content_references", ["instance_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("content_references")}
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("content_references")}

    if "ix_content_references_instance_id" in existing_indexes:
        op.drop_index("ix_content_references_instance_id", table_name="content_references")
    if "manifest_data" in existing_columns:
        op.drop_column("content_references", "manifest_data")
    if "instance_id" in existing_columns:
        op.drop_column("content_references", "instance_id")
