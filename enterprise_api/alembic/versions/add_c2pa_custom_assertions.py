"""add c2pa custom assertions support

Revision ID: add_c2pa_custom
Revises: add_manifest_storage
Create Date: 2025-11-03

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_c2pa_custom"
down_revision = "add_manifest_storage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Create c2pa_schemas table
    if "c2pa_schemas" not in existing_tables:
        op.create_table(
            "c2pa_schemas",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("namespace", sa.String(255), nullable=False),
            sa.Column("label", sa.String(255), nullable=False),
            sa.Column("version", sa.String(50), nullable=False),
            sa.Column("schema", postgresql.JSONB(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("organization_id", sa.String(255), nullable=True),
            sa.Column("is_public", sa.Boolean(), default=False, nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("namespace", "label", "version", name="uq_schema_namespace_label_version"),
        )

    # Create indexes for c2pa_schemas
    if "c2pa_schemas" in set(inspector.get_table_names()):
        c2pa_schema_indexes = {idx["name"] for idx in inspector.get_indexes("c2pa_schemas")}
        if "ix_c2pa_schemas_namespace" not in c2pa_schema_indexes:
            op.create_index("ix_c2pa_schemas_namespace", "c2pa_schemas", ["namespace"])
        if "ix_c2pa_schemas_label" not in c2pa_schema_indexes:
            op.create_index("ix_c2pa_schemas_label", "c2pa_schemas", ["label"])
        if "ix_c2pa_schemas_organization_id" not in c2pa_schema_indexes:
            op.create_index("ix_c2pa_schemas_organization_id", "c2pa_schemas", ["organization_id"])
        if "ix_c2pa_schemas_is_public" not in c2pa_schema_indexes:
            op.create_index("ix_c2pa_schemas_is_public", "c2pa_schemas", ["is_public"])

    # Create c2pa_assertion_templates table
    if "c2pa_assertion_templates" not in set(inspector.get_table_names()):
        op.create_table(
            "c2pa_assertion_templates",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("assertions", postgresql.JSONB(), nullable=False),
            sa.Column("organization_id", sa.String(255), nullable=True),
            sa.Column("is_public", sa.Boolean(), default=False, nullable=False),
            sa.Column("category", sa.String(100), nullable=True),  # news, legal, academic, publisher
            sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )

    # Create indexes for c2pa_assertion_templates
    if "c2pa_assertion_templates" in set(inspector.get_table_names()):
        c2pa_template_indexes = {idx["name"] for idx in inspector.get_indexes("c2pa_assertion_templates")}
        if "ix_c2pa_templates_name" not in c2pa_template_indexes:
            op.create_index("ix_c2pa_templates_name", "c2pa_assertion_templates", ["name"])
        if "ix_c2pa_templates_organization_id" not in c2pa_template_indexes:
            op.create_index("ix_c2pa_templates_organization_id", "c2pa_assertion_templates", ["organization_id"])
        if "ix_c2pa_templates_is_public" not in c2pa_template_indexes:
            op.create_index("ix_c2pa_templates_is_public", "c2pa_assertion_templates", ["is_public"])
        if "ix_c2pa_templates_category" not in c2pa_template_indexes:
            op.create_index("ix_c2pa_templates_category", "c2pa_assertion_templates", ["category"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "c2pa_assertion_templates" in existing_tables:
        c2pa_template_indexes = {idx["name"] for idx in inspector.get_indexes("c2pa_assertion_templates")}
        if "ix_c2pa_templates_category" in c2pa_template_indexes:
            op.drop_index("ix_c2pa_templates_category", table_name="c2pa_assertion_templates")
        if "ix_c2pa_templates_is_public" in c2pa_template_indexes:
            op.drop_index("ix_c2pa_templates_is_public", table_name="c2pa_assertion_templates")
        if "ix_c2pa_templates_organization_id" in c2pa_template_indexes:
            op.drop_index("ix_c2pa_templates_organization_id", table_name="c2pa_assertion_templates")
        if "ix_c2pa_templates_name" in c2pa_template_indexes:
            op.drop_index("ix_c2pa_templates_name", table_name="c2pa_assertion_templates")
        op.drop_table("c2pa_assertion_templates")

    if "c2pa_schemas" in existing_tables:
        c2pa_schema_indexes = {idx["name"] for idx in inspector.get_indexes("c2pa_schemas")}
        if "ix_c2pa_schemas_is_public" in c2pa_schema_indexes:
            op.drop_index("ix_c2pa_schemas_is_public", table_name="c2pa_schemas")
        if "ix_c2pa_schemas_organization_id" in c2pa_schema_indexes:
            op.drop_index("ix_c2pa_schemas_organization_id", table_name="c2pa_schemas")
        if "ix_c2pa_schemas_label" in c2pa_schema_indexes:
            op.drop_index("ix_c2pa_schemas_label", table_name="c2pa_schemas")
        if "ix_c2pa_schemas_namespace" in c2pa_schema_indexes:
            op.drop_index("ix_c2pa_schemas_namespace", table_name="c2pa_schemas")
        op.drop_table("c2pa_schemas")
