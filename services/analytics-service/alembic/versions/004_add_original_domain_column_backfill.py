"""Ensure content_discoveries.original_domain exists in deployed databases.

Revision ID: 004
Revises: 003
Create Date: 2026-02-16
"""

from typing import Sequence, Union

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Some existing environments were created before original_domain was
    # introduced. Add it defensively if missing.
    op.execute(
        """
        ALTER TABLE content_discoveries
        ADD COLUMN IF NOT EXISTS original_domain VARCHAR(255)
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_content_discoveries_original_domain
        ON content_discoveries (original_domain)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_content_discoveries_original_domain")
    op.execute(
        """
        ALTER TABLE content_discoveries
        DROP COLUMN IF EXISTS original_domain
        """
    )
