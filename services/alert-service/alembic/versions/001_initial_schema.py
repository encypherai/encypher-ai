"""Initial alert-service schema.

Revision ID: 001
Revises:
Create Date: 2026-03-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("fingerprint", sa.String(128), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open", index=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="warning", index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("service_name", sa.String(100), index=True),
        sa.Column("endpoint", sa.String(500)),
        sa.Column("error_code", sa.String(50)),
        sa.Column("first_seen_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("occurrence_count", sa.Integer, server_default="1"),
        sa.Column("sample_error", sa.Text),
        sa.Column("sample_stack", sa.Text),
        sa.Column("sample_request_id", sa.String(64)),
        sa.Column("sample_organization_id", sa.String(64)),
        sa.Column("resolved_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "alert_events",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("incident_id", sa.String(64), sa.ForeignKey("incidents.id"), index=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("raw_payload", JSONB, nullable=False),
        sa.Column("status_code", sa.Integer),
        sa.Column("endpoint", sa.String(500)),
        sa.Column("error_code", sa.String(50)),
        sa.Column("error_message", sa.Text),
        sa.Column("service_name", sa.String(100), index=True),
        sa.Column("organization_id", sa.String(64)),
        sa.Column("user_id", sa.String(64)),
        sa.Column("request_id", sa.String(64)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), index=True),
    )

    op.create_table(
        "notification_log",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("incident_id", sa.String(64), sa.ForeignKey("incidents.id"), index=True),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("payload", JSONB),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("notification_log")
    op.drop_table("alert_events")
    op.drop_table("incidents")
