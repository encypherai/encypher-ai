"""
Rights Management System Pydantic Schemas.

Request, response, and nested schemas for the publisher rights management
endpoints: profiles, document overrides, formal notices, licensing requests,
detection analytics, and the public rights resolution API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ============================================================================
# Bronze Tier Nested Schemas
# ============================================================================


class BronzeTierPermissions(BaseModel):
    """Permissions block for the bronze licensing tier."""

    allowed: bool = True
    requires_license: bool = False
    license_url: Optional[str] = None
    rate_limits: Optional[Dict[str, Any]] = None
    allowed_purposes: List[str] = Field(default_factory=list)
    prohibited_purposes: List[str] = Field(default_factory=list)
    geographic_restrictions: List[str] = Field(default_factory=list)
    temporal_restrictions: Optional[Dict[str, Any]] = None


class BronzeTierPricing(BaseModel):
    """Pricing terms for the bronze licensing tier."""

    model: str = Field(..., description="Pricing model, e.g. 'free', 'per_api_call', 'flat_rate'")
    indicative_rate: Optional[str] = None
    currency: str = "USD"
    minimum_commitment: Optional[str] = None
    bulk_discount_available: bool = False


class BronzeTierAttribution(BaseModel):
    """Attribution requirements for the bronze licensing tier."""

    required: bool = True
    format: Optional[str] = None
    link_back_required: bool = False
    brand_usage_allowed: bool = False


class BronzeTierTechnicalRequirements(BaseModel):
    """Technical requirements for bronze tier consumers."""

    respect_robots_txt: bool = True
    crawl_delay_seconds: Optional[int] = None
    user_agent_identification: bool = True
    api_preferred: bool = False
    api_endpoint: Optional[str] = None


class BronzeTier(BaseModel):
    """
    Complete bronze tier definition.

    Bronze covers broad-access / read-only / low-value AI use cases
    (e.g. search indexing, RAG, summaries).
    """

    tier: str = "bronze"
    usage_type: str = Field(..., description="Primary usage type for this tier")
    description: Optional[str] = None
    permissions: BronzeTierPermissions = Field(default_factory=BronzeTierPermissions)
    pricing: Optional[BronzeTierPricing] = None
    attribution: BronzeTierAttribution = Field(default_factory=BronzeTierAttribution)
    technical_requirements: BronzeTierTechnicalRequirements = Field(default_factory=BronzeTierTechnicalRequirements)


# ============================================================================
# Silver Tier Nested Schemas
# ============================================================================


class SilverTierPermissions(BaseModel):
    """Permissions block for the silver licensing tier."""

    allowed: bool = True
    requires_license: bool = True
    license_url: Optional[str] = None
    rate_limits: Optional[Dict[str, Any]] = None
    allowed_purposes: List[str] = Field(default_factory=list)
    prohibited_purposes: List[str] = Field(default_factory=list)
    geographic_restrictions: List[str] = Field(default_factory=list)
    temporal_restrictions: Optional[Dict[str, Any]] = None
    sublicensing_allowed: bool = False


class SilverTierPricing(BaseModel):
    """Pricing terms for the silver licensing tier."""

    model: str = Field(..., description="Pricing model, e.g. 'revenue_share', 'per_article', 'subscription'")
    indicative_rate: Optional[str] = None
    currency: str = "USD"
    minimum_commitment: Optional[str] = None
    bulk_discount_available: bool = True
    revenue_share_percentage: Optional[float] = None


class SilverTierAttribution(BaseModel):
    """Attribution requirements for the silver licensing tier."""

    required: bool = True
    format: Optional[str] = None
    link_back_required: bool = True
    brand_usage_allowed: bool = False
    co_branding_allowed: bool = False


class SilverTierTechnicalRequirements(BaseModel):
    """Technical requirements for silver tier consumers."""

    respect_robots_txt: bool = True
    crawl_delay_seconds: Optional[int] = None
    user_agent_identification: bool = True
    api_required: bool = True
    api_endpoint: Optional[str] = None
    rate_limit_per_minute: Optional[int] = None


class SilverTier(BaseModel):
    """
    Complete silver tier definition.

    Silver covers licensed AI training and commercial ingestion use cases
    that require a formal agreement with the publisher.
    """

    tier: str = "silver"
    usage_type: str = Field(..., description="Primary usage type for this tier")
    description: Optional[str] = None
    permissions: SilverTierPermissions = Field(default_factory=SilverTierPermissions)
    pricing: Optional[SilverTierPricing] = None
    attribution: SilverTierAttribution = Field(default_factory=SilverTierAttribution)
    technical_requirements: SilverTierTechnicalRequirements = Field(default_factory=SilverTierTechnicalRequirements)


# ============================================================================
# Gold Tier Nested Schemas
# ============================================================================


class GoldTierPermissions(BaseModel):
    """Permissions block for the gold licensing tier."""

    allowed: bool = True
    requires_license: bool = True
    license_url: Optional[str] = None
    rate_limits: Optional[Dict[str, Any]] = None
    allowed_purposes: List[str] = Field(default_factory=list)
    prohibited_purposes: List[str] = Field(default_factory=list)
    geographic_restrictions: List[str] = Field(default_factory=list)
    temporal_restrictions: Optional[Dict[str, Any]] = None
    sublicensing_allowed: bool = False
    exclusivity_available: bool = True
    custom_terms_available: bool = True


class GoldTierPricing(BaseModel):
    """Pricing terms for the gold licensing tier."""

    model: str = Field(..., description="Pricing model, e.g. 'enterprise_negotiated', 'custom'")
    indicative_rate: Optional[str] = None
    currency: str = "USD"
    minimum_commitment: Optional[str] = None
    bulk_discount_available: bool = True
    revenue_share_percentage: Optional[float] = None
    negotiated_rate: Optional[str] = None


class GoldTierAttribution(BaseModel):
    """Attribution requirements for the gold licensing tier."""

    required: bool = True
    format: Optional[str] = None
    link_back_required: bool = True
    brand_usage_allowed: bool = True
    co_branding_allowed: bool = True
    custom_attribution_allowed: bool = True


class GoldTierTechnicalRequirements(BaseModel):
    """Technical requirements for gold tier consumers."""

    respect_robots_txt: bool = True
    crawl_delay_seconds: Optional[int] = None
    user_agent_identification: bool = True
    api_required: bool = True
    api_endpoint: Optional[str] = None
    dedicated_endpoint_available: bool = True
    rate_limit_per_minute: Optional[int] = None
    sla_available: bool = True


class GoldTier(BaseModel):
    """
    Complete gold tier definition.

    Gold covers fully negotiated enterprise agreements with custom terms,
    exclusivity options, and dedicated technical support.
    """

    tier: str = "gold"
    usage_type: str = Field(..., description="Primary usage type for this tier")
    description: Optional[str] = None
    permissions: GoldTierPermissions = Field(default_factory=GoldTierPermissions)
    pricing: Optional[GoldTierPricing] = None
    attribution: GoldTierAttribution = Field(default_factory=GoldTierAttribution)
    technical_requirements: GoldTierTechnicalRequirements = Field(default_factory=GoldTierTechnicalRequirements)


# ============================================================================
# Publisher Rights Profile Schemas
# ============================================================================


class PublisherRightsProfileCreate(BaseModel):
    """Request body for creating or updating a publisher rights profile."""

    publisher_name: str = Field(..., min_length=1)
    publisher_url: Optional[str] = None
    contact_email: EmailStr
    contact_url: Optional[str] = None
    legal_entity: Optional[str] = None
    jurisdiction: str = "US"

    default_license_type: str = "all_rights_reserved"

    # Tier configs serialised as plain dicts (validated at the service layer)
    bronze_tier: Dict[str, Any] = Field(default_factory=dict)
    silver_tier: Dict[str, Any] = Field(default_factory=dict)
    gold_tier: Dict[str, Any] = Field(default_factory=dict)

    # Formal notice fields
    notice_status: str = "draft"

    # Coalition
    coalition_member: bool = True
    licensing_track: str = "both"


class PublisherRightsProfileResponse(BaseModel):
    """Response schema for a publisher rights profile."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: str
    profile_version: int
    effective_date: datetime
    created_at: datetime
    updated_by: Optional[UUID] = None

    # Publisher identity
    publisher_name: str
    publisher_url: Optional[str] = None
    contact_email: str
    contact_url: Optional[str] = None
    legal_entity: Optional[str] = None
    jurisdiction: str

    # Rights
    default_license_type: str
    bronze_tier: Dict[str, Any]
    silver_tier: Dict[str, Any]
    gold_tier: Dict[str, Any]

    # Formal notice
    notice_status: str
    notice_effective_date: Optional[datetime] = None
    notice_text: Optional[str] = None
    notice_hash: Optional[str] = None

    # Coalition
    coalition_member: bool
    coalition_joined_at: Optional[datetime] = None
    licensing_track: str


