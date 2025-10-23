"""
Tests for the Settings class.
"""

import json
import os
import tempfile

from encypher.config.settings import Settings
from encypher.core.unicode_metadata import MetadataTarget


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings."""
        settings = Settings()

        # Check default values
        assert settings.get("metadata_target") == "whitespace"
        assert settings.get("encode_first_chunk_only") is True
        assert settings.get("timestamp_format") == "%Y-%m-%dT%H:%M%z"
        assert settings.get("logging_level") == "INFO"
        assert settings.get("report_usage_metrics") is False

    def test_load_from_file(self):
        """Test loading settings from a file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as temp_file:
            config = {
                "metadata_target": "punctuation",
                "encode_first_chunk_only": False,
                "logging_level": "DEBUG",
            }
            json.dump(config, temp_file)
            temp_file_path = temp_file.name

        try:
            # Load settings from the file
            settings = Settings(config_file=temp_file_path)

            # Check values from the file
            assert settings.get("metadata_target") == "punctuation"
            assert settings.get("encode_first_chunk_only") is False
            assert settings.get("logging_level") == "DEBUG"

            # Check default values for fields not in the file
            assert settings.get("timestamp_format") == "%Y-%m-%dT%H:%M%z"
            assert settings.get("report_usage_metrics") is False
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_load_from_env(self, monkeypatch):
        """Test loading settings from environment variables."""
        # Set environment variables
        monkeypatch.setenv("ENCYPHER_METADATA_TARGET", "first_letter")
        monkeypatch.setenv("ENCYPHER_ENCODE_FIRST_CHUNK_ONLY", "false")
        monkeypatch.setenv("ENCYPHER_LOGGING_LEVEL", "WARNING")

        # Load settings
        settings = Settings()

        # Check values from environment variables
        assert settings.get("metadata_target") == "first_letter"
        assert settings.get("encode_first_chunk_only") is False
        assert settings.get("logging_level") == "WARNING"

    def test_env_overrides_file(self, monkeypatch):
        """Test that environment variables override file settings."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as temp_file:
            config = {
                "metadata_target": "punctuation",
                "encode_first_chunk_only": False,
                "logging_level": "DEBUG",
            }
            json.dump(config, temp_file)
            temp_file_path = temp_file.name

        try:
            # Set environment variables
            monkeypatch.setenv("ENCYPHER_METADATA_TARGET", "first_letter")

            # Load settings
            settings = Settings(config_file=temp_file_path)

            # Check that environment variables override file settings
            assert settings.get("metadata_target") == "first_letter"  # From env
            assert settings.get("encode_first_chunk_only") is False  # From file
            assert settings.get("logging_level") == "DEBUG"  # From file
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_get_metadata_target(self):
        """Test getting metadata target as enum."""
        # Test with valid target
        settings = Settings()
        settings.config["metadata_target"] = "punctuation"

        target = settings.get_metadata_target()
        assert target == MetadataTarget.PUNCTUATION

        # Test with invalid target
        settings.config["metadata_target"] = "invalid_target"

        target = settings.get_metadata_target()
        assert target == MetadataTarget.WHITESPACE  # Default

    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = Settings()

        # Modify some settings
        settings.config["metadata_target"] = "punctuation"

        # Convert to dictionary
        config_dict = settings.to_dict()

        # Check dictionary values
        assert config_dict["metadata_target"] == "punctuation"
        assert config_dict["encode_first_chunk_only"] is True
        assert config_dict["timestamp_format"] == "%Y-%m-%dT%H:%M%z"
        assert config_dict["logging_level"] == "INFO"
        assert config_dict["report_usage_metrics"] is False
