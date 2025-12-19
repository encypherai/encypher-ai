"""
OpenAI chat completion integration example.

Run with:
    ENCYPHER_API_KEY=encypher_live_xxx \
    OPENAI_API_KEY=sk-... \
    python examples/openai_integration.py
"""
from __future__ import annotations

import os

from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.openai import chat_completion_with_signing, stream_chat_completion_with_signing


def main() -> None:
    api_key = os.environ.get("ENCYPHER_API_KEY")
    if not api_key:
        raise SystemExit("Set ENCYPHER_API_KEY before running this example.")

    with EncypherClient(api_key=api_key) as client:
        signed = chat_completion_with_signing(
            client,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a provenance assistant."},
                {"role": "user", "content": "Summarize Encypher's C2PA capabilities."},
            ],
            document_title="OpenAI Signing Demo",
            metadata={"example": "openai"},
        )

        print("Signed completion:\n", signed.signed_text)

        print("\nStreaming signed response:")
        stream = stream_chat_completion_with_signing(
            client,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a provenance assistant."},
                {"role": "user", "content": "Provide three bullet points about C2PA."},
            ],
            document_title="OpenAI Streaming Demo",
            metadata={"example": "openai-stream"},
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