class RightsProfileHistory(BaseModel):
    """All versions of a publisher rights profile."""

    organization_id: str
    versions: List[PublisherRightsProfileResponse]
    total: int


# ============================================================================
# Document Rights Override Schemas
# ============================================================================


class DocumentRightsOverrideCreate(BaseModel):
    """Request body for creating a document rights override."""

    document_id: Optional[UUID] = None
    override_type: str = "document"
    collection_id: Optional[UUID] = None
    content_type_filter: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

    bronze_tier_override: Optional[Dict[str, Any]] = None
    silver_tier_override: Optional[Dict[str, Any]] = None
    gold_tier_override: Optional[Dict[str, Any]] = None

    do_not_license: bool = False
    premium_content: bool = False
    embargo_until: Optional[datetime] = None
    syndication_rights: Optional[Dict[str, Any]] = None


class DocumentRightsOverrideResponse(BaseModel):
    """Response schema for a document rights override."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: Optional[UUID] = None
    organization_id: str
    override_version: int
    created_at: datetime
    updated_by: Optional[UUID] = None

    override_type: str
    collection_id: Optional[UUID] = None
    content_type_filter: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

    bronze_tier_override: Optional[Dict[str, Any]] = None
    silver_tier_override: Optional[Dict[str, Any]] = None
    gold_tier_override: Optional[Dict[str, Any]] = None

    do_not_license: bool
    premium_content: bool
    embargo_until: Optional[datetime] = None
    syndication_rights: Optional[Dict[str, Any]] = None


# ============================================================================
# Public Rights API Schemas
# ============================================================================


class PublicRightsPublisher(BaseModel):
    """Publisher identity block in the public rights response."""

    name: str
    url: Optional[str] = None
    contact: Optional[str] = None
    legal_entity: Optional[str] = None


class PublicRightsTiers(BaseModel):
    """Tier licensing terms block in the public rights response."""

    license_type: str
    bronze_tier: Dict[str, Any]
    silver_tier: Dict[str, Any]
    gold_tier: Dict[str, Any]


class PublicRightsFormalNotice(BaseModel):
    """Formal notice summary for the public rights response."""

    status: str
    effective_date: Optional[datetime] = None
    notice_text: Optional[str] = None
    notice_hash: Optional[str] = None


class PublicRightsLicensingContact(BaseModel):
    """Licensing contact information in the public rights response."""

    email: Optional[str] = None
    url: Optional[str] = None
    coalition: bool = False
    coalition_contact: Optional[str] = None


class PublicRightsVerification(BaseModel):
    """Cryptographic verification signals in the public rights response."""

    c2pa_valid: Optional[bool] = None
    merkle_root: Optional[str] = None
    signed_at: Optional[datetime] = None


class PublicRightsResponse(BaseModel):
    """
    Top-level public rights resolution response.

    Returned by GET /rights/{document_id} and the rights resolution URL
    embedded in signed content.
    """

    publisher: PublicRightsPublisher
    rights: PublicRightsTiers
    formal_notice: Optional[PublicRightsFormalNotice] = None
    licensing_contact: PublicRightsLicensingContact
    verification: Optional[PublicRightsVerification] = None


# ============================================================================
# Formal Notice Schemas
# ============================================================================


class FormalNoticeTarget(BaseModel):
    """Target entity specification for a formal notice."""

    entity_name: str
    entity_domain: Optional[str] = None
    contact_email: Optional[str] = None
    entity_type: str = "ai_company"


class FormalNoticeScope(BaseModel):
    """Scope definition for a formal notice."""

    scope_type: str = Field(..., description="all_content | date_range | specific_documents")
    document_ids: Optional[List[UUID]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None


class FormalNoticeCreate(BaseModel):
    """Request body for creating a formal notice."""

    target: FormalNoticeTarget
    scope: FormalNoticeScope
    notice_type: str = Field(..., description="cease_and_desist | licensing_demand | dmca | gdpr_removal")
    demands: Dict[str, Any] = Field(default_factory=dict)


class EvidenceChainEventResponse(BaseModel):
    """Single event in a notice evidence chain."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notice_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    event_hash: str
    previous_hash: Optional[str] = None
    created_at: datetime


