import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from './PublisherIntegrationGuideClient';

// Skip static generation - this page reads from filesystem which isn't available in isolated builds
export const dynamic = 'force-dynamic';

// Inline guide content for production builds where filesystem access is limited
const GUIDE_CONTENT = `# Publisher Integration Guide

This guide covers integrating Encypher's content provenance API into your publishing workflow.

## Overview

Encypher provides cryptographic content attribution that:
- Embeds invisible provenance markers in your text
- Survives copy-paste and distribution
- Enables formal notice to AI companies
- Creates court-admissible proof of ownership

## Quick Start

1. **Get API Key**: Visit the [API Keys](/api-keys) page to create your key
2. **Install SDK**: \`pip install encypher-ai\` or use our REST API
3. **Sign Content**: Call the \`/sign\` endpoint with your text
4. **Verify Content**: Use \`/verify\` to check provenance

## API Endpoints

### Sign Content
\`\`\`bash
curl -X POST https://api.encypherai.com/v1/sign \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"content": "Your article text here..."}'
\`\`\`

### Verify Content
\`\`\`bash
curl -X POST https://api.encypherai.com/v1/verify \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"content": "Text to verify..."}'
\`\`\`

## Python SDK

\`\`\`python
from encypher import Encypher

client = Encypher(api_key="YOUR_API_KEY")

# Sign content
result = client.sign("Your article text here...")
signed_text = result.embedded_text

# Verify content
verification = client.verify(signed_text)
print(f"Verified: {verification.is_valid}")
print(f"Signer: {verification.signer_name}")
\`\`\`

## WordPress Integration

Install our WordPress plugin for automatic content signing:

1. Download from the WordPress plugin directory
2. Activate and enter your API key in Settings > Encypher
3. All new posts will be automatically signed

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
