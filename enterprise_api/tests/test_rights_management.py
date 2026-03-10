"""
Tests for Rights Management System (TEAM_215).

Covers:
- Unit tests: rights resolution cascade, notice hashing, RSL XML generation, templates
- Integration tests: publisher profile CRUD, public rights resolution, formal notice lifecycle,
  licensing request/response flow
"""

from __future__ import annotations

import hashlib
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

# ════════════════════════════════════════════════════════════════════════════════
# Unit Tests — Rights Service Business Logic
# ════════════════════════════════════════════════════════════════════════════════


class TestSha256Hash:
    """Test the sha256_hash helper."""

    def test_produces_hex_sha256(self):
        from app.services.rights_service import sha256_hash

        content = "This is a formal notice."
        result = sha256_hash(content)

        expected = hashlib.sha256(content.encode()).hexdigest()
        assert result == expected
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_input_same_output(self):
        from app.services.rights_service import sha256_hash

        text = "Reproducible notice content"
        assert sha256_hash(text) == sha256_hash(text)

    def test_different_input_different_output(self):
        from app.services.rights_service import sha256_hash

        assert sha256_hash("notice A") != sha256_hash("notice B")


class TestMergeTierOverride:
    """Test _merge_tier_override shallow-merge helper."""

    def test_none_override_returns_base(self):
        from app.services.rights_service import _merge_tier_override

        base = {"permissions": {"allowed": True}, "pricing": {"model": "free"}}
        result = _merge_tier_override(base, None)
        assert result == base

    def test_override_wins_on_conflict(self):
        from app.services.rights_service import _merge_tier_override

        base = {"permissions": {"allowed": True}, "rate_limit": 1000}
        override = {"rate_limit": 500}
        result = _merge_tier_override(base, override)
        assert result["rate_limit"] == 500
        assert result["permissions"] == {"allowed": True}  # untouched

    def test_override_adds_new_keys(self):
        from app.services.rights_service import _merge_tier_override

        base = {"permissions": {"allowed": True}}
        override = {"pricing": {"model": "metered"}}
        result = _merge_tier_override(base, override)
        assert result["pricing"] == {"model": "metered"}
        assert result["permissions"] == {"allowed": True}

    def test_empty_override_returns_base_unchanged(self):
        from app.services.rights_service import _merge_tier_override

        base = {"k": "v"}
        result = _merge_tier_override(base, {})
        assert result == base


