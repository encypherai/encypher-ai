"""Add organization_subscriptions table for Stripe subscription tracking

Revision ID: 20251125_150600
Revises: add_coalition_tracking
Create Date: 2025-11-25 15:06:00

This migration adds:
- organization_subscriptions table for tracking Stripe subscriptions
- Links organizations to their subscription tier and billing status
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers
revision = '20251125_150600'
down_revision = 'add_coalition_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'organization_subscriptions',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('organization_id', sa.String(64), nullable=False, unique=True),
        sa.Column('tier_id', sa.String(32), nullable=False),  # starter, professional, business, enterprise
        sa.Column('status', sa.String(32), nullable=False, server_default='active'),  # active, past_due, canceled, trialing
        
        # Stripe integration
        sa.Column('stripe_customer_id', sa.String(64), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(64), nullable=True),
        sa.Column('stripe_price_id', sa.String(64), nullable=True),
        
        # Billing period
        sa.Column('current_period_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default='false'),
        
        # Trial info
        sa.Column('trial_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('trial_end', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Pricing
        sa.Column('billing_interval', sa.String(16), nullable=False, server_default='monthly'),  # monthly, annual
        sa.Column('price_cents', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        
        # Metadata
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Indexes
    op.create_index(
        'ix_org_subscriptions_org_id',
        'organization_subscriptions',
        ['organization_id']
    )
    op.create_index(
        'ix_org_subscriptions_stripe_customer',
        'organization_subscriptions',
        ['stripe_customer_id']
    )
    op.create_index(
        'ix_org_subscriptions_stripe_sub',
        'organization_subscriptions',
        ['stripe_subscription_id']
    )
    op.create_index(
        'ix_org_subscriptions_status',
        'organization_subscriptions',
        ['status']
    )


def downgrade() -> None:
    op.drop_index('ix_org_subscriptions_status')
    op.drop_index('ix_org_subscriptions_stripe_sub')
    op.drop_index('ix_org_subscriptions_stripe_customer')
    op.drop_index('ix_org_subscriptions_org_id')
    op.drop_table('organization_subscriptions')
