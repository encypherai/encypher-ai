"""Tests for AI-company licensing access to rights signals at scale."""

from __future__ import annotations

import calendar
from datetime import date, datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.utils.api_key import generate_api_key


@pytest.mark.asyncio
async def test_licensing_content_include_rights_signals_creates_audit_log(
    async_client: AsyncClient,
    db,
    content_db,
):
    api_key, api_key_hash, api_key_prefix = generate_api_key()
    company_name = f"Test AI Company {api_key_prefix}"

    today = date.today()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]

    ai_company_id = await db.scalar(
        text(
            """
            INSERT INTO ai_companies (company_name, company_email, api_key_hash, api_key_prefix, status)
            VALUES (:name, :email, :api_key_hash, :api_key_prefix, 'active')
            RETURNING id
            """
        ),
        {
            "name": company_name,
            "email": "licensing@test-ai.local",
            "api_key_hash": api_key_hash,
            "api_key_prefix": api_key_prefix,
        },
    )

    assert ai_company_id is not None

    agreement_id = await db.scalar(
        text(
            """
            INSERT INTO licensing_agreements (
                agreement_name,
                ai_company_id,
                agreement_type,
                total_value,
                currency,
                start_date,
                end_date,
                content_types,
                min_word_count,
                status
            )
            VALUES (
                :agreement_name,
                :ai_company_id,
                'subscription',
                120000.00,
                'USD',
                :start_date,
                :end_date,
                ARRAY['article'],
                0,
                'active'
            )
            RETURNING id
            """
        ),
        {
            "agreement_name": "Test Agreement",
            "ai_company_id": ai_company_id,
            "start_date": today.replace(day=1),
            "end_date": today.replace(day=last_day_of_month),
        },
    )

    assert agreement_id is not None

    created_at = datetime.now(timezone.utc)
    content_id = await content_db.scalar(
        text(
            """
            INSERT INTO content_references (
                organization_id,
                document_id,
                merkle_root_id,
                leaf_hash,
                leaf_index,
                signature_hash,
                license_type,
                license_url,
                created_at,
                manifest_data
            )
            VALUES (
                :organization_id,
                :document_id,
                NULL,
                :leaf_hash,
                0,
                :signature_hash,
                'article',
                'https://example.com/license',
                :created_at,
                CAST(:manifest_data AS jsonb)
            )
            RETURNING id
            """
        ),
        {
            "organization_id": "org_business",
            "document_id": "doc_test_licensing_1",
            "leaf_hash": "a" * 64,
            "signature_hash": "b" * 64,
            "created_at": created_at,
            "manifest_data": '{"assertions": [{"label": "c2pa.training-mining.v1", "data": {"use": {"ai_training": true}}}, {"label": "com.encypher.rights.v1", "data": {"copyright_holder": "ACME News"}}]}',
        },
    )

    await content_db.commit()

    assert content_id is not None

    response = await async_client.get(
        "/api/v1/licensing/content?content_type=article&include_rights_signals=true&limit=10&offset=0",
        headers={"Authorization": f"Bearer {api_key}"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] >= 1
    assert payload["content"]

    first = payload["content"][0]
    assert "rights_signals" in first
    assert first["rights_signals"]["training_mining"]["use"]["ai_training"] is True
    assert first["rights_signals"]["rights"]["copyright_holder"] == "ACME News"

    audit_count = await db.scalar(
        text(
            """
            SELECT COUNT(*) FROM content_access_logs
            WHERE agreement_id = :agreement_id
              AND access_type = 'list'
            """
        ),
        {"agreement_id": agreement_id},
    )

    assert audit_count == 1
