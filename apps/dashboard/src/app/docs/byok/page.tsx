import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from '../publisher-integration/PublisherIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# Bring Your Own Key (BYOK) Guide

Encypher supports Bring Your Own Key (BYOK), allowing Enterprise customers to sign content using their own Ed25519 key pairs. This gives you full custody of signing keys and the ability to prove provenance independently of the Encypher platform.

## When to Use BYOK

- **Regulatory compliance**: Your organization requires key custody for data sovereignty.
- **Independent verification**: You want third parties to verify content without querying Encypher servers.
- **Key rotation**: You manage your own key lifecycle and revocation.
- **On-premise signing**: You generate signatures in your own infrastructure and only use Encypher for embedding.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Plan | Enterprise tier |
| Key type | Ed25519 (recommended) or ECDSA P-256 |
| Format | PEM-encoded public key |
| Dashboard access | Admin role on your organization |

## Step 1: Generate Your Ed25519 Key Pair

\`\`\`bash
# Generate private key (keep this secret!)
openssl genpkey -algorithm Ed25519 -out encypher_private.pem

# Extract public key
openssl pkey -in encypher_private.pem -pubout -out encypher_public.pem

# View the public key
cat encypher_public.pem
\`\`\`

## Step 2: Register Your Public Key

Register the public half with Encypher so we can embed it into signed manifests:

\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/admin/public-keys \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\\nMCowBQYDK2VwAyEA...\\n-----END PUBLIC KEY-----",
    "key_name": "Production signing key",
    "key_algorithm": "Ed25519"
  }'
\`\`\`

Response:

\`\`\`json
{
  "success": true,
  "data": {
    "key_id": "key_abc123",
    "key_name": "Production signing key",
    "fingerprint": "SHA256:abc123...",
    "algorithm": "Ed25519",
    "created_at": "2026-02-21T00:00:00Z"
  }
}
\`\`\`

You can also register keys from the Dashboard: **Settings > API Keys > Public Keys**.

## Step 3: Sign Content with Your Key

When calling the \`/sign\` endpoint, pass \`byok: true\` and provide the signature you generated locally:

\`\`\`python
from encypher import Encypher
import nacl.signing

# Load your private key
with open("encypher_private.pem", "rb") as f:
    signing_key = nacl.signing.SigningKey(f.read())

client = Encypher(api_key="YOUR_API_KEY")

# Sign content — the SDK handles local signing + remote embedding
result = client.sign(
    text="Your article text here...",
    byok=True,
    signing_key=signing_key,
)
\`\`\`

Or via the REST API:

\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/sign \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Your article text here...",
    "options": {
      "byok": true,
      "key_id": "key_abc123",
      "signature": "base64-encoded-signature"
    }
  }'
\`\`\`

## Step 4: Verify BYOK Content

Verification works the same way. Encypher checks the embedded signature against your registered public key:

\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/verify \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Signed text to verify..."}'
\`\`\`

The response includes \`signer_name\` and \`key_id\` so you can confirm which key was used.

## Key Rotation

To rotate keys without downtime:

1. Generate a new key pair
2. Register the new public key (both old and new are active simultaneously)
3. Switch your signing infrastructure to the new private key
4. Revoke the old public key once all in-flight content is signed

\`\`\`bash
# Revoke the old key
curl -X DELETE https://api.encypherai.com/api/v1/admin/public-keys/key_old123 \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

## Listing Your Keys

\`\`\`bash
curl https://api.encypherai.com/api/v1/admin/public-keys \\
  -H "Authorization: Bearer YOUR_API_KEY"
\`\`\`

## Security Best Practices

- **Never share your private key.** Only the public key is registered with Encypher.
- **Use hardware security modules (HSMs)** for production private key storage.
- **Rotate keys** at least annually or after any suspected compromise.
- **Monitor key usage** via the Dashboard analytics to detect anomalous signing activity.
- **Separate environments**: use different key pairs for staging and production.

## Support

For BYOK integration support, contact your account manager or email enterprise@encypherai.com.
`;

export default function ByokGuidePage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
      </div>
    </DashboardLayout>
  );
}
