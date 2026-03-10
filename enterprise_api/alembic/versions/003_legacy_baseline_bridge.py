"""Legacy baseline bridge revision.

Revision ID: 003
Revises:
Create Date: 2026-02-14

This is a no-op bridge revision so environments that were historically
stamped to legacy Alembic revision id `003` can upgrade into the current
revision graph.
"""

# revision identifiers, used by Alembic.
revision = "003"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Intentionally no-op: this only bridges legacy Alembic state.
    pass


def downgrade() -> None:
    # Intentionally no-op.
    pass
