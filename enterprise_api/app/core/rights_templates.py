"""
Pre-built rights profile templates for the Encypher Rights Management System.

TEAM_215: Pure Python dict file — no DB interactions. Each template fully populates
the bronze/silver/gold tier structure that maps to the publisher_rights_profiles table.

Usage:
    from app.core.rights_templates import get_template, list_templates, RIGHTS_TEMPLATES
"""

from __future__ import annotations

RIGHTS_TEMPLATES: dict[str, dict] = {
    # --------------------------------------------------------------------------
    # News Publisher Default
    # --------------------------------------------------------------------------
    "news_publisher_default": {
        "name": "News Publisher Default",
        "description": (
            "Standard template for news organizations — scraping allowed with attribution, RAG requires license, training requires negotiation"
        ),
        "default_license_type": "all_rights_reserved",
        "bronze_tier": {
            "tier": "bronze",
            "usage_type": "scraping_crawling",
            "description": "Automated access to content via web crawlers for indexing purposes",
            "permissions": {
                "allowed": True,
                "requires_license": False,
                "rate_limits": {
                    "requests_per_day": 10000,
                    "requests_per_month": None,
                },
                "allowed_purposes": ["search_indexing", "news_aggregation", "caching"],
                "prohibited_purposes": ["training", "fine_tuning", "rag_retrieval"],
                "geographic_restrictions": [],
                "temporal_restrictions": {
                    "embargo_period_hours": 24,
                    "content_age_minimum_days": None,
                },
            },
            "pricing": {
                "model": "per_request",
                "indicative_rate": "$0.001/article",
                "currency": "USD",
                "minimum_commitment": None,
                "bulk_discount_available": True,
            },
            "attribution": {
                "required": True,
                "format": "Publisher Name, Original URL",
                "link_back_required": True,
                "brand_usage_allowed": False,
            },
            "technical_requirements": {
                "respect_robots_txt": True,
                "crawl_delay_seconds": 2,
                "user_agent_identification": True,
                "api_preferred": False,
                "api_endpoint": None,
            },
        },
        "silver_tier": {
            "tier": "silver",
            "usage_type": "rag_retrieval_grounding",
            "description": "Real-time retrieval of content to augment AI-generated responses",
            "permissions": {
                "allowed": True,
                "requires_license": True,
                "allowed_purposes": ["rag_grounding", "fact_checking", "citation"],
                "prohibited_purposes": ["training", "fine_tuning", "verbatim_reproduction"],
                "max_excerpt_length": {
                    "sentences": 3,
                    "characters": 500,
                    "percentage_of_article": 10,
                },
                "verbatim_reproduction": {
                    "allowed": False,
                    "max_consecutive_words": 25,
                    "requires_quotation_marks": True,
                },
            },
            "pricing": {
                "model": "per_retrieval",
                "indicative_rate": "$0.01/retrieval",
                "currency": "USD",
                "revenue_share_on_ai_output": None,
            },
            "attribution": {
                "required": True,
                "format": "inline_citation",
                "must_include": ["publisher_name", "article_title", "url", "date"],
                "brand_usage_allowed": True,
                "accuracy_verification_required": True,
            },
            "quote_integrity": {
                "verification_required": True,
                "verification_endpoint": "https://api.encypherai.com/api/v1/verify",
                "accuracy_threshold": 0.95,
                "paraphrase_permitted": True,
                "fabrication_prohibited": True,
            },
        },
        "gold_tier": {
            "tier": "gold",
            "usage_type": "training_fine_tuning",
            "description": ("Incorporation of content into model weights through training or fine-tuning"),
            "permissions": {
                "allowed": True,
                "requires_license": True,
                "allowed_model_types": ["llm", "search", "summarization"],
                "prohibited_model_types": ["image_generation", "voice_cloning"],
                "dataset_retention": {
                    "max_retention_days": 365,
                    "deletion_on_license_expiry": True,
                    "audit_right": True,
                },
                "model_versioning": {
                    "applies_to_version": "all",
                    "retraining_notification_required": True,
                },
                "exclusivity": {
                    "exclusive": False,
                    "exclusive_period_days": None,
                    "exclusive_premium_multiplier": None,
                },
            },
            "pricing": {
                "model": "negotiate",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "minimum_commitment": "$10,000/year",
            },
            "attribution": {
                "required": True,
                "training_data_disclosure": True,
                "model_card_inclusion": True,
                "output_attribution_preferred": True,
            },
            "legal": {
                "indemnification": "mutual",
                "liability_cap": "license_fees_paid",
                "governing_law": "publisher_jurisdiction",
                "audit_rights": {
                    "publisher_can_audit": True,
                    "audit_frequency": "annual",
                    "audit_scope": ["ingestion_logs", "training_data_manifests"],
                },
            },
        },
    },
    # --------------------------------------------------------------------------
    # Blog / Independent Creator
    # --------------------------------------------------------------------------
    "blog_independent": {
        "name": "Blog / Independent Creator",
        "description": ("Template for individual bloggers and independent creators — open for crawling, stricter on AI training"),
        "default_license_type": "all_rights_reserved",
        "bronze_tier": {
            "tier": "bronze",
            "usage_type": "scraping_crawling",
            "description": "Automated access for search indexing and aggregation",
            "permissions": {
                "allowed": True,
                "requires_license": False,
                "rate_limits": {
                    "requests_per_day": 5000,
                    "requests_per_month": None,
                },
                "allowed_purposes": ["search_indexing", "news_aggregation", "caching"],
                "prohibited_purposes": ["training", "fine_tuning", "rag_retrieval"],
                "geographic_restrictions": [],
                "temporal_restrictions": {
                    "embargo_period_hours": 0,
                    "content_age_minimum_days": None,
                },
            },
            "pricing": {
                "model": "free",
                "indicative_rate": "$0.00",
                "currency": "USD",
                "minimum_commitment": None,
                "bulk_discount_available": False,
            },
            "attribution": {
                "required": True,
                "format": "Author Name, Blog Name, Original URL",
                "link_back_required": True,
                "brand_usage_allowed": False,
            },
            "technical_requirements": {
                "respect_robots_txt": True,
                "crawl_delay_seconds": 5,
                "user_agent_identification": True,
                "api_preferred": False,
                "api_endpoint": None,
            },
        },
        "silver_tier": {
            "tier": "silver",
            "usage_type": "rag_retrieval_grounding",
            "description": "Real-time retrieval for AI grounding — requires contact and agreement",
            "permissions": {
                "allowed": True,
                "requires_license": True,
                "allowed_purposes": ["rag_grounding", "fact_checking", "citation"],
                "prohibited_purposes": ["training", "fine_tuning", "verbatim_reproduction"],
                "max_excerpt_length": {
                    "sentences": 2,
                    "characters": 300,
                    "percentage_of_article": 5,
                },
                "verbatim_reproduction": {
                    "allowed": False,
                    "max_consecutive_words": 15,
                    "requires_quotation_marks": True,
                },
            },
            "pricing": {
                "model": "contact_us",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "revenue_share_on_ai_output": None,
            },
            "attribution": {
                "required": True,
                "format": "inline_citation",
                "must_include": ["author_name", "blog_name", "url", "date"],
                "brand_usage_allowed": False,
                "accuracy_verification_required": True,
            },
            "quote_integrity": {
                "verification_required": True,
                "verification_endpoint": "https://api.encypherai.com/api/v1/verify",
                "accuracy_threshold": 0.95,
                "paraphrase_permitted": True,
                "fabrication_prohibited": True,
            },
        },
        "gold_tier": {
            "tier": "gold",
            "usage_type": "training_fine_tuning",
            "description": "Training use not permitted without explicit negotiation and written consent",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "allowed_model_types": [],
                "prohibited_model_types": ["llm", "search", "summarization", "image_generation", "voice_cloning"],
                "dataset_retention": {
                    "max_retention_days": 0,
                    "deletion_on_license_expiry": True,
                    "audit_right": True,
                },
                "model_versioning": {
                    "applies_to_version": "all",
                    "retraining_notification_required": True,
                },
                "exclusivity": {
                    "exclusive": False,
                    "exclusive_period_days": None,
                    "exclusive_premium_multiplier": None,
                },
            },
            "pricing": {
                "model": "negotiate",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "minimum_commitment": None,
            },
            "attribution": {
                "required": True,
                "training_data_disclosure": True,
                "model_card_inclusion": True,
                "output_attribution_preferred": True,
            },
            "legal": {
                "indemnification": "mutual",
                "liability_cap": "negotiated",
                "governing_law": "publisher_jurisdiction",
                "audit_rights": {
                    "publisher_can_audit": True,
                    "audit_frequency": "annual",
                    "audit_scope": ["ingestion_logs", "training_data_manifests"],
                },
            },
        },
    },
    # --------------------------------------------------------------------------
    # Academic Open Access
    # --------------------------------------------------------------------------
    "academic_open_access": {
        "name": "Academic Open Access",
        "description": ("Open access research — share freely with attribution, training allowed under open license terms"),
        "default_license_type": "creative_commons_by",
        "bronze_tier": {
            "tier": "bronze",
            "usage_type": "scraping_crawling",
            "description": "Open access — crawling and indexing permitted without license",
            "permissions": {
                "allowed": True,
                "requires_license": False,
                "rate_limits": {
                    "requests_per_day": None,
                    "requests_per_month": None,
                },
                "allowed_purposes": [
                    "search_indexing",
                    "news_aggregation",
                    "caching",
                    "research",
                    "education",
                ],
                "prohibited_purposes": [],
                "geographic_restrictions": [],
                "temporal_restrictions": {
                    "embargo_period_hours": 0,
                    "content_age_minimum_days": None,
                },
            },
            "pricing": {
                "model": "free",
                "indicative_rate": "$0.00",
                "currency": "USD",
                "minimum_commitment": None,
                "bulk_discount_available": False,
            },
            "attribution": {
                "required": True,
                "format": "Author(s), Title, Journal/Repository, DOI/URL, Year (CC BY)",
                "link_back_required": True,
                "brand_usage_allowed": True,
            },
            "technical_requirements": {
                "respect_robots_txt": True,
                "crawl_delay_seconds": 1,
                "user_agent_identification": True,
                "api_preferred": True,
                "api_endpoint": None,
            },
        },
        "silver_tier": {
            "tier": "silver",
            "usage_type": "rag_retrieval_grounding",
            "description": "Open access — RAG retrieval permitted without license under CC BY",
            "permissions": {
                "allowed": True,
                "requires_license": False,
                "allowed_purposes": [
                    "rag_grounding",
                    "fact_checking",
                    "citation",
                    "research",
                    "education",
                ],
                "prohibited_purposes": [],
                "max_excerpt_length": {
                    "sentences": 10,
                    "characters": 2000,
                    "percentage_of_article": 25,
                },
                "verbatim_reproduction": {
                    "allowed": True,
                    "max_consecutive_words": None,
                    "requires_quotation_marks": True,
                },
            },
            "pricing": {
                "model": "free",
                "indicative_rate": "$0.00",
                "currency": "USD",
                "revenue_share_on_ai_output": None,
            },
            "attribution": {
                "required": True,
                "format": "inline_citation",
                "must_include": ["author_names", "title", "doi_or_url", "year", "license"],
                "brand_usage_allowed": True,
                "accuracy_verification_required": True,
            },
            "quote_integrity": {
                "verification_required": True,
                "verification_endpoint": "https://api.encypherai.com/api/v1/verify",
                "accuracy_threshold": 0.98,
                "paraphrase_permitted": True,
                "fabrication_prohibited": True,
            },
        },
        "gold_tier": {
            "tier": "gold",
            "usage_type": "training_fine_tuning",
            "description": "Training permitted under CC BY — attribution and model card required",
            "permissions": {
                "allowed": True,
                "requires_license": False,
                "allowed_model_types": ["llm", "search", "summarization", "research"],
                "prohibited_model_types": [],
                "dataset_retention": {
                    "max_retention_days": None,
                    "deletion_on_license_expiry": False,
                    "audit_right": False,
                },
                "model_versioning": {
                    "applies_to_version": "all",
                    "retraining_notification_required": False,
                },
                "exclusivity": {
                    "exclusive": False,
                    "exclusive_period_days": None,
                    "exclusive_premium_multiplier": None,
                },
            },
            "pricing": {
                "model": "free",
                "indicative_rate": "$0.00",
                "currency": "USD",
                "minimum_commitment": None,
            },
            "attribution": {
                "required": True,
                "training_data_disclosure": True,
                "model_card_inclusion": True,
                "output_attribution_preferred": True,
            },
            "legal": {
                "indemnification": "none",
                "liability_cap": "none",
                "governing_law": "cc_by_4_0",
                "audit_rights": {
                    "publisher_can_audit": False,
                    "audit_frequency": None,
                    "audit_scope": [],
                },
            },
        },
    },
    # --------------------------------------------------------------------------
    # All Rights Reserved
    # --------------------------------------------------------------------------
    "all_rights_reserved": {
        "name": "All Rights Reserved",
        "description": "Maximum protection — all AI uses require explicit licensing",
        "default_license_type": "all_rights_reserved",
        "bronze_tier": {
            "tier": "bronze",
            "usage_type": "scraping_crawling",
            "description": "Crawling not permitted without an executed license agreement",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "rate_limits": {
                    "requests_per_day": 0,
                    "requests_per_month": 0,
                },
                "allowed_purposes": [],
                "prohibited_purposes": [
                    "search_indexing",
                    "news_aggregation",
                    "caching",
                    "training",
                    "fine_tuning",
                    "rag_retrieval",
                ],
                "geographic_restrictions": [],
                "temporal_restrictions": {
                    "embargo_period_hours": None,
                    "content_age_minimum_days": None,
                },
            },
            "pricing": {
                "model": "negotiate",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "minimum_commitment": None,
                "bulk_discount_available": False,
            },
            "attribution": {
                "required": True,
                "format": "Publisher Name, Original URL",
                "link_back_required": True,
                "brand_usage_allowed": False,
            },
            "technical_requirements": {
                "respect_robots_txt": True,
                "crawl_delay_seconds": None,
                "user_agent_identification": True,
                "api_preferred": False,
                "api_endpoint": None,
            },
        },
        "silver_tier": {
            "tier": "silver",
            "usage_type": "rag_retrieval_grounding",
            "description": "RAG retrieval not permitted without an executed license agreement",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "allowed_purposes": [],
                "prohibited_purposes": [
                    "rag_grounding",
                    "fact_checking",
                    "citation",
                    "training",
                    "fine_tuning",
                    "verbatim_reproduction",
                ],
                "max_excerpt_length": {
                    "sentences": 0,
                    "characters": 0,
                    "percentage_of_article": 0,
                },
                "verbatim_reproduction": {
                    "allowed": False,
                    "max_consecutive_words": 0,
                    "requires_quotation_marks": True,
                },
            },
            "pricing": {
                "model": "negotiate",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "revenue_share_on_ai_output": None,
            },
            "attribution": {
                "required": True,
                "format": "inline_citation",
                "must_include": ["publisher_name", "article_title", "url", "date"],
                "brand_usage_allowed": False,
                "accuracy_verification_required": True,
            },
            "quote_integrity": {
                "verification_required": True,
                "verification_endpoint": "https://api.encypherai.com/api/v1/verify",
                "accuracy_threshold": 1.0,
                "paraphrase_permitted": False,
                "fabrication_prohibited": True,
            },
        },
        "gold_tier": {
            "tier": "gold",
            "usage_type": "training_fine_tuning",
            "description": "Training or fine-tuning on this content is prohibited without an executed license",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "allowed_model_types": [],
                "prohibited_model_types": ["llm", "search", "summarization", "image_generation", "voice_cloning"],
                "dataset_retention": {
                    "max_retention_days": 0,
                    "deletion_on_license_expiry": True,
                    "audit_right": True,
                },
                "model_versioning": {
                    "applies_to_version": "all",
                    "retraining_notification_required": True,
                },
                "exclusivity": {
                    "exclusive": False,
                    "exclusive_period_days": None,
                    "exclusive_premium_multiplier": None,
                },
            },
            "pricing": {
                "model": "negotiate",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "minimum_commitment": None,
            },
            "attribution": {
                "required": True,
                "training_data_disclosure": True,
                "model_card_inclusion": True,
                "output_attribution_preferred": True,
            },
            "legal": {
                "indemnification": "full_publisher",
                "liability_cap": "unlimited",
                "governing_law": "publisher_jurisdiction",
                "audit_rights": {
                    "publisher_can_audit": True,
                    "audit_frequency": "quarterly",
                    "audit_scope": [
                        "ingestion_logs",
                        "training_data_manifests",
                        "model_registry",
                        "data_deletion_certificates",
                    ],
                },
            },
        },
    },
    # --------------------------------------------------------------------------
    # Premium / Paywalled Content
    # --------------------------------------------------------------------------
    "premium_paywalled": {
        "name": "Premium / Paywalled Content",
        "description": ("Subscription content — no free access for AI, all uses require premium licensing"),
        "default_license_type": "all_rights_reserved",
        "bronze_tier": {
            "tier": "bronze",
            "usage_type": "scraping_crawling",
            "description": "No automated access — all crawling requires a paid monthly crawl license",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "rate_limits": {
                    "requests_per_day": 0,
                    "requests_per_month": 0,
                },
                "allowed_purposes": [],
                "prohibited_purposes": [
                    "search_indexing",
                    "news_aggregation",
                    "caching",
                    "training",
                    "fine_tuning",
                    "rag_retrieval",
                ],
                "geographic_restrictions": [],
                "temporal_restrictions": {
                    "embargo_period_hours": None,
                    "content_age_minimum_days": None,
                },
            },
            "pricing": {
                "model": "flat_monthly",
                "indicative_rate": "$500/month",
                "currency": "USD",
                "minimum_commitment": "$500/month",
                "bulk_discount_available": True,
            },
            "attribution": {
                "required": True,
                "format": "Publisher Name, Original URL (Subscription Required)",
                "link_back_required": True,
                "brand_usage_allowed": False,
            },
            "technical_requirements": {
                "respect_robots_txt": True,
                "crawl_delay_seconds": None,
                "user_agent_identification": True,
                "api_preferred": True,
                "api_endpoint": None,
            },
        },
        "silver_tier": {
            "tier": "silver",
            "usage_type": "rag_retrieval_grounding",
            "description": "RAG retrieval of paywalled content requires a premium monthly license",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "allowed_purposes": [],
                "prohibited_purposes": [
                    "rag_grounding",
                    "fact_checking",
                    "citation",
                    "training",
                    "fine_tuning",
                    "verbatim_reproduction",
                ],
                "max_excerpt_length": {
                    "sentences": 0,
                    "characters": 0,
                    "percentage_of_article": 0,
                },
                "verbatim_reproduction": {
                    "allowed": False,
                    "max_consecutive_words": 0,
                    "requires_quotation_marks": True,
                },
            },
            "pricing": {
                "model": "flat_monthly",
                "indicative_rate": "$2,000/month",
                "currency": "USD",
                "revenue_share_on_ai_output": 0.05,
            },
            "attribution": {
                "required": True,
                "format": "inline_citation",
                "must_include": ["publisher_name", "article_title", "url", "date"],
                "brand_usage_allowed": True,
                "accuracy_verification_required": True,
            },
            "quote_integrity": {
                "verification_required": True,
                "verification_endpoint": "https://api.encypherai.com/api/v1/verify",
                "accuracy_threshold": 1.0,
                "paraphrase_permitted": False,
                "fabrication_prohibited": True,
            },
        },
        "gold_tier": {
            "tier": "gold",
            "usage_type": "training_fine_tuning",
            "description": "Training on premium/paywalled content requires a corpus license negotiated directly",
            "permissions": {
                "allowed": False,
                "requires_license": True,
                "allowed_model_types": [],
                "prohibited_model_types": ["llm", "search", "summarization", "image_generation", "voice_cloning"],
                "dataset_retention": {
                    "max_retention_days": 365,
                    "deletion_on_license_expiry": True,
                    "audit_right": True,
                },
                "model_versioning": {
                    "applies_to_version": "all",
                    "retraining_notification_required": True,
                },
                "exclusivity": {
                    "exclusive": False,
                    "exclusive_period_days": None,
                    "exclusive_premium_multiplier": 3.0,
                },
            },
            "pricing": {
                "model": "corpus_license",
                "indicative_rate": "contact_us",
                "currency": "USD",
                "minimum_commitment": None,
            },
            "attribution": {
                "required": True,
                "training_data_disclosure": True,
                "model_card_inclusion": True,
                "output_attribution_preferred": True,
            },
            "legal": {
                "indemnification": "mutual",
                "liability_cap": "license_fees_paid",
                "governing_law": "publisher_jurisdiction",
                "audit_rights": {
                    "publisher_can_audit": True,
                    "audit_frequency": "semi_annual",
                    "audit_scope": [
                        "ingestion_logs",
                        "training_data_manifests",
                        "model_registry",
                        "data_deletion_certificates",
                        "revenue_reports",
                    ],
                },
            },
        },
    },
}


def get_template(template_id: str) -> dict | None:
    """Return a single rights template by ID (with 'id' injected), or None if not found."""
    tpl = RIGHTS_TEMPLATES.get(template_id)
    if tpl is None:
        return None
    return {"id": template_id, **tpl}


def list_templates() -> list[dict]:
    """Return a summary list of all available templates (id, name, description)."""
    return [{"id": k, "name": v["name"], "description": v["description"]} for k, v in RIGHTS_TEMPLATES.items()]
