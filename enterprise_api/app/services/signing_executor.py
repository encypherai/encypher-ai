"""
Shared signing logic reused by HTTP endpoints and batch workers.

Two-Database Architecture:
- Content DB: Stores documents and sentence_records
- Core DB: Stores organization usage counters
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, cast

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from encypher import UnicodeMetadata
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError("encypher-ai package not found. Please install the preview version with C2PA support.") from exc

from app.config import settings
from app.database import content_session_factory, core_session_factory
from app.models.request_models import SignRequest
from app.models.response_models import SignResponse
from app.services.organization_bootstrap import ensure_organization_exists
from app.services.provisioning_service import ProvisioningService
from app.services.status_service import status_service
from app.utils.coalition_client import CoalitionClient
from app.utils.crypto_utils import get_demo_private_key, load_organization_private_key
from app.utils.sentence_parser import compute_sentence_hash, compute_text_hash, parse_sentences

logger = logging.getLogger(__name__)

STARTER_CUSTOM_ASSERTION_LIMIT = 1


def _get_custom_assertion_limit(tier: str) -> Optional[int]:
    if tier == "starter":
        return STARTER_CUSTOM_ASSERTION_LIMIT
    return None


coalition_client = CoalitionClient(settings.coalition_service_url)


async def execute_signing(
    *,
    request: SignRequest,
    organization: dict,
    db: AsyncSession,
    document_id: Optional[str] = None,
) -> SignResponse:
    """
    Perform signing, persistence, and coalition indexing.

    Args:
        request: Sign request payload.
        organization: Authenticated organization data.
        db: Database session.
        document_id: Optional document identifier override.
    """

    logger.info(
        "Signing request from organization %s (%s chars, type=%s)",
        organization["organization_id"],
        len(request.text),
        request.document_type,
    )

    is_demo_org = organization.get("is_demo", False)
    org_id = organization["organization_id"]

    await ensure_organization_exists(db, organization)

    if not is_demo_org and not org_id.startswith("user_"):
        await ProvisioningService._ensure_organization_certificate(
            db=db,
            organization_id=org_id,
            organization_name=organization.get("organization_name") or org_id,
            authorization=None,
        )

    # Load organization's private key
    # For demo orgs (including user-level keys), use demo key but keep actual org_id as signer
    # This allows verification to look up the org and find they use the demo key
    try:
        if is_demo_org:
            private_key = get_demo_private_key()
            # Use actual org ID as signer - verification will look up and find demo key association
            signer_id = org_id
            logger.info(f"Using demo key for org {org_id} (is_demo=True)")
        else:
            private_key = await load_organization_private_key(org_id, db)
            signer_id = org_id
    except ValueError as exc:
        logger.error("Failed to load private key: %s", exc)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_PRIVATE_KEY",
                "message": "Organization has no private key configured. Please complete certificate onboarding first.",
                "details": str(exc),
            },
        )

    document_id = document_id or f"doc_{uuid.uuid4().hex[:16]}"

    # Embed manifest
    try:
        custom_assertions: Optional[List[Dict[str, Any]]] = None
        raw_assertions: List[Dict[str, Any]] = []

        tier = str(organization.get("tier", "starter")).lower()
        request_custom_assertions = list(request.custom_assertions or [])
        if request_custom_assertions:
            assertion_limit = _get_custom_assertion_limit(tier)
            if assertion_limit is not None and len(request_custom_assertions) > assertion_limit:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "CUSTOM_ASSERTION_LIMIT_EXCEEDED",
                        "message": f"Starter tier supports up to {assertion_limit} custom assertion(s) per sign request",
                        "current_tier": tier,
                        "upgrade_url": "/billing/upgrade",
                    },
                )
            raw_assertions.extend(request_custom_assertions)

        effective_template_id = request.template_id
        if effective_template_id is None:
            row = await db.execute(
                text("SELECT default_c2pa_template_id FROM organizations WHERE id = :org_id"),
                {"org_id": org_id},
            )
            effective_template_id = row.scalar_one_or_none()

        if effective_template_id or request.rights:
            features = organization.get("features", {})
            custom_assertions_enabled = False
            if isinstance(features, dict):
                custom_assertions_enabled = features.get("custom_assertions", False)
            custom_assertions_enabled = custom_assertions_enabled or organization.get("custom_assertions_enabled", False)

            if not custom_assertions_enabled:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "FEATURE_NOT_AVAILABLE",
                        "message": "Custom assertion templates require Business tier or higher",
                        "upgrade_url": "/billing/upgrade",
                    },
                )

        if effective_template_id:
            from app.models.c2pa_template import C2PAAssertionTemplate

            stmt = (
                select(C2PAAssertionTemplate)
                .where(
                    C2PAAssertionTemplate.id == effective_template_id,
                    ((C2PAAssertionTemplate.organization_id == org_id) | (C2PAAssertionTemplate.is_public)),
                    C2PAAssertionTemplate.is_active,
                )
                .limit(1)
            )
            result = await db.execute(stmt)
            template = result.scalar_one_or_none()

            template_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
            if template:
                template_data = cast(Union[Dict[str, Any], List[Dict[str, Any]]], template.template_data or {})
            else:
                from app.services.c2pa_builtin_templates import get_builtin_template

                builtin = get_builtin_template(template_id=effective_template_id)
                if builtin is not None:
                    template_data = builtin.get("template_data") or {}

            if template_data is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "TEMPLATE_NOT_FOUND",
                        "message": "Assertion template not found",
                    },
                )

            assertions_payload: List[Dict[str, Any]] = []
            if isinstance(template_data, dict):
                assertions_payload = [
                    assertion
                    for assertion in (template_data.get("assertions") or [])
                    if isinstance(assertion, dict)
                ]
            elif isinstance(template_data, list):
                assertions_payload = [assertion for assertion in template_data if isinstance(assertion, dict)]

            for assertion in assertions_payload:
                if not isinstance(assertion, dict):
                    continue
                label = assertion.get("label")
                if not label:
                    continue
                data = assertion.get("data")
                if data is None:
                    data = assertion.get("default_data")
                if data is None:
                    continue
                raw_assertions.append({"label": label, "data": data})

        if request.rights:
            rights_payload = request.rights.model_dump(exclude_none=True, mode="json")
            if rights_payload:
                raw_assertions.append({"label": "com.encypher.rights.v1", "data": rights_payload})

        if raw_assertions and request.validate_assertions:
            from app.models.c2pa_schema import C2PASchema
            from app.services.c2pa_validator import validator

            registered_schemas: Dict[str, Dict[str, Any]] = {}
            for assertion in raw_assertions:
                label = assertion.get("label")
                if not label or label in registered_schemas:
                    continue
                stmt = (
                    select(C2PASchema)
                    .where(
                        C2PASchema.label == label,
                        ((C2PASchema.organization_id == org_id) | (C2PASchema.is_public)),
                    )
                    .order_by(C2PASchema.created_at.desc())
                )
                schema_result = await db.execute(stmt)
                schema_model = schema_result.scalar_one_or_none()
                if schema_model:
                    registered_schemas[label] = cast(Dict[str, Any], schema_model.json_schema)

            all_valid, validation_results = validator.validate_custom_assertions(
                raw_assertions,
                registered_schemas,
            )
            if not all_valid:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_ASSERTIONS",
                        "message": "One or more custom assertions failed validation",
                        "validation_results": validation_results,
                    },
                )

        try:
            await ensure_organization_exists(db, organization)
            _list_index, bit_index, status_list_url = await status_service.allocate_status_index(
                db=db,
                organization_id=org_id,
                document_id=document_id,
            )
        except Exception as exc:
            logger.error("Failed to allocate status list index: %s", exc, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "STATUS_LIST_ALLOCATION_FAILED",
                    "message": "Failed to allocate status list entry",
                },
            ) from exc

        status_assertion = {
            "label": "org.encypher.status",
            "data": {
                "statusListCredential": status_list_url,
                "statusListIndex": str(bit_index),
            },
        }

        custom_assertions = list(raw_assertions) if raw_assertions else []
        custom_assertions.append(status_assertion)

        logger.debug("Embedding C2PA manifest for document %s", document_id)
        # Use caller-provided claim_generator, or default to enterprise-api identity
        from app import __version__ as api_version

        effective_claim_generator = request.claim_generator or f"encypher-enterprise-api/{api_version}"

        signed_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="c2pa",
            claim_generator=effective_claim_generator,
            actions=request.actions,
            custom_assertions=custom_assertions,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("C2PA embedding failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "C2PA_EMBEDDING_FAILED",
                "message": "Failed to embed C2PA manifest",
                "details": str(exc) if settings.is_development else None,
            },
        )

    sentences = parse_sentences(request.text)
    text_hash = compute_text_hash(request.text)
    current_time = datetime.now(timezone.utc)

    # Two-Database Architecture:
    # 1. Store document/sentences in CONTENT database
    # 2. Update usage counters in CORE database

    try:
        # Write to CONTENT database (documents, sentences)
        async with content_session_factory() as content_db:
            await content_db.execute(
                text(
                    """
                    INSERT INTO documents (
                        id, organization_id, title, url, document_type,
                        total_sentences, signed_text, text_hash, publication_date, created_at
                    )
                    VALUES (
                        :doc_id, :org_id, :title, :url, :doc_type,
                        :total, :signed, :hash, :pub_date, :created_at
                    )
                    """
                ),
                {
                    "doc_id": document_id,
                    "org_id": organization["organization_id"],
                    "title": request.document_title or "Untitled Document",
                    "url": request.document_url,
                    "doc_type": request.document_type,
                    "total": len(sentences),
                    "signed": signed_text,
                    "hash": text_hash,
                    "pub_date": current_time,
                    "created_at": current_time,
                },
            )

            sentence_records = []
            for idx, sentence in enumerate(sentences):
                sentence_id = f"sent_{uuid.uuid4().hex[:20]}"
                sentence_hash = compute_sentence_hash(sentence)
                sentence_records.append(
                    {
                        "sent_id": sentence_id,
                        "doc_id": document_id,
                        "org_id": organization["organization_id"],
                        "text": sentence,
                        "hash": sentence_hash,
                        "idx": idx,
                    }
                )

            if sentence_records:
                await content_db.execute(
                    text(
                        """
                        INSERT INTO sentence_records (
                            id, document_id, organization_id,
                            sentence_text, sentence_hash, sentence_index, embedded_in_manifest
                        )
                        VALUES (:sent_id, :doc_id, :org_id, :text, :hash, :idx, TRUE)
                        """
                    ),
                    sentence_records,
                )

            await content_db.commit()

        # Write to CORE database (usage counters)
        async with core_session_factory() as core_db:
            await core_db.execute(
                text(
                    """
                    UPDATE organizations
                    SET monthly_api_usage = monthly_api_usage + 1,
                        updated_at = :updated_at
                    WHERE id = :org_id
                    """
                ),
                {
                    "org_id": organization["organization_id"],
                    "updated_at": current_time,
                },
            )
            await core_db.commit()

    except Exception as exc:
        logger.error("Database error while storing document: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to store signed document",
                "details": str(exc) if settings.is_development else None,
            },
        )

    # Best-effort coalition indexing - don't fail signing if this fails
    try:
        await _index_in_coalition(
            document_id=document_id,
            organization=organization,
            request=request,
            text_hash=text_hash,
            current_time=current_time,
            db=db,
        )
    except Exception as exc:
        logger.warning("Coalition indexing failed (non-critical): %s", exc)

    verification_url = _build_verification_url(document_id=document_id, is_demo_org=is_demo_org)

    return SignResponse(
        success=True,
        document_id=document_id,
        signed_text=signed_text,
        total_sentences=len(sentences),
        verification_url=verification_url,
    )


def _build_verification_url(*, document_id: str, is_demo_org: bool) -> str:
    if settings.is_development:
        return f"http://localhost:9000/api/v1/verify/{document_id}"
    if is_demo_org:
        return f"https://verify.{settings.infrastructure_domain}/demo/{document_id}"
    return f"https://verify.{settings.infrastructure_domain}/{document_id}"


async def _index_in_coalition(
    *,
    document_id: str,
    organization: dict,
    request: SignRequest,
    text_hash: str,
    current_time: datetime,
    db: AsyncSession,
) -> None:
    """Best-effort coalition indexing."""

    try:
        # Get the owner user_id from organization_members
        org_result = await db.execute(
            text("SELECT user_id FROM organization_members WHERE organization_id = :org_id AND role = 'owner' LIMIT 1"),
            {"org_id": organization["organization_id"]},
        )
        org_row = org_result.fetchone()
        if not org_row or not org_row.user_id:
            return

        member = await coalition_client.get_member_by_user_id(str(org_row.user_id))
        if not member or member.get("status") != "active":
            return

        member_id = member.get("member_id")
        if not isinstance(member_id, str):
            return

        word_count = len(request.text.split())
        indexed = await coalition_client.index_content(
            member_id=member_id,
            document_id=document_id,
            content_hash=text_hash,
            content_type=request.document_type,
            word_count=word_count,
            signed_at=current_time,
        )
        if indexed:
            logger.info(
                "Document %s indexed in coalition for member %s",
                document_id,
                member.get("member_id"),
            )
    except Exception as exc:  # pragma: no cover - external dependency
        logger.warning("Coalition indexing failed for %s: %s", document_id, exc, exc_info=True)
