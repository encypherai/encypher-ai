"""Add coalition revenue tracking tables

Revision ID: add_coalition_tracking
Revises: add_team_members
Create Date: 2025-11-25

This migration adds:
- coalition_content_stats table for tracking corpus size
- coalition_earnings table for revenue attribution
- coalition_payouts table for tracking payments
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers
revision = 'add_coalition_tracking'
down_revision = 'add_team_members'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create coalition_content_stats table
    # Tracks content corpus size per organization over time
    op.create_table(
        'coalition_content_stats',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('organization_id', sa.String(64), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('documents_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sentences_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_characters', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('unique_content_hash_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('content_categories', JSONB, nullable=True),  # e.g., {"news": 1000, "opinion": 500}
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Create unique constraint on org + period
    op.create_unique_constraint(
        'uq_coalition_content_stats_org_period',
        'coalition_content_stats',
        ['organization_id', 'period_start', 'period_end']
    )
    
    op.create_index(
        'ix_coalition_content_stats_org',
        'coalition_content_stats',
        ['organization_id']
    )
    
    # Create coalition_earnings table
    # Tracks revenue attribution from AI licensing deals
    op.create_table(
        'coalition_earnings',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('organization_id', sa.String(64), nullable=False),
        sa.Column('deal_id', sa.String(64), nullable=False),  # Reference to AI deal
        sa.Column('deal_name', sa.String(255), nullable=True),
        sa.Column('ai_company', sa.String(255), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('gross_revenue_cents', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('publisher_share_percent', sa.Integer(), nullable=False),  # e.g., 65, 70, 80, 85
        sa.Column('publisher_earnings_cents', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('encypher_share_cents', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('attribution_method', sa.String(32), nullable=False),  # corpus_size, usage_based, hybrid
        sa.Column('attribution_weight', sa.Float(), nullable=True),  # Publisher's share of total corpus
        sa.Column('content_stats_id', sa.String(32), nullable=True),  # Reference to content stats
        sa.Column('status', sa.String(32), nullable=False, server_default="'pending'"),  # pending, confirmed, paid
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    op.create_index(
        'ix_coalition_earnings_org',
        'coalition_earnings',
        ['organization_id']
    )
    op.create_index(
        'ix_coalition_earnings_deal',
        'coalition_earnings',
        ['deal_id']
    )
    op.create_index(
        'ix_coalition_earnings_period',
        'coalition_earnings',
        ['period_start', 'period_end']
    )
    op.create_index(
        'ix_coalition_earnings_status',
        'coalition_earnings',
        ['status']
    )
    
    # Create coalition_payouts table
    # Tracks actual payments to publishers
    op.create_table(
        'coalition_payouts',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('organization_id', sa.String(64), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('total_earnings_cents', sa.BigInteger(), nullable=False),
        sa.Column('payout_amount_cents', sa.BigInteger(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default="'USD'"),
        sa.Column('status', sa.String(32), nullable=False, server_default="'pending'"),  # pending, processing, paid, failed
        sa.Column('payment_method', sa.String(32), nullable=True),  # stripe, wire, ach
        sa.Column('payment_reference', sa.String(255), nullable=True),  # External payment ID
        sa.Column('paid_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('earnings_ids', JSONB, nullable=True),  # List of earnings IDs included
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    op.create_index(
        'ix_coalition_payouts_org',
        'coalition_payouts',
        ['organization_id']
    )
    op.create_index(
        'ix_coalition_payouts_status',
        'coalition_payouts',
        ['status']
    )


def downgrade() -> None:
    op.drop_index('ix_coalition_payouts_status')
    op.drop_index('ix_coalition_payouts_org')
    op.drop_table('coalition_payouts')
    
    op.drop_index('ix_coalition_earnings_status')
    op.drop_index('ix_coalition_earnings_period')
    op.drop_index('ix_coalition_earnings_deal')
    op.drop_index('ix_coalition_earnings_org')
    op.drop_table('coalition_earnings')
    
    op.drop_index('ix_coalition_content_stats_org')
    op.drop_constraint('uq_coalition_content_stats_org_period', 'coalition_content_stats')
    op.drop_table('coalition_content_stats')
