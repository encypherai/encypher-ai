"""Add usage_records table for metering and billing

Revision ID: 20251125_150700
Revises: 20251125_150600
Create Date: 2025-11-25 15:07:00

This migration adds:
- usage_records table for tracking billable usage metrics
- Supports time-series usage data for billing calculations
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers
revision = "20251125_150700"
down_revision = "20251125_150600"
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


def _has_unique_constraint(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_unique_constraints(table_name)
    return any(constraint.get("name") == constraint_name for constraint in constraints)


def upgrade() -> None:
    if not _has_table("usage_records"):
        op.create_table(
            "usage_records",
            sa.Column("id", sa.String(32), primary_key=True),
            sa.Column("organization_id", sa.String(64), nullable=False),
            # Usage metric
            sa.Column("metric", sa.String(64), nullable=False),  # c2pa_signatures, sentences_tracked, api_calls, batch_operations
            sa.Column("count", sa.BigInteger(), nullable=False, server_default="0"),
            sa.Column("unit", sa.String(32), nullable=True),  # documents, sentences, calls, operations
            # Time period
            sa.Column("period_start", sa.TIMESTAMP(timezone=True), nullable=False),
            sa.Column("period_end", sa.TIMESTAMP(timezone=True), nullable=False),
            sa.Column("period_type", sa.String(16), nullable=False, server_default="monthly"),  # hourly, daily, monthly
            # Billing info
            sa.Column("billable", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("billed", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("invoice_id", sa.String(64), nullable=True),
            # Rate info (for overage billing)
            sa.Column("rate_cents", sa.Integer(), nullable=True),  # Price per unit for overages
            sa.Column("included_in_plan", sa.BigInteger(), nullable=True),  # Units included in plan
            sa.Column("overage_count", sa.BigInteger(), nullable=True),  # Units over plan limit
            sa.Column("overage_amount_cents", sa.BigInteger(), nullable=True),
            # Metadata
            sa.Column("metadata", JSONB, nullable=True),
            sa.Column("recorded_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    # Unique constraint on org + metric + period
    if not _has_unique_constraint("usage_records", "uq_usage_records_org_metric_period"):
        op.create_unique_constraint("uq_usage_records_org_metric_period", "usage_records", ["organization_id", "metric", "period_start", "period_end"])

    # Indexes
    if not _has_index("usage_records", "ix_usage_records_org_id"):
        op.create_index("ix_usage_records_org_id", "usage_records", ["organization_id"])
    if not _has_index("usage_records", "ix_usage_records_metric"):
        op.create_index("ix_usage_records_metric", "usage_records", ["metric"])
    if not _has_index("usage_records", "ix_usage_records_period"):
        op.create_index("ix_usage_records_period", "usage_records", ["period_start", "period_end"])
    if not _has_index("usage_records", "ix_usage_records_org_metric"):
        op.create_index("ix_usage_records_org_metric", "usage_records", ["organization_id", "metric"])
    if not _has_index("usage_records", "ix_usage_records_billed"):
        op.create_index("ix_usage_records_billed", "usage_records", ["billed"])


def downgrade() -> None:
    op.drop_index("ix_usage_records_billed")
    op.drop_index("ix_usage_records_org_metric")
    op.drop_index("ix_usage_records_period")
    op.drop_index("ix_usage_records_metric")
    op.drop_index("ix_usage_records_org_id")
    op.drop_constraint("uq_usage_records_org_metric_period", "usage_records")
    op.drop_table("usage_records")
