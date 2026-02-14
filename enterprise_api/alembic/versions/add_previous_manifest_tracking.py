"""add previous manifest tracking for edit provenance

Revision ID: add_prev_manifest
Revises: free_tier_nullable
Create Date: 2025-11-03

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_prev_manifest"
down_revision = "free_tier_nullable"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("content_references")}
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("content_references")}

    # Add column to track previous manifest for edit provenance chain
    if "previous_instance_id" not in existing_columns:
        op.add_column("content_references", sa.Column("previous_instance_id", sa.String(), nullable=True))

    # Add index for efficient lookups
    if "ix_content_references_previous_instance_id" not in existing_indexes:
        op.create_index("ix_content_references_previous_instance_id", "content_references", ["previous_instance_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("content_references")}
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("content_references")}

    if "ix_content_references_previous_instance_id" in existing_indexes:
        op.drop_index("ix_content_references_previous_instance_id", table_name="content_references")
    if "previous_instance_id" in existing_columns:
        op.drop_column("content_references", "previous_instance_id")
