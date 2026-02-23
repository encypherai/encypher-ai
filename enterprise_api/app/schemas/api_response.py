"""
Standardized API response models for consistent, future-compatible responses.

All API endpoints should use these models to ensure:
- Consistent response structure across all endpoints
- Clear tier-based feature gating visibility
- Future compatibility for new features
- Proper error handling with machine-readable codes
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

# Generic type for response data
T = TypeVar("T")


# =============================================================================
# Tier Definitions
# =============================================================================

class TierName:
    """Tier name constants.

    TEAM_145: Consolidated to free/enterprise/strategic_partner.
    Legacy aliases kept for backward compatibility in tier_at_least().
    """

    FREE = "free"
    ENTERPRISE = "enterprise"
    STRATEGIC_PARTNER = "strategic_partner"
    DEMO = "demo"


from app.core.tier_config import TIER_HIERARCHY, BATCH_LIMITS  # SSOT


def tier_at_least(current_tier: str, required_tier: str) -> bool:
    """Check if current tier meets or exceeds required tier."""
    current = TIER_HIERARCHY.get(current_tier.lower().replace("-", "_"), 0)
    required = TIER_HIERARCHY.get(required_tier.lower().replace("-", "_"), 0)
    return current >= required


# =============================================================================
# Feature Definitions with Tier Requirements
# =============================================================================

class FeatureDefinition(BaseModel):
    """Definition of a feature with its tier requirement."""
    
    name: str = Field(..., description="Feature identifier")
    display_name: str = Field(..., description="Human-readable feature name")
    description: str = Field(..., description="Feature description")
    required_tier: str = Field(..., description="Minimum tier required")
    category: str = Field(default="general", description="Feature category")


# Master feature registry - single source of truth for tier requirements
FEATURE_REGISTRY: Dict[str, FeatureDefinition] = {
    # === Signing Features ===
    "basic_signing": FeatureDefinition(
        name="basic_signing",
        display_name="Basic C2PA Signing",
        description="Sign content with C2PA manifest at document level",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "sentence_segmentation": FeatureDefinition(
        name="sentence_segmentation",
        display_name="Sentence-Level Segmentation",
        description="Sign content with sentence-level granularity",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "paragraph_segmentation": FeatureDefinition(
        name="paragraph_segmentation",
        display_name="Paragraph-Level Segmentation",
        description="Sign content with paragraph-level granularity",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "section_segmentation": FeatureDefinition(
        name="section_segmentation",
        display_name="Section-Level Segmentation",
        description="Sign content with section-level granularity",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "word_segmentation": FeatureDefinition(
        name="word_segmentation",
        display_name="Word-Level Segmentation",
        description="Sign content with word-level granularity",
        required_tier=TierName.ENTERPRISE,
        category="signing",
    ),
    "manifest_modes": FeatureDefinition(
        name="manifest_modes",
        display_name="Advanced Manifest Modes",
        description="Use lightweight_uuid, minimal_uuid, hybrid, or zw_embedding modes",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "embedding_strategies": FeatureDefinition(
        name="embedding_strategies",
        display_name="Advanced Embedding Strategies",
        description="Use distributed or distributed_redundant embedding strategies",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "attribution_indexing": FeatureDefinition(
        name="attribution_indexing",
        display_name="Attribution Indexing",
        description="Index content for attribution and plagiarism detection",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "custom_assertions": FeatureDefinition(
        name="custom_assertions",
        display_name="Custom C2PA Assertions",
        description="Add custom assertions to C2PA manifest",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "assertion_templates": FeatureDefinition(
        name="assertion_templates",
        display_name="Assertion Templates",
        description="Use pre-defined assertion templates",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "rights_metadata": FeatureDefinition(
        name="rights_metadata",
        display_name="Rights Metadata",
        description="Embed licensing and rights metadata",
        required_tier=TierName.FREE,
        category="signing",
    ),
    "dual_binding": FeatureDefinition(
        name="dual_binding",
        display_name="Dual Binding",
        description="Additional integrity binding for enhanced security",
        required_tier=TierName.ENTERPRISE,
        category="signing",
    ),
    "fingerprinting": FeatureDefinition(
        name="fingerprinting",
        display_name="Content Fingerprinting",
        description="Robust fingerprinting that survives text modifications",
        required_tier=TierName.ENTERPRISE,
        category="signing",
    ),
    "print_fingerprint": FeatureDefinition(
        name="print_fingerprint",
        display_name="Print Leak Detection",
        description="Embed imperceptible spacing patterns that survive printing and scanning for source identification",
        required_tier=TierName.ENTERPRISE,
        category="signing",
    ),
    "batch_signing": FeatureDefinition(
        name="batch_signing",
        display_name="Batch Signing",
        description="Sign multiple documents in a single request",
        required_tier=TierName.FREE,
        category="signing",
    ),
    
    # === Verification Features ===
    "basic_verification": FeatureDefinition(
        name="basic_verification",
        display_name="Basic Verification",
        description="Verify C2PA signed content",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "c2pa_details": FeatureDefinition(
        name="c2pa_details",
        display_name="C2PA Details",
        description="Full C2PA manifest details in verification response",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "document_info": FeatureDefinition(
        name="document_info",
        display_name="Document Information",
        description="Document metadata in verification response",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "licensing_info": FeatureDefinition(
        name="licensing_info",
        display_name="Licensing Information",
        description="License and rights info in verification response",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "merkle_proof": FeatureDefinition(
        name="merkle_proof",
        display_name="Merkle Proof",
        description="Merkle tree proof in verification response",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "attribution_lookup": FeatureDefinition(
        name="attribution_lookup",
        display_name="Attribution Lookup",
        description="Find original sources of content",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "plagiarism_detection": FeatureDefinition(
        name="plagiarism_detection",
        display_name="Plagiarism Detection",
        description="Detect unauthorized content reuse",
        required_tier=TierName.FREE,
        category="verification",
    ),
    "fuzzy_matching": FeatureDefinition(
        name="fuzzy_matching",
        display_name="Fuzzy Matching",
        description="Match paraphrased or modified content",
        required_tier=TierName.ENTERPRISE,
        category="verification",
    ),
    
    # === Account Features ===
    "team_management": FeatureDefinition(
        name="team_management",
        display_name="Team Management",
        description="Manage team members and permissions",
        required_tier=TierName.ENTERPRISE,
        category="account",
    ),
    "audit_logs": FeatureDefinition(
        name="audit_logs",
        display_name="Audit Logs",
        description="Complete activity tracking and audit logs",
        required_tier=TierName.ENTERPRISE,
        category="account",
    ),
    "sso": FeatureDefinition(
        name="sso",
        display_name="Single Sign-On",
        description="SAML/SSO integration",
        required_tier=TierName.ENTERPRISE,
        category="account",
    ),
    "byok": FeatureDefinition(
        name="byok",
        display_name="Bring Your Own Key",
        description="Use your own signing keys",
        required_tier=TierName.ENTERPRISE,
        category="account",
    ),
    "webhooks": FeatureDefinition(
        name="webhooks",
        display_name="Webhooks",
        description="Event notifications via webhooks",
        required_tier=TierName.ENTERPRISE,
        category="account",
    ),
}


def get_feature_tier(feature_name: str) -> str:
    """Get the required tier for a feature."""
    feature = FEATURE_REGISTRY.get(feature_name)
    if feature:
        return feature.required_tier
    return TierName.ENTERPRISE  # Default to highest tier for unknown features


def is_feature_available(feature_name: str, current_tier: str) -> bool:
    """Check if a feature is available for the given tier."""
    required_tier = get_feature_tier(feature_name)
    return tier_at_least(current_tier, required_tier)


def get_available_features(current_tier: str, category: Optional[str] = None) -> List[str]:
    """Get list of features available for the given tier."""
    available = []
    for name, feature in FEATURE_REGISTRY.items():
        if category and feature.category != category:
            continue
        if is_feature_available(name, current_tier):
            available.append(name)
    return available


def get_gated_features(current_tier: str, category: Optional[str] = None) -> List[Dict[str, str]]:
    """Get list of features that require upgrade, with their required tier."""
    gated = []
    for name, feature in FEATURE_REGISTRY.items():
        if category and feature.category != category:
            continue
        if not is_feature_available(name, current_tier):
            gated.append({
                "feature": name,
                "display_name": feature.display_name,
                "required_tier": feature.required_tier,
                "description": feature.description,
            })
    return gated


# =============================================================================
# Batch Limits by Tier
# =============================================================================

from app.core.tier_config import get_batch_limit  # SSOT


# =============================================================================
# Error Models
# =============================================================================

class ErrorDetail(BaseModel):
    """Standard API error object."""
    
    code: str = Field(..., description="Stable machine-readable error code (e.g., E_RATE_LIMIT)")
    message: str = Field(..., description="Human-readable error description")
    hint: Optional[str] = Field(None, description="Optional remediation hint")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")


# Common error codes
class ErrorCode:
    """Standard error codes."""
    
    # Authentication/Authorization
    E_UNAUTHORIZED = "E_UNAUTHORIZED"
    E_FORBIDDEN = "E_FORBIDDEN"
    E_INVALID_API_KEY = "E_INVALID_API_KEY"
    E_EXPIRED_API_KEY = "E_EXPIRED_API_KEY"
    
    # Rate Limiting
    E_RATE_LIMIT = "E_RATE_LIMIT"
    E_RATE_SIGN = "E_RATE_SIGN"
    E_RATE_VERIFY = "E_RATE_VERIFY"
    
    # Quota
    E_QUOTA_EXCEEDED = "E_QUOTA_EXCEEDED"
    E_QUOTA_SIGNATURES = "E_QUOTA_SIGNATURES"
    
    # Tier/Feature
    E_TIER_REQUIRED = "E_TIER_REQUIRED"
    E_FEATURE_UNAVAILABLE = "E_FEATURE_UNAVAILABLE"
    
    # Validation
    E_VALIDATION = "E_VALIDATION"
    E_INVALID_REQUEST = "E_INVALID_REQUEST"
    E_PAYLOAD_TOO_LARGE = "E_PAYLOAD_TOO_LARGE"
    
    # Resource
    E_NOT_FOUND = "E_NOT_FOUND"
    E_DOCUMENT_NOT_FOUND = "E_DOCUMENT_NOT_FOUND"
    
    # Server
    E_INTERNAL = "E_INTERNAL"
    E_SERVICE_UNAVAILABLE = "E_SERVICE_UNAVAILABLE"
    
    # Deprecated
    E_DEPRECATED = "E_DEPRECATED"


# =============================================================================
# Response Metadata
# =============================================================================

class ResponseMeta(BaseModel):
    """Response metadata for observability and tier info."""
    
    tier: str = Field(..., description="Current organization tier")
    features_used: List[str] = Field(default_factory=list, description="Features used in this request")
    features_available: List[str] = Field(default_factory=list, description="Features available at current tier")
    features_gated: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Features requiring upgrade, with required tier",
    )
    rate_limit_remaining: Optional[int] = Field(None, description="Remaining rate limit for this endpoint")
    rate_limit_reset: Optional[datetime] = Field(None, description="When rate limit resets")
    quota_remaining: Optional[int] = Field(None, description="Remaining quota for this operation type")
    quota_reset: Optional[datetime] = Field(None, description="When quota resets")
    processing_time_ms: Optional[int] = Field(None, description="Server processing time in milliseconds")
    api_version: str = Field(default="v1", description="API version")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID for tracing")


# =============================================================================
# Standard API Response Envelope
# =============================================================================

class ApiResponse(BaseModel, Generic[T]):
    """
    Standard API response envelope.
    
    All API endpoints should return this structure for consistency.
    The `data` field contains the actual response payload.
    The `meta` field contains tier info, rate limits, and feature availability.
    
    Example success response:
    ```json
    {
        "success": true,
        "data": { ... },
        "error": null,
        "correlation_id": "req-abc123",
        "meta": {
            "tier": "professional",
            "features_used": ["sentence_segmentation"],
            "features_available": ["basic_signing", "sentence_segmentation", ...],
            "features_gated": [
                {"feature": "custom_assertions", "required_tier": "business"}
            ],
            "rate_limit_remaining": 95,
            "api_version": "v1"
        }
    }
    ```
    
    Example error response:
    ```json
    {
        "success": false,
        "data": null,
        "error": {
            "code": "E_TIER_REQUIRED",
            "message": "This feature requires Enterprise tier or higher",
            "hint": "Upgrade at https://encypherai.com/pricing"
        },
        "correlation_id": "req-abc123",
        "meta": {
            "tier": "free",
            "features_gated": [...]
        }
    }
    ```
    """
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(None, description="Response payload when success is true")
    error: Optional[ErrorDetail] = Field(None, description="Error details when success is false")
    correlation_id: str = Field(..., description="Request correlation ID for tracing")
    meta: Optional[ResponseMeta] = Field(None, description="Response metadata including tier and feature info")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {"document_id": "doc_abc123"},
                    "error": None,
                    "correlation_id": "req-abc123",
                    "meta": {
                        "tier": "free",
                        "features_used": ["basic_signing"],
                        "api_version": "v1",
                    },
                }
            ]
        }
    }


# =============================================================================
# Helper Functions for Building Responses
# =============================================================================

def build_success_response(
    data: Any,
    correlation_id: str,
    tier: str,
    features_used: Optional[List[str]] = None,
    category: Optional[str] = None,
    rate_limit_remaining: Optional[int] = None,
    quota_remaining: Optional[int] = None,
    processing_time_ms: Optional[int] = None,
) -> Dict[str, Any]:
    """Build a standardized success response dict."""
    meta = ResponseMeta(
        tier=tier,
        features_used=features_used or [],
        features_available=get_available_features(tier, category),
        features_gated=get_gated_features(tier, category),
        rate_limit_remaining=rate_limit_remaining,
        quota_remaining=quota_remaining,
        processing_time_ms=processing_time_ms,
        correlation_id=correlation_id,
    )
    
    return {
        "success": True,
        "data": data,
        "error": None,
        "correlation_id": correlation_id,
        "meta": meta.model_dump(),
    }


def build_error_response(
    code: str,
    message: str,
    correlation_id: str,
    tier: str,
    hint: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a standardized error response dict."""
    error = ErrorDetail(
        code=code,
        message=message,
        hint=hint,
        details=details,
    )
    
    meta = ResponseMeta(
        tier=tier,
        features_available=get_available_features(tier, category),
        features_gated=get_gated_features(tier, category),
        correlation_id=correlation_id,
    )
    
    return {
        "success": False,
        "data": None,
        "error": error.model_dump(),
        "correlation_id": correlation_id,
        "meta": meta.model_dump(),
    }


def build_tier_error(
    feature_name: str,
    current_tier: str,
    correlation_id: str,
) -> Dict[str, Any]:
    """Build a tier requirement error response."""
    feature = FEATURE_REGISTRY.get(feature_name)
    required_tier = feature.required_tier if feature else TierName.ENTERPRISE
    display_name = feature.display_name if feature else feature_name
    
    return build_error_response(
        code=ErrorCode.E_TIER_REQUIRED,
        message=f"{display_name} requires {required_tier.title()} tier or higher",
        correlation_id=correlation_id,
        tier=current_tier,
        hint=f"Upgrade your plan at https://encypherai.com/pricing to access {display_name}",
        details={
            "feature": feature_name,
            "required_tier": required_tier,
            "current_tier": current_tier,
        },
    )
