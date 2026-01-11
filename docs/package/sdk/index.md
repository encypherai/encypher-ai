# Encypher Enterprise SDK

The Encypher Enterprise SDK provides a production-ready Python client for the commercial
Encypher Enterprise API. It builds on top of the open-source `encypher-ai` package, adding
configuration helpers, streaming utilities, framework integrations, and a CLI tailored for
enterprise deployments.

## Installation

```bash
uv add encypher-enterprise
```

Optional extras enable first-class integrations:

```bash
uv add 'encypher-enterprise[langchain]'   # LangChain helpers
uv add 'encypher-enterprise[openai]'      # OpenAI client wrappers
uv add 'encypher-enterprise[litellm]'     # LiteLLM adapter
uv add 'encypher-enterprise[all]'         # Install every integration
```

## Quick Start

```python
from encypher_enterprise import EncypherClient

client = EncypherClient(api_key="encypher_live_xxx")

result = client.sign(
    text="Example article content.",
    title="Enterprise SDK intro",
    metadata={"source": "docs"},
)

print(result.document_id)
print(result.verification_url)
```

## Streaming Helpers

Real-time LLM output can be signed chunk-by-chunk by wrapping a stream:

```python
from encypher_enterprise import EncypherClient, sign_stream

client = EncypherClient(api_key="encypher_live_xxx")

for signed_chunk in sign_stream(client, llm_stream):
    print(signed_chunk, end="", flush=True)
```

Async and callback-based variants are available via
`AsyncStreamingSigner` and the LangChain integration helpers.

## CLI

The SDK bundles an `encypher` command for quick testing:

```bash
export ENCYPHER_API_KEY=encypher_live_xxx
encypher sign --text "Hello world" --title "CLI Demo"
encypher verify --file signed.txt
encypher stats
```

## Links

- Repository: `enterprise_sdk` directory inside the `encypherai-commercial` monorepo
- SDK README: `enterprise_sdk/README.md`
- API Reference: `enterprise_api/docs/API.md`
- Integration examples: `enterprise_sdk/examples/`