class FormalNoticeResponse(BaseModel):
    """Response schema for a formal notice, including its evidence chain."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: str
    created_at: datetime
    created_by: Optional[UUID] = None

    target_entity_name: str
    target_entity_domain: Optional[str] = None
    target_contact_email: Optional[str] = None
    target_entity_type: str

    scope_type: str
    scope_document_ids: Optional[List[UUID]] = None
    scope_date_range_start: Optional[datetime] = None
    scope_date_range_end: Optional[datetime] = None

    notice_type: str
    notice_text: str
    notice_hash: str
    demands: Dict[str, Any]

    status: str
    delivered_at: Optional[datetime] = None
    delivery_method: Optional[str] = None
    delivery_receipt: Optional[Dict[str, Any]] = None
    delivery_receipt_hash: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    response: Optional[Dict[str, Any]] = None

    evidence_chain: List[EvidenceChainEventResponse] = Field(default_factory=list)


class NoticeDeliverRequest(BaseModel):
    """Request body to initiate delivery of a formal notice."""

    delivery_method: str = Field(..., description="email | certified_mail | api_webhook | legal_portal")
    message: Optional[str] = None


class SignedContentProof(BaseModel):
    """Cryptographic proof of specific signed content."""

    document_id: UUID
    content_hash: str
    merkle_root: Optional[str] = None
    signed_at: datetime
    signature: Optional[str] = None


class EvidencePackageResponse(BaseModel):
    """
    Full evidence package for a formal notice.

    Includes cryptographic proofs of content ownership, notice integrity,
    delivery records, and usage evidence.
    """

    notice_id: UUID
    notice_hash: str

    # Ownership proofs
    signed_content_proofs: List[SignedContentProof] = Field(default_factory=list)

    # Notice record
    notice: FormalNoticeResponse

    # Delivery evidence
    delivery_receipts: List[Dict[str, Any]] = Field(default_factory=list)

    # Usage evidence (detection events supporting the notice)
    usage_evidence: List[Dict[str, Any]] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Licensing Request Schemas
# ============================================================================


class RequesterInfo(BaseModel):
    """Requester contact and identity information."""

    name: str
    organization_name: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    intended_use: Optional[str] = None


class LicensingRequestCreate(BaseModel):
    """Request body for submitting a licensing request to a publisher."""

    publisher_org_id: str = Field(..., description="Organization ID of the publisher being requested")
    requester_org_id: Optional[str] = None
    tier: str = Field(..., description="bronze | silver | gold")
    scope: Dict[str, Any] = Field(default_factory=dict)
    proposed_terms: Dict[str, Any] = Field(default_factory=dict)
    requester: RequesterInfo


class LicensingRequestResponse(BaseModel):
    """Response schema for a licensing request."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    publisher_org_id: str
    requester_org_id: Optional[str] = None

    tier: str
    scope: Dict[str, Any]
    proposed_terms: Dict[str, Any]
    requester_info: Dict[str, Any]

    status: str
    response: Optional[Dict[str, Any]] = None
    responded_at: Optional[datetime] = None
    agreement_id: Optional[UUID] = None

    created_at: datetime
    updated_at: datetime


