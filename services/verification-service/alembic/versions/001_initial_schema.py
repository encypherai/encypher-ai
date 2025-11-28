"""Initial schema for verification-service

Revision ID: 001
Revises: 
Create Date: 2024-11-28

Tables: verification_results, verification_logs
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
    # Verification results table
    op.create_table(
        'verification_results',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('document_id', sa.String(64), nullable=False, index=True),
        sa.Column('user_id', sa.String(64), nullable=True, index=True),
        sa.Column('organization_id', sa.String(64), nullable=True, index=True),
        
        # Verification details
        sa.Column('is_valid', sa.Boolean, nullable=False),
        sa.Column('is_tampered', sa.Boolean, server_default='false'),
        sa.Column('signature_valid', sa.Boolean, nullable=False),
        sa.Column('hash_valid', sa.Boolean, nullable=False),
        
        # Scores and metrics
        sa.Column('confidence_score', sa.Numeric(5, 4), server_default='0'),
        sa.Column('similarity_score', sa.Numeric(5, 4), nullable=True),
        
        # Content information
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('signature', sa.Text, nullable=False),
        sa.Column('signer_id', sa.String(64), nullable=True),
        
        # Verification metadata
        sa.Column('verification_method', sa.String(50), server_default='signature'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('warnings', postgresql.JSONB, nullable=True),
        
        # Performance
        sa.Column('verification_time_ms', sa.Integer, nullable=True),
        
        # Client info
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )
    
    # Verification audit log
    op.create_table(
        'verification_logs',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('document_id', sa.String(64), nullable=False, index=True),
        sa.Column('user_id', sa.String(64), nullable=True, index=True),
        
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('result', sa.String(20), nullable=False),
        
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table('verification_logs')
    op.drop_table('verification_results')
