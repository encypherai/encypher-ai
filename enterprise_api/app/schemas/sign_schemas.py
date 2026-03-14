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
    TierName,
    get_batch_limit,
    is_feature_available,
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

    | Feature                  | Free | Enterprise |
    |--------------------------|:----:|:----------:|
    | document_type            | yes  | yes        |
    | claim_generator          | yes  | yes        |
    | segmentation_level       | all except word | all |
    | manifest_mode            | all  | all        |
    | embedding_strategy       | all  | all        |
    | index_for_attribution    | yes  | yes        |
    | custom_assertions        | yes  | yes        |
    | template_id              | yes  | yes        |
    | rights / use_rights_profile | yes | yes     |
    | add_dual_binding         | no   | yes        |
    | include_fingerprint      | no   | yes        |
    | enable_print_fingerprint | no   | yes        |
    | word segmentation        | no   | yes        |
    | batch (documents array)  | 10   | 100        |
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

    # === Free Tier (signing + segmentation + manifest modes + rights) ===
    segmentation_level: str = Field(
        default="document",
        description="Segmentation level: document, sentence, paragraph, section (all Free); word (Enterprise only)",
    )
    segmentation_levels: Optional[List[str]] = Field(
        default=None,
        description="Optional list of Merkle segmentation levels to build in one pass (Free)",
    )
    manifest_mode: str = Field(
        default="full",
        description="Manifest mode: full or micro. micro uses ultra-compact per-segment markers; behaviour controlled by ecc, embed_c2pa, and legacy_safe flags.",
    )
    ecc: bool = Field(
        default=True,
        description="Enable Reed-Solomon error correction for micro mode (44 chars/segment vs 36). Ignored for non-micro modes.",
    )
    legacy_safe: bool = Field(
        default=False,
        description="Use Word-safe/terminal-safe base-6 encoding for micro mode instead of VS256. ecc=False -> 100 chars/segment; ecc=True -> 112 chars/segment (RS parity). Ignored for non-micro modes.",
    )
    embed_c2pa: bool = Field(
        default=True,
        description="Embed full C2PA document manifest into signed content for micro mode. When false, per-sentence markers only; C2PA manifest is still generated and stored in DB. Ignored for non-micro modes.",
    )
    embedding_strategy: str = Field(
        default="single_point",
        description="Embedding strategy: single_point, distributed, distributed_redundant (all Free)",
    )
    distribution_target: Optional[str] = Field(
        default=None,
        description="Target for distributed embedding: whitespace, punctuation, all_chars (Free)",
    )
    index_for_attribution: bool = Field(
        default=False,
        description="Index content for attribution and plagiarism detection (Free)",
    )
    custom_assertions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Custom C2PA assertions to include in manifest (Free)",
    )
    template_id: Optional[str] = Field(
        default=None,
        description="Assertion template ID to apply (Free)",
    )
    validate_assertions: bool = Field(
        default=True,
        description="Whether to validate custom assertions against registered schemas (Free)",
    )
    rights: Optional[RightsMetadata] = Field(
        default=None,
        description="Rights and licensing metadata to embed in the manifest (Free)",
    )
    use_rights_profile: bool = Field(
        default=False,
        description="When True, fetches the publisher's active rights profile, stores a snapshot on the content reference, and adds rights_resolution_url to the response (Free)",
    )
    license: Optional[LicenseInfo] = Field(
        default=None,
        description="License information to embed (Free)",
    )
    actions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of C2PA action assertions (Free)",
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
    enable_print_fingerprint: bool = Field(
        default=False,
        description=(
            "Print Leak Detection - embed imperceptible spacing patterns that survive "
            "printing and scanning, enabling source identification from physical or PDF "
            "copies (Enterprise)"
        ),
    )
    disable_c2pa: bool = Field(
        default=False,
        description="Opt-out of C2PA embedding for non-micro modes, only basic metadata (Enterprise). For micro mode use embed_c2pa instead.",
    )
    store_c2pa_manifest: bool = Field(
        default=True,
        description="Persist generated C2PA manifest in content DB for DB-backed verification. Applies to all modes that generate a manifest.",
    )

    # === Output Options ===
    embedding_options: EmbeddingOptions = Field(
        default_factory=EmbeddingOptions,
        description="Embedding output format options",
    )
    return_embedding_plan: bool = Field(
        default=False,
        description="When true, include an embedding_plan with index-based marker insertion operations in the response.",
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


_ALLOWED_CONTROL = frozenset({0x09, 0x0A, 0x0D})  # tab, newline, carriage return


def validate_text_content(v: str) -> str:
    """Reject binary or malformed content in text fields.

    Checks for null bytes and control characters (except tab/newline/CR)
    that indicate binary data was submitted to a text endpoint.

    Scans the first 10K chars for all control characters, then does a fast
    null-byte check on the remainder to catch nulls anywhere without a
    full character-by-character scan.
    """
    scan_limit = min(len(v), 10_000)
    for i in range(scan_limit):
        cp = ord(v[i])
        if cp < 0x20 and cp not in _ALLOWED_CONTROL:
            if cp == 0:
                raise ValueError("Text contains null bytes. Text endpoints accept UTF-8 only; binary content is not supported.")
            raise ValueError(
                f"Text contains control character U+{cp:04X} at position {i}. Text endpoints accept UTF-8 only; binary content is not supported."
            )
    # Fast null-byte check on the remainder beyond the scan limit
    if scan_limit < len(v) and "\x00" in v[scan_limit:]:
        raise ValueError("Text contains null bytes. Text endpoints accept UTF-8 only; binary content is not supported.")
    return v


class SignDocument(BaseModel):
    """A single document in a batch sign request."""

    text: str = Field(
        ...,
        description="Content to sign",
        min_length=1,
        max_length=1_000_000,
    )

    @field_validator("text")
    @classmethod
    def validate_text_is_not_binary(cls, v: str) -> str:
        return validate_text_content(v)

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

    For batch signing (up to 10 documents Free, up to 100 Enterprise):
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

    @field_validator("text")
    @classmethod
    def validate_text_is_not_binary(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_text_content(v)
        return v

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
        description="List of documents for batch signing (up to 10 Free, up to 100 Enterprise)",
    )

    # Options (tier-gated)
    options: SignOptions = Field(
        default_factory=SignOptions,
        description="Signing options - features gated by tier",
    )

    # Platform partner proxy signing
    publisher_org_id: Optional[str] = Field(
        default=None,
        description=(
            "Platform partner only (strategic_partner tier): sign on behalf of this publisher organization. Publisher's quota and rate limits apply."
        ),
        max_length=128,
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
    Sentence segmentation and all manifest modes are available on the Free tier.
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
                features_denied.append(
                    {
                        "feature": "word_segmentation",
                        "display_name": "Word-Level Segmentation",
                        "required_tier": TierName.ENTERPRISE,
                        "requested_value": options.segmentation_level,
                    }
                )
            else:
                features_used.append("word_segmentation")
        else:
            feature_name = f"{options.segmentation_level}_segmentation"
            if not is_feature_available(feature_name, tier_normalized):
                features_denied.append(
                    {
                        "feature": feature_name,
                        "display_name": f"{options.segmentation_level.title()}-Level Segmentation",
                        "required_tier": TierName.FREE,
                        "requested_value": options.segmentation_level,
                    }
                )
            else:
                features_used.append(feature_name)

    # Check manifest mode
    if options.manifest_mode != "full":
        if not is_feature_available("manifest_modes", tier_normalized):
            features_denied.append(
                {
                    "feature": "manifest_modes",
                    "display_name": "Advanced Manifest Modes",
                    "required_tier": TierName.FREE,
                    "requested_value": options.manifest_mode,
                }
            )
        else:
            features_used.append("manifest_modes")

    # Check embedding strategy
    if options.embedding_strategy != "single_point":
        if not is_feature_available("embedding_strategies", tier_normalized):
            features_denied.append(
                {
                    "feature": "embedding_strategies",
                    "display_name": "Advanced Embedding Strategies",
                    "required_tier": TierName.FREE,
                    "requested_value": options.embedding_strategy,
                }
            )
        else:
            features_used.append("embedding_strategies")

    # Check attribution indexing
    if options.index_for_attribution:
        if not is_feature_available("attribution_indexing", tier_normalized):
            features_denied.append(
                {
                    "feature": "attribution_indexing",
                    "display_name": "Attribution Indexing",
                    "required_tier": TierName.FREE,
                    "requested_value": "true",
                }
            )
        else:
            features_used.append("attribution_indexing")

    # Check custom assertions
    if options.custom_assertions:
        if not is_feature_available("custom_assertions", tier_normalized):
            features_denied.append(
                {
                    "feature": "custom_assertions",
                    "display_name": "Custom C2PA Assertions",
                    "required_tier": TierName.FREE,
                    "requested_value": f"{len(options.custom_assertions)} assertions",
                }
            )
        else:
            features_used.append("custom_assertions")

    # Check template
    if options.template_id:
        if not is_feature_available("assertion_templates", tier_normalized):
            features_denied.append(
                {
                    "feature": "assertion_templates",
                    "display_name": "Assertion Templates",
                    "required_tier": TierName.FREE,
                    "requested_value": options.template_id,
                }
            )
        else:
            features_used.append("assertion_templates")

    # Check rights metadata
    if options.rights:
        if not is_feature_available("rights_metadata", tier_normalized):
            features_denied.append(
                {
                    "feature": "rights_metadata",
                    "display_name": "Rights Metadata",
                    "required_tier": TierName.FREE,
                    "requested_value": "provided",
                }
            )
        else:
            features_used.append("rights_metadata")

    # Check dual binding
    if options.add_dual_binding:
        if not is_feature_available("dual_binding", tier_normalized):
            features_denied.append(
                {
                    "feature": "dual_binding",
                    "display_name": "Dual Binding",
                    "required_tier": TierName.ENTERPRISE,
                    "requested_value": "true",
                }
            )
        else:
            features_used.append("dual_binding")

    # Check fingerprinting
    if options.include_fingerprint:
        if not is_feature_available("fingerprinting", tier_normalized):
            features_denied.append(
                {
                    "feature": "fingerprinting",
                    "display_name": "Content Fingerprinting",
                    "required_tier": TierName.ENTERPRISE,
                    "requested_value": "true",
                }
            )
        else:
            features_used.append("fingerprinting")

    # Check print fingerprint (Print Leak Detection)
    if options.enable_print_fingerprint:
        if not is_feature_available("print_fingerprint", tier_normalized):
            features_denied.append(
                {
                    "feature": "print_fingerprint",
                    "display_name": "Print Leak Detection",
                    "required_tier": TierName.ENTERPRISE,
                    "requested_value": "true",
                }
            )
        else:
            features_used.append("print_fingerprint")

    # Check batch size
    batch_limit = get_batch_limit(tier_normalized)
    if batch_size > batch_limit:
        features_denied.append(
            {
                "feature": "batch_signing",
                "display_name": "Batch Signing",
                "required_tier": TierName.ENTERPRISE,
                "requested_value": f"{batch_size} documents (limit: {batch_limit})",
            }
        )
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


class EmbeddingPlanOperation(BaseModel):
    """Single index-based embedding insertion operation."""

    insert_after_index: int = Field(
        ...,
        description="0-based codepoint index after which to insert marker chars. Use -1 to insert before the first codepoint.",
    )
    marker: str = Field(..., description="Invisible marker characters to insert at the specified index.")


class EmbeddingPlan(BaseModel):
    """Index-based embedding insertion plan for formatting-preserving clients."""

    index_unit: str = Field(default="codepoint", description="Index unit used by operations. Currently always 'codepoint'.")
    operations: List[EmbeddingPlanOperation] = Field(
        default_factory=list,
        description="Ordered embedding insertion operations for reconstructing signed_text without replacing full content.",
    )


class SignedDocumentResult(BaseModel):
    """Result for a single signed document."""

    document_id: str = Field(..., description="Unique document identifier")
    signed_text: str = Field(..., description="Text with embedded C2PA manifest")
    verification_url: str = Field(..., description="URL for public verification")
    total_segments: int = Field(..., description="Number of segments signed")
    merkle_root: Optional[str] = Field(None, description="Merkle tree root hash (if segmentation enabled)")
    instance_id: Optional[str] = Field(None, description="C2PA manifest instance ID for provenance chain")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    publisher_attribution: Optional[str] = Field(
        None, description="Publisher identity shown on verification (e.g. 'Sarah Chen · Powered by Encypher')"
    )
    embedding_plan: Optional[EmbeddingPlan] = Field(
        None,
        description="Optional index-based marker insertion plan (returned when options.return_embedding_plan=true).",
    )


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
