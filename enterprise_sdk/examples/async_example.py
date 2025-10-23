"""
Async operations example.
"""
import asyncio
import os
from encypher_enterprise import AsyncEncypherClient

async def main():
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        print("❌ Please set ENCYPHER_API_KEY environment variable")
        return

    async with AsyncEncypherClient(api_key=api_key) as client:
        print("🚀 Running async operations...\n")

        # Async signing
        print("📝 Signing content...")
        result = await client.sign(
            text="Async operations make high-performance signing possible. "
                 "Multiple documents can be signed concurrently.",
            title="Async Signing Example"
        )
        print(f"✅ Signed! Document ID: {result.document_id}")

        # Async verification
        print(f"\n🔍 Verifying signature...")
        verification = await client.verify(result.signed_text)
        print(f"✅ Valid: {verification.is_valid}")

        # Async lookup
        print(f"\n🔎 Looking up sentence...")
        provenance = await client.lookup("Async operations make high-performance signing possible.")
        print(f"✅ Found: {provenance.found}")

        # Async stats
        print(f"\n📊 Getting usage statistics...")
        stats = await client.get_stats()
        print(f"✅ Organization: {stats.organization_name}")
        print(f"   Documents signed: {stats.usage.documents_signed}")
        print(f"   API calls this month: {stats.usage.api_calls_this_month}")

if __name__ == "__main__":
    asyncio.run(main())
