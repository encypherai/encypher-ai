"""Initial schema for key-service

Revision ID: 001
Revises: 
Create Date: 2024-11-28

This migration creates the core tables for key-service:
- organizations: Billing entities that own API keys
- api_keys: API keys for authentication
- key_usage: Usage tracking for API keys
- key_rotations: Audit log for key rotations
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
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        
        # Subscription
        sa.Column('tier', sa.String(32), nullable=False, server_default='starter'),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('stripe_subscription_id', sa.String(255)),
        sa.Column('subscription_status', sa.String(32), server_default='active'),
        
        # Features (JSONB)
        sa.Column('features', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Usage
        sa.Column('monthly_api_limit', sa.Integer, server_default='10000'),
        sa.Column('monthly_api_usage', sa.Integer, server_default='0'),
        
        # Coalition
        sa.Column('coalition_member', sa.Boolean, server_default='true'),
        sa.Column('coalition_rev_share', sa.Integer, server_default='65'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('organization_id', sa.String(64), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('user_id', sa.String(64), nullable=True, index=True),  # For users without orgs
        
        # Key information
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('key_prefix', sa.String(20), nullable=False),
        sa.Column('fingerprint', sa.String(64), nullable=True),
        
        # Permissions (JSONB array)
        sa.Column('permissions', postgresql.JSONB, nullable=False, server_default='["sign", "verify", "lookup"]'),
        
        # Status
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('is_revoked', sa.Boolean, server_default='false', nullable=False),
        
        # Usage tracking
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer, server_default='0', nullable=False),
        
        # Lifecycle
        sa.Column('created_by', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        
        # Metadata
        sa.Column('description', sa.Text, nullable=True),
    )
    
    # Create key_usage table
    op.create_table(
        'key_usage',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('key_id', sa.String(64), sa.ForeignKey('api_keys.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', sa.String(64), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True),
        
        # Request information
        sa.Column('endpoint', sa.String(255), nullable=True),
        sa.Column('method', sa.String(10), nullable=True),
        sa.Column('status_code', sa.Integer, nullable=True),
        
        # Client information
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create key_rotations table
    op.create_table(
        'key_rotations',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('old_key_id', sa.String(64), nullable=False, index=True),
        sa.Column('new_key_id', sa.String(64), nullable=False, index=True),
        sa.Column('organization_id', sa.String(64), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True),
        
        # Rotation information
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('rotated_by', sa.String(64), nullable=True),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index('idx_api_keys_org', 'api_keys', ['organization_id'])
    op.create_index('idx_api_keys_user', 'api_keys', ['user_id'])
    op.create_index('idx_api_keys_hash', 'api_keys', ['key_hash'])


def downgrade() -> None:
    op.drop_table('key_rotations')
    op.drop_table('key_usage')
    op.drop_table('api_keys')
    op.drop_table('organizations')
