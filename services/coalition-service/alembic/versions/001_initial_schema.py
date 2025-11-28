"""Initial schema for coalition-service

Revision ID: 001
Revises: 
Create Date: 2024-11-28

Tables: coalition_members, coalition_content, licensing_agreements, 
        content_access_logs, revenue_distributions, member_revenue, coalition_settings
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
    # Coalition members table
    op.create_table(
        'coalition_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True, index=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(20), server_default='active', index=True),
        sa.Column('tier', sa.String(20), nullable=False, index=True),
        sa.Column('opt_out_reason', sa.Text, nullable=True),
        sa.Column('opted_out_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Coalition content table
    op.create_table(
        'coalition_content',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('member_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coalition_members.id'), nullable=False, index=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True, index=True),
        sa.Column('content_hash', sa.String(64), nullable=False, index=True),
        sa.Column('content_type', sa.String(50), nullable=True),
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('verification_count', sa.Integer, server_default='0'),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('indexed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Licensing agreements table
    op.create_table(
        'licensing_agreements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agreement_name', sa.String(255), nullable=False),
        sa.Column('ai_company_name', sa.String(255), nullable=False, index=True),
        sa.Column('ai_company_id', sa.String(255), nullable=True),
        sa.Column('agreement_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='draft', index=True),
        
        # Financial terms
        sa.Column('total_value', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('payment_frequency', sa.String(20), nullable=True),
        
        # Content scope
        sa.Column('content_types', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('min_word_count', sa.Integer, nullable=True),
        sa.Column('date_range_start', sa.Date, nullable=True),
        sa.Column('date_range_end', sa.Date, nullable=True),
        
        # Dates
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('signed_date', sa.Date, nullable=True),
        
        # Metadata
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Content access logs table
    op.create_table(
        'content_access_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agreement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('licensing_agreements.id'), nullable=False, index=True),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coalition_content.id'), nullable=False, index=True),
        sa.Column('member_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coalition_members.id'), nullable=False, index=True),
        sa.Column('accessed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column('access_type', sa.String(50), nullable=True),
        sa.Column('ai_company_name', sa.String(255), nullable=False),
        sa.Column('extra_metadata', postgresql.JSONB, nullable=True),
    )
    
    # Revenue distributions table
    op.create_table(
        'revenue_distributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agreement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('licensing_agreements.id'), nullable=False, index=True),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('total_revenue', sa.Numeric(12, 2), nullable=False),
        sa.Column('encypher_share', sa.Numeric(12, 2), nullable=False),
        sa.Column('member_pool', sa.Numeric(12, 2), nullable=False),
        
        # Distribution calculation
        sa.Column('total_content_count', sa.Integer, nullable=False),
        sa.Column('total_access_count', sa.Integer, nullable=False),
        sa.Column('calculation_method', sa.String(50), nullable=True),
        
        # Status
        sa.Column('status', sa.String(20), server_default='pending', index=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Member revenue table
    op.create_table(
        'member_revenue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('distribution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('revenue_distributions.id'), nullable=False, index=True),
        sa.Column('member_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coalition_members.id'), nullable=False, index=True),
        
        # Content contribution
        sa.Column('content_count', sa.Integer, nullable=False),
        sa.Column('access_count', sa.Integer, nullable=False),
        sa.Column('contribution_percentage', sa.Numeric(5, 2), nullable=False),
        
        # Revenue
        sa.Column('revenue_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        
        # Payment
        sa.Column('status', sa.String(20), server_default='pending', index=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_reference', sa.String(255), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Coalition settings table
    op.create_table(
        'coalition_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('setting_key', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('setting_value', postgresql.JSONB, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('coalition_settings')
    op.drop_table('member_revenue')
    op.drop_table('revenue_distributions')
    op.drop_table('content_access_logs')
    op.drop_table('licensing_agreements')
    op.drop_table('coalition_content')
    op.drop_table('coalition_members')
