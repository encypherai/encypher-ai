"""Add coalition tables

Revision ID: a1b2c3d4e5f6
Revises: 7e4827b6f4e7
Create Date: 2025-11-04 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7e4827b6f4e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create coalition_members table
    op.create_table(
        'coalition_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('joined_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('total_documents', sa.Integer(), nullable=True),
        sa.Column('total_verifications', sa.Integer(), nullable=True),
        sa.Column('total_earned', sa.Float(), nullable=True),
        sa.Column('pending_payout', sa.Float(), nullable=True),
        sa.Column('last_payout_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_payout_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_coalition_member_user', 'coalition_members', ['user_id'], unique=False)
    op.create_index('idx_coalition_member_status', 'coalition_members', ['status'], unique=False)

    # Create content_items table
    op.create_table(
        'content_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.Text(), nullable=True),
        sa.Column('c2pa_manifest_url', sa.Text(), nullable=True),
        sa.Column('verification_count', sa.Integer(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True),
        sa.Column('revenue_generated', sa.Float(), nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_content_user', 'content_items', ['user_id'], unique=False)
    op.create_index('idx_content_type', 'content_items', ['content_type'], unique=False)
    op.create_index('idx_content_signed', 'content_items', ['signed_at'], unique=False)

    # Create revenue_transactions table
    op.create_table(
        'revenue_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['content_id'], ['content_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_revenue_user', 'revenue_transactions', ['user_id'], unique=False)
    op.create_index('idx_revenue_type', 'revenue_transactions', ['transaction_type'], unique=False)
    op.create_index('idx_revenue_status', 'revenue_transactions', ['status'], unique=False)
    op.create_index('idx_revenue_created', 'revenue_transactions', ['created_at'], unique=False)

    # Create content_access_logs table
    op.create_table(
        'content_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ai_company', sa.String(), nullable=False),
        sa.Column('access_type', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('revenue_amount', sa.Float(), nullable=True),
        sa.Column('accessed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content_items.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_access_content', 'content_access_logs', ['content_id'], unique=False)
    op.create_index('idx_access_user', 'content_access_logs', ['user_id'], unique=False)
    op.create_index('idx_access_company', 'content_access_logs', ['ai_company'], unique=False)
    op.create_index('idx_access_date', 'content_access_logs', ['accessed_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_access_date', table_name='content_access_logs')
    op.drop_index('idx_access_company', table_name='content_access_logs')
    op.drop_index('idx_access_user', table_name='content_access_logs')
    op.drop_index('idx_access_content', table_name='content_access_logs')
    op.drop_table('content_access_logs')

    op.drop_index('idx_revenue_created', table_name='revenue_transactions')
    op.drop_index('idx_revenue_status', table_name='revenue_transactions')
    op.drop_index('idx_revenue_type', table_name='revenue_transactions')
    op.drop_index('idx_revenue_user', table_name='revenue_transactions')
    op.drop_table('revenue_transactions')

    op.drop_index('idx_content_signed', table_name='content_items')
    op.drop_index('idx_content_type', table_name='content_items')
    op.drop_index('idx_content_user', table_name='content_items')
    op.drop_table('content_items')

    op.drop_index('idx_coalition_member_status', table_name='coalition_members')
    op.drop_index('idx_coalition_member_user', table_name='coalition_members')
    op.drop_table('coalition_members')
