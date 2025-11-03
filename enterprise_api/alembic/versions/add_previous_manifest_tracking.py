"""add previous manifest tracking for edit provenance

Revision ID: add_prev_manifest
Revises: free_tier_nullable
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_prev_manifest'
down_revision = 'free_tier_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add column to track previous manifest for edit provenance chain
    op.add_column('content_references', 
                  sa.Column('previous_instance_id', sa.String(), nullable=True))
    
    # Add index for efficient lookups
    op.create_index('ix_content_references_previous_instance_id', 
                    'content_references', 
                    ['previous_instance_id'])


def downgrade() -> None:
    op.drop_index('ix_content_references_previous_instance_id', 
                  table_name='content_references')
    op.drop_column('content_references', 'previous_instance_id')
