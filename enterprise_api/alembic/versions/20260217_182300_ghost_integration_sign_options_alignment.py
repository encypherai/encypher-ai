"""Align Ghost integration signing options with canonical sign schema.

Revision ID: 20260217_182300
Revises: 20260216_170200
Create Date: 2026-02-17 18:23:00.000000

Adds explicit micro-mode option columns (ecc, embed_c2pa) and normalizes
legacy manifest_mode values persisted before canonical schema convergence.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260217_182300"
down_revision = "20260216_170200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ghost_integrations",
        sa.Column("ecc", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "ghost_integrations",
        sa.Column("embed_c2pa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.execute(
        """
        UPDATE ghost_integrations
        SET
            manifest_mode = 'micro',
            ecc = CASE
                WHEN lower(replace(manifest_mode, '-', '_')) IN ('micro_ecc_c2pa', 'micro_ecc') THEN true
                ELSE ecc
            END,
            embed_c2pa = CASE
                WHEN lower(replace(manifest_mode, '-', '_')) = 'micro_ecc_c2pa' THEN true
                WHEN lower(replace(manifest_mode, '-', '_')) = 'micro_ecc' THEN false
                ELSE embed_c2pa
            END
        WHERE lower(replace(manifest_mode, '-', '_')) IN ('micro_ecc_c2pa', 'micro_ecc');
        """
    )


def downgrade() -> None:
    op.drop_column("ghost_integrations", "embed_c2pa")
    op.drop_column("ghost_integrations", "ecc")
