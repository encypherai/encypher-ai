"""
Example of real-time LLM streaming with C2PA signing.

This example shows how to wrap OpenAI streaming responses
with real-time C2PA signing.
"""
from encypher_enterprise import EncypherClient, StreamingSigner
import os

def simulate_llm_stream():
    """Simulate LLM streaming response."""
    # In real usage, this would be:
    # for chunk in openai.chat.completions.create(stream=True):
    #     yield chunk.choices[0].delta.content

    text = (
        "Artificial intelligence is transforming healthcare. "
        "AI models can now diagnose diseases with high accuracy. "
        "This technology will revolutionize patient care."
    )

    # Simulate streaming by yielding small chunks
    for i in range(0, len(text), 5):
        yield text[i:i+5]

def main():
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        print("❌ Please set ENCYPHER_API_KEY environment variable")
        return

    client = EncypherClient(api_key=api_key)
    signer = StreamingSigner(client, sign_on_sentence=True)

    print("🤖 Starting LLM stream (simulated)...")
    print("📝 Signing in real-time:\n")

    # Process streaming chunks
    for chunk in simulate_llm_stream():
        # Display chunk
        print(chunk, end='', flush=True)

        # Sign if sentence boundary reached
        signed_chunk = signer.process_chunk(chunk)
        if signed_chunk:
            print(f"\n✅ Signed chunk ({len(signed_chunk)} chars)", flush=True)

    # Finalize and sign remaining content
    print(f"\n\n🔒 Finalizing signature...")
    final_signed_text = signer.finalize()

    print(f"✅ Complete signed text generated ({len(final_signed_text)} chars)")
    print(f"\n📄 Signed text (first 150 chars):")
    print(f"   {final_signed_text[:150]}...")

if __name__ == "__main__":
    main()
