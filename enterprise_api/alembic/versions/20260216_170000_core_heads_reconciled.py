"""Reconcile existing core Alembic heads into a single lineage anchor.

Revision ID: 20260216_170000
Revises: add_batch_requests, add_kms_support, 20260213_190000
Create Date: 2026-02-16 17:00:00.000000

This is a no-op reconciliation revision used to collapse the historical
multi-head graph into a single forward-only path.
"""

# revision identifiers, used by Alembic.
revision = "20260216_170000"
down_revision = ("add_batch_requests", "add_kms_support", "20260213_190000")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No schema mutation; this revision reconciles lineage only.
    pass


def downgrade() -> None:
    # No-op downgrade for lineage-only revision.
    pass
