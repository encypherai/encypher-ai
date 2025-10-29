"""
LiteLLM integration example.

Run with:
    ENCYPHER_API_KEY=encypher_live_xxx \
    LITELLM_API_KEY=... \
    python examples/litellm_integration.py
"""
from __future__ import annotations

import os

from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.litellm import (
    completion_with_signing,
    stream_completion_with_signing,
)


def main() -> None:
    api_key = os.environ.get("ENCYPHER_API_KEY")
    if not api_key:
        raise SystemExit("Set ENCYPHER_API_KEY before running this example.")

    with EncypherClient(api_key=api_key) as client:
        signed = completion_with_signing(
            client,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a provenance assistant."},
                {"role": "user", "content": "Explain why C2PA manifests matter."},
            ],
            document_title="LiteLLM Signing Demo",
            metadata={"example": "litellm"},
        )

        print("Signed completion:\n", signed.signed_text)

        print("\nStreaming signed response:")
        stream = stream_completion_with_signing(
            client,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a provenance assistant."},
                {"role": "user", "content": "List two ways Encypher integrates with LiteLLM."},
            ],
            document_title="LiteLLM Streaming Demo",
            metadata={"example": "litellm-stream"},
        )

        signed_output = []
        for event in stream:
            if event.signed_chunk:
                signed_output.append(event.signed_chunk)
                print(event.signed_chunk, end="", flush=True)

        final_signed = "".join(signed_output)
        print("\n\nSigned stream complete.")
        print(final_signed)


if __name__ == "__main__":
    main()
