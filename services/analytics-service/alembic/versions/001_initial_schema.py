"""Initial schema for analytics-service

Revision ID: 001
Revises: 
Create Date: 2024-11-28

Tables: usage_metrics, aggregated_metrics
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Usage metrics table (raw events)
    op.create_table(
        'usage_metrics',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.String(64), nullable=False, index=True),
        sa.Column('organization_id', sa.String(64), nullable=True, index=True),

        # Metric details
        sa.Column('metric_type', sa.String(50), nullable=False, index=True),
        sa.Column('service_name', sa.String(50), nullable=False, index=True),
        sa.Column('endpoint', sa.String(255), nullable=True),

        # Counts and values
        sa.Column('count', sa.Integer, server_default='1'),
        sa.Column('value', sa.Numeric(10, 2), nullable=True),

        # Performance
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('status_code', sa.Integer, nullable=True),

        # Metadata
        sa.Column('meta', postgresql.JSONB, nullable=True),

        # Time partitioning keys
        sa.Column('date', sa.String(10), nullable=False, index=True),
        sa.Column('hour', sa.Integer, nullable=False),

        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )

    # Aggregated metrics table (pre-computed)
    op.create_table(
        'aggregated_metrics',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.String(64), nullable=True, index=True),
        sa.Column('organization_id', sa.String(64), nullable=True, index=True),

        # Aggregation details
        sa.Column('metric_type', sa.String(50), nullable=False, index=True),
        sa.Column('service_name', sa.String(50), nullable=False, index=True),
        sa.Column('aggregation_period', sa.String(20), nullable=False, index=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),

        # Aggregated values
        sa.Column('total_count', sa.Integer, server_default='0'),
        sa.Column('total_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('avg_response_time_ms', sa.Numeric(10, 2), nullable=True),
        sa.Column('min_response_time_ms', sa.Integer, nullable=True),
        sa.Column('max_response_time_ms', sa.Integer, nullable=True),
        sa.Column('success_count', sa.Integer, server_default='0'),
        sa.Column('error_count', sa.Integer, server_default='0'),

        # Metadata
        sa.Column('meta', postgresql.JSONB, nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Composite indexes for common queries
    op.create_index('idx_usage_org_date', 'usage_metrics', ['organization_id', 'date'])
    op.create_index('idx_aggregated_org_period', 'aggregated_metrics', ['organization_id', 'period_start'])


def downgrade() -> None:
    op.drop_index('idx_aggregated_org_period')
    op.drop_index('idx_usage_org_date')
    op.drop_table('aggregated_metrics')
    op.drop_table('usage_metrics')
