from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "021"
down_revision = "020"
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


def upgrade() -> None:
    conn = op.get_bind()

    if not column_exists(conn, "organizations", "status"):
        op.add_column(
            "organizations",
            sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        )

    if not column_exists(conn, "organizations", "suspended_at"):
        op.add_column(
            "organizations",
            sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not column_exists(conn, "organizations", "suspension_reason"):
        op.add_column(
            "organizations",
            sa.Column("suspension_reason", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()

    if column_exists(conn, "organizations", "suspension_reason"):
        op.drop_column("organizations", "suspension_reason")

    if column_exists(conn, "organizations", "suspended_at"):
        op.drop_column("organizations", "suspended_at")

    if column_exists(conn, "organizations", "status"):
        op.drop_column("organizations", "status")