class LicensingRequestRespond(BaseModel):
    """Request body for a publisher to respond to a licensing request."""

    action: str = Field(..., description="approve | counter | reject")
    terms: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated terms for counter-offers or approved agreements",
    )
    message: Optional[str] = None


class RightsLicensingAgreementResponse(BaseModel):
    """Response schema for an active rights licensing agreement."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: Optional[UUID] = None
    publisher_org_id: str
    licensee_org_id: Optional[str] = None
    licensee_name: Optional[str] = None

    tier: str
    scope: Dict[str, Any]
    terms: Dict[str, Any]

    effective_date: datetime
    expiry_date: Optional[datetime] = None
    auto_renew: bool

    status: str
    usage_metrics: Dict[str, Any]

    created_at: datetime
    updated_at: datetime


# ============================================================================
# Rights Audit Log Schemas
# ============================================================================


class RightsAuditLogEntry(BaseModel):
    """Single entry from the rights audit log."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: str
    action: str
    resource_type: str
    resource_id: Optional[UUID] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    performed_by: Optional[UUID] = None
    performed_at: datetime
    ip_address: Optional[str] = None


class RightsAuditLogResponse(BaseModel):
    """Paginated rights audit log response."""

    entries: List[RightsAuditLogEntry]
    total: int
    limit: int
    offset: int