class TestResolveRightsNoProfle:
    """Test resolve_rights when no profile configured."""

    @pytest.mark.asyncio
    async def test_no_profile_returns_error_key(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

        result = await svc.resolve_rights(db=db, document_id=None, organization_id="org_missing")
        assert result["error"] == "no_profile_configured"
        assert result["resolved_from"] == []
        assert result["bronze_tier"] == {}

    @pytest.mark.asyncio
    async def test_no_profile_returns_all_rights_reserved(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

        result = await svc.resolve_rights(db=db, document_id=None, organization_id="org_missing")
        assert result["default_license_type"] == "all_rights_reserved"


class TestResolveRightsCascade:
    """Test the 4-level priority cascade in resolve_rights."""

    def _make_profile(self, bronze=None, silver=None, gold=None):
        profile = MagicMock()
        profile.bronze_tier = bronze or {"permissions": {"allowed": True}, "rate_limit": 1000}
        profile.silver_tier = silver or {"permissions": {"allowed": False}}
        profile.gold_tier = gold or {"permissions": {"allowed": False}}
        profile.default_license_type = "tiered"
        profile.profile_version = 1
        return profile

    def _make_override(self, override_type, bronze=None, silver=None, gold=None, do_not_license=False, embargo_until=None):
        ov = MagicMock()
        ov.override_type = override_type
        ov.bronze_tier_override = bronze
        ov.silver_tier_override = silver
        ov.gold_tier_override = gold
        ov.do_not_license = do_not_license
        ov.embargo_until = embargo_until
        ov.id = uuid.uuid4()
        return ov

    @pytest.mark.asyncio
    async def test_profile_only_no_overrides(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        profile = self._make_profile(bronze={"rate_limit": 100})

        async def _exec(query):
            mock = MagicMock()
            mock.scalar_one_or_none.return_value = None
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)
        svc.get_current_profile = AsyncMock(return_value=profile)

        result = await svc.resolve_rights(db=db, document_id=None, organization_id="org_1")
        assert result["bronze_tier"]["rate_limit"] == 100
        assert result["resolved_from"] == ["publisher_default_profile"]

    @pytest.mark.asyncio
    async def test_document_override_takes_priority(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        profile = self._make_profile(bronze={"rate_limit": 1000})
        doc_override = self._make_override("document", bronze={"rate_limit": 50})

        # Only document_id is passed — resolve_rights calls db.execute once (document check)
        async def _exec(query):
            mock = MagicMock()
            mock.scalar_one_or_none.return_value = doc_override
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)
        svc.get_current_profile = AsyncMock(return_value=profile)

        doc_id = uuid.uuid4()
        result = await svc.resolve_rights(db=db, document_id=doc_id, organization_id="org_1")
        assert result["bronze_tier"]["rate_limit"] == 50
        assert any("document_override" in s for s in result["resolved_from"])

    @pytest.mark.asyncio
    async def test_do_not_license_flag_disables_all_tiers(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        profile = self._make_profile(
            bronze={"permissions": {"allowed": True}},
            silver={"permissions": {"allowed": True}},
            gold={"permissions": {"allowed": True}},
        )
        doc_override = self._make_override("document", do_not_license=True)

        # Only document_id passed — resolve_rights calls db.execute once
        async def _exec(query):
            mock = MagicMock()
            mock.scalar_one_or_none.return_value = doc_override
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)
        svc.get_current_profile = AsyncMock(return_value=profile)

        result = await svc.resolve_rights(db=db, document_id=uuid.uuid4(), organization_id="org_1")
        assert result["bronze_tier"]["permissions"]["allowed"] is False
        assert result["silver_tier"]["permissions"]["allowed"] is False
        assert result["gold_tier"]["permissions"]["allowed"] is False
        assert "flag:do_not_license" in result["resolved_from"]


class TestCreateNotice:
    """Test notice creation and hash computation."""

    @pytest.mark.asyncio
    async def test_notice_hash_is_sha256_of_text(self):
        from app.services.rights_service import RightsService, sha256_hash

        svc = RightsService()
        notice_text = "We hereby formally notify you that your use of our content is unauthorized."

        created_notice = MagicMock()
        created_notice.id = uuid.uuid4()
        created_notice.notice_hash = sha256_hash(notice_text)
        created_notice.notice_text = notice_text
        created_notice.status = "created"
        created_notice.notice_type = "cease_and_desist"
        created_notice.target_entity_name = "ExampleAI Inc."
        created_notice.organization_id = "org_pub"

        db = AsyncMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock(return_value=created_notice)

        # Patch internal db.add and evidence chain appending
        added_objects = []
        db.add = MagicMock(side_effect=lambda obj: added_objects.append(obj))

        with (
            patch.object(svc, "append_evidence", new=AsyncMock()),
            patch.object(svc, "_write_audit_log", new=AsyncMock()),
        ):
            # Stub out refresh to return the created notice
            async def _refresh(obj):
                pass

            db.refresh = AsyncMock(side_effect=_refresh)

            result = await svc.create_notice(
                db=db,
                organization_id="org_pub",
                notice_data={
                    "notice_text": notice_text,
                    "notice_type": "cease_and_desist",
                    "target_entity_name": "ExampleAI Inc.",
                    "scope_type": "all_content",
                    "demands": {"stop_use": True},
                },
            )

        # The FormalNotice object added to db should have the correct hash
        assert len(added_objects) >= 1
        notice_obj = added_objects[0]
        assert notice_obj.notice_hash == sha256_hash(notice_text)

    @pytest.mark.asyncio
    async def test_create_notice_calls_append_evidence(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        evidence_calls = []

        async def _append(db, notice_id, event_type, event_data):
            evidence_calls.append({"event_type": event_type, "event_data": event_data})

        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        with (
            patch.object(svc, "append_evidence", side_effect=_append),
            patch.object(svc, "_write_audit_log", new=AsyncMock()),
        ):
            await svc.create_notice(
                db=db,
                organization_id="org_pub",
                notice_data={
                    "notice_text": "Formal notice content",
                    "notice_type": "licensing_notice",
                    "target_entity_name": "TestBot Corp",
                    "scope_type": "all_content",
                    "demands": {},
                },
            )

        assert len(evidence_calls) == 1
        assert evidence_calls[0]["event_type"] == "notice_created"


class TestAppendEvidence:
    """Test evidence chain hashing (tamper-evident linked list)."""

    @pytest.mark.asyncio
    async def test_first_entry_uses_genesis_as_previous(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        db = AsyncMock()

        # Simulate no prior evidence entry
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        db.add = MagicMock()
        db.flush = AsyncMock()

        notice_id = uuid.uuid4()
        event_data = {"foo": "bar"}

        await svc.append_evidence(
            db=db,
            notice_id=notice_id,
            event_type="notice_created",
            event_data=event_data,
        )

        # The chain entry added to the session must have previous_hash=None (genesis)
        added = db.add.call_args_list[0][0][0]
        assert added.previous_hash is None
        expected_hash = hashlib.sha256((json.dumps(event_data, sort_keys=True) + "genesis").encode()).hexdigest()
        assert added.event_hash == expected_hash

    @pytest.mark.asyncio
    async def test_subsequent_entry_links_to_previous(self):
        from app.services.rights_service import RightsService

        svc = RightsService()
        db = AsyncMock()

        previous_entry = MagicMock()
        previous_entry.event_hash = "abc123"

        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=previous_entry)))
        db.add = MagicMock()
        db.flush = AsyncMock()

        event_data = {"delivery_method": "email"}
        await svc.append_evidence(
            db=db,
            notice_id=uuid.uuid4(),
            event_type="notice_delivered",
            event_data=event_data,
        )

        added = db.add.call_args_list[0][0][0]
        assert added.previous_hash == "abc123"
        expected_hash = hashlib.sha256((json.dumps(event_data, sort_keys=True) + "abc123").encode()).hexdigest()
        assert added.event_hash == expected_hash


# ════════════════════════════════════════════════════════════════════════════════
# Unit Tests — RSL XML Generation
# ════════════════════════════════════════════════════════════════════════════════


class TestRSLXmlGeneration:
    """Test RSL 1.0 XML generation from a publisher profile."""

    def _make_profile_obj(self, **kwargs):
        """Build a mock profile object with ORM-like attributes."""
        obj = MagicMock()
        obj.publisher_name = kwargs.get("publisher_name", "Test Publisher")
        obj.publisher_url = kwargs.get("publisher_url", "https://testpublisher.com")
        obj.contact_email = kwargs.get("contact_email", "rights@testpublisher.com")
        obj.contact_url = kwargs.get("contact_url", None)
        obj.legal_entity = kwargs.get("legal_entity", None)
        obj.jurisdiction = kwargs.get("jurisdiction", "US")
        obj.default_license_type = kwargs.get("default_license_type", "tiered")
        obj.bronze_tier = kwargs.get(
            "bronze_tier",
            {
                "permissions": {"allowed": True, "crawling": True},
                "attribution": {"required": True, "format": "Name + URL"},
                "rate_limit": 5000,
            },
        )
        obj.silver_tier = kwargs.get(
            "silver_tier",
            {
                "permissions": {"allowed": True, "rag_retrieval": True},
            },
        )
        obj.gold_tier = kwargs.get(
            "gold_tier",
            {
                "permissions": {"allowed": False, "requires_license": True},
            },
        )
        obj.notice_status = kwargs.get("notice_status", None)
        return obj

    def test_rsl_xml_contains_root_element(self):
        """RSL output starts with an XML declaration and <rights> root."""
        from app.api.v1.public.rights import _build_rsl_xml

        profile = self._make_profile_obj()
        xml = _build_rsl_xml(org_id="org_abc", profile=profile)
        assert "<?xml" in xml or "<rights" in xml

    def test_rsl_xml_contains_license_elements(self):
        """RSL output contains at least one <license> element."""
        from app.api.v1.public.rights import _build_rsl_xml

        profile = self._make_profile_obj()
        xml = _build_rsl_xml(org_id="org_abc", profile=profile)
        assert "<license" in xml

    def test_rsl_xml_contains_publisher_name(self):
        """RSL output encodes the publisher name."""
        from app.api.v1.public.rights import _build_rsl_xml

        profile = self._make_profile_obj(publisher_name="Acme News Corp")
        xml = _build_rsl_xml(org_id="org_abc", profile=profile)
        assert "Acme News Corp" in xml

    def test_rsl_xml_bronze_tier_present(self):
        """Bronze tier (crawling) appears in RSL output."""
        from app.api.v1.public.rights import _build_rsl_xml

        profile = self._make_profile_obj()
        xml = _build_rsl_xml(org_id="org_abc", profile=profile)
        assert "bronze" in xml.lower() or "crawl" in xml.lower()


# ════════════════════════════════════════════════════════════════════════════════
# Unit Tests — Rights Templates
# ════════════════════════════════════════════════════════════════════════════════


class TestRightsTemplates:
    """Test pre-built rights templates."""

    def test_list_templates_returns_five(self):
        from app.core.rights_templates import list_templates

        templates = list_templates()
        assert len(templates) == 5

    def test_all_templates_have_required_keys(self):
        from app.core.rights_templates import get_template, list_templates

        for summary in list_templates():
            assert "id" in summary
            assert "name" in summary
            # Full template has tier data
            tpl = get_template(summary["id"])
            assert tpl is not None
            assert "bronze_tier" in tpl
            assert "silver_tier" in tpl
            assert "gold_tier" in tpl

    def test_get_template_news_publisher(self):
        from app.core.rights_templates import get_template

        tpl = get_template("news_publisher_default")
        assert tpl is not None
        assert tpl["id"] == "news_publisher_default"

    def test_get_template_unknown_returns_none(self):
        from app.core.rights_templates import get_template

        assert get_template("nonexistent_template") is None

    def test_all_rights_reserved_template_disallows_tiers(self):
        from app.core.rights_templates import get_template

        tpl = get_template("all_rights_reserved")
        # All tiers should have allowed=False
        for tier_key in ("bronze_tier", "silver_tier", "gold_tier"):
            perms = tpl[tier_key].get("permissions", {})
            assert perms.get("allowed") is False, f"{tier_key} should have allowed=False in all_rights_reserved"

    def test_academic_open_access_allows_bronze(self):
        from app.core.rights_templates import get_template

        tpl = get_template("academic_open_access")
        assert tpl is not None
        bronze_perms = tpl["bronze_tier"].get("permissions", {})
        assert bronze_perms.get("allowed") is True


# ════════════════════════════════════════════════════════════════════════════════
# Unit Tests — JSON-LD and ODRL Builders
# ════════════════════════════════════════════════════════════════════════════════


class TestJsonLdBuilder:
    """Test _build_json_ld schema.org output."""

    def _make_profile(self, name="Test Publisher", url="https://testpublisher.com"):
        obj = MagicMock()
        obj.publisher_name = name
        obj.publisher_url = url
        obj.contact_email = "rights@test.com"
        obj.contact_url = None
        obj.legal_entity = None
        return obj

    def test_json_ld_has_context(self):
        from app.api.v1.public.rights import _build_json_ld

        profile = self._make_profile()
        rights = {
            "bronze_tier": {"permissions": {"allowed": True}},
            "silver_tier": {},
            "gold_tier": {},
        }
        ld = _build_json_ld(document_id="doc_123", profile=profile, rights=rights)
        assert "@context" in ld
        assert "@type" in ld

    def test_json_ld_has_publisher(self):
        from app.api.v1.public.rights import _build_json_ld

        profile = self._make_profile(name="Acme Press", url="https://acmepress.com")
        rights = {"bronze_tier": {}, "silver_tier": {}, "gold_tier": {}}
        ld = _build_json_ld(document_id="doc_456", profile=profile, rights=rights)
        assert "Acme Press" in str(ld)


class TestOdrlBuilder:
    """Test _build_odrl W3C ODRL output."""

    def _make_profile(self):
        obj = MagicMock()
        obj.publisher_name = "Test Publisher"
        obj.publisher_url = "https://testpublisher.com"
        return obj

    def test_odrl_has_context(self):
        from app.api.v1.public.rights import _build_odrl

        profile = self._make_profile()
        rights = {
            "bronze_tier": {"permissions": {"allowed": True, "crawling": True}},
            "silver_tier": {},
            "gold_tier": {},
        }
        odrl = _build_odrl(document_id="doc_789", profile=profile, rights=rights)
        assert "@context" in odrl
        assert "odrl" in str(odrl).lower()


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests — Publisher Rights Profile API
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_templates_no_auth(async_client: AsyncClient) -> None:
    """GET /api/v1/rights/templates should work without authentication."""
    resp = await async_client.get("/api/v1/rights/templates")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 5


@pytest.mark.asyncio
async def test_put_rights_profile_unauthenticated(async_client: AsyncClient) -> None:
    """PUT /api/v1/rights/profile requires authentication."""
    resp = await async_client.put(
        "/api/v1/rights/profile",
        json={"publisher_name": "Test"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_rights_profile_unauthenticated(async_client: AsyncClient) -> None:
    """GET /api/v1/rights/profile requires authentication."""
    resp = await async_client.get("/api/v1/rights/profile")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_put_rights_profile_and_get(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """PUT a rights profile then GET it back — round-trip test."""
    profile_data = {
        "publisher_name": "Integration Test Publisher",
        "publisher_url": "https://test.example.com",
        "contact_email": "rights@test.example.com",
        "default_license_type": "tiered",
        "bronze_tier": {
            "permissions": {"allowed": True, "crawling": True},
            "rate_limit": 2000,
            "attribution": {"required": True, "format": "Name + URL"},
        },
        "silver_tier": {
            "permissions": {"allowed": True, "rag_retrieval": True},
        },
        "gold_tier": {
            "permissions": {"allowed": False, "requires_license": True},
        },
    }

    put_resp = await async_client.put(
        "/api/v1/rights/profile",
        json=profile_data,
        headers=auth_headers,
    )
    assert put_resp.status_code in (200, 201), put_resp.text

    body = put_resp.json()
    assert body["publisher_name"] == "Integration Test Publisher"
    assert body["profile_version"] >= 1

    # Now GET the profile back
    get_resp = await async_client.get("/api/v1/rights/profile", headers=auth_headers)
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["publisher_name"] == "Integration Test Publisher"
    assert get_body["bronze_tier"]["rate_limit"] == 2000


@pytest.mark.asyncio
async def test_profile_from_template(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST /api/v1/rights/profile/from-template/{id} creates profile from built-in template."""
    resp = await async_client.post(
        "/api/v1/rights/profile/from-template/blog_independent",
        headers=auth_headers,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert "profile_version" in body
    assert "bronze_tier" in body


@pytest.mark.asyncio
async def test_profile_from_template_unknown_404(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST /api/v1/rights/profile/from-template/<nonexistent> → 404."""
    resp = await async_client.post(
        "/api/v1/rights/profile/from-template/nonexistent_template_xyz",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_profile_version_increments(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """Updating a profile creates a new version (append-only)."""
    base_data = {
        "publisher_name": "Version Test Publisher",
        "default_license_type": "tiered",
        "bronze_tier": {"permissions": {"allowed": True}},
        "silver_tier": {},
        "gold_tier": {},
    }

    r1 = await async_client.put("/api/v1/rights/profile", json=base_data, headers=auth_headers)
    assert r1.status_code in (200, 201)
    v1 = r1.json()["profile_version"]

    r2 = await async_client.put(
        "/api/v1/rights/profile",
        json={**base_data, "publisher_name": "Version Test Publisher v2"},
        headers=auth_headers,
    )
    assert r2.status_code in (200, 201)
    v2 = r2.json()["profile_version"]

    assert v2 > v1

    # History should show both versions
    hist = await async_client.get("/api/v1/rights/profile/history", headers=auth_headers)
    assert hist.status_code == 200
    history = hist.json()
    assert len(history) >= 2


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests — Public Rights Resolution
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_public_rights_no_auth_required(async_client: AsyncClient) -> None:
    """Public rights endpoint requires no authentication (returns 200 or 404, not 401)."""
    resp = await async_client.get("/api/v1/public/rights/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_public_rights_nonexistent_document(async_client: AsyncClient) -> None:
    """Public rights for a nonexistent document_id returns 404."""
    doc_id = str(uuid.uuid4())
    resp = await async_client.get(f"/api/v1/public/rights/{doc_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_public_rights_for_signed_document(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """
    Full sign → public rights lookup flow:
    1. Set a rights profile
    2. Sign a document
    3. Call public rights API with the returned document_id
    4. Verify the rights response matches the profile
    """
    # Step 1 — set rights profile
    await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "E2E Test Publisher",
            "default_license_type": "tiered",
            "bronze_tier": {"permissions": {"allowed": True}, "rate_limit": 999},
            "silver_tier": {"permissions": {"allowed": True}},
            "gold_tier": {"permissions": {"allowed": False}},
        },
        headers=auth_headers,
    )

    # Step 2 — sign a document (reuse existing sign endpoint)
    sign_resp = await async_client.post(
        "/api/v1/sign",
        json={"text": "This is test content for rights resolution."},
        headers=auth_headers,
    )
    if sign_resp.status_code not in (200, 201):
        pytest.skip("Sign endpoint not available or failed — skip E2E rights flow")

    doc_id = sign_resp.json().get("document_id") or sign_resp.json().get("id")
    if not doc_id:
        pytest.skip("Sign response did not return document_id")

    # Step 3 — call public rights API
    rights_resp = await async_client.get(f"/api/v1/public/rights/{doc_id}")
    assert rights_resp.status_code == 200

    rights = rights_resp.json()
    assert "bronze_tier" in rights
    assert "silver_tier" in rights
    assert "gold_tier" in rights
    assert rights["organization"]["name"] == "E2E Test Publisher"


@pytest.mark.asyncio
async def test_public_org_rights_no_auth(
    async_client: AsyncClient,
    auth_headers: dict,
    organization_id: str,
) -> None:
    """GET /api/v1/public/rights/organization/{org_id} works without auth."""
    # First set a profile so the org has something to return
    await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "Org Rights Test Publisher",
            "default_license_type": "tiered",
            "bronze_tier": {"permissions": {"allowed": True}},
            "silver_tier": {},
            "gold_tier": {},
        },
        headers=auth_headers,
    )

    resp = await async_client.get(f"/api/v1/public/rights/organization/{organization_id}")
    assert resp.status_code in (200, 404)  # 404 if org doesn't have profile yet in DB state


@pytest.mark.asyncio
async def test_rsl_xml_endpoint(
    async_client: AsyncClient,
    auth_headers: dict,
    organization_id: str,
) -> None:
    """GET /api/v1/public/rights/organization/{org_id}/rsl returns XML."""
    # Set a profile first
    await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "RSL Test Publisher",
            "default_license_type": "tiered",
            "bronze_tier": {"permissions": {"allowed": True}},
            "silver_tier": {"permissions": {"allowed": False}},
            "gold_tier": {"permissions": {"allowed": False}},
        },
        headers=auth_headers,
    )

    resp = await async_client.get(f"/api/v1/public/rights/organization/{organization_id}/rsl")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "xml" in resp.headers.get("content-type", "").lower() or "<" in resp.text


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests — Formal Notice Lifecycle
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_notice_unauthenticated(async_client: AsyncClient) -> None:
    """POST /api/v1/notices/create requires authentication."""
    resp = await async_client.post("/api/v1/notices/create", json={"notice_text": "test"})
    assert resp.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_notice_full_lifecycle(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """
    Full formal notice lifecycle:
    create → verify hash → deliver → locked → evidence package.
    """
    notice_text = "FORMAL NOTICE: We hereby notify ExampleAI Inc. that their scraping of our content constitutes copyright infringement."

    # Step 1 — Create notice
    create_resp = await async_client.post(
        "/api/v1/notices/create",
        json={
            "notice_text": notice_text,
            "notice_type": "cease_and_desist",
            "target_entity_name": "ExampleAI Inc.",
            "target_entity_domain": "exampleai.com",
            "target_contact_email": "legal@exampleai.com",
            "target_entity_type": "ai_company",
            "scope_type": "all_content",
            "demands": {"stop_use": True, "delete_all_copies": True},
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    notice = create_resp.json()
    notice_id = notice["id"]

    # Verify the hash is correct SHA-256 of notice_text
    expected_hash = hashlib.sha256(notice_text.encode()).hexdigest()
    assert notice["notice_hash"] == expected_hash
    assert notice["status"] == "created"

    # Step 2 — Get notice (with evidence chain)
    get_resp = await async_client.get(f"/api/v1/notices/{notice_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    notice_detail = get_resp.json()
    assert notice_detail["notice_hash"] == expected_hash
    assert "evidence_chain" in notice_detail
    assert len(notice_detail["evidence_chain"]) >= 1

    first_event = notice_detail["evidence_chain"][0]
    assert first_event["event_type"] == "notice_created"
    assert first_event["previous_hash"] is None  # genesis

    # Step 3 — Deliver notice
    deliver_resp = await async_client.post(
        f"/api/v1/notices/{notice_id}/deliver",
        json={
            "delivery_method": "email",
            "recipient_email": "legal@exampleai.com",
        },
        headers=auth_headers,
    )
    assert deliver_resp.status_code == 200, deliver_resp.text
    delivery = deliver_resp.json()
    assert delivery["status"] == "delivered"
    assert delivery["delivery_receipt_hash"] is not None
    assert "Notice delivered and content locked" in delivery["message"]

    # Step 4 — Cannot re-deliver (409 Conflict)
    re_deliver = await async_client.post(
        f"/api/v1/notices/{notice_id}/deliver",
        json={"delivery_method": "api"},
        headers=auth_headers,
    )
    assert re_deliver.status_code == 409

    # Step 5 — Evidence package
    evidence_resp = await async_client.get(
        f"/api/v1/notices/{notice_id}/evidence",
        headers=auth_headers,
    )
    assert evidence_resp.status_code == 200
    package = evidence_resp.json()
    assert "notice" in package
    assert "evidence_chain" in package
    assert package["notice"]["notice_hash"] == expected_hash


@pytest.mark.asyncio
async def test_notice_list(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """GET /api/v1/notices/ returns list of notices for the org."""
    # Create at least one notice
    await async_client.post(
        "/api/v1/notices/create",
        json={
            "notice_text": "List test notice",
            "notice_type": "licensing_notice",
            "target_entity_name": "TestCorp",
            "scope_type": "all_content",
            "demands": {},
        },
        headers=auth_headers,
    )

    resp = await async_client.get("/api/v1/notices/", headers=auth_headers)
    assert resp.status_code == 200
    notices = resp.json()
    assert isinstance(notices, list)
    assert len(notices) >= 1


@pytest.mark.asyncio
async def test_notice_access_control(
    async_client: AsyncClient,
    auth_headers: dict,
    starter_auth_headers: dict,
) -> None:
    """An org cannot access another org's notice (403)."""
    # Create a notice as auth_headers org
    create_resp = await async_client.post(
        "/api/v1/notices/create",
        json={
            "notice_text": "Private notice content",
            "notice_type": "formal_awareness",
            "target_entity_name": "SomeAI",
            "scope_type": "all_content",
            "demands": {},
        },
        headers=auth_headers,
    )
    if create_resp.status_code != 201:
        pytest.skip("Could not create notice for access control test")

    notice_id = create_resp.json()["id"]

    # Try to access as different org
    other_resp = await async_client.get(
        f"/api/v1/notices/{notice_id}",
        headers=starter_auth_headers,
    )
    # Should be 403 (wrong org) or 404
    assert other_resp.status_code in (403, 404)


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests — Licensing Request / Response Flow
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_submit_licensing_request(
    async_client: AsyncClient,
    auth_headers: dict,
    organization_id: str,
) -> None:
    """POST /api/v1/rights-licensing/request creates a pending request."""
    # Use a known existing org as the "publisher" target (org_pubkey_fallback exists in seed data)
    publisher_org_id = "org_pubkey_fallback"

    resp = await async_client.post(
        "/api/v1/rights-licensing/request",
        json={
            "organization_id": publisher_org_id,
            "tier": "bronze",
            "scope": {"content_types": ["article"], "date_range": "all"},
            "proposed_terms": {"rate_limit": 1000, "attribution_required": True},
            "requester": {"company_name": "TestAI Corp", "use_case": "research"},
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "pending"
    assert body["tier"] == "bronze"
    assert "request_id" in body


@pytest.mark.asyncio
async def test_submit_licensing_request_invalid_tier(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """Invalid tier returns 422."""
    resp = await async_client.post(
        "/api/v1/rights-licensing/request",
        json={
            "organization_id": "org_publisher_xyz",
            "tier": "platinum",  # invalid
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_licensing_request_missing_publisher(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """Missing organization_id (publisher) returns 422."""
    resp = await async_client.post(
        "/api/v1/rights-licensing/request",
        json={"tier": "bronze"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_outgoing_requests(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """GET /api/v1/rights-licensing/requests?view=outgoing lists own requests."""
    # Create a request first (using known org as publisher target)
    await async_client.post(
        "/api/v1/rights-licensing/request",
        json={
            "organization_id": "org_pubkey_fallback",
            "tier": "silver",
            "scope": {},
            "proposed_terms": {},
        },
        headers=auth_headers,
    )

    resp = await async_client.get(
        "/api/v1/rights-licensing/requests?view=outgoing",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    requests = resp.json()
    assert isinstance(requests, list)


@pytest.mark.asyncio
async def test_list_agreements(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """GET /api/v1/rights-licensing/agreements returns list (may be empty)."""
    resp = await async_client.get("/api/v1/rights-licensing/agreements", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests — Document Override
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_document_override_unauthenticated(async_client: AsyncClient) -> None:
    """PUT /api/v1/rights/documents/{id} requires authentication."""
    doc_id = str(uuid.uuid4())
    resp = await async_client.put(
        f"/api/v1/rights/documents/{doc_id}",
        json={"bronze_tier_override": {"rate_limit": 100}},
    )
    assert resp.status_code in (401, 403)


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests — Enhanced Sign Endpoint (use_rights_profile)
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sign_use_rights_profile_false_default(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST /api/v1/sign with no use_rights_profile does not add rights_resolution_url."""
    resp = await async_client.post(
        "/api/v1/sign",
        json={"text": "Test content for signing without rights profile."},
        headers=auth_headers,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body.get("success") is True
    doc = body.get("data", {}).get("document", {})
    # rights_resolution_url should NOT be present when use_rights_profile is False
    assert "rights_resolution_url" not in doc


@pytest.mark.asyncio
async def test_sign_use_rights_profile_true_with_profile(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST /api/v1/sign with use_rights_profile=True returns rights_resolution_url."""
    # Set a rights profile first
    profile_resp = await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "Sign With Rights Publisher",
            "default_license_type": "tiered",
            "bronze_tier": {"permissions": {"allowed": True}},
            "silver_tier": {"permissions": {"allowed": True}},
            "gold_tier": {"permissions": {"allowed": False}},
        },
        headers=auth_headers,
    )
    assert profile_resp.status_code in (200, 201), profile_resp.text

    # Sign with use_rights_profile=True
    resp = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "Test content for signing with rights profile.",
            "options": {"use_rights_profile": True},
        },
        headers=auth_headers,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body.get("success") is True
    doc = body.get("data", {}).get("document", {})
    # rights_resolution_url should be present when use_rights_profile is True and a profile exists
    assert "rights_resolution_url" in doc, f"Expected rights_resolution_url in {doc}"
    url = doc["rights_resolution_url"]
    assert "public/rights/" in url
    doc_id = doc.get("document_id", "")
    assert doc_id and doc_id in url


@pytest.mark.asyncio
async def test_sign_use_rights_profile_true_no_profile(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    """POST /api/v1/sign with use_rights_profile=True succeeds even without a profile (graceful)."""
    # starter org likely has no rights profile; signing should succeed regardless
    resp = await async_client.post(
        "/api/v1/sign",
        json={
            "text": "Test content for signing; no rights profile configured.",
            "options": {"use_rights_profile": True},
        },
        headers=starter_auth_headers,
    )
    # Should succeed (200/201) — the rights snapshot hook is best-effort
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body.get("success") is True


# ════════════════════════════════════════════════════════════════════════════════
# Regression Tests — Existing Tests Unaffected
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_health_endpoint_still_works(async_client: AsyncClient) -> None:
    """Health check should still pass after adding rights routes."""
    resp = await async_client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_still_works_2(async_client: AsyncClient) -> None:
    """Health check is unaffected by rights routes (second check for regression)."""
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy" or "status" in data
