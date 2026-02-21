"""Rights Management System — all new tables for publisher rights, formal notices, and licensing.

Revision ID: 20260221_120000
Revises: 20260217_182300
Create Date: 2026-02-21 12:00:00.000000

Adds:
- publisher_rights_profiles: versioned publisher rights defaults (bronze/silver/gold tiers)
- document_rights_overrides: per-document / collection / content-type overrides
- formal_notices: immutable formal notice records with cryptographic hashing
- notice_evidence_chain: append-only linked evidence chain for each notice
- rights_licensing_requests: licensing request/negotiation flow (distinct from existing agreements)
- rights_audit_log: append-only audit trail for all rights changes
- content_detection_events: phone-home analytics (partitioned by month)
- known_crawlers: user-agent classification registry
- rights_snapshot column on content_references (content DB)
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "20260221_120000"
down_revision = "20260217_182300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─────────────────────────────────────────────────────────────────────────
    # 1. publisher_rights_profiles
    # Versioned, append-only. Each UPDATE creates a new row.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "publisher_rights_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("effective_date", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),

        # Identity
        sa.Column("publisher_name", sa.Text(), nullable=False),
        sa.Column("publisher_url", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.Text(), nullable=True),
        sa.Column("contact_url", sa.Text(), nullable=True),
        sa.Column("legal_entity", sa.Text(), nullable=True),
        sa.Column("jurisdiction", sa.Text(), nullable=False, server_default=sa.text("'US'")),

        # Default rights
        sa.Column(
            "default_license_type",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'all_rights_reserved'"),
        ),

        # Tier-specific licensing terms (JSONB)
        sa.Column("bronze_tier", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("silver_tier", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("gold_tier", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),

        # Formal notice
        sa.Column("notice_status", sa.Text(), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("notice_effective_date", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("notice_text", sa.Text(), nullable=True),
        sa.Column("notice_hash", sa.Text(), nullable=True),

        # Coalition
        sa.Column("coalition_member", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("coalition_joined_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("licensing_track", sa.Text(), nullable=False, server_default=sa.text("'both'")),

        sa.UniqueConstraint("organization_id", "profile_version", name="uq_rights_profile_org_version"),
    )

    op.create_index("idx_rights_profiles_org", "publisher_rights_profiles", ["organization_id", sa.text("profile_version DESC")])

    # ─────────────────────────────────────────────────────────────────────────
    # 2. document_rights_overrides
    # Per-document / collection / content-type overrides of publisher defaults.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "document_rights_overrides",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),  # nullable for collection/content-type overrides
        sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("override_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),

        # Scope
        sa.Column("override_type", sa.Text(), nullable=False, server_default=sa.text("'document'")),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content_type_filter", sa.Text(), nullable=True),
        sa.Column("date_range_start", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("date_range_end", sa.TIMESTAMP(timezone=True), nullable=True),

        # Tier overrides (null = use publisher default)
        sa.Column("bronze_tier_override", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("silver_tier_override", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("gold_tier_override", postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Special flags
        sa.Column("do_not_license", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("premium_content", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("embargo_until", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("syndication_rights", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.create_index("idx_doc_overrides_doc", "document_rights_overrides", ["document_id", sa.text("override_version DESC")])
    op.create_index("idx_doc_overrides_org", "document_rights_overrides", ["organization_id"])
    op.create_index("idx_doc_overrides_collection", "document_rights_overrides", ["collection_id"])
    op.create_index("idx_doc_overrides_content_type", "document_rights_overrides", ["organization_id", "content_type_filter"])

    # ─────────────────────────────────────────────────────────────────────────
    # 3. formal_notices
    # Immutable once delivered. Content hash proves integrity.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "formal_notices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),

        # Target entity
        sa.Column("target_entity_name", sa.Text(), nullable=False),
        sa.Column("target_entity_domain", sa.Text(), nullable=True),
        sa.Column("target_contact_email", sa.Text(), nullable=True),
        sa.Column("target_entity_type", sa.Text(), nullable=False, server_default=sa.text("'ai_company'")),

        # Scope
        sa.Column("scope_type", sa.Text(), nullable=False),
        sa.Column("scope_document_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("scope_date_range_start", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("scope_date_range_end", sa.TIMESTAMP(timezone=True), nullable=True),

        # Notice content (immutable once delivered)
        sa.Column("notice_type", sa.Text(), nullable=False),
        sa.Column("notice_text", sa.Text(), nullable=False),
        sa.Column("notice_hash", sa.Text(), nullable=False),  # SHA-256 of notice_text

        # Demands
        sa.Column("demands", postgresql.JSONB(astext_type=sa.Text()), nullable=False),

        # Lifecycle
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'created'")),
        sa.Column("delivered_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("delivery_method", sa.Text(), nullable=True),
        sa.Column("delivery_receipt", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("delivery_receipt_hash", sa.Text(), nullable=True),
        sa.Column("acknowledged_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.create_index("idx_formal_notices_org", "formal_notices", ["organization_id"])
    op.create_index("idx_formal_notices_target", "formal_notices", ["target_entity_domain"])
    op.create_index("idx_formal_notices_status", "formal_notices", ["organization_id", "status"])

    # ─────────────────────────────────────────────────────────────────────────
    # 4. notice_evidence_chain
    # Append-only linked list of events in a notice's lifecycle.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "notice_evidence_chain",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("notice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("formal_notices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("event_hash", sa.Text(), nullable=False),  # SHA-256 of event_data + previous_hash
        sa.Column("previous_hash", sa.Text(), nullable=True),  # Links to prior event (chain)
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_evidence_chain_notice", "notice_evidence_chain", ["notice_id", sa.text("created_at")])

    # ─────────────────────────────────────────────────────────────────────────
    # 5. rights_licensing_requests
    # New licensing request/negotiation flow (distinct from existing licensing_agreements).
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "rights_licensing_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("publisher_org_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("requester_org_id", sa.String(64), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),

        sa.Column("tier", sa.Text(), nullable=False),  # bronze, silver, gold
        sa.Column("scope", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("proposed_terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("requester_info", postgresql.JSONB(astext_type=sa.Text()), nullable=False),

        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("responded_at", sa.TIMESTAMP(timezone=True), nullable=True),

        # If approved → creates rights_licensing_agreement
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=True),

        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_rights_requests_publisher", "rights_licensing_requests", ["publisher_org_id", "status"])
    op.create_index("idx_rights_requests_requester", "rights_licensing_requests", ["requester_org_id", "status"])

    # ─────────────────────────────────────────────────────────────────────────
    # 6. rights_licensing_agreements
    # Active licensing agreements created after request approval.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "rights_licensing_agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rights_licensing_requests.id"), nullable=True),
        sa.Column("publisher_org_id", sa.String(64), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("licensee_org_id", sa.String(64), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("licensee_name", sa.Text(), nullable=True),  # For non-org licensees

        sa.Column("tier", sa.Text(), nullable=False),
        sa.Column("scope", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),

        sa.Column("effective_date", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expiry_date", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
        sa.Column("usage_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),

        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_rights_agreements_active", "rights_licensing_agreements", ["status", "expiry_date"], postgresql_where=sa.text("status = 'active'"))
    op.create_index("idx_rights_agreements_publisher", "rights_licensing_agreements", ["publisher_org_id"])

    # ─────────────────────────────────────────────────────────────────────────
    # 7. rights_audit_log
    # Append-only audit trail for all rights-related changes.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "rights_audit_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.Text(), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("old_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("performed_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
    )

    op.create_index("idx_rights_audit_org", "rights_audit_log", ["organization_id", sa.text("performed_at DESC")])
    op.create_index("idx_rights_audit_resource", "rights_audit_log", ["resource_type", "resource_id"])

    # ─────────────────────────────────────────────────────────────────────────
    # 8. content_detection_events
    # Phone-home analytics — append-only, high-volume.
    # NOTE: True PARTITION BY RANGE requires native DDL; we create as regular table
    # with a monthly partition naming convention. Can be converted later.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "content_detection_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("organization_id", sa.String(64), nullable=False),

        # Detection source
        sa.Column("detection_source", sa.Text(), nullable=False),
        # e.g. 'chrome_extension', 'api_verification', 'rsl_olp_check',
        # 'http_header_lookup', 'rights_api_lookup', 'crawl_detected'

        # Location
        sa.Column("detected_on_url", sa.Text(), nullable=True),
        sa.Column("detected_on_domain", sa.Text(), nullable=True),

        # Requester info
        sa.Column("requester_ip", postgresql.INET(), nullable=True),
        sa.Column("requester_org_id", sa.String(64), nullable=True),
        sa.Column("requester_user_agent", sa.Text(), nullable=True),
        sa.Column("user_agent_category", sa.Text(), nullable=True),
        # e.g. 'human_browser', 'ai_crawler', 'search_crawler', 'aggregator', 'unknown'

        # Content info
        sa.Column("segments_found", sa.Integer(), nullable=True),
        sa.Column("integrity_status", sa.Text(), nullable=True),
        # 'intact', 'partial_tampering', 'significant_tampering', 'stripped'

        # Rights signals
        sa.Column("rights_served", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("rights_acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_detection_events_org_date", "content_detection_events", ["organization_id", sa.text("created_at DESC")])
    op.create_index("idx_detection_events_domain", "content_detection_events", ["detected_on_domain", sa.text("created_at DESC")])
    op.create_index("idx_detection_events_document", "content_detection_events", ["document_id", sa.text("created_at DESC")])
    op.create_index("idx_detection_events_ua_category", "content_detection_events", ["user_agent_category", sa.text("created_at DESC")])

    # ─────────────────────────────────────────────────────────────────────────
    # 9. known_crawlers
    # User-agent classification registry for detection analytics.
    # ─────────────────────────────────────────────────────────────────────────
    op.create_table(
        "known_crawlers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_agent_pattern", sa.Text(), nullable=False),
        sa.Column("crawler_name", sa.Text(), nullable=False),
        sa.Column("operator_org", sa.Text(), nullable=False),
        sa.Column("crawler_type", sa.Text(), nullable=False),
        # 'ai_training', 'ai_search', 'search_engine', 'aggregator', 'monitoring'
        sa.Column("respects_robots_txt", sa.Boolean(), nullable=True),
        sa.Column("respects_rsl", sa.Boolean(), nullable=True),
        sa.Column("known_ip_ranges", postgresql.ARRAY(postgresql.INET()), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 10. Add rights_snapshot column to content_references (core DB)
    # Stores a snapshot of the rights profile at time of signing.
    # ─────────────────────────────────────────────────────────────────────────
    op.add_column(
        "content_references",
        sa.Column("rights_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "content_references",
        sa.Column("rights_resolution_url", sa.Text(), nullable=True),
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 11. Seed known_crawlers with major AI crawlers
    # ─────────────────────────────────────────────────────────────────────────
    op.execute("""
        INSERT INTO known_crawlers (user_agent_pattern, crawler_name, operator_org, crawler_type, respects_robots_txt, respects_rsl)
        VALUES
            ('GPTBot', 'GPTBot', 'OpenAI', 'ai_training', true, false),
            ('ChatGPT-User', 'ChatGPT-User', 'OpenAI', 'ai_search', true, false),
            ('OAI-SearchBot', 'OAI-SearchBot', 'OpenAI', 'ai_search', true, false),
            ('ClaudeBot', 'ClaudeBot', 'Anthropic', 'ai_training', true, false),
            ('Claude-Web', 'Claude-Web', 'Anthropic', 'ai_search', true, false),
            ('anthropic-ai', 'Anthropic AI', 'Anthropic', 'ai_training', true, false),
            ('Google-Extended', 'Google-Extended', 'Google', 'ai_training', true, false),
            ('Googlebot', 'Googlebot', 'Google', 'search_engine', true, false),
            ('PerplexityBot', 'PerplexityBot', 'Perplexity AI', 'ai_search', true, false),
            ('Meta-ExternalAgent', 'Meta-ExternalAgent', 'Meta', 'ai_training', true, false),
            ('Meta-ExternalFetcher', 'Meta-ExternalFetcher', 'Meta', 'ai_training', true, false),
            ('Applebot-Extended', 'Applebot-Extended', 'Apple', 'ai_training', true, false),
            ('CCBot', 'Common Crawl Bot', 'Common Crawl', 'aggregator', true, false),
            ('ia_archiver', 'Internet Archive', 'Internet Archive', 'aggregator', true, false),
            ('Bytespider', 'Bytespider', 'ByteDance', 'ai_training', true, false)
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    # Remove in reverse order of dependencies
    op.execute("DELETE FROM known_crawlers")
    op.drop_column("content_references", "rights_resolution_url")
    op.drop_column("content_references", "rights_snapshot")
    op.drop_table("known_crawlers")
    op.drop_table("content_detection_events")
    op.drop_table("rights_audit_log")
    op.drop_table("rights_licensing_agreements")
    op.drop_table("rights_licensing_requests")
    op.drop_table("notice_evidence_chain")
    op.drop_table("formal_notices")
    op.drop_table("document_rights_overrides")
    op.drop_table("publisher_rights_profiles")
