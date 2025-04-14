# ruff: noqa: E501
"""
Integration tests for EncypherAI with sample LLM outputs.
"""

from datetime import datetime, timezone
from typing import Callable, Optional, Tuple

import pytest
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes

from encypher.core.crypto_utils import generate_key_pair  # Import key gen
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# Sample LLM outputs from different providers
SAMPLE_OUTPUTS = {
    "openai": "The quick brown fox jumps over the lazy dog. This is a sample output from OpenAI's GPT model that demonstrates how text might be formatted, including punctuation, spacing, and paragraph breaks.\n\nMultiple paragraphs might be included in the response, with varying lengths and structures. This helps test the robustness of the metadata encoding system across different text patterns.",
    "anthropic": "Here's what I know about that topic:\n\n1. First, it's important to understand the basic principles.\n2. Second, we should consider the historical context.\n3. Finally, let's examine the practical applications.\n\nIn conclusion, this sample output from Anthropic's Claude model demonstrates different formatting styles including lists and structured content.",
    "gemini": "When considering this question, I'd approach it from multiple angles:\n\n• Technical feasibility\n• Economic implications\n• Ethical considerations\n• Social impact\n\nThis sample from Google's Gemini model includes bullet points and special characters to test encoding resilience.",
    "llama": "To answer your question:\nThe solution involves several steps. First, we need to analyze the problem domain. Second, we should identify potential approaches. Third, we implement the most promising solution.\n\nThis sample from Llama includes line breaks and a structured response format typical of instruction-tuned models.",
}


# --- Test Fixtures ---


@pytest.fixture(scope="class")  # Use class scope if multiple tests in class need it
def test_key_pair() -> Tuple[PrivateKeyTypes, PublicKeyTypes]:
    """Generate a key pair for integration tests."""
    return generate_key_pair()


@pytest.fixture
def test_public_key_provider(
    test_key_pair,
) -> Callable[[str], Optional[PublicKeyTypes]]:
    """Provides a simple key provider for integration tests."""
    _, public_key = test_key_pair
    key_map = {"integration_signer": public_key}

    def resolver(signer_id: str) -> Optional[PublicKeyTypes]:
        return key_map.get(signer_id)

    return resolver


# --- Test Classes ---


class TestLLMOutputsIntegration:
    """Integration tests with sample LLM outputs."""

    # Skip this test: The static LLM output examples are often too short
    # to embed the full signature payload (~300 bytes) reliably.
    @pytest.mark.skip(reason="Static LLM output snippets are too short for signature metadata " "embedding.")
    @pytest.mark.parametrize("provider,sample_text", SAMPLE_OUTPUTS.items())
    def test_unicode_metadata_with_llm_outputs(self, provider, sample_text, test_key_pair, test_public_key_provider):
        """Test UnicodeMetadata with various LLM outputs using signatures."""
        private_key, public_key = test_key_pair
        signer_id = "integration_signer"

        # Test data (using basic format for simplicity)
        basic_metadata = {
            "model_id": f"{provider}-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),  # Use current time
            "custom_metadata": {
                "request_id": "test-123",
                "user_id": "user-456",
                "cost": 0.0023,
                "tokens": 150,
            },
        }

        # Test with different metadata targets
        # Combine target loop with metadata format parameterization if needed
        for target in [
            MetadataTarget.WHITESPACE,
            MetadataTarget.PUNCTUATION,
            MetadataTarget.FIRST_LETTER,
        ]:
            # Embed metadata
            embedded_text = UnicodeMetadata.embed_metadata(
                text=sample_text,
                private_key=private_key,
                signer_id=signer_id,
                metadata_format="basic",  # Explicitly basic for this test data
                **basic_metadata,  # Pass dict content as kwargs
            )

            # Verify text appearance is unchanged (basic check)
            assert len(embedded_text) > len(sample_text), f"Encoded text should be longer than original for {provider} with {target.name}"

            # Verify and Extract metadata
            extracted_payload, is_valid, extracted_signer_id = UnicodeMetadata.verify_and_extract_metadata(embedded_text, test_public_key_provider)

            # Verify extracted metadata
            assert is_valid is True, f"Verification failed for {provider} with {target.name}"
            assert extracted_signer_id == signer_id, f"Signer ID mismatch for {provider} with {target.name}"
            assert extracted_payload is not None
            assert extracted_payload.get("format") == "basic"

            inner_payload = extracted_payload.get("payload")
            assert inner_payload is not None
            assert inner_payload.get("model_id") == basic_metadata["model_id"], f"Model ID mismatch for {provider} with {target.name}"
            # Timestamp comparison can be tricky due to potential slight format diffs,
            # comparing the core custom data is usually sufficient for integration tests
            assert (
                inner_payload.get("custom_metadata") == basic_metadata["custom_metadata"]
            ), f"Custom metadata mismatch for {provider} with {target.name}"


