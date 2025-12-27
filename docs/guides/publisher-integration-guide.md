# Publisher Integration Guide

**Integrate Encypher into Your Publishing Workflow**

This guide walks you through integrating Encypher's C2PA content authentication into your CMS or publishing system. We'll use a custom CMS example to demonstrate the integration patterns that work with any platform.

---

## Quick Start by Tier

| Tier | Best For | Key Features | Integration Time |
|------|----------|--------------|------------------|
| **Starter** | Small publishers, blogs | Basic signing & verification | 1-2 hours |
| **Professional** | News organizations | + Advanced signing (`/sign/advanced`), sentence tracking | 2-4 hours |
| **Business** | Large publishers | + Webhooks, bulk operations (`/batch/*`), Merkle trees, BYOK key registration, team management, audit logs | 4-8 hours |
| **Enterprise** | Media conglomerates | + SSO/SAML, custom assertion authoring (schemas/templates), unlimited team | 1-2 days |

---

## Table of Contents

1. [Getting Your API Key](#getting-your-api-key)
2. [Starter Tier Integration](#starter-tier-integration)
3. [Professional Tier Integration](#professional-tier-integration)
4. [Business Tier Integration](#business-tier-integration)
5. [Enterprise Tier Integration](#enterprise-tier-integration)
6. [Webhook Integration](#webhook-integration)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Getting Your API Key

1. Log in to your [Encypher Dashboard](https://dashboard.encypherai.com)
2. Navigate to **Settings** → **API Keys**
3. Click **Create New Key**
4. Name your key (e.g., "Production CMS Key")
5. Select permissions: `sign`, `verify`
6. Copy and securely store your key

```bash
# Your key looks like this:
ek_live_abc123def456...

# Set it as an environment variable
export ENCYPHER_API_KEY="ek_live_abc123def456..."
```

---

## Starter Tier Integration

**Perfect for:** Blogs, small news sites, individual journalists

### What You Get
- 10,000 C2PA signatures/month
- Sign & verify endpoints
- Basic verification badges

### Integration Example: Simple CMS Plugin

```python
# cms_encypher_plugin.py
"""
Simple Encypher integration for any CMS.
Signs articles on publish, verifies on display.
"""
import os
import requests
from typing import Optional

ENCYPHER_API_URL = "https://api.encypherai.com/api/v1"
API_KEY = os.environ.get("ENCYPHER_API_KEY")


class EncypherClient:
    """Minimal client for Starter tier."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def sign_article(self, title: str, content: str, author: str) -> dict:
        """
        Sign an article when it's published.
        
        Args:
            title: Article title
            content: Article body text
            author: Author name
            
        Returns:
            dict with signed_text and document_id
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/sign",
            headers=self.headers,
            json={
                "text": content,
                "document_title": title,
                "document_type": "article",
                "claim_generator": f"CMS/{author}",
            }
        )
        response.raise_for_status()
        return response.json()
    
    def verify_content(self, content: str) -> dict:
        """
        Verify if content has a valid C2PA signature.
        
        Supports multiple embeddings automatically:
        - If content has multiple signed sections, all are verified
        - Returns embeddings_found count and all_embeddings array
        - Backwards compatible with single-embedding responses
        
        Args:
            content: Text content to verify (can contain multiple embeddings)
            
        Returns:
            dict with verification status and signer info
            
        Example response (multiple embeddings):
            {
                "valid": True,
                "embeddings_found": 3,
                "all_embeddings": [
                    {"index": 0, "valid": True, "signer_name": "Acme Corp", ...},
                    {"index": 1, "valid": True, "signer_name": "Acme Corp", ...},
                    {"index": 2, "valid": True, "signer_name": "Acme Corp", ...}
                ]
            }
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/verify",
            headers=self.headers,
            json={"text": content}
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("success") is True:
            return payload.get("data") or {}
        raise ValueError(payload.get("error") or "Verification failed")


# === CMS Integration Hooks ===

def on_article_publish(article: dict) -> dict:
    """
    Hook: Call this when an article is published.
    
    Example CMS integration:
        @cms.on_publish
        def publish_handler(article):
            return on_article_publish(article)
    """
    client = EncypherClient()
    
    result = client.sign_article(
        title=article["title"],
        content=article["body"],
        author=article["author_name"]
    )
    
    # Store the document_id with your article
    article["encypher_document_id"] = result["document_id"]
    article["signed_body"] = result["signed_text"]
    article["verification_url"] = result.get("verification_url")
    
    return article


def on_article_display(article: dict) -> dict:
    """
    Hook: Call this when displaying an article to add verification badge.
    """
    client = EncypherClient()
    
    verification = client.verify_content(article.get("signed_body", article["body"]))
    
    article["is_verified"] = verification.get("valid", False)
    article["signer_name"] = verification.get("signer_name")
    article["verification_url"] = article.get("verification_url") or f"https://verify.encypherai.com/{article.get('encypher_document_id', '')}".rstrip("/")
    
    return article
```

### HTML Verification Badge

```html
<!-- Add to your article template -->
{% if article.is_verified %}
<div class="encypher-badge">
  <a href="{{ article.verification_url }}" target="_blank">
    <img src="https://encypherai.com/encypher_check_color.svg" 
         alt="Verified by {{ article.signer_name }}" />
    <span>Verified Content</span>
  </a>
</div>
{% endif %}

<style>
.encypher-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background: #f0fdf4;
  border: 1px solid #22c55e;
  border-radius: 6px;
  font-size: 14px;
}
.encypher-badge img {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}
</style>
```

---

## Professional Tier Integration

**Perfect for:** News organizations, multi-author publications

### What You Get
- Unlimited C2PA signatures
- Sentence-level tracking (plagiarism detection)
- Advanced signing (`/sign/advanced`) (Professional+)

### Integration Example: News CMS with Sentence Tracking

```python
# news_cms_encypher.py
"""
Professional tier integration with sentence tracking.
Enables plagiarism detection and content attribution.
"""
import os
import requests
import uuid
from typing import List, Optional
from dataclasses import dataclass

ENCYPHER_API_URL = "https://api.encypherai.com/api/v1"


@dataclass
class SentenceMatch:
    """Result of a sentence lookup."""
    sentence: str
    original_document: str
    original_author: str
    publication_date: str
    match_url: str


class ProfessionalEncypherClient:
    """Client for Professional tier with sentence tracking."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ENCYPHER_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def sign_with_tracking(
        self, 
        title: str, 
        content: str, 
        author: str,
        url: str,
        publication_date: str = None
    ) -> dict:
        """
        Sign article AND register sentences for tracking.
        
        This enables:
        - Plagiarism detection when others copy your content
        - Attribution when your content is quoted
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/sign",
            headers=self.headers,
            json={
                "text": content,
                "document_id": f"doc_{uuid.uuid4().hex[:16]}",
                "document_title": title,
                "document_url": url,
                "document_type": "article",
            }
        )
        response.raise_for_status()
        return response.json()
    
    def check_for_plagiarism(self, content: str) -> List[SentenceMatch]:
        """
        Check if any sentences in content match existing tracked content.
        
        Use this before publishing to detect potential plagiarism.
        """
        # Split into sentences (simplified - use NLP in production)
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        matches = []
        for sentence in sentences[:50]:  # Check first 50 sentences
            response = requests.post(
                f"{ENCYPHER_API_URL}/lookup",
                headers=self.headers,
                json={"sentence_text": sentence}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("found"):
                    matches.append(SentenceMatch(
                        sentence=sentence,
                        original_document=data.get("document_title"),
                        original_author=data.get("organization_name"),
                        publication_date=data.get("publication_date"),
                        match_url=data.get("document_url")
                    ))
        
        return matches
    
    def get_usage_stats(self) -> dict:
        """Get current usage statistics."""
        response = requests.get(
            f"{ENCYPHER_API_URL}/account/quota",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["data"]


# === CMS Integration for News Organizations ===

def pre_publish_check(article: dict) -> dict:
    """
    Run before publishing to check for plagiarism.
    
    Returns article with plagiarism_warnings if any found.
    """
    client = ProfessionalEncypherClient()
    
    matches = client.check_for_plagiarism(article["body"])
    
    if matches:
        article["plagiarism_warnings"] = [
            {
                "sentence": m.sentence[:100] + "...",
                "original_source": m.original_document,
                "original_author": m.original_author,
                "url": m.match_url
            }
            for m in matches
        ]
        article["requires_review"] = True
    
    return article


def on_article_publish_pro(article: dict) -> dict:
    """
    Professional tier publish hook with sentence tracking.
    """
    client = ProfessionalEncypherClient()
    
    result = client.sign_with_tracking(
        title=article["title"],
        content=article["body"],
        author=article["author_name"],
        url=article["canonical_url"],
        publication_date=article["publish_date"]
    )
    
    article["encypher_document_id"] = result["document_id"]
    article["signed_body"] = result["signed_text"]
    article["sentences_tracked"] = result.get("total_sentences", 0)
    
    return article
```

### Editor Dashboard Widget

```javascript
// editor-plagiarism-check.js
// Add to your CMS editor

async function checkPlagiarism(content) {
  const response = await fetch('/api/encypher/plagiarism-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  
  const { warnings } = await response.json();
  
  if (warnings.length > 0) {
    showPlagiarismWarnings(warnings);
    return false; // Block publish
  }
  
  return true; // Allow publish
}

function showPlagiarismWarnings(warnings) {
  const modal = document.createElement('div');
  modal.className = 'plagiarism-modal';
  modal.innerHTML = `
    <h2>⚠️ Potential Plagiarism Detected</h2>
    <p>The following sentences match existing published content:</p>
    <ul>
      ${warnings.map(w => `
        <li>
          <blockquote>"${w.sentence}"</blockquote>
          <p>Originally published by <strong>${w.original_author}</strong> 
             in <a href="${w.url}" target="_blank">${w.original_source}</a></p>
        </li>
      `).join('')}
    </ul>
    <button onclick="this.parentElement.remove()">Review & Edit</button>
  `;
  document.body.appendChild(modal);
}
```

---

## Business Tier Integration

**Perfect for:** Large publishers, content networks

### What You Get
- Everything in Professional
- Bulk operations (sign/verify many documents at once)
- Merkle tree indexing (advanced attribution)
- Team management and audit logs

### Integration Example: Bulk Publishing Pipeline

```python
# bulk_publisher.py
"""
Business tier integration with bulk operations.
Perfect for publishing pipelines that handle many articles.
"""
import os
import requests
import uuid
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import time

ENCYPHER_API_URL = "https://api.encypherai.com/api/v1"


class BusinessEncypherClient:
    """Client for Business tier with bulk operations."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ENCYPHER_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def bulk_sign(self, documents: List[Dict]) -> Dict:
        """
        Sign multiple documents in a single API call.
        
        Args:
            documents: List of dicts with 'text' and optional 'metadata'
            
        Returns:
            dict with results for each document
            
        Example:
            results = client.bulk_sign([
                {"text": "Article 1...", "metadata": {"title": "Article 1"}},
                {"text": "Article 2...", "metadata": {"title": "Article 2"}},
            ])
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/batch/sign",
            headers=self.headers,
            json={
                "mode": "c2pa",
                "idempotency_key": f"bulk-sign-{uuid.uuid4().hex}",
                "items": [
                    {
                        "document_id": doc.get("document_id") or f"doc_{uuid.uuid4().hex[:16]}",
                        "text": doc["text"],
                        "title": (doc.get("metadata") or {}).get("title"),
                        "metadata": doc.get("metadata"),
                    }
                    for doc in documents
                ],
            }
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def bulk_verify(self, contents: List[str]) -> Dict:
        """
        Verify multiple documents in a single API call.
        
        NOTE: Batch endpoints require at least 2 documents per request.
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/batch/verify",
            headers=self.headers,
            json={
                "mode": "c2pa",
                "idempotency_key": f"bulk-verify-{uuid.uuid4().hex}",
                "items": [
                    {"document_id": f"doc_{idx}", "text": content}
                    for idx, content in enumerate(contents)
                ],
            }
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def sign_with_merkle(
        self, 
        content: str, 
        metadata: Dict
    ) -> Dict:
        """
        Sign with Merkle tree for advanced attribution.
        
        Merkle trees enable:
        - Efficient proof of any sentence's origin
        - Tamper detection at paragraph level
        - Cryptographic audit trail
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/enterprise/merkle/encode",
            headers=self.headers,
            json={
                "document_id": f"doc_{uuid.uuid4().hex[:16]}",
                "text": content,
                "segmentation_levels": ["sentence"],
                "include_words": False,
                "metadata": metadata,
            }
        )
        response.raise_for_status()
        return response.json()
    
    def list_documents(
        self, 
        page: int = 1, 
        page_size: int = 100,
        status: str = None
    ) -> Dict:
        """List all signed documents with pagination."""
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
            
        response = requests.get(
            f"{ENCYPHER_API_URL}/documents",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]


# === Bulk Publishing Pipeline ===

class BulkPublishingPipeline:
    """
    Pipeline for publishing many articles efficiently.
    
    Usage:
        pipeline = BulkPublishingPipeline()
        results = pipeline.process_batch(articles)
    """
    
    def __init__(self, batch_size: int = 50):
        self.client = BusinessEncypherClient()
        self.batch_size = batch_size
    
    def process_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Process a batch of articles through the signing pipeline.
        """
        results = []
        
        # Process in batches
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            
            # Prepare documents for bulk signing
            documents = [
                {
                    "text": article["body"],
                    "metadata": {
                        "title": article["title"],
                        "author": article["author"],
                        "url": article.get("url"),
                        "category": article.get("category")
                    }
                }
                for article in batch
            ]
            
            # Bulk sign
            sign_results = self.client.bulk_sign(documents)
            
            # Merge results back into articles
            for article, result in zip(batch, sign_results["results"]):
                article["encypher_document_id"] = result["document_id"]
                article["signed_body"] = result["signed_text"]
                article["signing_status"] = result["status"]
                results.append(article)
            
            # Respect rate limits
            time.sleep(0.5)
        
        return results


# === Nightly Batch Job Example ===

def nightly_signing_job():
    """
    Example nightly job to sign all unpublished articles.
    Run via cron: 0 2 * * * python -c "from bulk_publisher import nightly_signing_job; nightly_signing_job()"
    """
    from your_cms import get_unsigned_articles, save_article
    
    pipeline = BulkPublishingPipeline()
    
    # Get articles that need signing
    articles = get_unsigned_articles(limit=1000)
    print(f"Processing {len(articles)} articles...")
    
    # Process in bulk
    results = pipeline.process_batch(articles)
    
    # Save results
    for article in results:
        if article["signing_status"] == "ok":
            save_article(article)
    
    print(f"Signed {len([a for a in results if a['signing_status'] == 'ok'])} articles")
```

---

## Enterprise Tier Integration

**Perfect for:** Media conglomerates, government publishers

### What You Get
- Everything in Business
- BYOK (Bring Your Own Key) - register your public keys (Business+)
- SSO/SAML integration
- Custom C2PA assertion authoring (schemas/templates)
- Unlimited team members
- Dedicated support

### Integration Example: Enterprise with BYOK

```python
# enterprise_publisher.py
"""
Enterprise tier integration with BYOK and custom assertions.
"""
import os
import requests
import uuid
from typing import Dict, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

ENCYPHER_API_URL = "https://api.encypherai.com/api/v1"


class EnterpriseEncypherClient:
    """Client for Enterprise tier with BYOK support."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ENCYPHER_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def register_public_key(
        self, 
        public_key_pem: str, 
        key_name: str,
        algorithm: str = "Ed25519"
    ) -> Dict:
        """
        Register your organization's public key for BYOK.
        
        After registration, you can sign content with your private key
        and Encypher will verify using your registered public key.
        
        Args:
            public_key_pem: PEM-encoded public key
            key_name: Friendly name for the key
            algorithm: Key algorithm (Ed25519, RSA-2048, RSA-4096)
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/byok/public-keys",
            headers=self.headers,
            json={
                "public_key_pem": public_key_pem,
                "key_name": key_name,
                "key_algorithm": algorithm,
            }
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def sign_with_custom_assertions(
        self,
        content: str,
        metadata: Dict,
        custom_assertions: list[Dict]
    ) -> Dict:
        """
        Sign content with custom C2PA assertions.
        
        Custom assertions allow you to embed additional
        verifiable claims in the C2PA manifest.
        
        Args:
            content: Document content
            metadata: Standard metadata
            custom_assertions: Custom claims to embed
            
        Example custom_assertions:
            [
                {"label": "c2pa.training-mining.v1", "data": {"use": {"ai_training": False, "ai_inference": False, "data_mining": False}}}
            ]
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/sign/advanced",
            headers=self.headers,
            json={
                "document_id": f"doc_{uuid.uuid4().hex[:16]}",
                "text": content,
                "segmentation_level": "sentence",
                "metadata": metadata,
                "custom_assertions": custom_assertions,
            }
        )
        response.raise_for_status()
        return response.json()


    def sign_with_template(
        self,
        content: str,
        template_id: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Sign with a server-stored assertion template (Business+)."""
        response = requests.post(
            f"{ENCYPHER_API_URL}/sign/advanced",
            headers=self.headers,
            json={
                "document_id": f"doc_{uuid.uuid4().hex[:16]}",
                "text": content,
                "segmentation_level": "sentence",
                "metadata": metadata,
                "template_id": template_id,
                "validate_assertions": True,
            },
        )
        response.raise_for_status()
        return response.json()


    def sign_with_rights(
        self,
        content: str,
        rights: Dict,
        metadata: Optional[Dict] = None,
        template_id: Optional[str] = None,
    ) -> Dict:
        """Sign with explicit rights metadata (Business+)."""
        payload = {
            "document_id": f"doc_{uuid.uuid4().hex[:16]}",
            "text": content,
            "segmentation_level": "sentence",
            "metadata": metadata,
            "rights": rights,
        }
        if template_id:
            payload["template_id"] = template_id
            payload["validate_assertions"] = True

        response = requests.post(
            f"{ENCYPHER_API_URL}/sign/advanced",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()
    
    def setup_webhook(
        self, 
        url: str, 
        events: list,
        secret: str = None
    ) -> Dict:
        """
        Set up webhook for real-time notifications.
        
        Events:
        - document.signed
        - document.revoked
        - quota.warning
        - key.created
        - key.revoked
        """
        response = requests.post(
            f"{ENCYPHER_API_URL}/webhooks",
            headers=self.headers,
            json={
                "url": url,
                "events": events,
                "secret": secret
            }
        )
        response.raise_for_status()
        return response.json()["data"]


# === BYOK Setup Example ===

def setup_byok():
    """
    One-time setup: Generate and register your organization's key pair.
    
    IMPORTANT: Store the private key securely (HSM, vault, etc.)
    """
    # Generate Ed25519 key pair
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Export keys
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    # Register public key with Encypher
    client = EnterpriseEncypherClient()
    result = client.register_public_key(
        public_key_pem=public_pem,
        key_name="Production Signing Key 2024",
        algorithm="Ed25519"
    )
    
    print(f"Public key registered: {result['id']}")
    print(f"\n⚠️  SAVE THIS PRIVATE KEY SECURELY:\n{private_pem}")
    
    return result


# === Enterprise Publishing Workflow ===

class EnterprisePublisher:
    """
    Full enterprise publishing workflow with editorial assertions.
    """
    
    def __init__(self):
        self.client = EnterpriseEncypherClient()
    
    def publish_with_editorial_review(
        self,
        article: Dict,
        reviewer: str,
        fact_checked: bool = False
    ) -> Dict:
        """
        Publish article with editorial review assertions.
        
        These assertions are cryptographically bound to the content
        and can be verified by anyone.
        """
        custom_assertions = [
            {
                "label": "org.publisher.editorial.v1",
                "data": {
                    "reviewed_by": reviewer,
                    "review_timestamp": article.get("review_date"),
                    "fact_checked": fact_checked,
                    "editorial_standards": "AP Style Guide",
                },
            },
            {
                "label": "org.publisher.provenance.v1",
                "data": {
                    "original_source": article.get("source"),
                    "wire_service": article.get("wire_service"),
                    "embargo_lifted": article.get("embargo_date"),
                },
            },
        ]
        
        result = self.client.sign_with_custom_assertions(
            content=article["body"],
            metadata={
                "title": article["title"],
                "author": article["author"],
                "url": article["url"],
                "publication_date": article["publish_date"]
            },
            custom_assertions=custom_assertions
        )
        
        article["encypher_document_id"] = result["document_id"]
        article["signed_body"] = result["embedded_content"]
        article["assertions"] = custom_assertions
        
        return article

```


### Rights / AI Licensing Templates (Business+)

Business and Enterprise customers can apply **built-in** or **organization-specific** templates to embed licensing signals.

Key request fields:
- `template_id` (optional): apply a built-in or org template
- `rights` (optional): embed explicit publisher rights metadata as `com.encypher.rights.v1`

If your organization has a default template configured, you may omit `template_id` and the server will apply your org default.

Built-in template IDs:
- `tmpl_builtin_all_rights_reserved_v1`
- `tmpl_builtin_no_ai_training_v1`
- `tmpl_builtin_rag_allowed_with_attribution_v1`
- `tmpl_builtin_realtime_quotes_with_attribution_v1`
- `tmpl_builtin_cc_by_4_0_v1`
- `tmpl_builtin_cc_by_nc_4_0_v1`
- `tmpl_builtin_academic_open_access_v1`
- `tmpl_builtin_news_wire_syndication_v1`

Example: basic signing with a template (`/sign`):

```python
response = requests.post(
    f"{ENCYPHER_API_URL}/sign",
    headers=headers,
    json={
        "text": content,
        "document_type": "article",
        "template_id": "tmpl_builtin_news_wire_syndication_v1",
        "validate_assertions": True,
    },
)
response.raise_for_status()
```

Example: advanced signing with explicit rights metadata (`/sign/advanced`):

```python
response = requests.post(
    f"{ENCYPHER_API_URL}/sign/advanced",
    headers=headers,
    json={
        "document_id": f"doc_{uuid.uuid4().hex[:16]}",
        "text": content,
        "segmentation_level": "sentence",
        "rights": {
            "copyright_holder": "Example Publisher",
            "license_url": "https://example.com/license",
            "usage_terms": "RAG allowed with attribution.",
            "syndication_allowed": True,
            "contact_email": "licensing@example.com",
        },
    },
)
response.raise_for_status()
```

### Verifier Output: Rights Signals

When rights signals are present in the manifest, `/verify` returns them under:
- `data.details.rights_signals.training_mining` (from `c2pa.training-mining.v1`)
- `data.details.rights_signals.rights` (from `com.encypher.rights.v1`)

### Multi-Embedding Verification (Enterprise Feature)

**For pages with sentence-level embeddings or multiple signed sections:**

```python
def verify_entire_page(page_content: str) -> dict:
    """
    Verify an entire page that may contain multiple embeddings.
    
    The API automatically detects all embeddings and verifies each one.
    Perfect for:
    - Enterprise sentence-level signed content
    - Pages with multiple articles
    - Content aggregation from multiple sources
    """
    client = EnterpriseEncypherClient()
    
    # Send entire page content - API handles multiple embeddings automatically
    result = client.verify_content(page_content)
    
    if result.get("embeddings_found", 0) > 1:
        print(f"Found {result['embeddings_found']} embeddings")
        
        # Check each embedding individually
        for embedding in result.get("all_embeddings", []):
            print(f"Embedding {embedding['index']}: {embedding['signer_name']}")
            print(f"  Valid: {embedding['valid']}")
            print(f"  Text: {embedding['clean_text'][:100]}...")
        
        # Overall status
        all_valid = result.get("valid", False)
        if all_valid:
            print("✓ All embeddings verified successfully")
        else:
            print("⚠ Some embeddings failed verification")
    else:
        # Single embedding
        print(f"Single embedding: {result.get('signer_name')}")
        print(f"Valid: {result.get('valid')}")
    
    return result


# Example: Verify article with sentence-level embeddings
article_html = fetch_article_from_cms(article_id)
article_text = extract_text_from_html(article_html)

verification = verify_entire_page(article_text)

# Display verification badges for each verified section
if verification.get("embeddings_found", 0) > 1:
    for embedding in verification["all_embeddings"]:
        if embedding["valid"]:
            # Show badge for this text section
            display_verification_badge(
                text_span=embedding["text_span"],
                signer=embedding["signer_name"]
            )
```

**Benefits:**
- **Single API call** verifies entire page (no need for batch endpoint)
- **Automatic detection** of all C2PA embeddings
- **Individual results** for each embedding with text spans
- **Efficient** for Enterprise sentence-level verification

---

## Webhook Integration

Set up webhooks to receive real-time notifications when events occur.

### Webhook Events

| Event | Description | Payload |
|-------|-------------|---------|
| `document.signed` | Document was signed | `document_id`, `title`, `verification_url` |
| `document.revoked` | Document was revoked | `document_id`, `reason` |
| `quota.warning` | Usage at 80%+ | `metric`, `used`, `limit`, `percentage` |
| `key.created` | New API key created | `key_id`, `key_name` |
| `key.revoked` | API key revoked | `key_id` |

### Webhook Handler Example

```python
# webhook_handler.py
"""
Example webhook handler for your CMS.
"""
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = os.environ.get("ENCYPHER_WEBHOOK_SECRET")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature."""
    if not WEBHOOK_SECRET:
        return True  # Skip if no secret configured
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@app.route("/webhooks/encypher", methods=["POST"])
def handle_webhook():
    # Webhook payload is JSON.
    event = request.json
    event_type = event.get("event")
    
    if event_type == "document.signed":
        handle_document_signed(event["data"])
    elif event_type == "document.revoked":
        handle_document_revoked(event["data"])
    elif event_type == "quota.warning":
        handle_quota_warning(event["data"])
    
    return jsonify({"received": True}), 200


def handle_document_signed(data: dict):
    """Update CMS when document is signed."""
    document_id = data["document_id"]
    # Update your database, send notifications, etc.
    print(f"Document signed: {document_id}")


def handle_document_revoked(data: dict):
    """Handle document revocation."""
    document_id = data["document_id"]
    # Remove verification badge, notify editors, etc.
    print(f"Document revoked: {document_id}")


def handle_quota_warning(data: dict):
    """Alert when approaching quota limits."""
    metric = data["metric"]
    percentage = data["percentage"]
    # Send alert to admin
    print(f"⚠️ Quota warning: {metric} at {percentage}%")
```

---

## Error Handling

### Common Errors

```python
# error_handling.py

class EncypherError(Exception):
    """Base exception for Encypher API errors."""
    pass

class RateLimitError(EncypherError):
    """Too many requests."""
    pass

class QuotaExceededError(EncypherError):
    """Monthly quota exceeded."""
    pass

class AuthenticationError(EncypherError):
    """Invalid or expired API key."""
    pass


def handle_api_response(response):
    """Handle API response and raise appropriate errors."""
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", 60)
        raise RateLimitError(f"Rate limited. Retry after {retry_after}s")
    
    if response.status_code == 403:
        error = response.json().get("error", {})
        if "quota" in str(error).lower() or "limit" in str(error).lower():
            raise QuotaExceededError("Monthly quota exceeded. Upgrade your plan.")
        raise AuthenticationError("Access denied. Check your API key.")
    
    if response.status_code == 401:
        raise AuthenticationError("Invalid API key.")
    
    response.raise_for_status()
    return response.json()
```

---

## Best Practices

### 1. Store Document IDs
Always store the `document_id` returned from signing. You'll need it for:
- Verification links
- Revocation
- Audit trails

### 2. Use Webhooks for Real-Time Updates
Don't poll the API. Set up webhooks to receive instant notifications.

### 3. Implement Retry Logic
```python
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator
```

### 4. Cache Verification Results
Verification results don't change. Cache them to reduce API calls.

### 5. Use Bulk Operations
If you're on Business tier or higher, always use bulk endpoints for multiple documents.

---

## Need Help?

- **Documentation:** https://docs.encypherai.com
- **API Reference:** https://api.encypherai.com/docs
- **Support:** support@encypherai.com
- **Enterprise Support:** enterprise@encypherai.com (24/7 for Enterprise tier)
