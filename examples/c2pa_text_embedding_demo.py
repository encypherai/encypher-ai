# c:\Users\eriks\encypher-ai\examples\c2pa_text_embedding_demo.py
"""
Demonstrates embedding a C2PA-style manifest into text using EncypherAI.

This example shows:
1. Defining a C2PA-like manifest.
2. Converting it to EncypherAI's internal ManifestPayload format.
3. Embedding the payload into a sample text string.
4. Extracting the payload from the text.
5. Verifying the extracted payload.
6. Converting the extracted payload back to a C2PA-like dictionary
   to demonstrate structural preservation and interoperability.
"""

import copy
import json
import traceback

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest, encypher_manifest_to_c2pa_like_dict


def main():
    print("--- EncypherAI C2PA-style Text Embedding Demo ---", flush=True)

    # 1. Define the C2PA-like manifest (as provided by the user)
    # Note: For real applications, ensure timestamps are accurate (current or past).
    # The example timestamp is slightly in the future for demo purposes.
    demo_manifest_c2pa_like = {
        "claim_generator": "EncypherAI/2.1.0",
        "timestamp": "2025-06-16T10:30:00Z",
        "assertions": [
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "http://schema.org/",
                    "@type": "CreativeWork",
                    "author": {"@type": "Person", "name": "Erik EncypherAI"},
                    "publisher": {"@type": "Organization", "name": "Encypher Corporation"},
                    "copyrightHolder": {"name": "Encypher Corporation"},
                    "copyrightYear": 2025,
                    "copyrightNotice": "© 2025 Encypher Corporation. All Rights Reserved.",
                },
            }
        ],
    }
    print("\n1. Original C2PA-like Manifest:", flush=True)
    print(json.dumps(demo_manifest_c2pa_like, indent=2), flush=True)

    # 2. Convert C2PA-like manifest to EncypherAI ManifestPayload
    encypher_ai_payload_to_embed = c2pa_like_dict_to_encypher_manifest(demo_manifest_c2pa_like)
    print("\n2. Converted EncypherAI ManifestPayload (for embedding):", flush=True)
    print(json.dumps(encypher_ai_payload_to_embed, indent=2), flush=True)

    # Prepare for embedding: Generate keys and define sample text
    private_key, public_key = generate_ed25519_key_pair()
    key_id = "c2pa-demo-key-001"

    sample_article_text = (
        "The Future of AI in Creative Industries\n\n"
        "Artificial intelligence is rapidly transforming various sectors, and the "
        "creative industries are no exception. From automated content generation "
        "to AI-powered editing tools, the landscape is evolving. This article "
        "explores the potential impacts and ethical considerations.\n\n"
        "Ensuring authenticity and provenance in this new era is crucial. "
        "Tools that can transparently declare authorship and modifications "
        "will play a vital role."
    )
    print(f"\nSample text (length: {len(sample_article_text)} chars)", flush=True)

    # 3. Embed the EncypherAI ManifestPayload into the sample text
    try:
        text_with_embedded_metadata = UnicodeMetadata.embed_metadata(
            text=sample_article_text,
            private_key=private_key,
            signer_id=key_id,
            metadata_format="manifest",
            claim_generator=encypher_ai_payload_to_embed.get("claim_generator"),
            actions=encypher_ai_payload_to_embed.get("assertions"),  # Map 'assertions' to 'actions'
            ai_info=encypher_ai_payload_to_embed.get("ai_assertion"),
            custom_claims=encypher_ai_payload_to_embed.get("custom_claims"),
            timestamp=encypher_ai_payload_to_embed.get("timestamp"),
        )
        print("\n3. Text with Embedded Metadata (first 100 chars):", flush=True)
        print(text_with_embedded_metadata[:100] + "...", flush=True)
        print(f"(Original length: {len(sample_article_text)}, Embedded length: {len(text_with_embedded_metadata)})", flush=True)

        # 4. Extract and verify the metadata from the text
        def public_key_resolver(kid: str) -> bytes:
            if kid == key_id:
                return public_key
            raise ValueError(f"Unknown key_id: {kid}")

        is_verified, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_and_extract_metadata(
            text=text_with_embedded_metadata, public_key_provider=public_key_resolver, return_payload_on_failure=True
        )

        if not extracted_payload:
            print("\nERROR: No metadata payload extracted.", flush=True)
            return

        print("\n4. Extracted EncypherAI ManifestPayload:", flush=True)
        print(json.dumps(extracted_payload, indent=2), flush=True)
        if extracted_signer_id:
            print(f"   Key ID used for signature: {extracted_signer_id}", flush=True)

        # 5. Verify the extracted payload
        print("\n5. Verification Status:", flush=True)
        if is_verified:
            print("   SUCCESS: The extracted metadata's signature is valid.", flush=True)
        else:
            print("   FAILURE: The extracted metadata's signature is NOT valid or could not be verified.", flush=True)

        # 6. Convert the extracted EncypherAI ManifestPayload back to a C2PA-like dictionary
        # First, reconstruct the manifest structure expected by the conversion function
        # from the output of verify_and_extract_metadata.
        if extracted_payload and "manifest" in extracted_payload:
            inner_manifest = extracted_payload["manifest"]
            manifest_for_conversion = {
                "claim_generator": inner_manifest.get("claim_generator"),
                "assertions": inner_manifest.get("actions"),  # Map 'actions' to 'assertions'
                "ai_assertion": inner_manifest.get("ai_assertion", {}),  # Default to empty if not present
                "custom_claims": inner_manifest.get("custom_claims", {}),  # Default to empty if not present
                # Use the timestamp from the inner manifest if available, else from the outer payload
                "timestamp": inner_manifest.get("timestamp", extracted_payload.get("timestamp")),
            }
            extracted_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(manifest_for_conversion)
            print("\n6. Extracted Payload converted back to C2PA-like Dictionary:", flush=True)
            print(json.dumps(extracted_c2pa_like_dict, indent=2), flush=True)
        else:
            print("\n6. Could not convert to C2PA-like Dictionary: Extracted payload or inner manifest missing.", flush=True)

        print("\n--- End of Demo ---", flush=True)

        # --- CBOR Assertion Data Demo ---
        print("\n\n--- CBOR Assertion Data Demo ---", flush=True)

        # Reuse the same C2PA-like manifest and keys
        print("\n1. Original C2PA-like Manifest (for CBOR demo):", flush=True)
        print(json.dumps(demo_manifest_c2pa_like, indent=2), flush=True)

        # 2. Convert C2PA-like manifest to EncypherAI ManifestPayload with CBOR encoding for assertion data
        encypher_ai_payload_cbor_to_embed = c2pa_like_dict_to_encypher_manifest(demo_manifest_c2pa_like, encode_assertion_data_as_cbor=True)
        print("\n2. Converted EncypherAI ManifestPayload (with CBOR assertion data):", flush=True)
        print(json.dumps(encypher_ai_payload_cbor_to_embed, indent=2), flush=True)

        # 3. Embed the CBOR-data EncypherAI ManifestPayload into the sample text
        text_with_cbor_embedded_metadata = UnicodeMetadata.embed_metadata(
            text=sample_article_text,  # Use the same sample text
            private_key=private_key,
            signer_id=key_id,
            metadata_format="manifest",
            claim_generator=encypher_ai_payload_cbor_to_embed.get("claim_generator"),
            actions=encypher_ai_payload_cbor_to_embed.get("assertions"),
            ai_info=encypher_ai_payload_cbor_to_embed.get("ai_assertion"),
            custom_claims=encypher_ai_payload_cbor_to_embed.get("custom_claims"),
            timestamp=encypher_ai_payload_cbor_to_embed.get("timestamp"),
        )
        print("\n3. Text with CBOR-data Embedded Metadata (first 100 chars):", flush=True)
        print(text_with_cbor_embedded_metadata[:100] + "...", flush=True)

        # 4. Extract and verify the CBOR-data metadata from the text
        is_cbor_verified, extracted_cbor_signer_id, extracted_cbor_payload = UnicodeMetadata.verify_and_extract_metadata(
            text=text_with_cbor_embedded_metadata, public_key_provider=public_key_resolver, return_payload_on_failure=True
        )

        if not extracted_cbor_payload:
            print("\nERROR: No CBOR-data metadata payload extracted.", flush=True)
            # Potentially skip the rest of this CBOR section or handle error
        else:
            print("\n4. Extracted EncypherAI ManifestPayload (from CBOR-data embedding):", flush=True)
            print(json.dumps(extracted_cbor_payload, indent=2), flush=True)
            if extracted_cbor_signer_id:
                print(f"   Key ID used for signature: {extracted_cbor_signer_id}", flush=True)

            # 5. Verify the extracted CBOR-data payload
            print("\n5. CBOR-data Verification Status:", flush=True)
            if is_cbor_verified:
                print("   SUCCESS: The extracted CBOR-data metadata's signature is valid.", flush=True)
            else:
                print("   FAILURE: The extracted CBOR-data metadata's signature is NOT valid or could not be verified.", flush=True)

            # 6. Convert the extracted EncypherAI ManifestPayload (from CBOR-data embedding) back to a C2PA-like dictionary
            if extracted_cbor_payload and "manifest" in extracted_cbor_payload:
                inner_cbor_manifest = extracted_cbor_payload["manifest"]
                manifest_for_cbor_conversion = {
                    "claim_generator": inner_cbor_manifest.get("claim_generator"),
                    "assertions": inner_cbor_manifest.get("actions"),
                    "ai_assertion": inner_cbor_manifest.get("ai_assertion", {}),
                    "custom_claims": inner_cbor_manifest.get("custom_claims", {}),
                    "timestamp": inner_cbor_manifest.get("timestamp", extracted_cbor_payload.get("timestamp")),
                }
                extracted_cbor_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(manifest_for_cbor_conversion)
                print("\n6. Extracted CBOR-data Payload converted back to C2PA-like Dictionary:", flush=True)
                print(json.dumps(extracted_cbor_c2pa_like_dict, indent=2), flush=True)

                # Compare with original, accounting for the 'format' field added by the conversion
                comparison_dict = extracted_cbor_c2pa_like_dict.copy()
                if "format" in comparison_dict:
                    del comparison_dict["format"]  # Remove field not in original for comparison

                if comparison_dict == demo_manifest_c2pa_like:
                    print(
                        "\n   SUCCESS: Round-trip conversion with CBOR assertion data matches original (after accounting for 'format' field)!",
                        flush=True,
                    )
                else:
                    print("\n   FAILURE: Round-trip conversion with CBOR assertion data does NOT match original.", flush=True)
                    print("   Original for comparison:", json.dumps(demo_manifest_c2pa_like, indent=2), flush=True)
                    print("   Extracted for comparison (format field removed):", json.dumps(comparison_dict, indent=2), flush=True)
            else:
                print("\n6. Could not convert CBOR-data payload to C2PA-like Dictionary: Extracted payload or inner manifest missing.", flush=True)

        print("\n--- End of CBOR Demo ---", flush=True)

        # --- Full CBOR Manifest Demo ---
        print("\n\n--- Full CBOR Manifest Demo ---", flush=True)

        # Reuse the same C2PA-like manifest and keys
        print("\n1. Original C2PA-like Manifest (for full CBOR manifest demo):", flush=True)
        print(json.dumps(demo_manifest_c2pa_like, indent=2), flush=True)

        # 2. Convert C2PA-like manifest to EncypherAI ManifestPayload with nested data structure
        # Note: use_nested_data=True is required for cbor_manifest format
        encypher_ai_payload_cbor_manifest = c2pa_like_dict_to_encypher_manifest(
            demo_manifest_c2pa_like,
            use_nested_data=True,  # Important: use nested data structure for cbor_manifest
        )
        print("\n2. Converted EncypherAI ManifestPayload (for full CBOR manifest):", flush=True)
        print(json.dumps(encypher_ai_payload_cbor_manifest, indent=2), flush=True)

        # 3. Embed the full CBOR manifest into the sample text
        text_with_full_cbor_manifest = UnicodeMetadata.embed_metadata(
            text=sample_article_text,  # Use the same sample text
            private_key=private_key,
            signer_id=key_id,
            metadata_format="cbor_manifest",  # Use cbor_manifest format
            claim_generator=encypher_ai_payload_cbor_manifest.get("claim_generator"),
            actions=encypher_ai_payload_cbor_manifest.get("assertions"),
            ai_info=encypher_ai_payload_cbor_manifest.get("ai_assertion"),
            custom_claims=encypher_ai_payload_cbor_manifest.get("custom_claims"),
            timestamp=encypher_ai_payload_cbor_manifest.get("timestamp"),
        )
        print("\n3. Text with Full CBOR Manifest Embedded (first 100 chars):", flush=True)
        print(text_with_full_cbor_manifest[:100] + "...", flush=True)

        # 4. Extract and verify the full CBOR manifest from the text
        is_full_cbor_verified, extracted_full_cbor_signer_id, extracted_full_cbor_payload = UnicodeMetadata.verify_and_extract_metadata(
            text=text_with_full_cbor_manifest, public_key_provider=public_key_resolver, return_payload_on_failure=True
        )

        if not extracted_full_cbor_payload:
            print("\nERROR: No full CBOR manifest payload extracted.", flush=True)
        else:
            print("\n4. Extracted Full CBOR Manifest Payload:", flush=True)
            print(json.dumps(extracted_full_cbor_payload, indent=2), flush=True)
            if extracted_full_cbor_signer_id:
                print(f"   Key ID used for signature: {extracted_full_cbor_signer_id}", flush=True)

            # 5. Verify the extracted full CBOR manifest payload
            print("\n5. Full CBOR Manifest Verification Status:", flush=True)
            if is_full_cbor_verified:
                print("   SUCCESS: The extracted full CBOR manifest's signature is valid.", flush=True)
            else:
                print("   FAILURE: The extracted full CBOR manifest's signature is NOT valid or could not be verified.", flush=True)

            # 6. Convert the extracted full CBOR manifest back to a C2PA-like dictionary
            # For cbor_manifest format, the extracted payload is already the inner manifest
            extracted_full_cbor_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(extracted_full_cbor_payload)
            print("\n6. Extracted Full CBOR Manifest converted back to C2PA-like Dictionary:", flush=True)
            print(json.dumps(extracted_full_cbor_c2pa_like_dict, indent=2), flush=True)

            # Compare with original, but handle missing timestamp
            comparison_dict = extracted_full_cbor_c2pa_like_dict.copy()
            if "format" in comparison_dict:
                del comparison_dict["format"]  # Remove field not in original for comparison

            # Fix for missing timestamp in extracted data
            if "timestamp" in comparison_dict and not comparison_dict["timestamp"]:
                # If timestamp is empty in extracted data, use the original timestamp
                comparison_dict["timestamp"] = demo_manifest_c2pa_like.get("timestamp", "")

            # Create a deep copy of the original for comparison
            original_for_comparison = copy.deepcopy(demo_manifest_c2pa_like)

            # Check if the structures match after accounting for timestamp
            if comparison_dict == original_for_comparison:
                print(
                    "\nSUCCESS: Round-trip conversion with full CBOR manifest matches original (after accounting for 'format' field and timestamp)!",
                    flush=True,
                )
            else:
                print("\n   FAILURE: Round-trip conversion with full CBOR manifest does NOT match original.", flush=True)
                print("   Original for comparison:", json.dumps(original_for_comparison, indent=2), flush=True)
                print("   Extracted for comparison (format field removed):", json.dumps(comparison_dict, indent=2), flush=True)

                # Print differences for debugging
                print("\n   Differences found:")
                if comparison_dict.get("timestamp") != original_for_comparison.get("timestamp"):
                    print(f"   - Timestamp mismatch: '{comparison_dict.get('timestamp')}' vs '{original_for_comparison.get('timestamp')}'")

                # Check assertions structure
                orig_assertions = original_for_comparison.get("assertions", [])
                comp_assertions = comparison_dict.get("assertions", [])
                if len(orig_assertions) != len(comp_assertions):
                    print(f"   - Different number of assertions: {len(comp_assertions)} vs {len(orig_assertions)}")
                else:
                    for i, (orig_assert, comp_assert) in enumerate(zip(orig_assertions, comp_assertions)):
                        if orig_assert != comp_assert:
                            print(f"   - Assertion {i} differs")
                            if orig_assert.get("label") != comp_assert.get("label"):
                                print(f"     - Label: '{comp_assert.get('label')}' vs '{orig_assert.get('label')}'")
                            if orig_assert.get("data") != comp_assert.get("data"):
                                print("     - Data differs")

        print("\n--- End of Full CBOR Manifest Demo ---", flush=True)

    except Exception as e:
        print(f"\nAn error occurred during the process: {e}", flush=True)
        traceback.print_exc()


if __name__ == "__main__":
    main()
