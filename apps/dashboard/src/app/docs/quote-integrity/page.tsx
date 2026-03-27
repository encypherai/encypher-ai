import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from '../publisher-integration/PublisherIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# Quote Integrity Verification Guide

Encypher's Quote Integrity Verification lets you check whether a quoted passage accurately represents the original signed content. This is essential for detecting AI hallucinations, misattributions, and manipulated quotes.

## Use Cases

- **Journalists**: verify that a quote attributed to a source matches the signed original
- **AI companies**: confirm that RAG outputs faithfully represent source material
- **Legal teams**: prove that quoted evidence has not been altered
- **Fact-checkers**: detect paraphrased or fabricated attributions

## How It Works

1. A publisher signs their content with Encypher (the original is stored in the provenance database)
2. Someone quotes or paraphrases that content
3. You submit the claimed quote and the attributed source to the Quote Integrity endpoint
4. Encypher checks the quote against the Merkle tree of the original document
5. You receive a verdict: **accurate**, **approximate**, **hallucinated**, or **unverifiable**

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **accurate** | The quote exactly matches a passage in the signed original |
| **approximate** | The quote is a close paraphrase (similarity above threshold) |
| **hallucinated** | The quote does not appear in the signed document at all |
| **unverifiable** | The attributed source document could not be found |

## API Reference

### POST /api/v1/verify/quote-integrity

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/verify/quote-integrity \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "claimed_quote": "Scientists at CERN detected high-energy particles from a distant galaxy",
    "attributed_source_id": "doc_abc123xyz"
  }'
\`\`\`

### Response

\`\`\`json
{
  "success": true,
  "data": {
    "verdict": "accurate",
    "confidence": 0.97,
    "best_matching_segment": "Scientists at CERN have detected high-energy particles originating from a distant galaxy.",
    "similarity_score": 0.97,
    "document_id": "doc_abc123xyz",
    "document_title": "CERN Cosmic Ray Discovery",
    "signer_organization": "Reuters",
    "signed_at": "2026-02-20T15:30:00Z"
  }
}
\`\`\`

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| \`claimed_quote\` | string | Yes | The quote to verify |
| \`attributed_source_id\` | string | No | Document ID of the alleged source |
| \`attributed_source_url\` | string | No | URL of the alleged source (alternative to ID) |
| \`similarity_threshold\` | number | No | Minimum similarity for "approximate" (default: 0.7) |

At least one of \`attributed_source_id\` or \`attributed_source_url\` should be provided. If neither is given, Encypher searches the full provenance database.

## Python SDK

\`\`\`python
from encypher import Encypher

client = Encypher(api_key="YOUR_API_KEY")

result = client.verify_quote_integrity(
    claimed_quote="Scientists at CERN detected high-energy particles from a distant galaxy",
    attributed_source_id="doc_abc123xyz",
)

print(f"Verdict: {result.verdict}")       # accurate / approximate / hallucinated / unverifiable
print(f"Confidence: {result.confidence}")  # 0.0 - 1.0
print(f"Best match: {result.best_matching_segment}")
\`\`\`

## Integration Examples

### Fact-Checking Pipeline

\`\`\`python
from encypher import Encypher

client = Encypher(api_key="YOUR_API_KEY")

# Check multiple quotes in an article
quotes = [
    {"text": "Revenue grew 15% year-over-year", "source_id": "doc_earnings_q4"},
    {"text": "CEO announced major restructuring", "source_id": "doc_press_release"},
]

for quote in quotes:
    result = client.verify_quote_integrity(
        claimed_quote=quote["text"],
        attributed_source_id=quote["source_id"],
    )
    status = "PASS" if result.verdict in ("accurate", "approximate") else "FAIL"
    print(f"[{status}] \\"{quote['text'][:50]}...\\" -> {result.verdict} ({result.confidence:.0%})")
\`\`\`

### RAG Output Verification

\`\`\`python
# After your RAG pipeline generates a response with citations:
for citation in rag_response.citations:
    result = client.verify_quote_integrity(
        claimed_quote=citation.text,
        attributed_source_id=citation.document_id,
    )
    if result.verdict == "hallucinated":
        flag_for_review(citation)
\`\`\`

## Verdict Logic

| Similarity Score | Verdict | Confidence |
|-----------------|---------|------------|
| >= 0.95 | accurate | high |
| 0.70 - 0.95 | approximate | medium |
| < threshold | hallucinated | high |
| No signed content found | unverifiable | low |

## Authentication

This endpoint requires an API key. Include your key in the \`Authorization\` header or as an \`X-API-Key\` header.

## Testing in the Playground

You can test Quote Integrity Verification in the [API Playground](/playground):

1. Select the **Verify Quote Integrity** endpoint from the sidebar
2. Enter a claimed quote and the source document ID
3. Click **Send Request** to see the verdict

## Limitations

- The source document must have been signed with Encypher
- Very short quotes (under 10 words) may produce lower confidence scores
- The similarity algorithm uses fuzzy matching, not exact string comparison
- Rate limits apply: 100 requests/minute on Professional, 1000/minute on Enterprise

## Support

For integration help, contact support@encypher.com or test interactively in the [API Playground](/playground).
`;

export default function QuoteIntegrityGuidePage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
      </div>
    </DashboardLayout>
  );
}
