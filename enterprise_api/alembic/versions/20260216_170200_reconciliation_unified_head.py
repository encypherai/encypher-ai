"""Create unified reconciled Alembic head for enterprise-api.

Revision ID: 20260216_170200
Revises: 20260216_170000, 20260216_170100
Create Date: 2026-02-16 17:02:00.000000

This revision merges the reconciled core lineage and content baseline so all
future migrations can be forward-only from a single head.
"""

# revision identifiers, used by Alembic.
revision = "20260216_170200"
down_revision = ("20260216_170000", "20260216_170100")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No schema mutation; this revision establishes the unified head.
    pass


def downgrade() -> None:
    # No-op downgrade for lineage-only revision.
    pass
