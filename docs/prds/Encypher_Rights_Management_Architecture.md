# Encypher Rights Management System — Architecture Specification

**Document Type:** Systems Architecture Specification
**Audience:** Systems Architect / Engineering Lead
**Version:** 1.0
**Date:** February 20, 2026
**Author:** Erik Svilich, CEO & Founder
**Status:** DRAFT — For Architecture Review

---

## 1. Executive Summary

### What We're Building

A **publisher-controlled rights management system** where licensing terms, permissions, and usage options are cryptographically bound to content at the sentence level and stored in our database as the authoritative registry. Publishers define how their content can be used across three licensing tiers (scraping, RAG/retrieval, and training/fine-tuning), and those terms travel with the content through our embedded provenance markers. Any entity encountering marked content can resolve the embedded identifiers back to our registry to discover: who owns it, what's allowed, what it costs, and how to license it.

This is not DRM — we don't prevent access. This is a **machine-readable deed system** that transforms legal exposure for anyone who uses marked content after encountering the embedded rights notice.

### The Core Loop

```
PUBLISHER                           ENCYPHER DB                        AI COMPANY / CONSUMER
─────────                           ──────────                         ─────────────────────

1. Signs content via               2. Registry stores:                 4. Encounters marked content
   API / WordPress /                  - Content hashes (Merkle tree)      (scraping, RAG retrieval,
   CLI / platform partner             - Rights & licensing terms          training pipeline, etc.)
                                      - Contact / licensing info
3. Invisible markers                  - Usage tier permissions         5. Resolves markers via
   embedded in text                   - Pricing by tier                   public API lookup
   (Unicode variation selectors       - Formal notice status              → Gets rights info,
    + C2PA manifest)                  - Evidence chain                    licensing terms, contact
                                      - Publisher identity
                                                                       6. CHOICE:
                                                                          a) License → transaction
                                                                          b) Ignore → willful
                                                                             infringement exposure
                                                                          c) Strip markers →
                                                                             spoliation of evidence
```

### Why This Matters Commercially

Today, AI companies can claim innocent infringement: "We didn't know it was yours." Our system eliminates that defense by embedding machine-readable ownership and licensing terms directly into text that survives distribution, scraping, and processing. Once an AI company's ingestion pipeline encounters our markers — even if it strips them — the formal notice is served. Continued use without licensing becomes **provable willful infringement** (3x damages under US copyright law).

---

## 2. Existing Infrastructure (What's Built)

The rights management system extends — not replaces — the existing Encypher microservices architecture. The architect should understand the current stack before designing the rights layer.

