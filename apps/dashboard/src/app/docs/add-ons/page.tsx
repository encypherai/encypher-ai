import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from '../publisher-integration/PublisherIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# Add-Ons Overview

Encypher add-ons extend the free signing infrastructure with professional tools for branding, compliance, and scale. Each add-on is self-service -- purchase from your dashboard Billing page, no sales call required.

---

## Custom Signing Identity

**$20/mo** | Category: Infrastructure

Replace the default "Encypher Coalition Member" signer label with your verified organization name on all signed content and verification pages.

### What changes

- Signed documents display your organization name as the signer identity
- Verification pages show your brand instead of the generic coalition label
- API responses include your custom identity in the signer metadata

### How to configure

1. Purchase the Custom Signing Identity add-on from **Settings > Billing**
2. Go to **Settings > Organization** and set your preferred signing identity
3. Choose from: organization name, organization + author, or a fully custom label
4. All new documents will use the updated identity

---

## White-Label Verification

**$299/mo** | Category: Infrastructure | Requires: Custom Signing Identity

Remove all Encypher branding from public-facing verification pages. Your readers see your brand, not ours.

### What changes

- Verification portal footer shows "Verified by [Your Organization]" instead of "Verified by Encypher Verification Service"
- API responses remain unchanged (branding is visual only)
- Requires Custom Signing Identity add-on (purchased separately or via the Publisher Identity bundle)

### How it works

When enabled, the \`whitelabel\` feature flag is set on your organization. The verification portal checks this flag and renders your organization display name in place of Encypher branding.

---

## BYOK (Bring Your Own Keys)

**$499/mo** | Category: Infrastructure

Sign content using your own Ed25519 or ECDSA P-256 key pairs. Full key custody with independent verification capability.

For detailed setup instructions, key generation, and API usage, see the dedicated **[BYOK Guide](/docs/byok)**.

### Key benefits

- Regulatory compliance -- maintain key custody for data sovereignty
- Independent verification -- third parties verify without querying Encypher servers
- Key rotation -- manage your own key lifecycle and revocation
- On-premise signing -- generate signatures in your infrastructure

---

## Priority Support

**$199/mo** | Category: Operations

Dedicated support channel with guaranteed response times and onboarding assistance.

### SLA details

| Metric | Commitment |
|--------|------------|
| Initial response | 4 hours during business hours (Mon-Fri, 9am-6pm ET) |
| Critical issues | Same business day |
| Onboarding | Dedicated session within 48 hours of purchase |

### How to contact

After purchasing, you will receive an email with your dedicated support address. Priority tickets are routed ahead of the general queue and handled by senior engineers.

---

## Bulk Archive Backfill

**$0.01/document** | Category: Operations | One-time purchase

Sign your entire content archive in a single batch operation. Ideal for publishers with years of existing articles that need provenance protection.

### How it works

1. Purchase the Bulk Archive Backfill from **Settings > Billing**, specifying the number of documents
2. The add-on unlocks the batch signing endpoint (\`POST /api/v1/batch/sign\`) for your organization
3. Submit documents in batches of up to 100 per request
4. Each document gets full C2PA signing with Unicode embeddings

### WordPress integration

If you use the Encypher WordPress plugin, the backfill can be triggered from **WP Admin > Encypher > Backfill**. The plugin iterates through your published posts and signs them automatically.

### Pricing example

| Archive size | Cost |
|-------------|------|
| 1,000 articles | $10 |
| 10,000 articles | $100 |
| 50,000 articles | $500 |
`;

export default function AddOnsDocsPage() {
  return (
    <DashboardLayout>
      <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
    </DashboardLayout>
  );
}
