"""Create explicit baseline for content database reconciliation.

Revision ID: 20260216_170100
Revises:
Create Date: 2026-02-16 17:01:00.000000

This no-op baseline allows controlled stamping of content databases that were
created outside Alembic history.
"""

# revision identifiers, used by Alembic.
revision = "20260216_170100"
down_revision = None
branch_labels = ("content_reconciliation",)
depends_on = None


def upgrade() -> None:
    # Baseline-only revision: intentionally no-op.
    pass


def downgrade() -> None:
    # Baseline-only revision: intentionally no-op.
    pass
