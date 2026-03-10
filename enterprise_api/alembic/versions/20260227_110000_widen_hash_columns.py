"""Widen hash columns in article_images and composite_manifests to 128 chars.

Revision ID: 20260227_110000
Revises: 20260227_100000
Create Date: 2026-02-27 11:00:00.000000

Hash values are stored as "sha256:" (7 chars) + 64 hex chars = 71 chars total.
The original schema used VARCHAR(64) which is too narrow. This migration widens
all hash columns to VARCHAR(128) to accommodate the prefix + digest format.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "20260227_110000"
down_revision = "20260227_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # article_images: widen hash columns
    op.alter_column(
        "article_images",
        "original_hash",
        existing_type=sa.String(64),
        type_=sa.String(128),
        existing_nullable=False,
    )
    op.alter_column(
        "article_images",
        "signed_hash",
        existing_type=sa.String(64),
        type_=sa.String(128),
        existing_nullable=False,
    )
    op.alter_column(
        "article_images",
        "c2pa_manifest_hash",
        existing_type=sa.String(64),
        type_=sa.String(128),
        existing_nullable=True,
    )

    # composite_manifests: widen hash columns
    op.alter_column(
        "composite_manifests",
        "manifest_hash",
        existing_type=sa.String(64),
        type_=sa.String(128),
        existing_nullable=False,
    )
    op.alter_column(
        "composite_manifests",
        "text_merkle_root",
        existing_type=sa.String(64),
        type_=sa.String(128),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "composite_manifests",
        "text_merkle_root",
        existing_type=sa.String(128),
        type_=sa.String(64),
        existing_nullable=True,
    )
    op.alter_column(
        "composite_manifests",
        "manifest_hash",
        existing_type=sa.String(128),
        type_=sa.String(64),
        existing_nullable=False,
    )
    op.alter_column(
        "article_images",
        "c2pa_manifest_hash",
        existing_type=sa.String(128),
        type_=sa.String(64),
        existing_nullable=True,
    )
    op.alter_column(
        "article_images",
        "signed_hash",
        existing_type=sa.String(128),
        type_=sa.String(64),
        existing_nullable=False,
    )
    op.alter_column(
        "article_images",
        "original_hash",
        existing_type=sa.String(128),
        type_=sa.String(64),
        existing_nullable=False,
    )
