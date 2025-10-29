"""
Basic signing and verification example.
"""
from encypher_enterprise import EncypherClient
import os

def main():
    # Initialize client (API key from environment)
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        print("❌ Please set ENCYPHER_API_KEY environment variable")
        return

    client = EncypherClient(api_key=api_key)

    # Sign content
    print("📝 Signing content...")
    result = client.sign(
        text="Breaking news: Scientists discover new exoplanet 100 light-years away. "
             "The planet orbits a sun-like star.",
        title="New Exoplanet Discovered",
        document_type="article"
    )

    print(f"✅ Signed successfully!")
    print(f"   Document ID: {result.document_id}")
    print(f"   Sentences: {result.total_sentences}")
    print(f"   Verification URL: {result.verification_url}")
    print(f"\n📄 Signed text (first 100 chars):")
    print(f"   {result.signed_text[:100]}...")

    # Verify content
    print(f"\n🔍 Verifying signature...")
    verification = client.verify(result.signed_text)

    if verification.is_valid:
        print(f"✅ Valid signature!")
        print(f"   Signer: {verification.organization_name}")
        print(f"   Timestamp: {verification.signature_timestamp}")
    else:
        print(f"❌ Invalid signature (tampered: {verification.tampered})")

    # Look up sentence
    print(f"\n🔎 Looking up sentence provenance...")
    provenance = client.lookup("Breaking news: Scientists discover new exoplanet 100 light-years away.")

    if provenance.found:
        print(f"✅ Sentence found!")
        print(f"   Document: {provenance.document_title}")
        print(f"   Organization: {provenance.organization_name}")
        print(f"   Published: {provenance.publication_date}")
        print(f"   Sentence index: {provenance.sentence_index}")
    else:
        print(f"❌ Sentence not found")

if __name__ == "__main__":
    main()
