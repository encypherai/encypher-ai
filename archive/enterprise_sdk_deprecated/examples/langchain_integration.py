"""
LangChain integration example.

Run with:
    ENCYPHER_API_KEY=encypher_live_xxx \
    OPENAI_API_KEY=sk-... \
    python examples/langchain_integration.py
"""
from __future__ import annotations

import os

from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.langchain import apply_signing


def build_chain() -> any:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise SystemExit(
            "Install LangChain extras before running this example:\n"
            "  pip install encypher-enterprise[langchain]\n"
            "or manually install `langchain-core` and `langchain-openai`."
        ) from exc

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant focused on C2PA provenance."),
            ("human", "{question}"),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    return prompt | llm


def main() -> None:
    api_key = os.environ.get("ENCYPHER_API_KEY")
    if not api_key:
        raise SystemExit("Set ENCYPHER_API_KEY before running this example.")

    chain = build_chain()
    with EncypherClient(api_key=api_key) as client:
        signed_chain = apply_signing(
            chain,
            client,
            document_title="LangChain Signing Demo",
            metadata={"example": "langchain"},
        )

        result = signed_chain.invoke({"question": "How does Encypher track provenance?"})

    if isinstance(result, dict):
        print("Signed text:\n", result["signed_text"])
    else:
        print("Signed text:\n", result)


if __name__ == "__main__":
    main()
