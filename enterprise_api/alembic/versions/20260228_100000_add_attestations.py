"""Add attestations table for Encypher Attest platform.

Revision ID: 20260228_100000
Revises: 20260227_110000
Create Date: 2026-02-28 10:00:00.000000

Adds:
- attestations: AI content attestation records linking reviewer/model metadata
  to C2PA provenance chains, with diff reports and review tracking.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "20260228_100000"
down_revision = "20260227_110000"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(idx.get("name") == index_name for idx in indexes)


def upgrade() -> None:
    if not _has_table("attestations"):
        op.create_table(
            "attestations",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column("organization_id", sa.String(64), nullable=False),
            sa.Column("document_id", sa.String(255), nullable=False),
            sa.Column(
                "attestation_id",
                postgresql.UUID(as_uuid=True),
                nullable=False,
                unique=True,
            ),
            sa.Column("reviewer_identity", sa.String(255), nullable=True),
            sa.Column("reviewer_role", sa.String(100), nullable=True),
            sa.Column("model_name", sa.String(255), nullable=True),
            sa.Column("model_version", sa.String(100), nullable=True),
            sa.Column("model_provider", sa.String(255), nullable=True),
            sa.Column("prompt_hash", sa.CHAR(64), nullable=True),
            sa.Column(
                "human_reviewed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("generation_timestamp", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("review_timestamp", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("review_notes", sa.Text(), nullable=True),
            sa.Column("original_instance_id", sa.String(255), nullable=True),
            sa.Column("attested_instance_id", sa.String(255), nullable=True),
            sa.Column(
                "diff_report",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "status",
                sa.String(50),
                nullable=False,
                server_default=sa.text("'active'"),
            ),
            sa.ForeignKeyConstraint(
                ["organization_id"],
                ["organizations.id"],
                ondelete="CASCADE",
            ),
        )

    if not _has_index("attestations", "idx_attestations_org_date"):
        op.create_index(
            "idx_attestations_org_date",
            "attestations",
            ["organization_id", "created_at"],
        )
    if not _has_index("attestations", "idx_attestations_reviewer"):
        op.create_index(
            "idx_attestations_reviewer",
            "attestations",
            ["reviewer_identity"],
        )
    if not _has_index("attestations", "idx_attestations_model"):
        op.create_index(
            "idx_attestations_model",
            "attestations",
            ["model_name"],
        )


def downgrade() -> None:
    op.drop_index("idx_attestations_model", table_name="attestations")
    op.drop_index("idx_attestations_reviewer", table_name="attestations")
    op.drop_index("idx_attestations_org_date", table_name="attestations")
    op.drop_table("attestations")
