"""
Integration tests for EncypherAI with LiteLLM.

Note: These tests require API keys for the respective providers.
They will be skipped if the API keys are not available.
"""

import os
from datetime import datetime, timezone

import litellm
import pytest

from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# Skip all tests if no API keys are available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not available")
class TestOpenAIIntegration:
    """Integration tests with OpenAI models."""

    def test_openai_completion(self):
        """Test with OpenAI completion."""
        # Set up LiteLLM
        litellm.api_key = OPENAI_API_KEY

        # Generate completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short paragraph about AI ethics."},
        ]

        response = litellm.completion(model="gpt-3.5-turbo", messages=messages)

        # Extract content
        content = response.choices[0].message.content

        # Prepare metadata
        metadata = {
            "model_id": "gpt-3.5-turbo",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": response.id,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

        # Encode metadata
        encoded_content = UnicodeMetadata.embed_metadata(
            text=content,
            model_id=metadata["model_id"],
            timestamp=metadata["timestamp"],
            target="whitespace",
            custom_metadata={k: v for k, v in metadata.items() if k not in ["model_id", "timestamp"]},
        )

        # Extract metadata
        extracted = UnicodeMetadata.extract_metadata(encoded_content)

        # Assertions
        assert extracted["model_id"] == metadata["model_id"]
        assert extracted["timestamp"] == metadata["timestamp"]
        assert extracted["request_id"] == metadata["request_id"]
        assert "usage" in extracted

    @pytest.mark.skipif(True, reason="Streaming tests are expensive and time-consuming")
    def test_openai_streaming(self):
        """Test with OpenAI streaming."""
        # Set up LiteLLM
        litellm.api_key = OPENAI_API_KEY

        # Prepare metadata
        metadata = {
            "model_id": "gpt-3.5-turbo",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": f"req_{int(datetime.now().timestamp())}",
        }

        # Initialize streaming handler
        handler = StreamingHandler(metadata=metadata, target="whitespace", encode_first_chunk_only=True)

        # Generate streaming completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short paragraph about AI ethics."},
        ]

        stream = litellm.completion(model="gpt-3.5-turbo", messages=messages, stream=True)

        # Process streaming chunks
        processed_chunks = []
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                processed_chunk = handler.process_chunk(content)
                processed_chunks.append(processed_chunk)

        # Combine all chunks
        full_text = "".join(processed_chunks)

        # Extract metadata
        extracted = UnicodeMetadata.extract_metadata(full_text)

        # Assertions
        assert extracted["model_id"] == metadata["model_id"]
        assert extracted["timestamp"] == metadata["timestamp"]
        assert extracted["request_id"] == metadata["request_id"]


@pytest.mark.skipif(not ANTHROPIC_API_KEY, reason="Anthropic API key not available")
class TestAnthropicIntegration:
    """Integration tests with Anthropic models."""

    def test_anthropic_completion(self):
        """Test with Anthropic completion."""
        # Set up LiteLLM
        litellm.anthropic_api_key = ANTHROPIC_API_KEY

        # Generate completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short paragraph about AI ethics."},
        ]

        response = litellm.completion(model="claude-3-sonnet-20240229", messages=messages)

        # Extract content
        content = response.choices[0].message.content

        # Prepare metadata
        metadata = {
            "model_id": "claude-3-sonnet-20240229",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": response.id,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

        # Encode metadata
        encoded_content = UnicodeMetadata.embed_metadata(
            text=content,
            model_id=metadata["model_id"],
            timestamp=metadata["timestamp"],
            target="whitespace",
            custom_metadata={k: v for k, v in metadata.items() if k not in ["model_id", "timestamp"]},
        )

        # Extract metadata
        extracted = UnicodeMetadata.extract_metadata(encoded_content)

        # Assertions
        assert extracted["model_id"] == metadata["model_id"]
        assert extracted["timestamp"] == metadata["timestamp"]
        assert extracted["request_id"] == metadata["request_id"]
        assert "usage" in extracted


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
