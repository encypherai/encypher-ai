import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from './PublisherIntegrationGuideClient';

// Skip static generation - this page reads from filesystem which isn't available in isolated builds
export const dynamic = 'force-dynamic';

// Inline guide content for production builds where filesystem access is limited
const GUIDE_CONTENT = `# Publisher Integration Guide

This guide covers integrating Encypher's content provenance and rights management APIs into your publishing workflow.

## Overview

Encypher provides cryptographic content attribution that:
- Embeds invisible provenance markers in your text
- Survives copy-paste and distribution
- Enables formal notice to AI companies with cryptographic proof
- Creates court-admissible proof of ownership
- Lets you define machine-readable licensing terms (Bronze/Silver/Gold tiers)

## Quick Start

1. **Get API Key**: Visit the [API Keys](/api-keys) page to create your key
2. **Install SDK**: \`pip install encypher-ai\` or use our REST API
3. **Set Rights Profile**: Define your licensing terms once (5 minutes)
4. **Sign Content**: Call the \`/sign\` endpoint with \`use_rights_profile: true\`
5. **Verify Content**: Use \`/verify\` to check provenance

---

## Rights Management

Encypher's rights management system lets you define licensing terms for three use cases:

| Tier | Use Case | Examples |
|------|----------|---------|
| **Bronze** | Scraping / crawling | Allowed/disallowed crawlers, attribution requirements |
| **Silver** | RAG / retrieval / search | Conditions for AI-powered search and summarization |
| **Gold** | Training / fine-tuning | Conditions for model training on your content |

### Step 1: Set Your Rights Profile

\`\`\`bash
curl -X PUT https://api.encypherai.com/api/v1/rights/profile \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "bronze_tier": {
      "permitted": true,
      "requires_attribution": true,
      "attribution_format": "Cite: {publisher_name} ({url})"
    },
    "silver_tier": {
      "permitted": true,
      "requires_attribution": true,
      "commercial_use_requires_license": false
    },
    "gold_tier": {
      "permitted": false,
      "contact_for_licensing": "licensing@yourpublication.com"
    }
  }'
\`\`\`

Or start from a template:

\`\`\`bash
# List available templates
curl https://api.encypherai.com/api/v1/rights/templates \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Apply a template (e.g., "news_publisher_standard")
curl -X POST https://api.encypherai.com/api/v1/rights/profile/from-template/news_publisher_standard \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

### Step 2: Sign Content with Rights

\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/sign \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Your article text here...",
    "title": "Article Title",
    "options": {
      "use_rights_profile": true
    }
  }'
\`\`\`

The response will include a \`rights_resolution_url\` — a public endpoint embedded into the signed content that any AI system can call to discover your licensing terms.

\`\`\`json
{
  "success": true,
  "document_id": "doc_abc123xyz",
  "signed_text": "Your article text here...",
  "rights_resolution_url": "https://api.encypherai.com/api/v1/public/rights/doc_abc123xyz"
}
\`\`\`

### Step 3: Anyone Can Discover Your Rights

AI companies, search engines, and scrapers can call the public rights endpoint — no API key required:

\`\`\`bash
curl https://api.encypherai.com/api/v1/public/rights/doc_abc123xyz
\`\`\`

Or get machine-readable formats:
- **JSON-LD**: \`GET /api/v1/public/rights/doc_abc123xyz/json-ld\`
- **W3C ODRL**: \`GET /api/v1/public/rights/doc_abc123xyz/odrl\`
- **RSL 1.0 XML**: \`GET /api/v1/public/rights/organization/{org_id}/rsl\`
- **robots.txt additions**: \`GET /api/v1/public/rights/organization/{org_id}/robots-txt\`

---

## Formal Notices

When AI companies scrape or use your content without a license, Encypher lets you send cryptographically-provable formal notices that eliminate the "innocent infringement" defense.

\`\`\`bash
# Create a notice
curl -X POST https://api.encypherai.com/api/v1/notices/create \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "recipient_entity": "AI Company Inc.",
    "recipient_contact": "legal@aicompany.com",
    "document_ids": ["doc_abc123xyz"],
    "violation_type": "unauthorized_training",
    "notice_text": "This content was used for AI training without authorization."
  }'

# Deliver the notice
curl -X POST https://api.encypherai.com/api/v1/notices/{notice_id}/deliver \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Get court-ready evidence package
curl https://api.encypherai.com/api/v1/notices/{notice_id}/evidence \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

---

## API Endpoints

### Sign Content
\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/sign \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Your article text here...", "options": {"use_rights_profile": true}}'
\`\`\`

### Verify Content
\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/verify \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"content": "Text to verify..."}'
\`\`\`

---

## Python SDK

\`\`\`python
from encypher import Encypher

client = Encypher(api_key="YOUR_API_KEY")

# Sign content with rights profile attached
result = client.sign(
    "Your article text here...",
    options={"use_rights_profile": True}
)
signed_text = result.embedded_text
rights_url = result.rights_resolution_url

# Verify content
verification = client.verify(signed_text)
print(f"Verified: {verification.is_valid}")
print(f"Signer: {verification.signer_name}")
\`\`\`

---

## WordPress Integration

Install our WordPress plugin for automatic content signing:

1. Download from the WordPress plugin directory
2. Activate and enter your API key in Settings > Encypher
3. Enable **Attach Rights Profile** to automatically embed your licensing terms
4. All new posts will be automatically signed with rights metadata

---

## Support

For detailed integration support, contact us at support@encypherai.com or visit the [Support](/support) page.
`;

export default function PublisherIntegrationGuidePage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
      </div>
    </DashboardLayout>
  );
}