# ============================================================================
# Detection Analytics Schemas
# ============================================================================


class DetectionSummary(BaseModel):
    """Aggregated detection summary for a single source."""

    source: str
    count: int
    trend: Optional[str] = None  # up | down | stable


class CrawlerActivity(BaseModel):
    """Aggregated activity for a known crawler."""

    crawler: str
    visits: int
    licensed: bool


class DetectionTrendPoint(BaseModel):
    """Single data point in a detection trend series."""

    date: str
    count: int


class IntegrityBreakdown(BaseModel):
    """Breakdown of content integrity status across detection events."""

    intact: int = 0
    partial_tampering: int = 0
    significant_tampering: int = 0
    stripped: int = 0
    unknown: int = 0


class RightsAnalyticsResponse(BaseModel):
    """
    Aggregated rights analytics for a publisher's organisation.

    Covers detection source breakdowns, crawler activity, integrity signals,
    and rights acknowledgement rates over a requested time window.
    """

    organization_id: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    total_detections: int = 0
    detections_by_source: List[DetectionSummary] = Field(default_factory=list)
    crawler_activity: List[CrawlerActivity] = Field(default_factory=list)

    rights_served_count: int = 0
    rights_acknowledged_count: int = 0
    acknowledgement_rate: Optional[float] = None

    integrity_breakdown: IntegrityBreakdown = Field(default_factory=IntegrityBreakdown)
    detection_trend: List[DetectionTrendPoint] = Field(default_factory=list)

    top_detected_domains: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# Known Crawler Schemas
# ============================================================================


class KnownCrawlerResponse(BaseModel):
    """Response schema for a known crawler registry entry."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_agent_pattern: str
    crawler_name: str
    operator_org: str
    crawler_type: str
    respects_robots_txt: Optional[bool] = None
    respects_rsl: Optional[bool] = None
    known_ip_ranges: Optional[List[str]] = None
    updated_at: datetime
