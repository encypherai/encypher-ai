"""
Rights Management Service.

Business logic for publisher rights profiles, document overrides, formal notices,
evidence chain management, detection analytics, and audit logging.

TEAM_215: Implements the priority cascade for rights resolution:
    1. Document-level override  (most specific)
    2. Collection-level override
    3. Content-type override
    4. Publisher default profile  (least specific / always present)

All DB interactions use async SQLAlchemy (asyncpg driver). The session is passed
in from the caller — this service does not manage session lifecycle.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rights import (
    ContentDetectionEvent,
    DocumentRightsOverride,
    FormalNotice,
    KnownCrawler,
    NoticeEvidenceChain,
    PublisherRightsProfile,
    RightsAuditLog,
    RightsLicensingAgreement,
    RightsLicensingRequest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256_hash(content: str) -> str:
    """Return the hex-encoded SHA-256 digest of *content*."""
    return hashlib.sha256(content.encode()).hexdigest()


def _utcnow() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _merge_tier_override(base: dict, override: dict | None) -> dict:
    """
    Shallow-merge *override* on top of *base*.

    Keys present in *override* win; keys absent in *override* fall back to
    *base*. A full deep-merge is intentionally avoided — tier overrides are
    expected to specify only the keys they want to change (e.g. ``permissions``
    block) so a shallow merge at the top level is the correct semantic.
    """
    if not override:
        return base
    return {**base, **override}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class RightsService:
    """Service layer for the Encypher Rights Management System."""

    # ========================================================================
    # Profile Management
    # ========================================================================

    async def create_or_update_profile(
        self,
        db: AsyncSession,
        organization_id: str,
        profile_data: dict,
        performed_by: Optional[UUID] = None,
    ) -> PublisherRightsProfile:
        """
        Create or update a publisher rights profile for *organization_id*.

        Each call creates a **new version row** (append-only). The previous
        profile remains in the DB for history purposes.

        Args:
            db:              Async SQLAlchemy session.
            organization_id: String org ID (matches organizations.id).
            profile_data:    Dict containing profile fields (publisher_name,
                             contact_email, bronze_tier, silver_tier,
                             gold_tier, etc.).
            performed_by:    Optional UUID of the acting user.

        Returns:
            The newly created ``PublisherRightsProfile`` row.
        """
        # Determine the next version number
        result = await db.execute(
            select(func.coalesce(func.max(PublisherRightsProfile.profile_version), 0)).where(
                PublisherRightsProfile.organization_id == organization_id
            )
        )
        current_max: int = result.scalar_one()
        next_version = current_max + 1

        # Capture old value for audit log (current profile, if any)
        old_profile = await self.get_current_profile(db, organization_id)
        old_value: dict | None = None
        if old_profile is not None:
            old_value = {
                "profile_version": old_profile.profile_version,
                "default_license_type": old_profile.default_license_type,
                "notice_status": old_profile.notice_status,
            }

        # Build the new profile row
        now = _utcnow()
        profile = PublisherRightsProfile(
            organization_id=organization_id,
            profile_version=next_version,
            effective_date=profile_data.get("effective_date", now),
            created_at=now,
            updated_by=performed_by,
            # Identity
            publisher_name=profile_data["publisher_name"],
            publisher_url=profile_data.get("publisher_url"),
            contact_email=profile_data["contact_email"],
            contact_url=profile_data.get("contact_url"),
            legal_entity=profile_data.get("legal_entity"),
            jurisdiction=profile_data.get("jurisdiction", "US"),
            # Rights policy
            default_license_type=profile_data.get("default_license_type", "all_rights_reserved"),
            # Tier terms
            bronze_tier=profile_data.get("bronze_tier", {}),
            silver_tier=profile_data.get("silver_tier", {}),
            gold_tier=profile_data.get("gold_tier", {}),
            # Formal notice (embedded)
            notice_status=profile_data.get("notice_status", "draft"),
            notice_effective_date=profile_data.get("notice_effective_date"),
            notice_text=profile_data.get("notice_text"),
            notice_hash=profile_data.get("notice_hash"),
            # Coalition
            coalition_member=profile_data.get("coalition_member", True),
            coalition_joined_at=profile_data.get("coalition_joined_at"),
            licensing_track=profile_data.get("licensing_track", "both"),
        )
        db.add(profile)
        await db.flush()  # Populate profile.id before audit log

        # Audit log
        await self._write_audit_log(
            db=db,
            organization_id=organization_id,
            action="create_or_update_profile",
            resource_type="publisher_rights_profile",
            resource_id=profile.id,
            old_value=old_value,
            new_value={
                "profile_version": next_version,
                "default_license_type": profile.default_license_type,
                "notice_status": profile.notice_status,
            },
            performed_by=performed_by,
        )

        await db.commit()
        await db.refresh(profile)
        return profile

    async def get_current_profile(
        self,
        db: AsyncSession,
        organization_id: str,
    ) -> Optional[PublisherRightsProfile]:
        """Return the latest profile version for *organization_id*, or None."""
        result = await db.execute(
            select(PublisherRightsProfile)
            .where(PublisherRightsProfile.organization_id == organization_id)
            .order_by(desc(PublisherRightsProfile.profile_version))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_profile_history(
        self,
        db: AsyncSession,
        organization_id: str,
    ) -> list[PublisherRightsProfile]:
        """Return all profile versions for *organization_id*, newest first."""
        result = await db.execute(
            select(PublisherRightsProfile)
            .where(PublisherRightsProfile.organization_id == organization_id)
            .order_by(desc(PublisherRightsProfile.profile_version))
        )
        return list(result.scalars().all())

    # ========================================================================
    # Rights Resolution (Priority Cascade)
    # ========================================================================

    async def resolve_rights(
        self,
        db: AsyncSession,
        document_id: Optional[UUID],
        organization_id: str,
        content_type: Optional[str] = None,
        collection_id: Optional[UUID] = None,
    ) -> dict:
        """
        Resolve the effective rights for a piece of content using the cascade:

            1. Document-level override  (document_id match, override_type='document')
            2. Collection-level override (collection_id match, override_type='collection')
            3. Content-type override    (content_type_filter match, override_type='content_type')
            4. Publisher default profile (always present)

        Each more-specific level merges its tier dicts on top of the less-specific
        level. Absent keys fall through to the next level.

        Returns a dict with keys: ``bronze_tier``, ``silver_tier``, ``gold_tier``,
        ``default_license_type``, ``resolved_from`` (list of applied layers),
        ``profile_version``, and ``organization_id``.
        """
        # Step 1 — fetch the publisher default profile (required base)
        profile = await self.get_current_profile(db, organization_id)
        if profile is None:
            # No profile configured — return maximally permissive empty dict so callers
            # can handle missing profile gracefully.
            return {
                "organization_id": organization_id,
                "resolved_from": [],
                "default_license_type": "all_rights_reserved",
                "bronze_tier": {},
                "silver_tier": {},
                "gold_tier": {},
                "profile_version": None,
                "error": "no_profile_configured",
            }

        resolved_bronze: dict = dict(profile.bronze_tier or {})
        resolved_silver: dict = dict(profile.silver_tier or {})
        resolved_gold: dict = dict(profile.gold_tier or {})
        resolved_from: list[str] = ["publisher_default_profile"]

        # Helper to fetch the latest active override matching a filter condition
        async def _fetch_override(conditions: list[Any]) -> Optional[DocumentRightsOverride]:
            result = await db.execute(
                select(DocumentRightsOverride)
                .where(
                    and_(
                        DocumentRightsOverride.organization_id == organization_id,
                        *conditions,
                    )
                )
                .order_by(desc(DocumentRightsOverride.override_version))
                .limit(1)
            )
            return result.scalar_one_or_none()

        # Step 2 — content-type override (lowest priority override, checked first)
        if content_type:
            ct_override = await _fetch_override(
                [
                    DocumentRightsOverride.override_type == "content_type",
                    DocumentRightsOverride.content_type_filter == content_type,
                ]
            )
            if ct_override is not None:
                resolved_bronze = _merge_tier_override(resolved_bronze, ct_override.bronze_tier_override)
                resolved_silver = _merge_tier_override(resolved_silver, ct_override.silver_tier_override)
                resolved_gold = _merge_tier_override(resolved_gold, ct_override.gold_tier_override)
                resolved_from.append(f"content_type_override:{ct_override.id}")

        # Step 3 — collection-level override (higher priority than content-type)
        if collection_id:
            col_override = await _fetch_override(
                [
                    DocumentRightsOverride.override_type == "collection",
                    DocumentRightsOverride.collection_id == collection_id,
                ]
            )
            if col_override is not None:
                resolved_bronze = _merge_tier_override(resolved_bronze, col_override.bronze_tier_override)
                resolved_silver = _merge_tier_override(resolved_silver, col_override.silver_tier_override)
                resolved_gold = _merge_tier_override(resolved_gold, col_override.gold_tier_override)
                resolved_from.append(f"collection_override:{col_override.id}")

        # Step 4 — document-level override (highest priority override)
        if document_id:
            doc_override = await _fetch_override(
                [
                    DocumentRightsOverride.override_type == "document",
                    DocumentRightsOverride.document_id == document_id,
                ]
            )
            if doc_override is not None:
                resolved_bronze = _merge_tier_override(resolved_bronze, doc_override.bronze_tier_override)
                resolved_silver = _merge_tier_override(resolved_silver, doc_override.silver_tier_override)
                resolved_gold = _merge_tier_override(resolved_gold, doc_override.gold_tier_override)
                resolved_from.append(f"document_override:{doc_override.id}")

                # Honour special flags from the document override
                if doc_override.do_not_license:
                    for tier in (resolved_bronze, resolved_silver, resolved_gold):
                        if "permissions" in tier:
                            tier["permissions"]["allowed"] = False
                            tier["permissions"]["requires_license"] = False
                        else:
                            tier["permissions"] = {"allowed": False, "requires_license": False}
                    resolved_from.append("flag:do_not_license")

                if doc_override.embargo_until and doc_override.embargo_until > _utcnow():
                    resolved_from.append(f"flag:embargo_until:{doc_override.embargo_until.isoformat()}")

        return {
            "organization_id": organization_id,
            "resolved_from": resolved_from,
            "default_license_type": profile.default_license_type,
            "bronze_tier": resolved_bronze,
            "silver_tier": resolved_silver,
            "gold_tier": resolved_gold,
            "profile_version": profile.profile_version,
        }

    # ========================================================================
    # Document Overrides
    # ========================================================================

    async def create_document_override(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: UUID,
        override_data: dict,
        performed_by: Optional[UUID] = None,
    ) -> DocumentRightsOverride:
        """
        Create a new versioned document-level rights override.

        Args:
            db:              Async SQLAlchemy session.
            organization_id: Owning organization.
            document_id:     Document UUID to override.
            override_data:   Dict containing any subset of:
                             bronze_tier_override, silver_tier_override,
                             gold_tier_override, do_not_license, premium_content,
                             embargo_until, syndication_rights.
            performed_by:    Optional acting user UUID.

        Returns:
            The newly created ``DocumentRightsOverride`` row.
        """
        # Determine next override version for this document
        result = await db.execute(
            select(func.coalesce(func.max(DocumentRightsOverride.override_version), 0)).where(
                and_(
                    DocumentRightsOverride.organization_id == organization_id,
                    DocumentRightsOverride.document_id == document_id,
                    DocumentRightsOverride.override_type == "document",
                )
            )
        )
        next_version: int = (result.scalar_one() or 0) + 1

        override = DocumentRightsOverride(
            document_id=document_id,
            organization_id=organization_id,
            override_version=next_version,
            created_at=_utcnow(),
            updated_by=performed_by,
            override_type="document",
            collection_id=None,
            content_type_filter=None,
            date_range_start=override_data.get("date_range_start"),
            date_range_end=override_data.get("date_range_end"),
            bronze_tier_override=override_data.get("bronze_tier_override"),
            silver_tier_override=override_data.get("silver_tier_override"),
            gold_tier_override=override_data.get("gold_tier_override"),
            do_not_license=override_data.get("do_not_license", False),
            premium_content=override_data.get("premium_content", False),
            embargo_until=override_data.get("embargo_until"),
            syndication_rights=override_data.get("syndication_rights"),
        )
        db.add(override)
        await db.flush()

        await self._write_audit_log(
            db=db,
            organization_id=organization_id,
            action="create_document_override",
            resource_type="document_rights_override",
            resource_id=override.id,
            old_value=None,
            new_value={
                "document_id": str(document_id),
                "override_version": next_version,
                "do_not_license": override.do_not_license,
            },
            performed_by=performed_by,
        )

        await db.commit()
        await db.refresh(override)
        return override

    async def get_document_override(
        self,
        db: AsyncSession,
        document_id: UUID,
        organization_id: str,
    ) -> Optional[DocumentRightsOverride]:
        """Return the latest document-level override for *document_id*, or None."""
        result = await db.execute(
            select(DocumentRightsOverride)
            .where(
                and_(
                    DocumentRightsOverride.document_id == document_id,
                    DocumentRightsOverride.organization_id == organization_id,
                    DocumentRightsOverride.override_type == "document",
                )
            )
            .order_by(desc(DocumentRightsOverride.override_version))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ========================================================================
    # Formal Notices
    # ========================================================================

    async def create_notice(
        self,
        db: AsyncSession,
        organization_id: str,
        notice_data: dict,
        created_by: Optional[UUID] = None,
    ) -> FormalNotice:
        """
        Create a new formal notice for *organization_id*.

        The notice_text is SHA-256 hashed on creation. An initial evidence
        chain entry (event_type='notice_created') is appended automatically.

        Args:
            db:              Async SQLAlchemy session.
            organization_id: Issuing organization.
            notice_data:     Dict containing at minimum:
                             target_entity_name, notice_type, notice_text,
                             scope_type, demands. Optional: target_entity_domain,
                             target_contact_email, target_entity_type,
                             scope_document_ids, scope_date_range_start,
                             scope_date_range_end.
            created_by:      Optional acting user UUID.

        Returns:
            The newly created ``FormalNotice`` row.
        """
        notice_text: str = notice_data["notice_text"]
        notice_hash = sha256_hash(notice_text)

        now = _utcnow()
        notice = FormalNotice(
            organization_id=organization_id,
            created_at=now,
            created_by=created_by,
            # Target
            target_entity_name=notice_data["target_entity_name"],
            target_entity_domain=notice_data.get("target_entity_domain"),
            target_contact_email=notice_data.get("target_contact_email"),
            target_entity_type=notice_data.get("target_entity_type", "ai_company"),
            # Scope
            scope_type=notice_data["scope_type"],
            scope_document_ids=notice_data.get("scope_document_ids"),
            scope_date_range_start=notice_data.get("scope_date_range_start"),
            scope_date_range_end=notice_data.get("scope_date_range_end"),
            # Content
            notice_type=notice_data["notice_type"],
            notice_text=notice_text,
            notice_hash=notice_hash,
            demands=notice_data.get("demands", {}),
            status="created",
        )
        db.add(notice)
        await db.flush()  # Populate notice.id before evidence chain

        # Initial evidence chain entry
        await self.append_evidence(
            db=db,
            notice_id=notice.id,
            event_type="notice_created",
            event_data={
                "organization_id": organization_id,
                "notice_type": notice.notice_type,
                "target_entity_name": notice.target_entity_name,
                "notice_hash": notice_hash,
                "created_at": now.isoformat(),
                "created_by": str(created_by) if created_by else None,
            },
        )

        await self._write_audit_log(
            db=db,
            organization_id=organization_id,
            action="create_notice",
            resource_type="formal_notice",
            resource_id=notice.id,
            old_value=None,
            new_value={
                "notice_type": notice.notice_type,
                "target_entity_name": notice.target_entity_name,
                "notice_hash": notice_hash,
                "status": "created",
            },
            performed_by=created_by,
        )

        await db.commit()
        await db.refresh(notice)
        return notice

    async def deliver_notice(
        self,
        db: AsyncSession,
        notice_id: UUID,
        delivery_method: str,
        delivery_info: dict,
    ) -> FormalNotice:
        """
        Mark a notice as delivered and lock its content from further modification.

        Args:
            db:              Async SQLAlchemy session.
            notice_id:       UUID of the notice to deliver.
            delivery_method: String identifier (e.g. 'email', 'api', 'certified_mail').
            delivery_info:   Delivery metadata (receipts, timestamps, contacts, etc.).

        Returns:
            The updated ``FormalNotice`` row.

        Raises:
            ValueError: If the notice does not exist or is already delivered.
        """
        notice = await self.get_notice(db, notice_id)
        if notice is None:
            raise ValueError(f"FormalNotice {notice_id} not found")
        if notice.status in ("delivered", "acknowledged"):
            raise ValueError(f"FormalNotice {notice_id} is already in status '{notice.status}'")

        now = _utcnow()
        # Mutate via attribute assignment (works with SQLAlchemy instrumented attrs)
        notice_any = notice  # type: ignore[assignment]
        notice_any.status = "delivered"
        notice_any.delivered_at = now
        notice_any.delivery_method = delivery_method
        notice_any.delivery_receipt = delivery_info
        notice_any.delivery_receipt_hash = sha256_hash(json.dumps(delivery_info, sort_keys=True, default=str))

        # Evidence chain entry for delivery
        await self.append_evidence(
            db=db,
            notice_id=notice_id,
            event_type="notice_delivered",
            event_data={
                "delivery_method": delivery_method,
                "delivery_info": delivery_info,
                "delivered_at": now.isoformat(),
            },
        )

        await self._write_audit_log(
            db=db,
            organization_id=notice.organization_id,
            action="deliver_notice",
            resource_type="formal_notice",
            resource_id=notice_id,
            old_value={"status": "created"},
            new_value={"status": "delivered", "delivery_method": delivery_method},
        )

        await db.commit()
        await db.refresh(notice)
        return notice

    async def get_notice(
        self,
        db: AsyncSession,
        notice_id: UUID,
    ) -> Optional[FormalNotice]:
        """Return a FormalNotice by ID, or None."""
        result = await db.execute(select(FormalNotice).where(FormalNotice.id == notice_id))
        return result.scalar_one_or_none()

    async def generate_evidence_package(
        self,
        db: AsyncSession,
        notice_id: UUID,
    ) -> dict:
        """
        Assemble a court-ready evidence bundle for *notice_id*.

        The bundle includes:
        - The notice record with its hash
        - The full ordered evidence chain with per-entry hash verification
        - A chain-integrity flag (True if every link is verified)
        - The rights terms captured at notice creation time

        Returns:
            Dict with keys: ``notice``, ``evidence_chain``, ``chain_integrity_verified``,
            ``package_hash``, ``generated_at``.

        Raises:
            ValueError: If the notice does not exist.
        """
        notice = await self.get_notice(db, notice_id)
        if notice is None:
            raise ValueError(f"FormalNotice {notice_id} not found")

        # Fetch evidence chain ordered chronologically
        result = await db.execute(
            select(NoticeEvidenceChain).where(NoticeEvidenceChain.notice_id == notice_id).order_by(NoticeEvidenceChain.created_at)
        )
        chain_rows = list(result.scalars().all())

        # Verify chain integrity — recompute each hash and check links
        chain_valid = True
        chain_entries: list[dict] = []
        previous_hash: str | None = None

        for entry in chain_rows:
            expected_hash = sha256_hash(json.dumps(entry.event_data, sort_keys=True) + (previous_hash or "genesis"))
            entry_valid = entry.event_hash == expected_hash
            chain_entries.append(
                {
                    "id": str(entry.id),
                    "event_type": entry.event_type,
                    "event_data": entry.event_data,
                    "event_hash": entry.event_hash,
                    "previous_hash": entry.previous_hash,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None,
                    "hash_verified": entry_valid,
                }
            )
            if not entry_valid:
                chain_valid = False
            previous_hash = entry.event_hash

        notice_dict = {
            "id": str(notice.id),
            "organization_id": notice.organization_id,
            "created_at": notice.created_at.isoformat() if notice.created_at else None,
            "created_by": str(notice.created_by) if notice.created_by else None,
            "target_entity_name": notice.target_entity_name,
            "target_entity_domain": notice.target_entity_domain,
            "target_contact_email": notice.target_contact_email,
            "target_entity_type": notice.target_entity_type,
            "scope_type": notice.scope_type,
            "scope_document_ids": [str(d) for d in (notice.scope_document_ids or [])],
            "scope_date_range_start": (notice.scope_date_range_start.isoformat() if notice.scope_date_range_start else None),
            "scope_date_range_end": (notice.scope_date_range_end.isoformat() if notice.scope_date_range_end else None),
            "notice_type": notice.notice_type,
            "notice_text": notice.notice_text,
            "notice_hash": notice.notice_hash,
            "notice_hash_verified": sha256_hash(notice.notice_text or "") == (notice.notice_hash or ""),
            "demands": notice.demands,
            "status": notice.status,
            "delivered_at": notice.delivered_at.isoformat() if notice.delivered_at else None,
            "delivery_method": notice.delivery_method,
            "delivery_receipt": notice.delivery_receipt,
            "delivery_receipt_hash": notice.delivery_receipt_hash,
            "acknowledged_at": notice.acknowledged_at.isoformat() if notice.acknowledged_at else None,
        }

        generated_at = _utcnow().isoformat()
        # Package hash covers notice content + chain + generation timestamp
        package_payload = json.dumps(
            {
                "notice_hash": notice.notice_hash,
                "chain_tip_hash": previous_hash,
                "generated_at": generated_at,
            },
            sort_keys=True,
        )
        package_hash = sha256_hash(package_payload)

        return {
            "notice": notice_dict,
            "evidence_chain": chain_entries,
            "chain_integrity_verified": chain_valid,
            "package_hash": package_hash,
            "generated_at": generated_at,
        }

    # ========================================================================
    # Evidence Chain
    # ========================================================================

    async def append_evidence(
        self,
        db: AsyncSession,
        notice_id: UUID,
        event_type: str,
        event_data: dict,
    ) -> NoticeEvidenceChain:
        """
        Append an event to the cryptographic evidence chain for *notice_id*.

        Hash computation:
            event_hash = SHA-256(json.dumps(event_data, sort_keys=True) + (previous_hash or "genesis"))

        Args:
            db:          Async SQLAlchemy session.
            notice_id:   UUID of the parent FormalNotice.
            event_type:  Short label (e.g. 'notice_created', 'notice_delivered').
            event_data:  Arbitrary JSON-serialisable dict for this event.

        Returns:
            The newly created ``NoticeEvidenceChain`` row.
        """
        # Get the most recent entry's hash to form the chain link
        result = await db.execute(
            select(NoticeEvidenceChain).where(NoticeEvidenceChain.notice_id == notice_id).order_by(desc(NoticeEvidenceChain.created_at)).limit(1)
        )
        last_entry = result.scalar_one_or_none()
        previous_hash: str | None = last_entry.event_hash if last_entry is not None else None

        # Compute this entry's hash
        event_hash = sha256_hash(json.dumps(event_data, sort_keys=True, default=str) + (previous_hash or "genesis"))

        entry = NoticeEvidenceChain(
            notice_id=notice_id,
            event_type=event_type,
            event_data=event_data,
            event_hash=event_hash,
            previous_hash=previous_hash,
            created_at=_utcnow(),
        )
        db.add(entry)
        await db.flush()
        return entry

    # ========================================================================
    # Detection Analytics
    # ========================================================================

    async def log_detection_event(
        self,
        db: AsyncSession,
        event_data: dict,
    ) -> None:
        """
        Record a content detection event (non-blocking fire-and-forget insert).

        Classifies the requester_user_agent against known_crawlers and sets
        user_agent_category automatically.

        Args:
            db:          Async SQLAlchemy session.
            event_data:  Dict with detection fields; see ContentDetectionEvent columns.
        """
        user_agent: str = event_data.get("requester_user_agent", "")
        if user_agent:
            category = await self.classify_user_agent(db, user_agent)
        else:
            category = "unknown"

        event = ContentDetectionEvent(
            document_id=event_data.get("document_id"),
            organization_id=event_data.get("organization_id", ""),
            detection_source=event_data.get("detection_source", "unknown"),
            detected_on_url=event_data.get("detected_on_url"),
            detected_on_domain=event_data.get("detected_on_domain"),
            requester_ip=event_data.get("requester_ip"),
            requester_org_id=event_data.get("requester_org_id"),
            requester_user_agent=user_agent or None,
            user_agent_category=category,
            segments_found=event_data.get("segments_found"),
            integrity_status=event_data.get("integrity_status"),
            rights_served=event_data.get("rights_served", False),
            rights_acknowledged=event_data.get("rights_acknowledged", False),
            created_at=_utcnow(),
        )
        db.add(event)
        # Use flush rather than commit — caller manages transaction boundary.
        # For truly fire-and-forget callers should use a background task.
        await db.flush()

    async def classify_user_agent(
        self,
        db: AsyncSession,
        user_agent: str,
    ) -> str:
        """
        Classify *user_agent* by matching against known_crawlers patterns.

        Returns one of: 'ai_training', 'ai_search', 'search_engine',
        'aggregator', 'monitoring', 'human_browser', 'unknown'.
        """
        if not user_agent:
            return "unknown"

        result = await db.execute(select(KnownCrawler))
        crawlers = result.scalars().all()

        ua_lower = user_agent.lower()
        for crawler in crawlers:
            pattern = (crawler.user_agent_pattern or "").lower()
            if pattern and pattern in ua_lower:
                return crawler.crawler_type

        # Heuristic fallbacks for common human browsers
        browser_signals = ("mozilla/", "chrome/", "safari/", "firefox/", "edg/", "opera/")
        if any(sig in ua_lower for sig in browser_signals):
            # Exclude known bots that spoof browser strings
            if "bot" not in ua_lower and "crawl" not in ua_lower and "spider" not in ua_lower:
                return "human_browser"

        return "unknown"

    async def get_detection_summary(
        self,
        db: AsyncSession,
        organization_id: str,
        days: int = 30,
    ) -> dict:
        """
        Return aggregated detection statistics for *organization_id* over the last *days* days.

        Returns:
            Dict with keys: ``organization_id``, ``period_days``,
            ``total_events``, ``by_source``, ``by_category``,
            ``by_integrity_status``, ``rights_served_count``,
            ``rights_acknowledged_count``, ``unique_domains``.
        """
        cutoff = _utcnow() - timedelta(days=days)
        base_filter = and_(
            ContentDetectionEvent.organization_id == organization_id,
            ContentDetectionEvent.created_at >= cutoff,
        )

        # Total events
        total_result = await db.execute(select(func.count(ContentDetectionEvent.id)).where(base_filter))
        total_events: int = total_result.scalar_one() or 0

        # By detection source
        source_result = await db.execute(
            select(
                ContentDetectionEvent.detection_source,
                func.count(ContentDetectionEvent.id).label("cnt"),
            )
            .where(base_filter)
            .group_by(ContentDetectionEvent.detection_source)
        )
        by_source = {row.detection_source: row.cnt for row in source_result}

        # By user-agent category
        category_result = await db.execute(
            select(
                ContentDetectionEvent.user_agent_category,
                func.count(ContentDetectionEvent.id).label("cnt"),
            )
            .where(base_filter)
            .group_by(ContentDetectionEvent.user_agent_category)
        )
        by_category = {(row.user_agent_category or "unknown"): row.cnt for row in category_result}

        # By integrity status
        integrity_result = await db.execute(
            select(
                ContentDetectionEvent.integrity_status,
                func.count(ContentDetectionEvent.id).label("cnt"),
            )
            .where(base_filter)
            .group_by(ContentDetectionEvent.integrity_status)
        )
        by_integrity = {(row.integrity_status or "unknown"): row.cnt for row in integrity_result}

        # Rights-served / acknowledged counts
        rights_result = await db.execute(
            select(
                func.count(ContentDetectionEvent.id).filter(ContentDetectionEvent.rights_served.is_(True)).label("served"),
                func.count(ContentDetectionEvent.id).filter(ContentDetectionEvent.rights_acknowledged.is_(True)).label("acknowledged"),
            ).where(base_filter)
        )
        rights_row = rights_result.one()

        # Unique detected domains
        domain_result = await db.execute(
            select(func.count(func.distinct(ContentDetectionEvent.detected_on_domain))).where(
                and_(base_filter, ContentDetectionEvent.detected_on_domain.isnot(None))
            )
        )
        unique_domains: int = domain_result.scalar_one() or 0

        return {
            "organization_id": organization_id,
            "period_days": days,
            "total_events": total_events,
            "by_source": by_source,
            "by_category": by_category,
            "by_integrity_status": by_integrity,
            "rights_served_count": rights_row.served or 0,
            "rights_acknowledged_count": rights_row.acknowledged or 0,
            "unique_domains": unique_domains,
        }

    # ========================================================================
    # Audit Logging
    # ========================================================================

    async def _write_audit_log(
        self,
        db: AsyncSession,
        organization_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID],
        old_value: Optional[dict],
        new_value: Optional[dict],
        performed_by: Optional[UUID] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Insert an append-only audit log entry.

        This method uses ``flush`` (not ``commit``) so it participates in the
        caller's transaction. If the surrounding transaction is rolled back, the
        audit entry is also rolled back, which is the correct behaviour — we do
        not want ghost audit entries for failed operations.

        Args:
            db:              Async SQLAlchemy session.
            organization_id: Org context for the logged action.
            action:          Short action label (e.g. 'create_or_update_profile').
            resource_type:   Resource type string (e.g. 'publisher_rights_profile').
            resource_id:     UUID of the affected resource, or None.
            old_value:       Previous state dict (or None for creates).
            new_value:       New state dict (or None for deletes).
            performed_by:    UUID of the acting user, or None for system actions.
            ip_address:      Requester IP string, or None.
        """
        log_entry = RightsAuditLog(
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            performed_by=performed_by,
            performed_at=_utcnow(),
            ip_address=ip_address,
        )
        db.add(log_entry)
        await db.flush()


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors licensing_service pattern)
# ---------------------------------------------------------------------------

rights_service = RightsService()
