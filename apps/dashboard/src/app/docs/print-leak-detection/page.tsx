import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from '../publisher-integration/PublisherIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# Print Leak Detection

Print Leak Detection is an Enterprise-tier signing option that embeds an imperceptible spacing fingerprint into signed content. The fingerprint survives printing and high-quality scanning, letting you identify which digital copy was the source of a leaked physical document.

## The Problem

When you distribute signed articles, press proofs, board documents, or investor updates as PDFs or printed copies, the standard invisible Unicode watermarks (ZWC embeddings) are stripped out - once a document is printed and scanned, the cryptographic chain is lost.

**Print Leak Detection adds a complementary channel** that encodes a compact identifier directly into the letter spacing of the text. If a copy leaks, you scan it, run OCR, and submit the result to the verify endpoint. The fingerprint tells you the exact source document.

## How It Works

At signing time, the API replaces selected regular spaces (U+0020) between words with Unicode Thin Spaces (U+2009). Thin spaces are approximately 5/18 em wide — visually indistinguishable from regular spaces but measurably different in high-quality typesetting.

- **0-bit**: Regular space (U+0020) — unchanged
- **1-bit**: Thin space (U+2009) — replaces a regular space

A 16-byte (128-bit) HMAC-SHA256 fingerprint is encoded across the first 128 inter-word spaces. This fingerprint is deterministic: the same organisation + document always produces the same value, so you can verify authenticity offline.

## Survivability

| Scenario | Fingerprint survives? |
|---|---|
| PDF copy-paste | Yes - Unicode spaces preserved |
| High-quality OCR (Unicode-aware) | Yes - thin spaces retained |
| Print -> scan -> OCR (high DPI) | Yes - measurable letter spacing difference |
| Standard OCR (ASCII normalisation) | Partial - depends on OCR quality |
| Aggressive whitespace normalisation | No - all spaces collapsed to single space |
| ZWC stripping | Yes - orthogonal channel, not affected |

## Minimum Content Length

The fingerprint requires at least **128 inter-word spaces** (roughly 130+ words). For shorter texts the API returns the content unmodified with no error raised. The \`print_fingerprint.enabled\` field in the response will be \`false\` if the text was too short.

## API Usage

Enable Print Leak Detection by adding \`enable_print_fingerprint: true\` to the \`options\` object when signing:

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/sign \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Your article text here...",
    "document_title": "Q4 Investor Update",
    "options": {
      "segmentation_level": "sentence",
      "enable_print_fingerprint": true
    }
  }'
\`\`\`

The response includes a \`print_fingerprint\` object:

\`\`\`json
{
  "data": {
    "document": {
      "document_id": "doc-abc123",
      "signed_text": "Your article with invisible spacing...",
      "print_fingerprint": {
        "enabled": true,
        "payload_hex": "a3f9c2e1b4d8f07e..."
      }
    }
  }
}
\`\`\`

### Python SDK Example

\`\`\`python
import httpx

response = httpx.post(
    "https://api.encypher.com/api/v1/sign",
    headers={"X-API-Key": "YOUR_API_KEY"},
    json={
        "text": article_text,
        "document_title": "Q4 Investor Update",
        "options": {
            "segmentation_level": "sentence",
            "enable_print_fingerprint": True,
        },
    },
)

data = response.json()["data"]["document"]
payload_hex = data["print_fingerprint"]["payload_hex"]
print(f"Fingerprint: {payload_hex}")
\`\`\`

## Detection Flow

When a document is suspected to have leaked:

1. **Scan** the physical document at high resolution (300+ DPI).
2. **Run OCR** using a Unicode-aware engine (e.g. Tesseract with \`--oem 1\` or Google Cloud Vision).
3. **Submit the OCR'd text** to the verify endpoint:

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/verify/advanced \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "<OCR output here>"}'
\`\`\`

4. **Check the \`print_fingerprint\` field** in the response:

\`\`\`json
{
  "print_fingerprint": {
    "detected": true,
    "payload_hex": "a3f9c2e1b4d8f07e..."
  }
}
\`\`\`

5. **Cross-reference** \`payload_hex\` against your signing records to identify the source document and recipient.

The \`payload_hex\` is an HMAC-SHA256 of your org ID and document ID - you can verify it independently:

\`\`\`python
import hashlib, hmac

def verify_payload(org_id: str, document_id: str, payload_hex: str) -> bool:
    key = org_id.encode()
    msg = document_id.encode()
    expected = hmac.new(key, msg, hashlib.sha256).digest()[:16].hex()
    return expected == payload_hex
\`\`\`

## Limitations

- **Minimum length**: Requires at least ~130 words (128 inter-word spaces). Shorter texts are signed without the fingerprint.
- **Whitespace normalisation**: Any tool that collapses all spaces to U+0020 will erase the fingerprint. This includes many HTML renderers, plain-text email clients, and some CMS systems.
- **OCR quality**: Low-quality scans or OCR engines that normalise Unicode spaces will lose the signal.
- **Not a replacement for ZWC embeddings**: Print Leak Detection is a complementary channel for physical-copy scenarios. Digital verification still relies on the ZWC embedding.

## Tier

Print Leak Detection requires an **Enterprise** plan. Setting \`enable_print_fingerprint: true\` on a Free-tier key returns a \`403 Forbidden\` response.
`;

export default function PrintLeakDetectionPage() {
  return (
    <DashboardLayout>
      <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
    </DashboardLayout>
  );
}
