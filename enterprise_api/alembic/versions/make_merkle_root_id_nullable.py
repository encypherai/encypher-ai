"""make merkle_root_id nullable for free tier

Revision ID: free_tier_nullable
Revises: 
Create Date: 2025-11-02 00:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'free_tier_nullable'
down_revision = None  # Update this if there are previous migrations
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make merkle_root_id nullable to support free tier (no Merkle tree)
    op.alter_column('content_references', 'merkle_root_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=True)


def downgrade() -> None:
    # Revert to NOT NULL
    op.alter_column('content_references', 'merkle_root_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=False)
