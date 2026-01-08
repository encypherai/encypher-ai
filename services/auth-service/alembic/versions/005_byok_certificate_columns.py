"""Add BYOK certificate columns to organizations table

Revision ID: 005
Revises: 004
Create Date: 2026-01-08

Adds certificate-related columns for BYOK (Bring Your Own Key) support:
- certificate_pem: The PEM-encoded certificate
- certificate_chain: The certificate chain
- certificate_status: Status of the certificate (none, pending, active, expired)
- certificate_rotated_at: When the certificate was last rotated
- certificate_expiry: When the certificate expires
- kms_key_id: AWS KMS key ID for BYOK
- kms_region: AWS region for KMS key
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def upgrade() -> None:
    conn = op.get_bind()

    # Certificate columns for BYOK support
    byok_columns = [
        ("certificate_pem", sa.Text(), True, None),
        ("certificate_chain", sa.Text(), True, None),
        ("certificate_status", sa.String(20), True, "none"),
        ("certificate_rotated_at", sa.DateTime(timezone=True), True, None),
        ("certificate_expiry", sa.DateTime(timezone=True), True, None),
        ("kms_key_id", sa.String(255), True, None),
        ("kms_region", sa.String(50), True, None),
    ]

    for col_name, col_type, nullable, default in byok_columns:
        if not column_exists(conn, "organizations", col_name):
            op.add_column(
                "organizations",
                sa.Column(col_name, col_type, nullable=nullable, server_default=default),
            )


def downgrade() -> None:
    op.drop_column("organizations", "kms_region")
    op.drop_column("organizations", "kms_key_id")
    op.drop_column("organizations", "certificate_expiry")
    op.drop_column("organizations", "certificate_rotated_at")
    op.drop_column("organizations", "certificate_status")
    op.drop_column("organizations", "certificate_chain")
    op.drop_column("organizations", "certificate_pem")
