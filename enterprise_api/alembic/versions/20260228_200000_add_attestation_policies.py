"""Add attestation_policies table for compliance policy engine.

Revision ID: 20260228_200000
Revises: 20260228_100000
Create Date: 2026-02-28 20:00:00.000000

Adds:
- attestation_policies: compliance policy rules that govern attestation
  workflows with per-organization scoping and configurable enforcement.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "20260228_200000"
down_revision = "20260228_100000"
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
    if not _has_table("attestation_policies"):
        op.create_table(
            "attestation_policies",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column("organization_id", sa.String(64), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column(
                "rules",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "enforcement",
                sa.String(20),
                nullable=False,
                server_default=sa.text("'warn'"),
            ),
            sa.Column(
                "scope",
                sa.String(30),
                nullable=False,
                server_default=sa.text("'all'"),
            ),
            sa.Column("scope_value", sa.String(255), nullable=True),
            sa.Column(
                "active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.TIMESTAMP(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["organization_id"],
                ["organizations.id"],
                ondelete="CASCADE",
            ),
        )

    if not _has_index("attestation_policies", "idx_attestation_policies_org"):
        op.create_index(
            "idx_attestation_policies_org",
            "attestation_policies",
            ["organization_id"],
        )
    if not _has_index("attestation_policies", "idx_attestation_policies_active"):
        op.create_index(
            "idx_attestation_policies_active",
            "attestation_policies",
            ["organization_id", "active"],
        )


def downgrade() -> None:
    op.drop_index("idx_attestation_policies_active", table_name="attestation_policies")
    op.drop_index("idx_attestation_policies_org", table_name="attestation_policies")
    op.drop_table("attestation_policies")
