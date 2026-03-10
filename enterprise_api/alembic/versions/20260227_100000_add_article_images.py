"""Add article_images and composite_manifests tables for C2PA image signing.

Revision ID: 20260227_100000
Revises: 20260221_120000
Create Date: 2026-02-27 10:00:00.000000

Adds:
- article_images: metadata for signed images (sign-and-return model, no binary storage)
- composite_manifests: article-level C2PA manifest binding text + image ingredients
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "20260227_100000"
down_revision = "20260223_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. article_images (Content DB)
    # Stores metadata for signed images. Signed image bytes are returned in the
    # API response (base64). Publishers host signed images on their own CDN.
    # -------------------------------------------------------------------------
    op.create_table(
        "article_images",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("image_id", sa.String(64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("filename", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("alt_text", sa.Text(), nullable=True),
        sa.Column("original_hash", sa.String(128), nullable=False),
        sa.Column("signed_hash", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("c2pa_instance_id", sa.String(255), nullable=True),
        sa.Column("c2pa_manifest_hash", sa.String(128), nullable=True),
        sa.Column("phash", sa.BigInteger(), nullable=True),
        sa.Column("phash_algorithm", sa.String(20), nullable=True, server_default=sa.text("'average_hash'")),
        sa.Column("trustmark_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("trustmark_key", sa.String(100), nullable=True),
        sa.Column("exif_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "image_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("image_id", name="uq_article_images_image_id"),
    )

    op.create_index(
        "idx_article_images_org_doc",
        "article_images",
        ["organization_id", "document_id"],
    )
    op.create_index(
        "idx_article_images_image_id",
        "article_images",
        ["image_id"],
    )
    op.create_index(
        "idx_article_images_phash",
        "article_images",
        ["phash"],
        postgresql_where=sa.text("phash IS NOT NULL"),
    )
    op.create_index(
        "idx_article_images_signed_hash",
        "article_images",
        ["signed_hash"],
    )

    # -------------------------------------------------------------------------
    # 2. composite_manifests (Content DB)
    # Article-level C2PA manifest that references each image as an ingredient
    # and binds them to the signed text via the ZWC/Merkle pipeline.
    # -------------------------------------------------------------------------
    op.create_table(
        "composite_manifests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("instance_id", sa.String(255), nullable=False),
        sa.Column("manifest_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("manifest_hash", sa.String(128), nullable=False),
        sa.Column("text_merkle_root", sa.String(128), nullable=True),
        sa.Column("ingredient_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("document_id", name="uq_composite_manifests_document_id"),
    )

    op.create_index(
        "idx_composite_manifests_org",
        "composite_manifests",
        ["organization_id"],
    )
    op.create_index(
        "idx_composite_manifests_doc",
        "composite_manifests",
        ["document_id"],
    )
    op.create_index(
        "idx_composite_manifests_instance",
        "composite_manifests",
        ["instance_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_composite_manifests_instance", table_name="composite_manifests")
    op.drop_index("idx_composite_manifests_doc", table_name="composite_manifests")
    op.drop_index("idx_composite_manifests_org", table_name="composite_manifests")
    op.drop_table("composite_manifests")

    op.drop_index("idx_article_images_signed_hash", table_name="article_images")
    op.drop_index("idx_article_images_phash", table_name="article_images")
    op.drop_index("idx_article_images_image_id", table_name="article_images")
    op.drop_index("idx_article_images_org_doc", table_name="article_images")
    op.drop_table("article_images")
