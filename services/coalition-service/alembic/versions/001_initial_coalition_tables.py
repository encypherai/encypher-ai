"""Initial coalition tables

Revision ID: 001
Revises:
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create coalition_members table
    op.create_table(
        'coalition_members',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('organization_id', UUID(as_uuid=True), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('tier', sa.String(20), nullable=False),
        sa.Column('opt_out_reason', sa.Text(), nullable=True),
        sa.Column('opted_out_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_coalition_members_user_id', 'coalition_members', ['user_id'])
    op.create_index('ix_coalition_members_status', 'coalition_members', ['status'])
    op.create_index('ix_coalition_members_tier', 'coalition_members', ['tier'])

    # Create coalition_content table
    op.create_table(
        'coalition_content',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('member_id', UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.Column('verification_count', sa.Integer(), server_default='0'),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True),
        sa.Column('indexed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['member_id'], ['coalition_members.id']),
    )
    op.create_index('ix_coalition_content_member_id', 'coalition_content', ['member_id'])
    op.create_index('ix_coalition_content_document_id', 'coalition_content', ['document_id'])
    op.create_index('ix_coalition_content_content_hash', 'coalition_content', ['content_hash'])
    op.create_index('ix_coalition_content_signed_at', 'coalition_content', ['signed_at'])

    # Create licensing_agreements table
    op.create_table(
        'licensing_agreements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('agreement_name', sa.String(255), nullable=False),
        sa.Column('ai_company_name', sa.String(255), nullable=False),
        sa.Column('ai_company_id', sa.String(255), nullable=True),
        sa.Column('agreement_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('total_value', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('payment_frequency', sa.String(20), nullable=True),
        sa.Column('content_types', ARRAY(sa.Text()), nullable=True),
        sa.Column('min_word_count', sa.Integer(), nullable=True),
        sa.Column('date_range_start', sa.Date(), nullable=True),
        sa.Column('date_range_end', sa.Date(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('signed_date', sa.Date(), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_licensing_agreements_ai_company_name', 'licensing_agreements', ['ai_company_name'])
    op.create_index('ix_licensing_agreements_status', 'licensing_agreements', ['status'])

    # Create content_access_logs table
    op.create_table(
        'content_access_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('agreement_id', UUID(as_uuid=True), nullable=False),
        sa.Column('content_id', UUID(as_uuid=True), nullable=False),
        sa.Column('member_id', UUID(as_uuid=True), nullable=False),
        sa.Column('accessed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('access_type', sa.String(50), nullable=True),
        sa.Column('ai_company_name', sa.String(255), nullable=False),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['agreement_id'], ['licensing_agreements.id']),
        sa.ForeignKeyConstraint(['content_id'], ['coalition_content.id']),
        sa.ForeignKeyConstraint(['member_id'], ['coalition_members.id']),
    )
    op.create_index('ix_content_access_logs_agreement_id', 'content_access_logs', ['agreement_id'])
    op.create_index('ix_content_access_logs_content_id', 'content_access_logs', ['content_id'])
    op.create_index('ix_content_access_logs_member_id', 'content_access_logs', ['member_id'])
    op.create_index('ix_content_access_logs_accessed_at', 'content_access_logs', ['accessed_at'])

    # Create revenue_distributions table
    op.create_table(
        'revenue_distributions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('agreement_id', UUID(as_uuid=True), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('total_revenue', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('encypher_share', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('member_pool', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('total_content_count', sa.Integer(), nullable=False),
        sa.Column('total_access_count', sa.Integer(), nullable=False),
        sa.Column('calculation_method', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('calculated_at', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['agreement_id'], ['licensing_agreements.id']),
    )
    op.create_index('ix_revenue_distributions_agreement_id', 'revenue_distributions', ['agreement_id'])
    op.create_index('ix_revenue_distributions_status', 'revenue_distributions', ['status'])

    # Create member_revenue table
    op.create_table(
        'member_revenue',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('distribution_id', UUID(as_uuid=True), nullable=False),
        sa.Column('member_id', UUID(as_uuid=True), nullable=False),
        sa.Column('content_count', sa.Integer(), nullable=False),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.Column('contribution_percentage', sa.DECIMAL(5, 2), nullable=False),
        sa.Column('revenue_amount', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_reference', sa.String(255), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['distribution_id'], ['revenue_distributions.id']),
        sa.ForeignKeyConstraint(['member_id'], ['coalition_members.id']),
    )
    op.create_index('ix_member_revenue_distribution_id', 'member_revenue', ['distribution_id'])
    op.create_index('ix_member_revenue_member_id', 'member_revenue', ['member_id'])
    op.create_index('ix_member_revenue_status', 'member_revenue', ['status'])

    # Create coalition_settings table
    op.create_table(
        'coalition_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('setting_key', sa.String(100), nullable=False, unique=True),
        sa.Column('setting_value', JSONB(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_coalition_settings_setting_key', 'coalition_settings', ['setting_key'])

    # Insert initial coalition settings
    op.execute(
        """
        INSERT INTO coalition_settings (id, setting_key, setting_value, description)
        VALUES
            (gen_random_uuid(), 'revenue_split', '{"encypher": 30, "members": 70}', 'Revenue split percentage'),
            (gen_random_uuid(), 'auto_onboard_free_tier', 'true', 'Automatically onboard free tier users'),
            (gen_random_uuid(), 'min_payout_threshold', '{"amount": 10, "currency": "USD"}', 'Minimum payout amount')
        """
    )


def downgrade() -> None:
    op.drop_table('member_revenue')
    op.drop_table('revenue_distributions')
    op.drop_table('content_access_logs')
    op.drop_table('licensing_agreements')
    op.drop_table('coalition_content')
    op.drop_table('coalition_settings')
    op.drop_table('coalition_members')