# Sample streaming chunks for different providers
STREAMING_CHUNKS = {
    "openai": [
        "The quick brown",
        " fox jumps over",
        " the lazy dog.",
        " This is a sample",
        " output from OpenAI.",
    ],
    "anthropic": [
        "Here's what I know",
        " about that topic:",
        "\n\n1. First, it's important",
        " to understand the basic principles.",
        "\n2. Second, we should consider",
        " the historical context.",
    ],
    "gemini": [
        "When considering",
        " this question, I'd",
        " approach it from",
        " multiple angles:",
        "\n\n• Technical feasibility",
        "\n• Economic implications",
    ],
}


class TestStreamingIntegration:
    """Integration tests for embedding and verification with various LLM outputs."""

    # The handler now accumulates text until it finds a suitable target
    # and embeds all metadata after the first target character
    @pytest.mark.parametrize("provider,chunks", STREAMING_CHUNKS.items())
    def test_streaming_handler(self, provider, chunks, test_key_pair, test_public_key_provider):
        """Test StreamingHandler with streaming chunks."""
        private_key, public_key = test_key_pair
        signer_id = "integration_signer"
        metadata_format = "basic"  # Assuming basic format for this test

        # Metadata to embed
        metadata = {
            "model_id": f"{provider}-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),  # Use current time
            "custom_metadata": {
                "request_id": "stream-123",
                "cost": 0.0015,
            },
        }

        # Test with different configurations
        encode_first_only = True
        for target in [MetadataTarget.WHITESPACE, MetadataTarget.PUNCTUATION]:
            # Initialize streaming handler
            handler = StreamingHandler(
                metadata=metadata,
                target=target,
                encode_first_chunk_only=encode_first_only,
                private_key=private_key,  # Pass the key
                signer_id=signer_id,  # Pass the signer ID
                metadata_format=metadata_format,  # Pass the format
            )

            # Process chunks one by one to test true streaming behavior
            processed_chunks = []
            for chunk in chunks:
                processed_chunk = handler.process_chunk(chunk)
                processed_chunks.append(processed_chunk)

            # Finalize to handle any remaining accumulated text
            final_chunk = handler.finalize()
            if final_chunk:
                processed_chunks.append(final_chunk)

            # Combine all processed chunks
            processed_text = "".join(processed_chunks)

            # Verify and Extract metadata from the combined processed text
            extracted_payload, is_valid, extracted_signer_id = UnicodeMetadata.verify_and_extract_metadata(processed_text, test_public_key_provider)

            # Check if metadata was extracted and verified correctly
            assert is_valid is True, f"Verification failed for {provider}, target={target.name}, first_only={encode_first_only}"
            assert extracted_signer_id == signer_id, f"Signer ID mismatch for {provider}, target={target.name}, first_only={encode_first_only}"
            assert extracted_payload is not None
            assert extracted_payload.get("format") == metadata_format

            # Check that the model_id in the payload matches what we embedded
            assert (
                extracted_payload.get("model_id") == metadata["model_id"]
            ), f"Model ID mismatch for {provider}, target={target.name}, first_only={encode_first_only}"

    @pytest.mark.skip(reason="HMAC functionality removed in favor of signatures.")
    @pytest.mark.parametrize("provider,chunks", STREAMING_CHUNKS.items())
    def test_streaming_with_hmac(self, provider, chunks):
        """Test streaming with HMAC verification."""
        pass  # Test skipped


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
