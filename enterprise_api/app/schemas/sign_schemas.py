"""
Unified signing schemas with tier-gated options.

This module provides the unified SignRequest that replaces both the basic
/sign and /sign/advanced endpoints with a single endpoint that uses
options to control features, with tier-based gating.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.api_response import (
    BATCH_LIMITS,
    FEATURE_REGISTRY,
    TierName,
    get_batch_limit,
    is_feature_available,
    tier_at_least,
)
from app.schemas.signing_constants import (
    C2PA_ACTIONS,
    DISTRIBUTION_TARGETS,
    EMBEDDING_STRATEGIES,
    MANIFEST_MODES,
    MERKLE_SEGMENTATION_LEVELS,
    SEGMENTATION_LEVELS,
)


# =============================================================================
# Rights Metadata (reused from existing)
# =============================================================================

class RightsMetadata(BaseModel):
    """Rights and licensing metadata to embed in signed content."""
    
    copyright_holder: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Copyright holder / publisher name",
    )
    license_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="URL to license terms",
    )
    usage_terms: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Human-readable usage terms",
    )
    syndication_allowed: Optional[bool] = Field(
        default=None,
        description="Whether downstream syndication is permitted",
    )
    embargo_until: Optional[datetime] = Field(
        default=None,
        description="Optional embargo end timestamp",
    )
    contact_email: Optional[str] = Field(
        default=None,
        max_length=320,
        description="Contact email for licensing",
    )


class LicenseInfo(BaseModel):
    """License information for content."""
    
    type: str = Field(..., description="License type (e.g., 'All Rights Reserved', 'CC-BY-4.0')")
    url: Optional[str] = Field(None, description="License URL")
    contact_email: Optional[str] = Field(None, description="Contact email for licensing")


# =============================================================================
# Embedding Options
# =============================================================================

class EmbeddingOptions(BaseModel):
    """Options for embedding generation output format."""
    
    format: str = Field(
        default="plain",
        description="Output format: plain, html, markdown, json",
    )
    method: str = Field(
        default="invisible",
        description="Embedding method: invisible (zero-width Unicode), data-attribute, span, comment",
    )
    include_text: bool = Field(
        default=True,
        description="Whether to return text with embeddings in response",
    )

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed = ["plain", "html", "markdown", "json"]
        if v not in allowed:
            raise ValueError(f"format must be one of: {', '.join(allowed)}")
        return v

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        allowed = ["invisible", "data-attribute", "span", "comment"]
        if v not in allowed:
            raise ValueError(f"method must be one of: {', '.join(allowed)}")
        return v


# =============================================================================
# Sign Options - Tier-Gated Features
# =============================================================================

class SignOptions(BaseModel):
    """
    Options for signing - features are gated by tier.
    
    Tier Feature Matrix:
    
    | Feature                  | Free/Starter | Professional | Business | Enterprise |
    |--------------------------|--------------|--------------|----------|------------|
    | document_type            | ✅           | ✅           | ✅       | ✅         |
    | claim_generator          | ✅           | ✅           | ✅       | ✅         |
    | segmentation_level       | document     | all          | all      | all        |
    | manifest_mode            | full         | all          | all      | all        |
    | embedding_strategy       | single_point | all          | all      | all        |
    | index_for_attribution    | ❌           | ✅           | ✅       | ✅         |
    | custom_assertions        | ❌           | ❌           | ✅       | ✅         |
    | template_id              | ❌           | ❌           | ✅       | ✅         |
    | rights                   | ❌           | ❌           | ✅       | ✅         |
    | add_dual_binding         | ❌           | ❌           | ❌       | ✅         |
    | include_fingerprint      | ❌           | ❌           | ❌       | ✅         |
    | batch (documents array)  | 1            | 10           | 50       | 100        |
    """
    
    # === Free Tier (All) ===
    document_type: str = Field(
        default="article",
        description="Document type: article, legal_brief, contract, ai_output",
    )
    claim_generator: Optional[str] = Field(
        default=None,
        description="Optional claim generator identifier for C2PA manifests",
    )
    action: str = Field(
        default="c2pa.created",
        description="C2PA action type: c2pa.created (new) or c2pa.edited (modified)",
    )
    previous_instance_id: Optional[str] = Field(
        default=None,
        description="Previous manifest instance_id for edit provenance chain (required if action=c2pa.edited)",
    )
    digital_source_type: Optional[str] = Field(
        default=None,
        description="IPTC digital source type URI (e.g., for AI-generated content)",
    )
    
    # === Professional+ ===
    segmentation_level: str = Field(
        default="document",
        description="Segmentation level: document (free), sentence, paragraph, section (Professional+), word (Enterprise)",
    )
    segmentation_levels: Optional[List[str]] = Field(
        default=None,
        description="Optional list of Merkle segmentation levels to build (Professional+)",
    )
    manifest_mode: str = Field(
        default="full",
        description="Manifest mode: full (free), lightweight_uuid, minimal_uuid, hybrid, zw_embedding, micro, micro_ecc, micro_c2pa, micro_ecc_c2pa (Professional+)",
    )
    embedding_strategy: str = Field(
        default="single_point",
        description="Embedding strategy: single_point (free), distributed, distributed_redundant (Professional+)",
    )
    distribution_target: Optional[str] = Field(
        default=None,
        description="Target for distributed embedding: whitespace, punctuation, all_chars (Professional+)",
    )
    index_for_attribution: bool = Field(
        default=False,
        description="Index content for attribution/plagiarism detection (Professional+)",
    )
    
    # === Business+ ===
    custom_assertions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Custom C2PA assertions to include in manifest (Business+)",
    )
    template_id: Optional[str] = Field(
        default=None,
        description="Assertion template ID to apply (Business+)",
    )
    validate_assertions: bool = Field(
        default=True,
        description="Whether to validate custom assertions against registered schemas (Business+)",
    )
    rights: Optional[RightsMetadata] = Field(
        default=None,
        description="Rights and licensing metadata to embed (Business+)",
    )
    license: Optional[LicenseInfo] = Field(
        default=None,
        description="License information (Business+)",
    )
    actions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of C2PA action assertions (Business+)",
    )
    
    # === Enterprise ===
    add_dual_binding: bool = Field(
        default=False,
        description="Enable additional integrity binding (Enterprise)",
    )
    include_fingerprint: bool = Field(
        default=False,
        description="Include robust fingerprint that survives modifications (Enterprise)",
    )
    disable_c2pa: bool = Field(
        default=False,
        description="Opt-out of C2PA embedding, only basic metadata (Enterprise)",
    )
    
    # === Output Options ===
    embedding_options: EmbeddingOptions = Field(
        default_factory=EmbeddingOptions,
        description="Embedding output format options",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration datetime for embeddings",
    )

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v: str) -> str:
        allowed = ["article", "legal_brief", "contract", "ai_output"]
        if v not in allowed:
            raise ValueError(f"document_type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("segmentation_level")
    @classmethod
    def validate_segmentation_level(cls, v: str) -> str:
        if v not in SEGMENTATION_LEVELS:
            raise ValueError(f"segmentation_level must be one of: {', '.join(SEGMENTATION_LEVELS)}")
        return v

    @field_validator("segmentation_levels")
    @classmethod
    def validate_segmentation_levels(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        for level in v:
            if level not in MERKLE_SEGMENTATION_LEVELS:
                raise ValueError(f"segmentation_levels entries must be one of: {', '.join(sorted(MERKLE_SEGMENTATION_LEVELS))}")
        return v

    @field_validator("manifest_mode")
    @classmethod
    def validate_manifest_mode(cls, v: str) -> str:
        if v not in MANIFEST_MODES:
            raise ValueError(f"manifest_mode must be one of: {', '.join(MANIFEST_MODES)}")
        return v

    @field_validator("embedding_strategy")
    @classmethod
    def validate_embedding_strategy(cls, v: str) -> str:
        if v not in EMBEDDING_STRATEGIES:
            raise ValueError(f"embedding_strategy must be one of: {', '.join(EMBEDDING_STRATEGIES)}")
        return v

    @field_validator("distribution_target")
    @classmethod
    def validate_distribution_target(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in DISTRIBUTION_TARGETS:
            raise ValueError(f"distribution_target must be one of: {', '.join(DISTRIBUTION_TARGETS)}")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in C2PA_ACTIONS:
            raise ValueError(f"action must be one of: {', '.join(C2PA_ACTIONS)}")
        return v


# =============================================================================
# Single Document for Batch
# =============================================================================

class SignDocument(BaseModel):
    """A single document in a batch sign request."""
    
    text: str = Field(
        ...,
        description="Content to sign",
        min_length=1,
        max_length=1_000_000,
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Optional custom document identifier",
        min_length=1,
        max_length=255,
    )
    document_title: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional document title",
    )
    document_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional document URL",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional document metadata (title, author, etc.)",
    )


# =============================================================================
# Unified Sign Request
# =============================================================================

class UnifiedSignRequest(BaseModel):
    """
    Unified sign request supporting single document or batch.
    
    For single document signing:
    ```json
    {
        "text": "Content to sign...",
        "document_title": "My Article",
        "options": {
            "segmentation_level": "sentence"
        }
    }
    ```
    
    For batch signing (Professional+):
    ```json
    {
        "documents": [
            {"text": "First document...", "document_title": "Doc 1"},
            {"text": "Second document...", "document_title": "Doc 2"}
        ],
        "options": {
            "segmentation_level": "sentence"
        }
    }
    ```
    """
    
    # Single document fields
    text: Optional[str] = Field(
        default=None,
        description="Content to sign (for single document)",
        min_length=1,
        max_length=1_000_000,
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Optional custom document identifier",
        min_length=1,
        max_length=255,
    )
    document_title: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional document title",
    )
    document_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional document URL",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional document metadata",
    )
    
    # Batch mode
    documents: Optional[List[SignDocument]] = Field(
        default=None,
        description="List of documents for batch signing (Professional+)",
    )
    
    # Options (tier-gated)
    options: SignOptions = Field(
        default_factory=SignOptions,
        description="Signing options - features gated by tier",
    )

    @model_validator(mode="after")
    def validate_single_or_batch(self) -> "UnifiedSignRequest":
        """Ensure either text or documents is provided, not both."""
        has_text = self.text is not None
        has_documents = self.documents is not None and len(self.documents) > 0
        
        if not has_text and not has_documents:
            raise ValueError("Either 'text' (single document) or 'documents' (batch) must be provided")
        
        if has_text and has_documents:
            raise ValueError("Cannot provide both 'text' and 'documents'. Use 'text' for single document or 'documents' for batch.")
        
        return self

    def is_batch(self) -> bool:
        """Check if this is a batch request."""
        return self.documents is not None and len(self.documents) > 0

    def get_documents(self) -> List[SignDocument]:
        """Get list of documents (converts single to list if needed)."""
        if self.is_batch():
            return self.documents or []
        
        # Convert single document to list
        return [
            SignDocument(
                text=self.text or "",
                document_id=self.document_id,
                document_title=self.document_title,
                document_url=self.document_url,
                metadata=self.metadata,
            )
        ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "The Senate passed a landmark bill today. The vote was 67-33.",
                    "document_title": "Senate Passes Bill",
                    "options": {
                        "document_type": "article",
                        "segmentation_level": "sentence",
                    },
                },
                {
                    "documents": [
                        {"text": "First article content...", "document_title": "Article 1"},
                        {"text": "Second article content...", "document_title": "Article 2"},
                    ],
                    "options": {
                        "document_type": "article",
                        "segmentation_level": "sentence",
                    },
                },
            ]
        }
    }


# =============================================================================
# Tier Validation Helper
# =============================================================================

class TierValidationResult(BaseModel):
    """Result of tier validation for sign options."""
    
    valid: bool = Field(..., description="Whether all options are valid for the tier")
    features_used: List[str] = Field(default_factory=list, description="Features being used")
    features_denied: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Features denied due to tier, with required tier info",
    )
    adjusted_options: Optional[SignOptions] = Field(
        default=None,
        description="Options adjusted to tier limits (if auto-downgrade enabled)",
    )


def validate_sign_options_for_tier(
    options: SignOptions,
    tier: str,
    batch_size: int = 1,
    is_nma_member: bool = False,
) -> TierValidationResult:
    """
    Validate sign options against tier requirements.
    
    Returns validation result with list of denied features if any.
    NMA members on starter tier get special access to sentence segmentation.
    """
    features_used: List[str] = ["basic_signing"]
    features_denied: List[Dict[str, str]] = []
    
    # Normalize tier
    tier_normalized = tier.lower().replace("-", "_")
    
    # TEAM_166: Free tier has access to all segmentation levels except word.
    # NMA special-casing removed — free tier already has these features.
    
    # Check segmentation level
    if options.segmentation_level != "document":
        if options.segmentation_level == "word":
            if not is_feature_available("word_segmentation", tier_normalized):
                features_denied.append({
                    "feature": "word_segmentation",
                    "display_name": "Word-Level Segmentation",
                    "required_tier": TierName.ENTERPRISE,
                    "requested_value": options.segmentation_level,
                })
            else:
                features_used.append("word_segmentation")
        else:
            feature_name = f"{options.segmentation_level}_segmentation"
            if not is_feature_available(feature_name, tier_normalized):
                features_denied.append({
                    "feature": feature_name,
                    "display_name": f"{options.segmentation_level.title()}-Level Segmentation",
                    "required_tier": TierName.FREE,
                    "requested_value": options.segmentation_level,
                })
            else:
                features_used.append(feature_name)
    
    # Check manifest mode
    if options.manifest_mode != "full":
        if not is_feature_available("manifest_modes", tier_normalized):
            features_denied.append({
                "feature": "manifest_modes",
                "display_name": "Advanced Manifest Modes",
                "required_tier": TierName.FREE,
                "requested_value": options.manifest_mode,
            })
        else:
            features_used.append("manifest_modes")
    
    # Check embedding strategy
    if options.embedding_strategy != "single_point":
        if not is_feature_available("embedding_strategies", tier_normalized):
            features_denied.append({
                "feature": "embedding_strategies",
                "display_name": "Advanced Embedding Strategies",
                "required_tier": TierName.FREE,
                "requested_value": options.embedding_strategy,
            })
        else:
            features_used.append("embedding_strategies")
    
    # Check attribution indexing
    if options.index_for_attribution:
        if not is_feature_available("attribution_indexing", tier_normalized):
            features_denied.append({
                "feature": "attribution_indexing",
                "display_name": "Attribution Indexing",
                "required_tier": TierName.FREE,
                "requested_value": "true",
            })
        else:
            features_used.append("attribution_indexing")
    
    # Check custom assertions
    if options.custom_assertions:
        if not is_feature_available("custom_assertions", tier_normalized):
            features_denied.append({
                "feature": "custom_assertions",
                "display_name": "Custom C2PA Assertions",
                "required_tier": TierName.FREE,
                "requested_value": f"{len(options.custom_assertions)} assertions",
            })
        else:
            features_used.append("custom_assertions")
    
    # Check template
    if options.template_id:
        if not is_feature_available("assertion_templates", tier_normalized):
            features_denied.append({
                "feature": "assertion_templates",
                "display_name": "Assertion Templates",
                "required_tier": TierName.FREE,
                "requested_value": options.template_id,
            })
        else:
            features_used.append("assertion_templates")
    
    # Check rights metadata
    if options.rights:
        if not is_feature_available("rights_metadata", tier_normalized):
            features_denied.append({
                "feature": "rights_metadata",
                "display_name": "Rights Metadata",
                "required_tier": TierName.FREE,
                "requested_value": "provided",
            })
        else:
            features_used.append("rights_metadata")
    
    # Check dual binding
    if options.add_dual_binding:
        if not is_feature_available("dual_binding", tier_normalized):
            features_denied.append({
                "feature": "dual_binding",
                "display_name": "Dual Binding",
                "required_tier": TierName.ENTERPRISE,
                "requested_value": "true",
            })
        else:
            features_used.append("dual_binding")
    
    # Check fingerprinting
    if options.include_fingerprint:
        if not is_feature_available("fingerprinting", tier_normalized):
            features_denied.append({
                "feature": "fingerprinting",
                "display_name": "Content Fingerprinting",
                "required_tier": TierName.ENTERPRISE,
                "requested_value": "true",
            })
        else:
            features_used.append("fingerprinting")
    
    # Check batch size
    batch_limit = get_batch_limit(tier_normalized)
    if batch_size > batch_limit:
        features_denied.append({
            "feature": "batch_signing",
            "display_name": "Batch Signing",
            "required_tier": TierName.ENTERPRISE,
            "requested_value": f"{batch_size} documents (limit: {batch_limit})",
        })
    elif batch_size > 1:
        features_used.append("batch_signing")
    
    return TierValidationResult(
        valid=len(features_denied) == 0,
        features_used=features_used,
        features_denied=features_denied,
    )


# =============================================================================
# Sign Response Models
# =============================================================================

class SignedDocumentResult(BaseModel):
    """Result for a single signed document."""
    
    document_id: str = Field(..., description="Unique document identifier")
    signed_text: str = Field(..., description="Text with embedded C2PA manifest")
    verification_url: str = Field(..., description="URL for public verification")
    total_segments: int = Field(..., description="Number of segments signed")
    merkle_root: Optional[str] = Field(None, description="Merkle tree root hash (if segmentation enabled)")
    instance_id: Optional[str] = Field(None, description="C2PA manifest instance ID for provenance chain")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    publisher_attribution: Optional[str] = Field(None, description="Publisher identity shown on verification (e.g. 'Sarah Chen · Powered by Encypher')")


class SignResponseData(BaseModel):
    """
    Data payload for sign response.
    
    For single document, `document` contains the result.
    For batch, `documents` contains all results.
    """
    
    # Single document result
    document: Optional[SignedDocumentResult] = Field(
        None,
        description="Signed document result (single mode)",
    )
    
    # Batch results
    documents: Optional[List[SignedDocumentResult]] = Field(
        None,
        description="Signed document results (batch mode)",
    )
    
    # Summary stats
    total_documents: int = Field(..., description="Total documents processed")
    total_segments: int = Field(..., description="Total segments signed across all documents")
    
    # Processing info
    processing_time_ms: Optional[int] = Field(None, description="Total processing time in milliseconds")


# For backward compatibility, also export as SignResponse
# This allows existing code to continue working
class LegacySignResponse(BaseModel):
    """Legacy sign response for backward compatibility."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    document_id: str = Field(..., description="Unique document identifier")
    signed_text: str = Field(..., description="Text with embedded C2PA manifest")
    total_sentences: int = Field(..., description="Number of sentences signed")
    verification_url: str = Field(..., description="URL for public verification")
    publisher_attribution: Optional[str] = Field(None, description="Publisher identity shown on verification")
