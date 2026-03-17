from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None


def column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(
        text(
            f"""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = '{table_name}' AND column_name = '{column_name}'
            )
            """
        )
    )
    return bool(result.scalar())


def index_exists(conn, index_name: str) -> bool:
    result = conn.execute(
        text(
            f"""
            SELECT EXISTS (
                SELECT FROM pg_indexes WHERE indexname = '{index_name}'
            )
            """
        )
    )
    return bool(result.scalar())


def upgrade() -> None:
    conn = op.get_bind()

    if not column_exists(conn, "organizations", "parent_org_id"):
        op.add_column("organizations", sa.Column("parent_org_id", sa.String(length=64), nullable=True))

    if not index_exists(conn, "ix_organizations_parent_org_id"):
        op.create_index("ix_organizations_parent_org_id", "organizations", ["parent_org_id"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()

    if index_exists(conn, "ix_organizations_parent_org_id"):
        op.drop_index("ix_organizations_parent_org_id", table_name="organizations")

    if column_exists(conn, "organizations", "parent_org_id"):
        op.drop_column("organizations", "parent_org_id")
