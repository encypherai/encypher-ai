"""add licensing agreement management tables

Revision ID: add_licensing_mgmt
Revises: add_c2pa_custom
Create Date: 2025-11-04

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_licensing_mgmt"
down_revision = "add_c2pa_custom"
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


def _create_table_if_missing(table_name: str, *columns: sa.Column, **kwargs: object) -> None:
    if not _has_table(table_name):
        op.create_table(table_name, *columns, **kwargs)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _has_index(table_name, index_name):
        op.create_index(index_name, table_name, columns)


def upgrade() -> None:
    # Create ai_companies table
    _create_table_if_missing(
        "ai_companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_name", sa.String(255), nullable=False, unique=True),
        sa.Column("company_email", sa.String(255), nullable=False),
        sa.Column("api_key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("api_key_prefix", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # Create indexes for ai_companies
    _create_index_if_missing("ix_ai_companies_company_name", "ai_companies", ["company_name"])
    _create_index_if_missing("ix_ai_companies_status", "ai_companies", ["status"])

    # Create licensing_agreements table
    _create_table_if_missing(
        "licensing_agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("agreement_name", sa.String(255), nullable=False),
        sa.Column("ai_company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agreement_type", sa.String(50), nullable=False, server_default="subscription"),
        sa.Column("total_value", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("start_date", sa.DATE(), nullable=False),
        sa.Column("end_date", sa.DATE(), nullable=False),
        sa.Column("content_types", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("min_word_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["ai_company_id"], ["ai_companies.id"], ondelete="CASCADE"),
    )

    # Create indexes for licensing_agreements
    _create_index_if_missing("ix_licensing_agreements_ai_company_id", "licensing_agreements", ["ai_company_id"])
    _create_index_if_missing("ix_licensing_agreements_status", "licensing_agreements", ["status"])
    _create_index_if_missing("ix_licensing_agreements_dates", "licensing_agreements", ["start_date", "end_date"])

    # Create content_access_logs table
    _create_table_if_missing(
        "content_access_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("accessed_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("access_type", sa.String(50), nullable=True),
        sa.Column("ai_company_name", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["agreement_id"], ["licensing_agreements.id"], ondelete="CASCADE"),
    )

    # Create indexes for content_access_logs
    _create_index_if_missing("ix_content_access_logs_agreement_id", "content_access_logs", ["agreement_id"])
    _create_index_if_missing("ix_content_access_logs_content_id", "content_access_logs", ["content_id"])
    _create_index_if_missing("ix_content_access_logs_member_id", "content_access_logs", ["member_id"])
    _create_index_if_missing("ix_content_access_logs_accessed_at", "content_access_logs", ["accessed_at"])

    # Create revenue_distributions table
    _create_table_if_missing(
        "revenue_distributions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.DATE(), nullable=False),
        sa.Column("period_end", sa.DATE(), nullable=False),
        sa.Column("total_revenue", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("encypher_share", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("member_pool", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("processed_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["agreement_id"], ["licensing_agreements.id"], ondelete="CASCADE"),
    )

    # Create indexes for revenue_distributions
    _create_index_if_missing("ix_revenue_distributions_agreement_id", "revenue_distributions", ["agreement_id"])
    _create_index_if_missing("ix_revenue_distributions_period", "revenue_distributions", ["period_start", "period_end"])
    _create_index_if_missing("ix_revenue_distributions_status", "revenue_distributions", ["status"])

    # Create member_revenue table
    _create_table_if_missing(
        "member_revenue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("distribution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("access_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue_amount", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("payment_reference", sa.String(255), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["distribution_id"], ["revenue_distributions.id"], ondelete="CASCADE"),
    )

    # Create indexes for member_revenue
    _create_index_if_missing("ix_member_revenue_distribution_id", "member_revenue", ["distribution_id"])
    _create_index_if_missing("ix_member_revenue_member_id", "member_revenue", ["member_id"])
    _create_index_if_missing("ix_member_revenue_status", "member_revenue", ["status"])


def downgrade() -> None:
    # Drop member_revenue table and indexes
    op.drop_index("ix_member_revenue_status", table_name="member_revenue")
    op.drop_index("ix_member_revenue_member_id", table_name="member_revenue")
    op.drop_index("ix_member_revenue_distribution_id", table_name="member_revenue")
    op.drop_table("member_revenue")

    # Drop revenue_distributions table and indexes
    op.drop_index("ix_revenue_distributions_status", table_name="revenue_distributions")
    op.drop_index("ix_revenue_distributions_period", table_name="revenue_distributions")
    op.drop_index("ix_revenue_distributions_agreement_id", table_name="revenue_distributions")
    op.drop_table("revenue_distributions")

    # Drop content_access_logs table and indexes
    op.drop_index("ix_content_access_logs_accessed_at", table_name="content_access_logs")
    op.drop_index("ix_content_access_logs_member_id", table_name="content_access_logs")
    op.drop_index("ix_content_access_logs_content_id", table_name="content_access_logs")
    op.drop_index("ix_content_access_logs_agreement_id", table_name="content_access_logs")
    op.drop_table("content_access_logs")

    # Drop licensing_agreements table and indexes
    op.drop_index("ix_licensing_agreements_dates", table_name="licensing_agreements")
    op.drop_index("ix_licensing_agreements_status", table_name="licensing_agreements")
    op.drop_index("ix_licensing_agreements_ai_company_id", table_name="licensing_agreements")
    op.drop_table("licensing_agreements")

    # Drop ai_companies table and indexes
    op.drop_index("ix_ai_companies_status", table_name="ai_companies")
    op.drop_index("ix_ai_companies_company_name", table_name="ai_companies")
    op.drop_table("ai_companies")
