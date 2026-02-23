#!/usr/bin/env python3
"""
Seed script: The Encypher Times demo publisher account.

Creates a realistic midsized/large publisher account with pre-populated
analytics data suitable for showing off the dashboard and analytics pages.

Credentials:
  Email:    times@encypherai.com
  Password: TimesDemo2024!
  Org:      org_encypher_times

Usage:
  cd enterprise_api
  uv run python scripts/seed_encypher_times.py
"""

import random
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

import bcrypt
import psycopg2

# ---------------------------------------------------------------------------
# Database connections (container port 5432, host-mapped to 15432)
# ---------------------------------------------------------------------------
DB_HOST = "localhost"
DB_PORT = 15432
DB_USER = "encypher"
DB_PASS = "encypher_dev_password"


def connect(dbname: str) -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=dbname,
    )


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ORG_ID = "org_encypher_times"
USER_ID = "user_encypher_times"
ORG_NAME = "The Encypher Times"
ORG_EMAIL = "times@encypherai.com"
ORG_SLUG = "encypher-times"
USER_PASSWORD = "TimesDemo2024!"
API_KEY = "times-demo-api-key-2024"

NOW = datetime.now(timezone.utc)
TODAY = NOW.date()

# Realistic large-publisher stats
TOTAL_DOCS_SIGNED = 47_832
TOTAL_API_CALLS = 52_847
TOTAL_VERIFICATIONS = 843   # Just above 500 (Notice Ready threshold)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def hash_password(pw: str) -> str:
    """Hash password the same way the auth service does:
    SHA-256(password) -> base64 -> bcrypt
    """
    import hashlib, base64
    sha256_hash = hashlib.sha256(pw.encode("utf-8")).digest()
    prehashed = base64.b64encode(sha256_hash)
    return bcrypt.hashpw(prehashed, bcrypt.gensalt(12)).decode()


def days_ago(n: int) -> datetime:
    return NOW - timedelta(days=n)


