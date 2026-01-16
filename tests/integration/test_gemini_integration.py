import os
import time

import google.generativeai as genai
import pytest
from dotenv import load_dotenv

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# Load environment variables from .env file
load_dotenv()

# --- 1. Setup ---
# Pytest will skip tests if the API key is not found.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_NOT_SET = GEMINI_API_KEY is None

# In a real application, use a secure key management solution.
private_key, public_key = generate_ed25519_key_pair()
signer_id = "gemini-guide-signer-001"
public_keys_store = {signer_id: public_key}


def public_key_provider(kid):
    return public_keys_store.get(kid)


@pytest.mark.skipif(GEMINI_API_KEY_NOT_SET, reason="GEMINI_API_KEY not set in environment")
def test_gemini_non_streaming():
    """Tests the non-streaming Gemini integration."""
    print("--- Running Non-Streaming Gemini Test ---")
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Explain the significance of the C2PA standard in simple terms.")
    original_text = response.text

    custom_metadata = {
        "gemini_model": "gemini-pro",
        "safety_ratings": str(response.prompt_feedback.safety_ratings),
    }

    encoded_text = UnicodeMetadata.embed_metadata(
        text=original_text,
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        custom_claims=custom_metadata,
        timestamp=int(time.time()),
    )

    print("\n--- Response with Embedded Metadata ---")
    print(encoded_text)

    is_valid, _, payload = UnicodeMetadata.verify_metadata(text=encoded_text, public_key_resolver=public_key_provider)

    print(f"\nSignature valid: {is_valid}")
    if is_valid:
        print(f"Verified Payload: {payload}")

    assert is_valid
    assert payload is not None


@pytest.mark.skipif(GEMINI_API_KEY_NOT_SET, reason="GEMINI_API_KEY not set in environment")
def test_gemini_streaming():
    """Tests the streaming Gemini integration."""
    print("\n\n--- Running Streaming Gemini Test ---")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    streaming_handler = StreamingHandler(
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        custom_metadata={"gemini_model": "gemini-1.5-flash", "streaming": "true"},
        timestamp=int(time.time()),
    )

    stream = model.generate_content("Write a short story about a friendly robot.", stream=True)

    full_encoded_response = ""
    print("\n--- Streaming Response with Embedded Metadata ---")
    for chunk in stream:
        # Ensure chunk.text is not None before processing
        if chunk.text:
            encoded_chunk = streaming_handler.process_chunk(chunk=chunk.text)
            if encoded_chunk:
                print(encoded_chunk, end="")
                full_encoded_response += encoded_chunk

    # Finalize the stream to process any remaining buffered content
    final_chunk = streaming_handler.finalize()
    if final_chunk:
        print(final_chunk, end="")
        full_encoded_response += final_chunk

    print("\n--- End of Stream ---")

    is_valid_stream, _, payload_stream = UnicodeMetadata.verify_metadata(
        text=full_encoded_response,
        public_key_resolver=public_key_provider,
        require_hard_binding=False,
    )

    print(f"\nSignature valid: {is_valid_stream}")
    if is_valid_stream:
        print(f"Verified Payload: {payload_stream}")

    assert is_valid_stream
    assert payload_stream is not None
