import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from '../publisher-integration/PublisherIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# Coalition & Licensing Guide

Encypher's Coalition model lets publishers collectively license content to AI companies. This guide covers how the coalition works, how licensing deals flow, and how to manage your revenue share.

## How the Coalition Works

The Encypher Publisher Coalition pools participating publishers' content into a single licensing entity that negotiates deals with AI companies on behalf of all members.

| Model | Revenue split | Negotiation | Best for |
|-------|---------------|-------------|----------|
| **Coalition** | 60% publisher / 40% Encypher | Encypher negotiates | Publishers who want hands-off licensing |
| **Self-service** | 80% publisher / 20% Encypher | Publisher negotiates directly | Large publishers with legal teams |

## Joining the Coalition

Coalition membership is opt-in at the organization level. To join:

1. Navigate to **Billing > Coalition** in the Dashboard
2. Review the coalition terms
3. Click **Join Coalition**
4. Set your payout account (Stripe Connect)

Or via the API:

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/billing/coalition/join \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

## Licensing Tiers

Your rights profile defines what AI companies can license. The three tiers map to different use cases:

### Bronze (Scraping / Crawling)

Covers search indexing, price comparison, and web archiving. Most publishers allow this with attribution requirements.

### Silver (RAG / Retrieval)

Covers AI-powered search, retrieval-augmented generation, and summarization pipelines. This is the most common licensing tier.

### Gold (Training / Fine-tuning)

Covers use of your content for model training and fine-tuning. The highest-value tier, typically requires explicit licensing.

## Licensing Flow

### Inbound Requests

When an AI company wants to license your content:

1. They submit a licensing request via the Encypher platform
2. You receive a notification (email + dashboard)
3. Review the request in **Rights > Licensing**
4. Approve, counter, or reject

\`\`\`bash
# List pending requests
curl https://api.encypher.com/api/v1/rights-licensing/requests \\
  -H "Authorization: Bearer YOUR_API_KEY"

# Approve a request
curl -X PUT https://api.encypher.com/api/v1/rights-licensing/requests/{request_id}/respond \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"action": "approve"}'
\`\`\`

### Agreements

Once approved, a licensing agreement is automatically generated:

\`\`\`bash
# List active agreements
curl https://api.encypher.com/api/v1/rights-licensing/agreements \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

Each agreement includes:
- **Tier**: which use case is licensed
- **Scope**: specific content or entire catalog
- **Terms**: duration, renewal, usage limits
- **Status**: active, expired, or terminated

## Revenue & Payouts

### Tracking Earnings

View your coalition earnings in the Dashboard under **Billing > Coalition**, or via API:

\`\`\`bash
curl https://api.encypher.com/api/v1/billing/coalition \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

Response:

\`\`\`json
{
  "member": true,
  "publisher_share_percent": 60,
  "total_content": 1250,
  "total_earnings": 4500.00,
  "pending_earnings": 750.00,
  "last_payout_date": "2026-01-15",
  "earnings_history": [
    {"period": "2026-01", "amount": 1500.00, "status": "paid"},
    {"period": "2026-02", "amount": 750.00, "status": "pending"}
  ]
}
\`\`\`

### Payout Schedule

- Payouts are processed monthly on the 15th
- Minimum payout threshold: $50
- Funds are deposited to your connected Stripe account
- Detailed statements available in **Billing > Invoices**

## Opting Out

You can leave the coalition at any time. Existing agreements will be honored through their term, but no new coalition deals will include your content:

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/billing/coalition/opt-out \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

After opting out, you can still manage self-service licensing deals directly (80/20 split).

## Formal Notices

If your content is used without a license, you can issue formal notices with cryptographic proof:

1. Go to **Rights > Notices** in the Dashboard
2. Click **+ New Notice**
3. Specify the violating entity and violation type
4. Deliver the notice to generate a court-ready evidence package

See the [Publisher Integration Guide](/docs/publisher-integration) for detailed notice API examples.

## FAQ

**Q: Can I be in the coalition and also negotiate direct deals?**
A: Yes. Coalition deals cover the "default" licensing path. You can always negotiate direct deals with specific AI companies at different terms.

**Q: What happens to my content if I leave the coalition?**
A: Existing agreements are honored through their expiry date. Your content is removed from future coalition offers.

**Q: How are earnings calculated?**
A: Earnings are based on the number of licensed content items, the tier, and the deal value. You receive your share (60% coalition / 80% self-service) of the per-item licensing fee.

## Support

For coalition and licensing questions, contact partnerships@encypher.com or visit the [Rights Management](/rights) dashboard.
`;

export default function CoalitionGuidePage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
      </div>
    </DashboardLayout>
  );
}