def fmt_date(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# 1. encypher_auth -- user + organization + membership
# ---------------------------------------------------------------------------
def seed_auth(cur):
    pw_hash = hash_password(USER_PASSWORD)

    # Completed onboarding checklist -- all standard steps marked done
    onboarding = {
        "account_created":      {"completed_at": days_ago(90).isoformat()},
        "organization_created": {"completed_at": days_ago(90).isoformat()},
        "first_document_signed":{"completed_at": days_ago(88).isoformat()},
        "api_key_created":      {"completed_at": days_ago(87).isoformat()},
        "rights_profile_set":   {"completed_at": days_ago(85).isoformat()},
        "joined_coalition":     {"completed_at": days_ago(85).isoformat()},
    }

    import json
    onboarding_json = json.dumps(onboarding)

    # User
    cur.execute(
        """
        INSERT INTO users (
            id, email, password_hash, name, email_verified, email_verified_at,
            is_active, api_access_status, default_organization_id,
            onboarding_checklist, onboarding_completed_at,
            setup_completed_at, created_at, updated_at
        )
        VALUES (
            %s, %s, %s, %s, TRUE, %s,
            TRUE, 'approved', %s,
            %s::json, %s,
            %s, %s, %s
        )
        ON CONFLICT (email) DO UPDATE SET
            name = EXCLUDED.name,
            password_hash = EXCLUDED.password_hash,
            email_verified = TRUE,
            default_organization_id = EXCLUDED.default_organization_id,
            onboarding_checklist = EXCLUDED.onboarding_checklist,
            onboarding_completed_at = EXCLUDED.onboarding_completed_at,
            updated_at = NOW()
        RETURNING id
        """,
        (
            USER_ID,
            ORG_EMAIL,
            pw_hash,
            ORG_NAME,
            days_ago(90),             # email_verified_at
            ORG_ID,
            onboarding_json,
            days_ago(85),             # onboarding_completed_at
            days_ago(85),             # setup_completed_at
            days_ago(90),             # created_at
            days_ago(90),             # updated_at
        ),
    )
    row = cur.fetchone()
    actual_user_id = row[0]
    print(f"  [auth] user upserted: {actual_user_id}")

    # Organization (auth DB version -- simpler schema)
    cur.execute(
        """
        INSERT INTO organizations (
            id, name, slug, email, tier,
            features, monthly_api_limit, monthly_api_usage,
            max_seats, coalition_member, coalition_rev_share,
            created_at, updated_at
        )
        VALUES (
            %s, %s, %s, %s, 'enterprise',
            '{"merkle": true, "sentence_tracking": true, "analytics": true, "byok": true}'::jsonb,
            -1, 0,
            50, TRUE, 80,
            %s, %s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            tier = 'enterprise',
            coalition_member = TRUE,
            updated_at = NOW()
        """,
        (ORG_ID, ORG_NAME, ORG_SLUG, ORG_EMAIL, days_ago(90), days_ago(90)),
    )
    print(f"  [auth] organization upserted: {ORG_ID}")

    # Organization membership
    member_id = f"mem_{ORG_ID}_owner"
    cur.execute(
        """
        INSERT INTO organization_members (
            id, organization_id, user_id, role, status,
            accepted_at, created_at, updated_at
        )
        VALUES (%s, %s, %s, 'owner', 'active', %s, %s, %s)
        ON CONFLICT (organization_id, user_id) DO UPDATE SET
            role = 'owner', status = 'active', updated_at = NOW()
        """,
        (member_id, ORG_ID, actual_user_id, days_ago(90), days_ago(90), days_ago(90)),
    )
    print(f"  [auth] org membership upserted")


# ---------------------------------------------------------------------------
# 2. encypher_content -- organization + api_key + rights + detection events
#    + coalition earnings
# ---------------------------------------------------------------------------
def seed_content(cur):
    # Organization (content DB version -- rich schema)
    cur.execute(
        """
        INSERT INTO organizations (
            id, name, slug, email, tier,
            features, monthly_api_limit, monthly_api_usage,
            monthly_quota, documents_signed, sentences_signed,
            api_calls_this_month, sentences_tracked_this_month,
            batch_operations_this_month,
            merkle_enabled, advanced_analytics_enabled, bulk_operations_enabled,
            sentence_tracking_enabled, streaming_enabled, byok_enabled,
            team_management_enabled, audit_logs_enabled, sso_enabled,
            custom_assertions_enabled, fuzzy_fingerprint_enabled,
            coalition_member, coalition_rev_share_publisher, coalition_rev_share_encypher,
            coalition_opted_out,
            created_at, updated_at
        )
        VALUES (
            %s, %s, %s, %s, 'enterprise',
            '{}'::jsonb, -1, 0,
            -1, %s, %s,
            %s, 0,
            0,
            TRUE, TRUE, TRUE,
            TRUE, TRUE, TRUE,
            TRUE, TRUE, FALSE,
            TRUE, FALSE,
            TRUE, 80, 20,
            FALSE,
            %s, %s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            tier = 'enterprise',
            documents_signed = EXCLUDED.documents_signed,
            api_calls_this_month = EXCLUDED.api_calls_this_month,
            coalition_member = TRUE,
            updated_at = NOW()
        """,
        (
            ORG_ID, ORG_NAME, ORG_SLUG, ORG_EMAIL,
            TOTAL_DOCS_SIGNED,
            TOTAL_DOCS_SIGNED * 18,   # ~18 sentences per article
            TOTAL_API_CALLS,
            days_ago(90),
            days_ago(90),
        ),
    )
    print(f"  [content] organization upserted: {ORG_ID}")

    # API key -- new schema uses key_hash (bcrypt) + key_prefix
    import bcrypt as _bcrypt
    _key_hash = _bcrypt.hashpw(API_KEY.encode(), _bcrypt.gensalt(10)).decode()
    _key_prefix = API_KEY[:8]
    cur.execute(
        """
        INSERT INTO api_keys (
            organization_id, key_hash, key_prefix, name,
            scopes, is_active, created_at
        )
        VALUES (%s, %s, %s, 'Demo API Key',
                '["sign", "verify", "lookup"]'::jsonb, TRUE, %s)
        ON CONFLICT DO NOTHING
        """,
        (ORG_ID, _key_hash, _key_prefix, days_ago(87)),
    )
    print(f"  [content] api_key upserted (prefix: {_key_prefix})")

    # Publisher rights profile
    bronze = {
        "permitted": True,
        "license_type": "crawl_permitted",
        "conditions": ["search_indexing_only"],
    }
    silver = {
        "permitted": True,
        "license_type": "attribution_required",
        "conditions": ["author_credit", "canonical_url"],
        "contact_url": "https://times.encypherai.com/licensing",
    }
    gold = {
        "permitted": False,
        "license_type": "license_required",
        "contact_email": "licensing@encypherai.com",
        "contact_url": "https://times.encypherai.com/licensing",
        "conditions": ["written_license", "revenue_share"],
    }

    import json
    cur.execute(
        """
        INSERT INTO publisher_rights_profiles (
            organization_id, profile_version, effective_date,
            publisher_name, publisher_url, contact_email,
            legal_entity, jurisdiction, default_license_type,
            bronze_tier, silver_tier, gold_tier,
            notice_status, notice_effective_date,
            coalition_member, coalition_joined_at, licensing_track,
            created_at
        )
        VALUES (
            %s, 1, %s,
            %s, 'https://times.encypherai.com', 'licensing@encypherai.com',
            'Encypher Times Media LLC', 'US', 'all_rights_reserved',
            %s::jsonb, %s::jsonb, %s::jsonb,
            'published', %s,
            TRUE, %s, 'both',
            %s
        )
        ON CONFLICT (organization_id, profile_version) DO UPDATE SET
            notice_status = 'published',
            updated_by = NULL
        """,
        (
            ORG_ID, days_ago(85),
            ORG_NAME,
            json.dumps(bronze), json.dumps(silver), json.dumps(gold),
            days_ago(85),
            days_ago(85),
            days_ago(85),
        ),
    )
    print(f"  [content] publisher_rights_profile upserted")

    # Content detection events -- 843 events over 90 days
    _seed_detection_events(cur)

    # Coalition earnings -- 2 pending deals to show revenue pipeline
    _seed_coalition_earnings(cur)


def _seed_detection_events(cur):
    """Insert realistic provenance check events over 90 days."""

    domains = [
        ("chat.openai.com",   "ai_crawler",      "GPTBot/1.0"),
        ("openai.com",        "ai_crawler",      "GPTBot/1.0"),
        ("anthropic.com",     "ai_crawler",      "Claude-SearchBot/2.0"),
        ("claude.ai",         "ai_crawler",      "ClaudeBot/1.0"),
        ("perplexity.ai",     "ai_crawler",      "PerplexityBot/1.0"),
        ("bard.google.com",   "ai_crawler",      "Google-Extended/1.0"),
        ("bing.com",          "search_crawler",  "bingbot/2.0"),
        ("you.com",           "ai_crawler",      "YouBot/1.0"),
        ("brave.com",         "search_crawler",  "BraveSoftware/1.0"),
        ("news.ycombinator.com","human_browser", "Mozilla/5.0"),
        ("reddit.com",        "human_browser",   "Mozilla/5.0"),
        ("medium.com",        "aggregator",      "Mediaplex/3.0"),
        ("substack.com",      "human_browser",   "Mozilla/5.0"),
        ("axios.com",         "human_browser",   "Mozilla/5.0"),
        ("techcrunch.com",    "aggregator",      "TCrawler/2.0"),
    ]

    detection_sources = [
        "api_verification",    # 50%
        "api_verification",
        "api_verification",
        "chrome_extension",    # 30%
        "chrome_extension",
        "rsl_olp_check",       # 20%
    ]

    doc_ids = [str(uuid.uuid4()) for _ in range(50)]  # 50 sample document IDs

    rng = random.Random(42)  # deterministic seed for reproducibility

    # Delete existing events for this org first
    cur.execute(
        "DELETE FROM content_detection_events WHERE organization_id = %s",
        (ORG_ID,),
    )

    total = TOTAL_VERIFICATIONS  # 843 events
    # Distribute across 90 days with a realistic growth curve
    # More recent days have more events (content gaining traction)
    weights = [max(1, int(3 + (i / 90) * 8 + rng.gauss(0, 2))) for i in range(90)]
    weight_sum = sum(weights)
    events_per_day = [max(0, int(total * w / weight_sum)) for w in weights]
    # Ensure sum matches
    shortfall = total - sum(events_per_day)
    events_per_day[0] += shortfall

    inserted = 0
    for day_offset, count in enumerate(events_per_day):
        event_date = TODAY - timedelta(days=(89 - day_offset))
        for _ in range(count):
            domain_entry = rng.choice(domains)
            domain, ua_cat, ua_str = domain_entry
            doc_id = rng.choice(doc_ids)
            source = rng.choice(detection_sources)

            # Most content is intact; some tampered/stripped
            r = rng.random()
            if r < 0.90:
                integrity = "intact"
            elif r < 0.95:
                integrity = "partial_tampering"
            else:
                integrity = "stripped"

            rights_served = ua_cat in ("ai_crawler", "search_crawler")
            rights_ack = rights_served and rng.random() > 0.3
            bypassed = ua_cat == "ai_crawler" and rng.random() > 0.7

            event_dt = datetime(
                event_date.year, event_date.month, event_date.day,
                rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59),
                tzinfo=timezone.utc,
            )

            url = f"https://{domain}/article/{uuid.uuid4().hex[:8]}"

            cur.execute(
                """
                INSERT INTO content_detection_events (
                    organization_id, document_id, detection_source,
                    detected_on_url, detected_on_domain,
                    requester_user_agent, user_agent_category,
                    segments_found, integrity_status,
                    rights_served, rights_acknowledged,
                    robots_txt_bypassed, created_at
                )
                VALUES (%s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ORG_ID, doc_id, source, url, domain, ua_str, ua_cat,
                    rng.randint(1, 24),  # segments_found
                    integrity,
                    rights_served, rights_ack, bypassed,
                    event_dt,
                ),
            )
            inserted += 1

    print(f"  [content] inserted {inserted} content_detection_events")


def _seed_coalition_earnings(cur):
    """Insert a couple of coalition earnings entries to show revenue pipeline."""

    # Delete existing
    cur.execute(
        "DELETE FROM coalition_earnings WHERE organization_id = %s",
        (ORG_ID,),
    )

    entries = [
        {
            "id": f"earn_times_openai_q4",
            "deal_id": "deal_openai_coalition_q4_2025",
            "deal_name": "OpenAI Coalition License Q4 2025",
            "ai_company": "OpenAI",
            "period_start": date(2025, 10, 1),
            "period_end": date(2025, 12, 31),
            "gross_revenue_cents": 155_000,
            "publisher_share_percent": 80,
            "publisher_earnings_cents": 124_000,  # $1,240.00
            "attribution_method": "content_volume",
            "attribution_weight": "0.0081",
            "status": "confirmed",
        },
        {
            "id": f"earn_times_anthropic_q1",
            "deal_id": "deal_anthropic_coalition_q1_2026",
            "deal_name": "Anthropic Coalition License Q1 2026",
            "ai_company": "Anthropic",
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 3, 31),
            "gross_revenue_cents": 111_250,
            "publisher_share_percent": 80,
            "publisher_earnings_cents": 89_000,   # $890.00
            "attribution_method": "verification_weighted",
            "attribution_weight": "0.0063",
            "status": "pending",
        },
    ]

    for e in entries:
        cur.execute(
            """
            INSERT INTO coalition_earnings (
                id, organization_id, deal_id, deal_name, ai_company,
                period_start, period_end,
                gross_revenue_cents, publisher_share_percent, publisher_earnings_cents,
                attribution_method, attribution_weight, status,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
            """,
            (
                e["id"], ORG_ID, e["deal_id"], e["deal_name"], e["ai_company"],
                e["period_start"], e["period_end"],
                e["gross_revenue_cents"], e["publisher_share_percent"],
                e["publisher_earnings_cents"],
                e["attribution_method"], e["attribution_weight"], e["status"],
            ),
        )

    print(f"  [content] inserted {len(entries)} coalition_earnings entries")


# ---------------------------------------------------------------------------
# 3. encypher_analytics -- usage_metrics (30-day window + 60-day backfill)
# ---------------------------------------------------------------------------
def seed_analytics(cur):
    rng = random.Random(99)

    # Delete existing metrics for this org
    cur.execute(
        "DELETE FROM usage_metrics WHERE organization_id = %s",
        (ORG_ID,),
    )

    rows = []

    # -- Document signing: ~47k total over 90 days (bulk archive + ongoing)
    # Days 90-61 ago: archive signing job -- high daily volume
    # Days 60-31 ago: moderate ongoing volume
    # Days 30-1 ago: regular editorial cadence
    doc_daily_plan = []
    for i in range(90):
        day_offset = 89 - i  # 89 = oldest, 0 = yesterday
        if day_offset >= 60:
            # Archive batch signing: 800-1200/day
            count = rng.randint(800, 1200)
        elif day_offset >= 30:
            # Moderate: 200-400/day
            count = rng.randint(200, 400)
        else:
            # Editorial cadence: 50-120/day
            count = rng.randint(50, 120)
        doc_daily_plan.append((day_offset, count))

    total_docs = sum(c for _, c in doc_daily_plan)
    # Scale to target
    scale = TOTAL_DOCS_SIGNED / total_docs
    doc_daily_plan = [(d, max(1, int(c * scale))) for d, c in doc_daily_plan]

    for day_offset, count in doc_daily_plan:
        event_date = TODAY - timedelta(days=day_offset)
        # Spread across a few hours
        for hour in rng.sample(range(0, 20), k=min(6, count)):
            chunk = max(1, count // 6)
            event_dt = datetime(
                event_date.year, event_date.month, event_date.day,
                hour, rng.randint(0, 59), tzinfo=timezone.utc,
            )
            rows.append({
                "user_id": USER_ID,
                "org_id": ORG_ID,
                "metric_type": "document_signed",
                "service_name": "enterprise-api",
                "endpoint": "/api/v1/sign",
                "count": chunk,
                "response_time_ms": rng.randint(45, 180),
                "status_code": 200,
                "date": event_date.isoformat(),
                "hour": hour,
                "created_at": event_dt,
            })

    # -- Verifications: 843 total, heavier in last 30 days
    verify_daily_plan = []
    for i in range(90):
        day_offset = 89 - i
        if day_offset >= 60:
            count = rng.randint(2, 6)
        elif day_offset >= 30:
            count = rng.randint(5, 12)
        else:
            count = rng.randint(8, 20)
        verify_daily_plan.append((day_offset, count))

    total_verify = sum(c for _, c in verify_daily_plan)
    scale = TOTAL_VERIFICATIONS / total_verify
    verify_daily_plan = [(d, max(1, int(c * scale))) for d, c in verify_daily_plan]

    for day_offset, count in verify_daily_plan:
        event_date = TODAY - timedelta(days=day_offset)
        for hour in rng.sample(range(0, 24), k=min(4, count)):
            chunk = max(1, count // 4)
            event_dt = datetime(
                event_date.year, event_date.month, event_date.day,
                hour, rng.randint(0, 59), tzinfo=timezone.utc,
            )
            rows.append({
                "user_id": USER_ID,
                "org_id": ORG_ID,
                "metric_type": "document_verified",
                "service_name": "enterprise-api",
                "endpoint": "/api/v1/public/verify",
                "count": chunk,
                "response_time_ms": rng.randint(25, 100),
                "status_code": 200,
                "date": event_date.isoformat(),
                "hour": hour,
                "created_at": event_dt,
            })

    # -- API calls: everything else (status checks, webhooks, lookups)
    for day_offset in range(90):
        event_date = TODAY - timedelta(days=day_offset)
        count = rng.randint(80, 250) if day_offset < 30 else rng.randint(40, 120)
        for hour in [9, 12, 15, 18]:
            event_dt = datetime(
                event_date.year, event_date.month, event_date.day,
                hour, rng.randint(0, 59), tzinfo=timezone.utc,
            )
            rows.append({
                "user_id": USER_ID,
                "org_id": ORG_ID,
                "metric_type": "api_call",
                "service_name": "enterprise-api",
                "endpoint": "/api/v1/",
                "count": count // 4,
                "response_time_ms": rng.randint(30, 150),
                "status_code": 200,
                "date": event_date.isoformat(),
                "hour": hour,
                "created_at": event_dt,
            })

    for r in rows:
        cur.execute(
            """
            INSERT INTO usage_metrics (
                id, user_id, organization_id,
                metric_type, service_name, endpoint,
                count, response_time_ms, status_code,
                date, hour, created_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                str(uuid.uuid4()),
                r["user_id"], r["org_id"],
                r["metric_type"], r["service_name"], r["endpoint"],
                r["count"], r["response_time_ms"], r["status_code"],
                r["date"], r["hour"], r["created_at"],
            ),
        )

    print(f"  [analytics] inserted {len(rows)} usage_metrics rows")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Seeding The Encypher Times demo account...")
    print()

    print("[1/3] Auth database (encypher_auth)...")
    with connect("encypher_auth") as conn:
        with conn.cursor() as cur:
            seed_auth(cur)
        conn.commit()

    print()
    print("[2/3] Content database (encypher_content)...")
    with connect("encypher_content") as conn:
        with conn.cursor() as cur:
            seed_content(cur)
        conn.commit()

    print()
    print("[3/3] Analytics database (encypher_analytics)...")
    with connect("encypher_analytics") as conn:
        with conn.cursor() as cur:
            seed_analytics(cur)
        conn.commit()

    print()
    print("Done. Demo account ready:")
    print(f"  URL:      http://localhost:3000/auth/signin")
    print(f"  Email:    {ORG_EMAIL}")
    print(f"  Password: {USER_PASSWORD}")
    print(f"  Org ID:   {ORG_ID}")
    print(f"  API Key:  {API_KEY}")
    print()
    print("Analytics summary:")
    print(f"  Documents signed:   {TOTAL_DOCS_SIGNED:,}")
    print(f"  External verifications: {TOTAL_VERIFICATIONS:,}  (> 500 threshold -- Notice Ready)")
    print(f"  Coalition earnings: $1,240 confirmed + $890 pending")


if __name__ == "__main__":
    main()
