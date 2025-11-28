"""Initial schema for billing-service

Revision ID: 001
Revises: 
Create Date: 2024-11-28

Tables: subscriptions, invoices, payments
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
    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.String(64), nullable=False, index=True),
        sa.Column('organization_id', sa.String(64), nullable=True, index=True),

        sa.Column('plan_id', sa.String(64), nullable=False, index=True),
        sa.Column('plan_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, index=True),

        sa.Column('billing_cycle', sa.String(20), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),

        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cancel_at_period_end', sa.Boolean, server_default='false'),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('stripe_subscription_id', sa.String(255), unique=True),
        sa.Column('stripe_customer_id', sa.String(255)),

        sa.Column('extra_data', postgresql.JSONB, nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('subscription_id', sa.String(64), sa.ForeignKey('subscriptions.id'), nullable=True),
        sa.Column('user_id', sa.String(64), nullable=False, index=True),
        sa.Column('organization_id', sa.String(64), nullable=True, index=True),

        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        sa.Column('status', sa.String(32), nullable=False, index=True),

        sa.Column('amount_due', sa.Numeric(10, 2), nullable=False),
        sa.Column('amount_paid', sa.Numeric(10, 2), server_default='0'),
        sa.Column('currency', sa.String(3), server_default='USD'),

        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('stripe_invoice_id', sa.String(255), unique=True),
        sa.Column('line_items', postgresql.JSONB, nullable=True),
        sa.Column('extra_data', postgresql.JSONB, nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('invoice_id', sa.String(64), sa.ForeignKey('invoices.id'), nullable=True),
        sa.Column('user_id', sa.String(64), nullable=False, index=True),
        sa.Column('organization_id', sa.String(64), nullable=True, index=True),

        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('status', sa.String(32), nullable=False, index=True),

        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), unique=True),

        sa.Column('failure_message', sa.Text, nullable=True),
        sa.Column('extra_data', postgresql.JSONB, nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('invoices')
    op.drop_table('subscriptions')