### Current Microservice Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway (Traefik)                       │
│                        Port 8000                              │
│          Routes /api/v1/* to appropriate services             │
└──────────────────────────┬───────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
┌────────▼───────┐ ┌──────▼──────┐ ┌────────▼───────┐
│ Enterprise API │ │ Key Service │ │  Coalition     │
│   Port 9000    │ │  Port 8003  │ │  Service       │
│                │ │             │ │  Port 8009     │
│ - C2PA Signing │ │ - API Keys  │ │                │
│ - Verification │ │ - Org/Tier  │ │ - Membership   │
│ - Merkle Trees │ │ - Features  │ │ - Content Index│
│ - Embeddings   │ │ - Quotas    │ │ - Licensing    │
│ - Streaming    │ │             │ │ - Revenue Dist │
└────────┬───────┘ └──────┬──────┘ └────────┬───────┘
         │                │                 │
┌────────▼────────────────▼─────────────────▼───────┐
│                  PostgreSQL (per-service)           │
│                                                    │
│  encypher_content: documents, merkle_trees,        │
│    sentence_records, manifests, embeddings          │
│  encypher_keys: api_keys, orgs, subscriptions      │
│  encypher_coalition: members, content, licensing    │
│  encypher_auth: users, sessions, oauth             │
│  encypher_users: profiles, teams                   │
│  encypher_analytics: events, metrics               │
│  encypher_billing: invoices, payments              │
└────────────────────────────────────────────────────┘
```

### Current Signing Pipeline

When a publisher signs content today, the following happens:

1. **Segmentation:** Text is split into sentences (and optionally paragraphs/sections)
2. **Merkle Tree Construction:** Sentence hashes form a Merkle tree; root hash is the document fingerprint
3. **C2PA Manifest Generation:** A C2PA 2.3-compliant manifest is created (Erik authored Section A.7 of the spec)
4. **Invisible Embedding:** Unicode variation selectors encode segment UUIDs into the text — invisible to readers, survive copy-paste
5. **Database Storage:** Document record, Merkle tree, sentence records, manifest, and embeddings are persisted in `encypher_content`
6. **Coalition Indexing:** If publisher is a coalition member, content is indexed in `encypher_coalition` for aggregate licensing

### Current Verification Pipeline

When anyone verifies content:

1. **Embedding Extraction:** Unicode variation selectors are extracted from text, yielding segment UUIDs
2. **Registry Lookup:** UUIDs resolve to document records, publisher identity, and Merkle tree
3. **Integrity Verification:** Sentence hashes are verified against Merkle tree — any modification is detected
4. **C2PA Validation:** Manifest cryptographic signatures are validated against trust anchors (SSL.com certificates)
5. **Response:** Verification result includes publisher identity, document metadata, tamper detection, and licensing info

### What the Current `license` Field Does

The `/api/v1/sign` endpoint already accepts a `license` object:

```json
{
  "document_id": "article_001",
  "text": "Full article text...",
  "segmentation_level": "sentence",
  "license": {
    "type": "All Rights Reserved",
    "contact_email": "licensing@publisher.com"
  }
}
```

This is stored in the document record and returned on verification. **The rights management system extends this into a comprehensive, machine-readable, tiered licensing framework.**

---

## 3. Rights Management Data Model

### 3.1 The Rights Profile (Publisher-Level Defaults)

Every publisher organization has a **default rights profile** that applies to all their content unless overridden at the document or collection level. This is set once during onboarding and adjustable via dashboard or API.

```
TABLE: publisher_rights_profiles
─────────────────────────────────────────────────────────────────
organization_id        UUID FK → organizations
profile_version        INTEGER (auto-increment, immutable audit trail)
effective_date         TIMESTAMP (when this version takes effect)
created_at             TIMESTAMP
updated_by             UUID FK → users

── IDENTITY ──
publisher_name         TEXT (display name for licensing pages)
publisher_url          TEXT (canonical publisher URL)
contact_email          TEXT (licensing contact)
contact_url            TEXT (licensing portal URL, if publisher has one)
legal_entity           TEXT (legal entity name for contracts)
jurisdiction           TEXT (governing law, e.g. "US-NY", "UK", "EU")

── DEFAULT RIGHTS ──
default_license_type   ENUM: 'all_rights_reserved', 'custom_license',
                             'creative_commons_by', 'creative_commons_by_sa',
                             'creative_commons_by_nc', 'creative_commons_by_nd',
                             'creative_commons_by_nc_sa', 'creative_commons_by_nc_nd',
                             'public_domain', 'open_access'

── TIER-SPECIFIC LICENSING TERMS ──
(see Section 3.2 for detail)
bronze_tier            JSONB (scraping/crawling terms)
silver_tier            JSONB (RAG/retrieval terms)
gold_tier              JSONB (training/fine-tuning terms)

── FORMAL NOTICE ──
notice_status          ENUM: 'draft', 'active', 'suspended'
notice_effective_date  TIMESTAMP (when formal notice was first served)
notice_text            TEXT (the legal notice text)
notice_hash            TEXT (SHA-256 of notice, for immutability proof)

── COALITION ──
coalition_member       BOOLEAN
coalition_joined_at    TIMESTAMP
licensing_track        ENUM: 'coalition', 'self_service', 'both'
```

### 3.2 Tiered Licensing Terms (The Bronze/Silver/Gold Framework)

Each tier represents a fundamentally different kind of AI content usage, with different technical requirements, different value, and different pricing leverage.

```
BRONZE TIER — Scraping / Crawling Access
─────────────────────────────────────────
{
  "tier": "bronze",
  "usage_type": "scraping_crawling",
  "description": "Automated access to content via web crawlers, scrapers,
                  or API-based content retrieval for indexing or caching",

  "permissions": {
    "allowed": true | false,
    "requires_license": true | false,
    "license_url": "https://publisher.com/ai-licensing",
    "rate_limits": {
      "requests_per_day": 10000,
      "requests_per_month": null
    },
    "allowed_purposes": ["search_indexing", "news_aggregation", "caching"],
    "prohibited_purposes": ["training", "fine_tuning", "rag_retrieval"],
    "geographic_restrictions": [],
    "temporal_restrictions": {
      "embargo_period_hours": 24,
      "content_age_minimum_days": null
    }
  },

  "pricing": {
    "model": "per_request" | "flat_monthly" | "per_article" | "negotiate",
    "indicative_rate": "$0.001/article" | "$500/month" | "contact_us",
    "currency": "USD",
    "minimum_commitment": null,
    "bulk_discount_available": true
  },

  "attribution": {
    "required": true,
    "format": "Publisher Name, Original URL",
    "link_back_required": true,
    "brand_usage_allowed": false
  },

  "technical_requirements": {
    "respect_robots_txt": true,
    "crawl_delay_seconds": 2,
    "user_agent_identification": true,
    "api_preferred": true,
    "api_endpoint": "https://publisher.com/api/content"
  }
}


SILVER TIER — RAG / Retrieval / Grounding
──────────────────────────────────────────
{
  "tier": "silver",
  "usage_type": "rag_retrieval_grounding",
  "description": "Real-time retrieval of content to augment, ground, or
                  inform AI-generated responses",

  "permissions": {
    "allowed": true | false,
    "requires_license": true | false,
    "license_url": "https://publisher.com/ai-licensing",
    "allowed_purposes": ["rag_grounding", "fact_checking", "citation"],
    "prohibited_purposes": ["training", "fine_tuning", "verbatim_reproduction"],
    "max_excerpt_length": {
      "sentences": 3,
      "characters": 500,
      "percentage_of_article": 10
    },
    "verbatim_reproduction": {
      "allowed": false,
      "max_consecutive_words": 25,
      "requires_quotation_marks": true
    }
  },

  "pricing": {
    "model": "per_retrieval" | "per_token_output" | "flat_monthly" | "negotiate",
    "indicative_rate": "$0.01/retrieval" | "$2,000/month" | "contact_us",
    "currency": "USD",
    "revenue_share_on_ai_output": null
  },

  "attribution": {
    "required": true,
    "format": "inline_citation" | "footnote" | "source_link",
    "must_include": ["publisher_name", "article_title", "url", "date"],
    "brand_usage_allowed": true,
    "accuracy_verification_required": true,
    "hallucination_liability": "AI company bears responsibility for
                                misattributed quotes"
  },

  "quote_integrity": {
    "verification_required": true,
    "verification_endpoint": "https://api.encypher.com/api/v1/verify",
    "accuracy_threshold": 0.95,
    "paraphrase_permitted": true,
    "fabrication_prohibited": true
  }
}


GOLD TIER — Training / Fine-Tuning
───────────────────────────────────
{
  "tier": "gold",
  "usage_type": "training_fine_tuning",
  "description": "Incorporation of content into model weights through
                  pre-training, fine-tuning, RLHF, or similar processes",

  "permissions": {
    "allowed": true | false,
    "requires_license": true | false,
    "license_url": "https://publisher.com/ai-licensing",
    "allowed_model_types": ["llm", "search", "summarization"],
    "prohibited_model_types": ["image_generation", "voice_cloning"],
    "dataset_retention": {
      "max_retention_days": 365,
      "deletion_on_license_expiry": true,
      "audit_right": true
    },
    "model_versioning": {
      "applies_to_version": "all" | "specific",
      "retraining_notification_required": true
    },
    "exclusivity": {
      "exclusive": false,
      "exclusive_period_days": null,
      "exclusive_premium_multiplier": null
    }
  },

  "pricing": {
    "model": "per_article_ingested" | "corpus_license" |
             "revenue_share" | "flat_annual" | "negotiate",
    "indicative_rate": "$0.10/article" | "$50,000/year" | "contact_us",
    "currency": "USD",
    "minimum_commitment": "$10,000/year",
    "corpus_pricing": {
      "full_archive": "negotiate",
      "rolling_12_months": "negotiate",
      "specific_sections": "negotiate"
    }
  },

  "attribution": {
    "required": true,
    "training_data_disclosure": true,
    "model_card_inclusion": true,
    "output_attribution_preferred": true
  },

  "legal": {
    "indemnification": "mutual",
    "liability_cap": "license_fees_paid",
    "governing_law": "publisher_jurisdiction",
    "audit_rights": {
      "publisher_can_audit": true,
      "audit_frequency": "annual",
      "audit_scope": ["ingestion_logs", "training_data_manifests"]
    }
  }
}
```

### 3.3 Document-Level Rights Override

Publishers need the ability to override their default profile for specific documents or collections. A breaking news article might have different terms than archival content. An opinion column might be licensed differently than a news report.

```
TABLE: document_rights_overrides
────────────────────────────────────────────────────────────────
document_id            UUID FK → documents
organization_id        UUID FK → organizations
override_version       INTEGER (audit trail)
created_at             TIMESTAMP
updated_by             UUID FK → users

── OVERRIDE SCOPE ──
override_type          ENUM: 'document', 'collection', 'content_type',
                             'date_range', 'section'
collection_id          UUID (if collection-level override)
content_type_filter    TEXT (e.g. "opinion", "news", "analysis", "archive")
date_range_start       TIMESTAMP (for temporal overrides)
date_range_end         TIMESTAMP

── TIER OVERRIDES ──
bronze_tier_override   JSONB (null = use publisher default)
silver_tier_override   JSONB (null = use publisher default)
gold_tier_override     JSONB (null = use publisher default)

── SPECIAL FLAGS ──
do_not_license         BOOLEAN (explicit opt-out for sensitive content)
premium_content        BOOLEAN (higher pricing tier)
embargo_until          TIMESTAMP (time-delayed licensing availability)
syndication_rights     JSONB (specific terms for syndicated content)
```

### 3.4 Rights Resolution Logic

When a consumer encounters marked content and queries our API, the rights resolution follows this priority cascade:

```
1. Document-level override (most specific)
   ↓ if none exists
2. Collection-level override
   ↓ if none exists
3. Content-type override (e.g. "all opinion pieces")
   ↓ if none exists
4. Publisher default rights profile (always exists)
```

This is implemented as a single query with COALESCE logic — no waterfall of API calls.

---

## 4. API Design — Rights Endpoints

### 4.1 Rights Declaration (Publisher-Facing)

These endpoints are used by publishers (via API, WordPress plugin, dashboard, or platform partners) to set and manage their licensing terms.

```
── PUBLISHER RIGHTS PROFILE ──

PUT  /api/v1/rights/profile
     Set or update default rights profile for organization.
     Auth: Required (org admin)
     Body: Full publisher_rights_profiles object
     Returns: Profile with version number

GET  /api/v1/rights/profile
     Get current rights profile.
     Auth: Required (org member)
     Returns: Current active profile

GET  /api/v1/rights/profile/history
     Get version history of rights profile changes.
     Auth: Required (org admin)
     Returns: Array of profile versions with timestamps and diffs


── DOCUMENT-LEVEL OVERRIDES ──

PUT  /api/v1/rights/documents/{document_id}
     Set rights override for specific document.
     Auth: Required (org member, must own document)
     Body: document_rights_overrides object

PUT  /api/v1/rights/collections/{collection_id}
     Set rights override for a collection of documents.
     Auth: Required (org admin)
     Body: Override with collection scope

PUT  /api/v1/rights/content-types/{content_type}
     Set rights override for a content type.
     Auth: Required (org admin)
     Body: Override with content_type scope


── BULK OPERATIONS ──

POST /api/v1/rights/bulk-update
     Update rights for multiple documents/collections at once.
     Auth: Required (org admin)
     Body: Array of override objects with scope selectors
     Returns: Applied count, skipped count, errors


── RIGHTS TEMPLATES ──

GET  /api/v1/rights/templates
     Get pre-built rights templates (e.g. "News Publisher Default",
     "Academic Open Access", "Premium Paywalled", "Archive Only")
     Auth: None (public reference)
     Returns: Array of template objects

POST /api/v1/rights/profile/from-template/{template_id}
     Initialize rights profile from a template.
     Auth: Required (org admin)
```

### 4.2 Rights Resolution (Consumer-Facing / Public)

These endpoints are used by AI companies, developers, researchers, or anyone who encounters marked content and wants to know the licensing terms. These are **intentionally public** — discoverability is the entire point. Making rights information easy to find strengthens the formal notice argument.

```
── PUBLIC RIGHTS LOOKUP ──

GET  /api/v1/public/rights/{document_id}
     Resolve rights and licensing terms for a specific document.
     Auth: None (public, rate-limited)
     Returns: {
       publisher: { name, url, contact, legal_entity },
       rights: {
         license_type: "all_rights_reserved",
         bronze_tier: { ... full tier object ... },
         silver_tier: { ... full tier object ... },
         gold_tier: { ... full tier object ... }
       },
       formal_notice: {
         status: "active",
         effective_date: "2026-03-01T00:00:00Z",
         notice_text: "This content is cryptographically signed...",
         notice_hash: "sha256:abc123..."
       },
       licensing_contact: {
         email: "licensing@publisher.com",
         url: "https://publisher.com/ai-licensing",
         coalition: true,
         coalition_contact: "licensing@encypher.com"
       },
       verification: {
         c2pa_valid: true,
         merkle_root: "sha256:...",
         signed_at: "2026-02-15T10:00:00Z"
       }
     }

POST /api/v1/public/rights/resolve
     Resolve rights for text content (extracts embedded markers first,
     then resolves each to rights info). Accepts raw text.
     Auth: None (public, rate-limited)
     Body: { "text": "Article text with embedded markers..." }
     Returns: Array of resolved rights per detected segment

GET  /api/v1/public/rights/organization/{org_id}
     Get the default rights profile for a publisher organization.
     Auth: None (public)
     Returns: Publisher profile with tier terms (no document-specific overrides)


── MACHINE-READABLE FORMATS ──

GET  /api/v1/public/rights/{document_id}/json-ld
     Rights as JSON-LD (Schema.org compatible) for SEO/machine indexing.

GET  /api/v1/public/rights/{document_id}/odrl
     Rights as ODRL (Open Digital Rights Language, W3C standard).

GET  /api/v1/public/rights/organization/{org_id}/robots-meta
     Generate AI-specific robots meta directives that reference our
     rights registry. This bridges the access-tier (robots.txt) world
     with the provenance-tier (Encypher) world.
     Returns: Suggested meta tags and robots.txt additions that point
     AI crawlers to the rights endpoint for terms.
```

### 4.3 Licensing Transaction Endpoints

When a consumer wants to actually license content (not just discover terms), these endpoints facilitate the transaction.

```
── LICENSING REQUESTS ──

POST /api/v1/licensing/request
     Submit a licensing request for publisher content.
     Auth: Required (consumer API key)
     Body: {
       "organization_id": "publisher_org_id",
       "tier": "gold",
       "scope": {
         "type": "full_archive" | "date_range" | "specific_documents",
         "date_range": { "start": "...", "end": "..." },
         "document_ids": ["...", "..."],
         "content_types": ["news", "analysis"]
       },
       "proposed_terms": {
         "duration_months": 12,
         "model_types": ["llm"],
         "proposed_rate": "negotiate"
       },
       "requester": {
         "company": "AI Company Inc.",
         "contact_name": "...",
         "contact_email": "...",
         "intended_use": "LLM pre-training"
       }
     }
     Returns: Request ID, status, estimated response time

GET  /api/v1/licensing/requests
     List licensing requests (for publisher: incoming; for consumer: outgoing).
     Auth: Required
     Returns: Paginated request list with status

PUT  /api/v1/licensing/requests/{request_id}/respond
     Publisher responds to licensing request.
     Auth: Required (publisher org admin)
     Body: {
       "action": "approve" | "counter" | "reject",
       "terms": { ... final or counter terms ... },
       "message": "..."
     }


── ACTIVE LICENSES ──

GET  /api/v1/licensing/agreements
     List active licensing agreements.
     Auth: Required
     Returns: Agreements with terms, status, usage metrics

GET  /api/v1/licensing/agreements/{agreement_id}
     Get specific agreement details.
     Auth: Required (party to agreement)

GET  /api/v1/licensing/agreements/{agreement_id}/usage
     Get usage metrics against an active license.
     Auth: Required (party to agreement)
     Returns: Articles accessed, retrievals, ingestion events,
              compliance status
```

### 4.4 Formal Notice Endpoints

Formal notice is the legal mechanism that transforms innocent infringement into willful infringement. These endpoints manage the notice lifecycle.

```
── FORMAL NOTICE MANAGEMENT ──

POST /api/v1/notices/create
     Create a formal notice for an AI company or other entity.
     Auth: Required (publisher org admin)
     Body: {
       "target": {
         "entity_name": "AI Company Inc.",
         "entity_domain": "aicompany.com",
         "contact_email": "legal@aicompany.com",
         "entity_type": "ai_company" | "aggregator" | "other"
       },
       "scope": {
         "type": "all_content" | "specific_documents" | "date_range",
         "document_ids": [],
         "date_range": {}
       },
       "notice_type": "licensing_notice" | "cease_and_desist" |
                      "dmca_takedown" | "formal_awareness",
       "demands": {
         "licensing_required": true,
         "licensing_url": "https://publisher.com/ai-licensing",
         "response_deadline_days": 30,
         "retroactive_licensing_requested": true
       }
     }
     Returns: Notice ID, delivery status, cryptographic receipt

GET  /api/v1/notices/{notice_id}
     Get notice details and delivery status.
     Returns: Notice with cryptographic proof of creation,
              delivery confirmations, and response history

POST /api/v1/notices/{notice_id}/deliver
     Deliver notice via available channels (email, registered mail, API).
     Returns: Delivery receipt with timestamp and cryptographic proof

GET  /api/v1/notices/{notice_id}/evidence
     Generate evidence package proving notice was created, delivered,
     and (if applicable) acknowledged or ignored.
     Returns: Court-ready evidence bundle
```

---

## 5. Integration with Signing Pipeline

### 5.1 Enhanced `/api/v1/sign` Request

The existing sign endpoint is extended to include rights information that gets embedded into the C2PA manifest and stored in the registry.

```json
{
  "document_id": "article_2026_0220_001",
  "text": "Full article text here...",
  "segmentation_level": "sentence",
  "manifest_mode": "minimal_uuid",

  "metadata": {
    "title": "Article Title",
    "author": "Byline Author",
    "publisher": "Publisher Name",
    "published_date": "2026-02-20T10:00:00Z",
    "content_type": "news",
    "section": "politics",
    "url": "https://publisher.com/article-slug"
  },

  "rights": {
    "use_profile_defaults": true,

    "overrides": {
      "bronze_tier": {
        "embargo_period_hours": 48
      },
      "gold_tier": {
        "allowed": false,
        "reason": "Exclusive investigative content"
      }
    },

    "custom_notice": null
  }
}
```

When `use_profile_defaults: true`, the system pulls the publisher's rights profile and applies it. Any `overrides` are merged on top. This means the common case (use my defaults) is a single boolean flag, not a massive JSON blob on every signing request.

### 5.2 What Gets Embedded vs. What Stays in the Registry

**Embedded in the text** (via Unicode variation selectors):
- Segment UUID (already exists)
- These resolve to the registry — they are pointers, not data stores

**Embedded in the C2PA manifest** (attached to or referenced by the document):
- Publisher identity
- License type (e.g. "All Rights Reserved")
- Rights resolution URL (e.g. `https://api.encypher.com/api/v1/public/rights/{doc_id}`)
- Formal notice status flag
- Signing timestamp

**Stored in the registry only** (not embedded, accessed via API):
- Full tiered licensing terms (bronze/silver/gold)
- Pricing details
- Licensing contact information
- Formal notice history
- Evidence chain
- Usage analytics
- Licensing agreements

**Design rationale:** Embedding detailed licensing terms into text via Unicode selectors would be fragile and space-limited. Instead, we embed minimal pointers (UUIDs) that resolve to the full rights registry. The C2PA manifest carries enough information for immediate identification, and the API provides the comprehensive terms. This is analogous to how DNS works — you embed a domain name, not the full server configuration.

### 5.3 WordPress Plugin Integration

The WordPress plugin signing flow needs to surface rights management without adding complexity for non-technical publishers.

```
WORDPRESS PLUGIN UX FLOW
─────────────────────────

1. Plugin Settings (one-time setup):
   - "Set your default licensing terms" → Opens rights profile wizard
   - Pre-built templates: "News Publisher", "Blog/Independent",
     "Academic", "All Rights Reserved (Default)"
   - Template populates all three tiers with sensible defaults
   - Publisher can customize any tier
   - Saves to Encypher API as publisher rights profile

2. On Post Publish (automatic):
   - Plugin calls /api/v1/sign with use_profile_defaults: true
   - Content is signed, rights are registered, markers embedded
   - No per-article rights decisions required (unless publisher
     enables "Custom rights per post" in settings)

3. Optional: Per-Post Override
   - If enabled, post editor shows a "Licensing" meta box
   - Quick toggles: "Allow AI training?" "Allow RAG retrieval?"
   - "Premium content" checkbox (triggers higher pricing tier)
   - "Embargo" date picker (delay licensing availability)
   - These become document-level overrides in the registry

4. Dashboard Widget:
   - "X articles signed this month"
   - "Y licensing inquiries received"
   - "Z formal notices active"
   - Link to full Encypher dashboard
```

### 5.4 Chrome Extension Integration

The Chrome extension is the **detection and resolution** side — it doesn't create rights, it discovers them.

```
CHROME EXTENSION FLOW
─────────────────────

1. User browses web page containing text
2. Extension scans for Unicode variation selector patterns
3. If markers detected:
   a. Resolves UUIDs via /api/v1/public/c2pa/zw/resolve
   b. Fetches rights info via /api/v1/public/rights/{document_id}
   c. Displays overlay:
      ┌──────────────────────────────────────────┐
      │ ✓ SIGNED CONTENT DETECTED                │
      │                                          │
      │ Publisher: Associated Press               │
      │ Signed: February 15, 2026               │
      │ Integrity: ✓ Verified (no tampering)     │
      │                                          │
      │ LICENSING TERMS:                         │
      │ ├─ Scraping: Licensed access available   │
      │ ├─ RAG: Requires license ($0.01/query)   │
      │ └─ Training: Contact for terms           │
      │                                          │
      │ [View Full Terms] [Request License]      │
      └──────────────────────────────────────────┘
4. "Request License" button → Opens licensing request flow
5. "View Full Terms" → Opens public rights page
```

---

## 6. Platform Partner Integration

Sales houses and platform partners (Freestar, Mediavine, Raptive, etc.) need to sign content on behalf of their publishers. The rights management system needs to support delegated signing with proper rights inheritance.

```
PLATFORM PARTNER SIGNING FLOW
──────────────────────────────

1. Platform partner has org-level API key (strategic_partner tier)
2. Each publisher under the platform has their own rights profile
   in Encypher (set up during publisher onboarding through the partner)
3. Platform partner signs content on behalf of publishers:

   POST /api/v1/sign
   Authorization: Bearer platform_partner_key
   {
     "on_behalf_of": "publisher_org_id",
     "document_id": "...",
     "text": "...",
     "rights": {
       "use_profile_defaults": true
     }
   }

4. Rights profile of the publisher (not the platform) governs terms
5. Platform partner can set publisher defaults during onboarding
   but cannot override individual publisher's terms after setup
6. Publishers can access their own dashboard to modify terms directly


DELEGATED RIGHTS SETUP
──────────────────────

POST /api/v1/rights/profile/delegated-setup
Auth: Required (platform partner)
Body: {
  "publisher_organization_id": "new_publisher_org",
  "publisher_name": "Local News Daily",
  "publisher_url": "https://localnewsdaily.com",
  "contact_email": "editor@localnewsdaily.com",
  "template": "news_publisher_default",
  "overrides": { ... any partner-recommended customizations ... },
  "delegation": {
    "partner_can_sign": true,
    "partner_can_modify_rights": false,
    "publisher_can_override": true
  }
}
```

---

## 7. Formal Notice & Evidence Chain

### 7.1 The Legal Transformation Pipeline

This is the core commercial value: transforming the legal position from "prove they used your content" to "prove they ignored your notice."

```
LEGAL TRANSFORMATION PIPELINE
──────────────────────────────

STAGE 1: CONTENT SIGNED
├─ Cryptographic proof of ownership (C2PA manifest)
├─ Sentence-level Merkle tree (tamper detection)
├─ Invisible markers embedded (survive distribution)
├─ Rights and licensing terms registered
└─ Timestamp: Publisher establishes priority

STAGE 2: FORMAL NOTICE SERVED
├─ AI company receives notice that content is marked
├─ Notice includes: what's marked, where to verify, how to license
├─ Delivery confirmed (email receipt, API acknowledgment, registered mail)
├─ Cryptographic hash of notice recorded (immutable)
└─ Timestamp: "They knew" moment established

STAGE 3: CONTINUED USE DETECTED
├─ Attribution Analytics finds signed content on web surface (Tier 1)
├─ Or: AI company's own ingestion logs show marked content (Tier 2)
├─ Or: AI output contains verifiable fragments of signed content
├─ Usage documented with timestamps
└─ Evidence accumulates in registry

STAGE 4: EVIDENCE PACKAGE GENERATED
├─ Original signed content with Merkle proofs
├─ Formal notice with delivery confirmation
├─ Usage evidence with timestamps
├─ Chain-of-custody documentation
├─ Rights terms that were in effect at time of use
└─ Court-ready bundle (PDF + structured data + cryptographic proofs)

RESULT:
├─ Innocent infringement defense eliminated
├─ Willful infringement provable (3x damages territory)
├─ Settlement leverage dramatically increased
└─ Discovery costs dramatically reduced
```

### 7.2 Evidence Immutability

Critical design requirement: **the evidence chain must be tamper-evident and independently verifiable.** A publisher can't credibly claim "we notified them on date X" if the notification record can be modified.

```
IMMUTABILITY STRATEGY
─────────────────────

1. Every rights profile version is immutable (append-only versioning)
2. Every formal notice gets:
   - SHA-256 hash of notice content
   - Timestamp from trusted time source
   - Optional: hash anchored to public blockchain or timestamping authority
3. Every delivery confirmation is separately hashed and timestamped
4. Evidence packages are generated from immutable records
5. Any modification to historical records creates a new version
   (old version preserved, modification logged)

TABLES:
- rights_audit_log: Every change to any rights-related record
- notice_evidence_chain: Append-only log of notice lifecycle events
- evidence_packages: Generated bundles with cryptographic seals
```

---

## 8. Machine-Readable Rights Discovery

### 8.1 How AI Companies Find Our Rights Information

For the formal notice framework to work, AI companies need to be able to **discover** that content is marked and **find** the licensing terms — even if they're not specifically looking for Encypher markers. We need multiple discovery paths.

```
DISCOVERY PATH 1: Embedded Markers (Primary)
─────────────────────────────────────────────
AI company's ingestion pipeline processes text → Unicode variation
selectors are present → If they check, UUIDs resolve to rights info.
If they don't check, the markers still exist as evidence that rights
information was present and discoverable.

DISCOVERY PATH 2: C2PA Manifest (Standards-Based)
──────────────────────────────────────────────────
Content carries C2PA manifest (per the standard Erik authored) →
Any C2PA-aware system can extract publisher identity and rights URL →
Standard-compliant discovery without Encypher-specific tooling.

DISCOVERY PATH 3: HTTP Headers (For Crawlers)
──────────────────────────────────────────────
Publisher's web server includes HTTP headers on content pages:
  X-Content-Rights: https://api.encypher.com/api/v1/public/rights/{doc_id}
  X-Content-Provenance: c2pa
  X-Licensing-Contact: licensing@publisher.com

WordPress plugin can add these automatically.

DISCOVERY PATH 4: HTML Meta Tags (For Scrapers)
────────────────────────────────────────────────
<meta name="content-rights"
      content="https://api.encypher.com/api/v1/public/rights/{doc_id}" />
<meta name="content-provenance" content="c2pa-signed" />
<meta name="licensing-contact" content="licensing@publisher.com" />
<link rel="license"
      href="https://api.encypher.com/api/v1/public/rights/{doc_id}/json-ld"
      type="application/ld+json" />

DISCOVERY PATH 5: robots.txt Enhancement
─────────────────────────────────────────
# AI-specific licensing information
# See https://api.encypher.com/api/v1/public/rights/organization/{org_id}
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
Disallow: /  # Or specific paths
# License-URL: https://publisher.com/ai-licensing
# Rights-API: https://api.encypher.com/api/v1/public/rights/organization/{org_id}

DISCOVERY PATH 6: ODRL / JSON-LD (Semantic Web)
────────────────────────────────────────────────
Machine-readable rights in W3C standard formats, discoverable by any
semantic web crawler. Enables automated rights resolution without
Encypher-specific integration.

DISCOVERY PATH 7: Well-Known URL Convention
───────────────────────────────────────────
https://publisher.com/.well-known/ai-rights.json
→ Points to Encypher rights API for this publisher
→ Similar to /.well-known/security.txt pattern
→ Propose as industry convention through Syracuse / NMA
```

### 8.2 The "Constructive Notice" Doctrine

Even if an AI company doesn't actively check for rights information, the presence of multiple discovery paths creates a **constructive notice** argument: the rights information was available, accessible, machine-readable, and discoverable through standard methods. A reasonable actor should have discovered it. This strengthens the willful infringement argument regardless of whether the AI company claims they "didn't check."

---

## 9. Database Schema Extensions

### 9.1 New Tables (Added to Coalition Service Database)

The rights management tables live in `encypher_coalition` because they're fundamentally about the licensing relationship between publishers and consumers, not about the content signing itself.

```sql
-- Publisher rights profiles (versioned, append-only)
CREATE TABLE publisher_rights_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    profile_version INTEGER NOT NULL DEFAULT 1,
    effective_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES users(id),

    publisher_name TEXT NOT NULL,
    publisher_url TEXT,
    contact_email TEXT NOT NULL,
    contact_url TEXT,
    legal_entity TEXT,
    jurisdiction TEXT DEFAULT 'US',

    default_license_type TEXT NOT NULL DEFAULT 'all_rights_reserved',

    bronze_tier JSONB NOT NULL DEFAULT '{}',
    silver_tier JSONB NOT NULL DEFAULT '{}',
    gold_tier JSONB NOT NULL DEFAULT '{}',

    notice_status TEXT NOT NULL DEFAULT 'draft',
    notice_effective_date TIMESTAMPTZ,
    notice_text TEXT,
    notice_hash TEXT,

    coalition_member BOOLEAN NOT NULL DEFAULT true,
    coalition_joined_at TIMESTAMPTZ,
    licensing_track TEXT NOT NULL DEFAULT 'both',

    UNIQUE(organization_id, profile_version)
);

-- Document-level rights overrides
CREATE TABLE document_rights_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    organization_id UUID NOT NULL,
    override_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES users(id),

    override_type TEXT NOT NULL DEFAULT 'document',
    collection_id UUID,
    content_type_filter TEXT,
    date_range_start TIMESTAMPTZ,
    date_range_end TIMESTAMPTZ,

    bronze_tier_override JSONB,
    silver_tier_override JSONB,
    gold_tier_override JSONB,

    do_not_license BOOLEAN NOT NULL DEFAULT false,
    premium_content BOOLEAN NOT NULL DEFAULT false,
    embargo_until TIMESTAMPTZ,
    syndication_rights JSONB,

    UNIQUE(document_id, override_version)
);

-- Formal notices (immutable once sent)
CREATE TABLE formal_notices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    target_entity_name TEXT NOT NULL,
    target_entity_domain TEXT,
    target_contact_email TEXT,
    target_entity_type TEXT NOT NULL DEFAULT 'ai_company',

    scope_type TEXT NOT NULL,
    scope_document_ids UUID[],
    scope_date_range_start TIMESTAMPTZ,
    scope_date_range_end TIMESTAMPTZ,

    notice_type TEXT NOT NULL,
    notice_text TEXT NOT NULL,
    notice_hash TEXT NOT NULL,  -- SHA-256 of notice_text

    demands JSONB NOT NULL,

    status TEXT NOT NULL DEFAULT 'created',
    delivered_at TIMESTAMPTZ,
    delivery_method TEXT,
    delivery_receipt JSONB,
    delivery_receipt_hash TEXT,

    acknowledged_at TIMESTAMPTZ,
    response JSONB,

    CONSTRAINT notice_immutable CHECK (
        -- Once delivered, notice content cannot change
        -- (enforced at application layer, this is a safety net)
        status != 'delivered' OR notice_hash IS NOT NULL
    )
);

-- Append-only evidence chain
CREATE TABLE notice_evidence_chain (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notice_id UUID NOT NULL REFERENCES formal_notices(id),
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL,
    event_hash TEXT NOT NULL,
    previous_hash TEXT,  -- Chain link to previous event
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- No UPDATE or DELETE allowed (enforced at application layer + DB triggers)
    CONSTRAINT chain_immutable CHECK (event_hash IS NOT NULL)
);

-- Licensing requests and agreements
CREATE TABLE licensing_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publisher_org_id UUID NOT NULL,
    requester_org_id UUID,

    tier TEXT NOT NULL,
    scope JSONB NOT NULL,
    proposed_terms JSONB NOT NULL,
    requester_info JSONB NOT NULL,

    status TEXT NOT NULL DEFAULT 'pending',
    response JSONB,
    responded_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE licensing_agreements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES licensing_requests(id),
    publisher_org_id UUID NOT NULL,
    licensee_org_id UUID NOT NULL,

    tier TEXT NOT NULL,
    scope JSONB NOT NULL,
    terms JSONB NOT NULL,

    effective_date TIMESTAMPTZ NOT NULL,
    expiry_date TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT false,

    status TEXT NOT NULL DEFAULT 'active',

    usage_metrics JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Rights audit log (append-only)
CREATE TABLE rights_audit_log (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID NOT NULL,
    old_value JSONB,
    new_value JSONB,
    performed_by UUID,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address INET
);

-- Indexes
CREATE INDEX idx_rights_profiles_org ON publisher_rights_profiles(organization_id, profile_version DESC);
CREATE INDEX idx_document_overrides_doc ON document_rights_overrides(document_id, override_version DESC);
CREATE INDEX idx_document_overrides_org ON document_rights_overrides(organization_id);
CREATE INDEX idx_formal_notices_org ON formal_notices(organization_id);
CREATE INDEX idx_formal_notices_target ON formal_notices(target_entity_domain);
CREATE INDEX idx_evidence_chain_notice ON notice_evidence_chain(notice_id, created_at);
CREATE INDEX idx_licensing_requests_publisher ON licensing_requests(publisher_org_id, status);
CREATE INDEX idx_licensing_agreements_active ON licensing_agreements(status, expiry_date) WHERE status = 'active';
CREATE INDEX idx_rights_audit_org ON rights_audit_log(organization_id, performed_at DESC);
```

---

## 10. Implementation Priority

### Phase 1: Foundation (Build First)

These are the minimum viable components to start attaching rights to signed content:

1. **`publisher_rights_profiles` table + CRUD API** — Publishers need to set defaults
2. **Rights templates** (3-4 pre-built profiles) — Reduce onboarding friction
3. **Enhanced `/api/v1/sign` with `rights` parameter** — Wire rights into signing pipeline
4. **`/api/v1/public/rights/{document_id}` endpoint** — Public rights resolution
5. **WordPress plugin "Licensing" settings panel** — Non-technical publisher onboarding
6. **C2PA manifest includes rights URL** — Standards-compliant rights discovery

### Phase 2: Enforcement (Build Second)

These enable the commercial value — formal notice and evidence:

7. **`formal_notices` table + create/deliver API** — Notice lifecycle management
8. **`notice_evidence_chain` table** — Immutable evidence accumulation
9. **Evidence package generation endpoint** — Court-ready bundles
10. **Chrome extension rights overlay** — Visual rights discovery for end users
11. **HTTP headers + meta tag generation** — WordPress plugin auto-adds discovery paths

### Phase 3: Licensing Transactions (Build Third)

These enable actual deal-making through the platform:

12. **`licensing_requests` + `licensing_agreements` tables** — Transaction management
13. **Licensing request/response API** — Publisher ↔ consumer communication
14. **Usage metering against active licenses** — Compliance monitoring
15. **Dashboard for licensing management** — Publisher UI for managing requests/agreements
16. **Platform partner delegated setup API** — Sales houses onboard publishers

### Phase 4: Standards Interoperability (Build When Platform Partners Are Live)

17. **RSL XML generation from rights profiles** — Auto-generate RSL 1.0 documents
18. **RSL import** — Ingest existing publisher RSL terms into our rights registry
19. **RSL OLP bridge** — Serve as RSL-compatible license server for crawl authorization
20. **robots.txt generation with RSL License directives** — WordPress plugin auto-appends
21. **ODRL / JSON-LD output** — W3C standard machine-readable rights
22. **Well-known URL convention** — Propose through NMA/Syracuse

### Phase 5: Analytics & Ecosystem (Build When Detection Volume Justifies)

23. **Phone-home analytics tables and ingestion** — content_detection_events at scale
24. **Publisher analytics dashboard** — "Where is my content appearing?"
25. **Known crawler registry** — Classify user agents hitting rights endpoints
26. **Bulk rights resolution API** — For AI companies processing pipelines at scale
27. **RSL Collective interop** — Bridge to RSL Collective if publisher is a member
28. **Rights analytics export** — CSV/API for publishers feeding into their own systems

---

## 11. Open Architecture Questions

These need decisions before implementation begins:

1. **Rights profile versioning:** When a publisher changes their terms, do existing signed documents retroactively get the new terms, or do they retain the terms that were in effect at signing time? Recommendation: signed documents retain the terms at signing, but publisher can explicitly "re-publish" with new terms.

2. **Tier pricing visibility:** Should specific pricing (e.g., "$0.01/retrieval") be visible in the public rights API, or only "contact for pricing"? Recommendation: publisher chooses per tier — some may want transparent pricing, others may want negotiation.

3. **Coalition vs. self-service routing:** When a licensing request comes in, how does the system determine whether it's a coalition deal (60/40) vs. self-service (80/20)? Is this the publisher's choice per request, or is it determined by how the request originated?

4. **Evidence chain anchoring:** Do we anchor evidence hashes to an external timestamping authority (e.g., RFC 3161 TSA, or a blockchain) for independent verifiability? This adds cost and complexity but strengthens the legal argument. Recommendation: Phase 2 — use internal timestamps initially, add external anchoring when legal teams request it.

5. **Rate limiting on public rights endpoints:** How aggressively do we rate-limit the public rights resolution API? Too aggressive = AI companies can claim they couldn't discover terms. Too permissive = DoS risk. Recommendation: generous limits (10,000 requests/hour per IP) with clear error messages pointing to bulk resolution API for higher volumes.

6. **Rights inheritance for syndicated content:** When AP content is syndicated through wire services to hundreds of downstream publishers, and a downstream publisher signs the AP content through their own Encypher account — whose rights profile governs? Recommendation: original publisher's rights (AP) govern, with syndication terms overlaid. This needs a "syndication_source" field.

7. **RSL Collective membership vs. independence:** Should Encypher integrate with the RSL Collective's licensing server infrastructure, or should we serve as an independent RSL-compatible license server? The RSL Collective operates as a nonprofit rights organization (modeled on ASCAP/BMI). We could be a member, a compatible alternative, or both. Recommendation: compatible alternative that can also bridge to the Collective — maximum interoperability without dependency.

8. **RSL OLP token scope:** When issuing OLP tokens for crawl access, should the token grant access to all publisher content or per-URL/per-section? RSL supports both. Our rights profile supports per-document overrides. These need to align. Recommendation: match the granularity of the publisher's rights profile — if they have section-level overrides, issue section-scoped tokens.

9. **Phone-home analytics privacy:** Content detection events log requester IPs and user agents. This data has privacy implications (especially in EU/GDPR contexts). How long do we retain granular detection data vs. aggregated summaries? Recommendation: 90-day granular retention, then aggregate. Aggregated data retained indefinitely. Publisher can configure shorter retention.

---

## 12. Standards Interoperability Layer — RSL, robots.txt, and the "Source vs. Gate" Problem

### 12.1 The Fundamental Architecture Distinction

There are two fundamentally different approaches to content rights in the AI era, and understanding the distinction is essential to the architecture:

**Gate-Based Rights (RSL, robots.txt, Cloudflare AI Audit, Tollbit, Spawning)**

These operate at the **perimeter** — the publisher's web server. They answer: "Can this crawler access my content?" They declare licensing terms at the point of access and can enforce via HTTP 401/402, network-level blocking, or crawler authorization protocols.

Limitation: Once content passes through the gate — via B2B licensees, wire services, aggregators, cached copies, RSS feeds, or a paste into a training dataset — the gate-based system has zero visibility and zero leverage. As Paul Sarkis (AP) put it: "You can get all of AP's content without having to go to apnews.com." Gate-based rights are irrelevant for content that's already distributed.

**Source-Based Rights (Encypher / C2PA provenance)**

We operate at the **origin** — the content itself. We embed proof of ownership and rights metadata directly into the text at the sentence level. The cryptographic watermark doesn't care how the content was obtained. Whether an AI company scraped it directly, got it through a B2B feed, found it on an aggregator, or received it pasted into a prompt — the provenance markers are there, the rights are discoverable, and the formal notice framework applies.

**These approaches are complementary, not competitive.** A publisher using RSL at the gate AND Encypher at the source has a much stronger position than either alone. RSL locks the front door and captures bronze-tier revenue. Encypher proves ownership wherever content ends up, regardless of how it was obtained, and enables silver-tier and gold-tier deals that represent the vast majority of licensing value.

### 12.2 RSL 1.0 Technical Overview (For Architect Reference)

RSL (Really Simple Licensing) 1.0 is an XML-based standard published December 10, 2025 by the RSL Technical Steering Committee. Key technical facts:

- **XML vocabulary** for machine-readable licensing terms
- **Discovery channels:** robots.txt (`License:` directive), HTTP headers, HTML `<link>` elements, RSS/Atom feeds, standalone `rsl.txt` file
- **Enforcement protocols:** Open License Protocol (OLP — OAuth 2.0 extension for license acquisition), Crawler Authorization Protocol (CAP — HTTP authorization scheme for licensed crawlers)
- **Precedence rules:** Page-level > site-level; most restrictive combination governs conflicts
- **Supporters:** Cloudflare, Akamai, Fastly, Creative Commons, IAB Tech Lab, AP, Vox Media, USA Today, Reddit, Yahoo, Ziff Davis, 1,500+ organizations
- **Critical limitation:** No major AI model developer (OpenAI, Google, Anthropic, Meta, xAI) has committed to honoring RSL. It carries no legal force on its own. It only works if AI companies voluntarily comply or if infrastructure providers enforce it at the network level.

RSL XML structure (simplified):
```xml
<rsl xmlns="https://rslstandard.org/rsl">
  <content url="/articles" server="https://licensing-server.com/api">
    <license>
      <type>paid</type>
      <standard>https://rslstandard.org/licenses/commercial-ai</standard>
      <terms url="https://publisher.com/ai-terms" />
    </license>
  </content>
</rsl>
```

### 12.3 Why RSL Interoperability Matters (And Where It Falls Short)

**What RSL does well:**
- Machine-readable rights declaration at the domain/page level
- Broad publisher adoption (1,500+ orgs) creating industry momentum
- Infrastructure enforcement support (Cloudflare, Akamai, Fastly)
- Crawler authorization protocol for licensed access
- Industry standard vocabulary for access-tier licensing

**What RSL cannot do (and where Encypher fills the gap):**
- RSL terms live on the publisher's web server. They don't travel with content once it's scraped, syndicated, or distributed. Our markers do.
- RSL provides no proof of ownership for content encountered outside the publisher's domain. Our C2PA manifests and Merkle trees do.
- RSL has no mechanism for sentence-level attribution, quote integrity verification, or tamper detection. Our patent-pending infrastructure does.
- RSL formal notice is a declaration at the gate. Our formal notice is cryptographic proof embedded in the content itself — much harder to argue "we didn't know."
- RSL requires voluntary compliance by AI companies (none of the major ones have committed). Our system creates legal evidence whether or not the AI company cooperates.

**The strategic position:** We are not competing with RSL. We are the provenance and enforcement layer that makes RSL's licensing declarations legally enforceable beyond the front door. Publishers should use RSL AND Encypher. RSL tells crawlers "here are our terms." Encypher proves ownership and creates enforcement leverage wherever content ends up.

### 12.4 RSL Bridge Architecture

The system should generate and consume RSL as one of many standards-based expression formats for the publisher's rights profile. The canonical source of truth is always our rights registry — RSL is an output format, not our data model.

```
ENCYPHER RIGHTS REGISTRY (Source of Truth)
│
├──→ RSL XML output (/api/v1/public/rights/{org_id}/rsl)
│     → Publisher hosts as rsl.txt or embeds in robots.txt
│     → WordPress plugin auto-generates and serves
│     → Maps bronze/silver/gold tiers to RSL <license> elements
│
├──→ robots.txt integration (/api/v1/public/rights/{org_id}/robots-meta)
│     → Generates RSL-compatible License: directives
│     → References Encypher rights API for full terms
│     → WordPress plugin auto-appends to robots.txt
│
├──→ JSON-LD / ODRL output (existing from Section 4.2)
│
├──→ C2PA manifest (embedded in signed content)
│     → Rights URL points back to registry
│     → Travels with content regardless of distribution
│
├──→ HTTP headers (auto-generated by WordPress plugin)
│     → X-Content-Rights: registry URL
│     → X-RSL-License: RSL license URL
│     → Link: <registry URL>; rel="license"
│
└──→ Unicode embedded markers (in text itself)
      → Resolve to registry → which can output RSL, ODRL, JSON-LD
      → This is the path that works AFTER content leaves the gate
```

**RSL Generation API:**

```
GET  /api/v1/public/rights/organization/{org_id}/rsl
     Generate RSL 1.0 XML document from publisher's rights profile.
     Auth: None (public)
     Returns: RSL XML with tier-appropriate licensing terms

     Mapping logic:
     ┌─────────────────────────┬──────────────────────────────────┐
     │ Encypher Tier           │ RSL Expression                   │
     ├─────────────────────────┼──────────────────────────────────┤
     │ Bronze (scraping)       │ <license> with crawl terms,      │
     │                         │   rate limits, pricing           │
     │                         │   (maps directly to RSL's core   │
     │                         │    use case)                     │
     ├─────────────────────────┼──────────────────────────────────┤
     │ Silver (RAG/retrieval)  │ <license> with retrieval terms,  │
     │                         │   excerpt limits, attribution    │
     │                         │   requirements                   │
     │                         │   + <terms> URL pointing to      │
     │                         │   Encypher quote integrity API   │
     ├─────────────────────────┼──────────────────────────────────┤
     │ Gold (training)         │ <license> with training terms,   │
     │                         │   exclusivity flags, audit       │
     │                         │   rights                         │
     │                         │   + <terms> URL pointing to      │
     │                         │   Encypher licensing request API │
     └─────────────────────────┴──────────────────────────────────┘

GET  /api/v1/public/rights/organization/{org_id}/robots-txt
     Generate robots.txt additions with RSL License directives.
     Auth: None (public)
     Returns: Text block to append to publisher's robots.txt

POST /api/v1/rights/rsl/import
     Import existing RSL document and create rights profile from it.
     Auth: Required (org admin)
     Body: RSL XML document
     Returns: Created/updated rights profile
     Note: For publishers who already have RSL set up — we ingest
     their existing terms and enhance them with our provenance layer.
```

**RSL Import Logic (for publishers who already have RSL):**

A publisher already using RSL shouldn't have to re-enter their terms. The system should be able to ingest an existing RSL document and map it to our bronze/silver/gold schema:

```
RSL <license> with crawl terms    →  Bronze tier defaults populated
RSL <license> with retrieval terms →  Silver tier defaults populated
RSL <license> with training terms  →  Gold tier defaults populated
RSL <standard> URL                →  Stored as reference license
RSL <terms> URL                   →  Linked as publisher terms page
RSL server endpoint               →  Stored for OLP interop
```

### 12.5 "Phone Home" Analytics — Detection and Rights Resolution Telemetry

When marked content is encountered anywhere on the internet, it should trigger analytics that flow back to the publisher. This is the "the content itself reports back" capability that gate-based systems fundamentally cannot provide.

**How Phone-Home Works Across Discovery Paths:**

```
SCENARIO 1: Chrome Extension Detection (Tier 1 — Available Now)
──────────────────────────────────────────────────────────────────
1. User visits web page with Encypher-signed content
2. Chrome extension detects Unicode variation selector markers
3. Extension calls /api/v1/public/c2pa/zw/resolve/{segment_uuid}
4. Resolution API logs the detection event:
   {
     "event": "content_detected",
     "detection_source": "chrome_extension",
     "document_id": "doc_abc",
     "publisher_org_id": "org_xyz",
     "detected_on_url": "https://aggregator-site.com/article",
     "detected_at": "2026-02-20T14:30:00Z",
     "segments_found": 42,
     "integrity": "intact" | "partial_tampering" | "stripped",
     "user_agent_category": "human_browser"
   }
5. Publisher dashboard shows: "Your content appeared on aggregator-site.com"


SCENARIO 2: AI Crawler Encounters Marked Content
──────────────────────────────────────────────────
1. AI crawler (GPTBot, ClaudeBot, etc.) requests page
2. HTTP headers include rights URL (added by WordPress plugin)
3. If crawler checks rights:
   → API logs the rights lookup event
   → Publisher dashboard: "GPTBot looked up licensing terms for
      your content at 14:30 UTC"
   → This is gold-standard evidence of awareness
4. If crawler doesn't check rights but processes content:
   → Embedded markers are in the training data
   → If AI company later runs provenance check, it resolves
   → If they never check, markers are still evidence that
      rights information was embedded and discoverable


SCENARIO 3: API-Based Content Verification (Tier 1)
─────────────────────────────────────────────────────
1. Anyone calls /api/v1/verify with text containing markers
2. Verification API resolves markers, returns rights info
3. Every verification call is logged:
   {
     "event": "verification_request",
     "requester_ip": "...",
     "requester_org": "...",  (if authenticated)
     "document_id": "doc_abc",
     "publisher_org_id": "org_xyz",
     "verification_result": "authentic",
     "rights_included_in_response": true
   }
4. Publisher dashboard: "3 verification requests for your
   content from IP range associated with [AI Company]"


SCENARIO 4: RSL OLP License Check (Interop)
─────────────────────────────────────────────
1. RSL-compliant crawler requests content from publisher domain
2. Publisher's RSL License directive points to Encypher OLP endpoint
3. Crawler requests license via OLP (OAuth 2.0 extension)
4. Encypher OLP bridge:
   → Validates crawler identity
   → Returns license terms from rights profile
   → Logs the license acquisition/check event
   → Publisher dashboard: "[Crawler] requested RSL license
      for /articles section"
5. If crawler proceeds without obtaining license:
   → RSL-level violation (access-tier evidence)
   → Combined with Encypher provenance (source-tier evidence)
   → Dual evidence chain strengthens enforcement
```

**Analytics Tables:**

```sql
-- Content detection events (append-only, high-volume)
CREATE TABLE content_detection_events (
    id BIGSERIAL PRIMARY KEY,
    document_id UUID NOT NULL,
    organization_id UUID NOT NULL,

    detection_source TEXT NOT NULL,
        -- 'chrome_extension', 'api_verification', 'rsl_olp_check',
        -- 'http_header_lookup', 'rights_api_lookup', 'crawl_detected'

    detected_on_url TEXT,
    detected_on_domain TEXT,

    requester_ip INET,
    requester_org_id UUID,
    requester_user_agent TEXT,
    user_agent_category TEXT,
        -- 'human_browser', 'ai_crawler', 'search_crawler',
        -- 'aggregator', 'unknown'

    segments_found INTEGER,
    integrity_status TEXT,
        -- 'intact', 'partial_tampering', 'significant_tampering',
        -- 'stripped'

    rights_served BOOLEAN DEFAULT false,
    rights_acknowledged BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Partition by month for performance
    -- No updates or deletes — append-only analytics
) PARTITION BY RANGE (created_at);

-- Aggregated analytics for dashboard (materialized, refreshed periodically)
CREATE MATERIALIZED VIEW content_detection_summary AS
SELECT
    organization_id,
    date_trunc('day', created_at) as detection_date,
    detection_source,
    detected_on_domain,
    user_agent_category,
    COUNT(*) as detection_count,
    COUNT(DISTINCT document_id) as unique_documents,
    COUNT(DISTINCT detected_on_domain) as unique_domains,
    SUM(CASE WHEN rights_served THEN 1 ELSE 0 END) as rights_served_count,
    SUM(CASE WHEN rights_acknowledged THEN 1 ELSE 0 END) as rights_ack_count
FROM content_detection_events
GROUP BY 1, 2, 3, 4, 5;

-- Known crawler registry (for user_agent classification)
CREATE TABLE known_crawlers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_agent_pattern TEXT NOT NULL,
    crawler_name TEXT NOT NULL,
    operator_org TEXT NOT NULL,
    crawler_type TEXT NOT NULL,
        -- 'ai_training', 'ai_search', 'search_engine',
        -- 'aggregator', 'monitoring'
    respects_robots_txt BOOLEAN,
    respects_rsl BOOLEAN,
    known_ip_ranges INET[],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_detection_events_org_date
    ON content_detection_events(organization_id, created_at DESC);
CREATE INDEX idx_detection_events_domain
    ON content_detection_events(detected_on_domain, created_at DESC);
CREATE INDEX idx_detection_events_document
    ON content_detection_events(document_id, created_at DESC);
CREATE INDEX idx_detection_events_ua_category
    ON content_detection_events(user_agent_category, created_at DESC);
```

**Publisher Dashboard Analytics Views:**

The publisher dashboard surfaces phone-home analytics in actionable form:

```
DASHBOARD: "Where Is My Content Appearing?"
────────────────────────────────────────────

TOP LEVEL METRICS:
┌──────────────────┬──────────────────┬──────────────────┐
│ Signed Articles  │ Detections       │ Rights Lookups   │
│ 1,247            │ 8,432 this month │ 342 this month   │
└──────────────────┴──────────────────┴──────────────────┘

DETECTION BY SOURCE:
┌────────────────────────────┬───────┬──────────────────┐
│ Source                     │ Count │ Trend            │
├────────────────────────────┼───────┼──────────────────┤
│ Chrome Extension users     │ 5,120 │ ↑ 12%           │
│ API verification requests  │ 2,340 │ ↑ 8%            │
│ RSL license checks         │   872 │ new             │
│ HTTP header lookups        │   100 │ ↑ 3%            │
└────────────────────────────┴───────┴──────────────────┘

WHERE YOUR CONTENT WAS FOUND:
┌────────────────────────────┬───────┬──────────────────┐
│ Domain                     │ Count │ Rights Served?   │
├────────────────────────────┼───────┼──────────────────┤
│ perplexity.ai              │ 1,200 │ ✓ Yes (API)     │
│ news-aggregator.com        │   890 │ ✗ No            │
│ content-farm.xyz           │   450 │ ✗ No            │
│ chatgpt.com (via search)   │   230 │ ✓ Yes (API)     │
└────────────────────────────┴───────┴──────────────────┘

AI CRAWLER ACTIVITY:
┌────────────────────────────┬───────┬──────────────────┐
│ Crawler                    │ Visits│ Licensed?        │
├────────────────────────────┼───────┼──────────────────┤
│ GPTBot (OpenAI)            │ 3,400 │ ✗ No license    │
│ ClaudeBot (Anthropic)      │ 1,800 │ ✗ No license    │
│ Google-Extended             │ 2,100 │ ✗ No license    │
│ PerplexityBot              │   900 │ ✗ No license    │
└────────────────────────────┴───────┴──────────────────┘

ACTIONS AVAILABLE:
[Send Formal Notice to OpenAI]
[Generate Evidence Package for Google]
[View RSL Compliance Report]
[Export Detection Data (CSV)]
```

### 12.6 RSL OLP Bridge (Licensing Protocol Interoperability)

If a publisher wants to use the RSL Collective's Open License Protocol (OLP) for crawl-time license acquisition AND Encypher for provenance/enforcement, the system should bridge both. The Encypher rights registry can serve as the backend for RSL OLP requests.

```
RSL OLP BRIDGE ARCHITECTURE
────────────────────────────

1. Publisher's RSL document references Encypher as license server:
   <content url="/articles" server="https://api.encypher.com/rsl/olp">

2. AI crawler reads RSL, sees license requirement

3. Crawler sends OLP token request to Encypher:
   POST https://api.encypher.com/rsl/olp/token
   {
     "grant_type": "rsl_license",
     "scope": "crawl",
     "user_agent": "GPTBot/1.0",
     "target_url": "https://publisher.com/articles/*"
   }

4. Encypher OLP bridge:
   a. Looks up publisher rights profile
   b. Checks bronze tier terms
   c. If free access: issues token, logs event
   d. If paid: returns 402 with pricing terms
   e. If blocked: returns 401 with rights URL

5. Crawler includes token in subsequent requests:
   Authorization: License <token>

6. Publisher's server validates token (via Encypher API or cached)

7. All of this is logged in content_detection_events as
   detection_source = 'rsl_olp_check'


NEW ENDPOINT:

POST /api/v1/rsl/olp/token
     RSL Open License Protocol token endpoint.
     Implements RSL 1.0 Section 5 (OLP) with Encypher as
     the license server backend.
     Auth: Crawler identification (user agent + IP)
     Returns: OLP token or 401/402 with terms

GET  /api/v1/rsl/olp/validate/{token}
     Validate an issued OLP token.
     Used by publisher web servers to verify crawler authorization.
     Auth: Publisher API key
     Returns: Token validity, scope, requester identity
```

### 12.7 The Complete Standards Stack

When fully implemented, a publisher using Encypher has rights declared and enforceable through every major standard and discovery mechanism:

```
LAYER       STANDARD           WHAT IT DOES                    ENFORCEABILITY
──────      ──────────         ──────────────                  ──────────────
Gate        robots.txt         Block/allow crawlers            Voluntary
Gate        RSL 1.0            Machine-readable license terms  Voluntary (network
                               at domain level                 enforcement via CDN)
Gate        RSL OLP/CAP        Crawler authorization protocol  Token-based access
                                                               control
Content     C2PA 2.3 (A.7)     Cryptographic proof of origin   Cryptographic proof
                               in manifest                     (travels with content)
Content     Encypher markers   Sentence-level provenance       Cryptographic proof +
                               embedded in text                evidence chain
                                                               (survives distribution)
Registry    Encypher API       Full rights, licensing terms,   Formal notice +
                               formal notice, evidence chain   willful infringement
                                                               evidence
Semantic    JSON-LD / ODRL     W3C standard machine-readable   Semantic discovery
                               rights
Legal       Formal notice      Cryptographic proof of notice   Court-admissible
                               + delivery + awareness          evidence

───────────────────────────────────────────────────────────────────────────
KEY INSIGHT: Gate-layer standards (robots.txt, RSL) protect the front door.
Content-layer standards (C2PA, Encypher markers) protect everywhere else.
The registry unifies all layers into a single enforceable framework.
Only Encypher operates at all three layers simultaneously.
```

---

## 13. Success Criteria

The rights management system is working when:

1. A publisher can set up their licensing terms in under 5 minutes using a template
2. Any AI company encountering signed content can discover rights in a single API call
3. Formal notices are cryptographically provable and independently verifiable
4. Evidence packages are accepted as admissible in copyright proceedings
5. Platform partners can onboard publishers with rights profiles in a single API call
6. The bronze/silver/gold framework becomes the industry standard vocabulary for AI content licensing (validated through Syracuse and NMA)
7. Publishers with existing RSL implementations can import their terms and enhance them with provenance in a single API call
8. Phone-home analytics show publishers exactly where their content appears and which entities are accessing rights information
9. The publisher dashboard answers "who has my content, do they know the terms, and are they complying?" in real-time

---

*This system turns Encypher from a signing infrastructure into a complete rights management platform — where the cryptographic proof of ownership, the licensing terms, the formal notice, and the evidence chain are all unified in a single system that publishers control and AI companies can't ignore. RSL locks the front door. Encypher locks the content itself. Together, they close every side door.*
