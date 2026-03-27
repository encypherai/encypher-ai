import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from '../publisher-integration/PublisherIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# Streaming LLM Signing Guide

Sign AI-generated text in real-time as it streams from language models. Encypher's streaming mode embeds invisible provenance markers into each chunk so that AI output is attributable from the moment it reaches the user.

## Why Streaming Signing?

| Traditional signing | Streaming signing |
|---------------------|-------------------|
| Sign after full text is generated | Sign each chunk as it arrives |
| User sees unsigned text first | Every chunk is signed |
| Single document ID | Per-chunk manifests with session ID |
| Higher latency | Sub-millisecond overhead per chunk |

Streaming signing is ideal for:

- **Chatbots and assistants**: prove which model produced each response
- **Real-time content generation**: sign articles as they are drafted by AI
- **Compliance pipelines**: ensure all AI output is attributable before delivery

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Plan | Professional or Enterprise |
| SDK | Python SDK v2.0+ or REST API |
| LLM | Any streaming-capable model (OpenAI, Anthropic, etc.) |

## Quick Start with Python SDK

\`\`\`python
from encypher import Encypher

client = Encypher(api_key="YOUR_API_KEY")

# Start a streaming signing session
session = client.start_streaming_session(
    document_title="Chat response",
    document_type="ai_output",
)

# As chunks arrive from your LLM:
for chunk in llm.stream("Tell me about quantum computing"):
    signed_chunk = session.sign_chunk(chunk)
    yield signed_chunk  # Send to user

# Finalize the session
manifest = session.finalize()
print(f"Document ID: {manifest.document_id}")
print(f"Total chunks: {manifest.total_chunks}")
\`\`\`

## REST API Flow

### 1. Start a streaming session

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/sign/stream/start \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "document_title": "Chat response",
    "document_type": "ai_output"
  }'
\`\`\`

Response:

\`\`\`json
{
  "success": true,
  "session_id": "stream_abc123",
  "document_id": "doc_xyz789"
}
\`\`\`

### 2. Sign each chunk

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/sign/stream/chunk \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "stream_abc123",
    "chunk": "Quantum computing uses qubits instead of classical bits. ",
    "chunk_index": 0
  }'
\`\`\`

### 3. Finalize the session

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/sign/stream/finalize \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"session_id": "stream_abc123"}'
\`\`\`

## Integration with OpenAI

\`\`\`python
import openai
from encypher import Encypher

oai = openai.OpenAI()
encypher = Encypher(api_key="ENCYPHER_KEY")

session = encypher.start_streaming_session(
    document_title="GPT response",
    document_type="ai_output",
)

stream = oai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain photosynthesis"}],
    stream=True,
)

full_response = ""
for event in stream:
    chunk = event.choices[0].delta.content or ""
    signed = session.sign_chunk(chunk)
    full_response += signed
    print(signed, end="", flush=True)

manifest = session.finalize()
print(f"\\nSigned document: {manifest.document_id}")
\`\`\`

## Verification

Verifying streamed content works the same as verifying any signed text:

\`\`\`bash
curl -X POST https://api.encypher.com/api/v1/verify \\
  -H "Content-Type: application/json" \\
  -d '{"text": "The concatenated signed chunks..."}'
\`\`\`

The verify response includes the \`session_id\` and \`total_chunks\` so you can confirm the complete stream was received.

## Performance Considerations

- **Overhead**: streaming signing adds less than 1ms per chunk.
- **Chunk size**: we recommend chunks of at least 1 sentence for optimal embedding density.
- **Session timeout**: streaming sessions expire after 5 minutes of inactivity. Call \`finalize\` promptly.
- **Concurrent sessions**: Enterprise plans support up to 100 concurrent streaming sessions.

## Error Handling

If a chunk fails to sign, the session continues. Failed chunks are logged and the finalized manifest notes any gaps:

\`\`\`python
manifest = session.finalize()
if manifest.failed_chunks > 0:
    print(f"Warning: {manifest.failed_chunks} chunks failed to sign")
\`\`\`

## Support

For streaming integration support, contact support@encypher.com or visit the [API Playground](/playground) to test interactively.
`;

export default function StreamingGuidePage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <PublisherIntegrationGuideClient markdown={GUIDE_CONTENT} />
      </div>
    </DashboardLayout>
  );
}
