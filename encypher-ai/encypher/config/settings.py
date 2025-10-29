"""
Configuration settings for EncypherAI.

This module provides a centralized configuration system that supports
loading from environment variables and configuration files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from encypher.core.unicode_metadata import MetadataTarget


class Settings:
    """
    Settings class for EncypherAI configuration.

    This class handles loading configuration from environment variables
    and configuration files, with sensible defaults.
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        "metadata_target": "whitespace",
        "encode_first_chunk_only": True,
        "hmac_secret_key": "",
        "timestamp_format": "%Y-%m-%dT%H:%M%z",
        "logging_level": "INFO",
        "report_usage_metrics": False,
    }

    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = None,
        env_prefix: str = "ENCYPHER_",
    ):
        """
        Initialize settings from environment variables and/or config file.

        Args:
            config_file: Path to configuration file (JSON)
            env_prefix: Prefix for environment variables
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.env_prefix = env_prefix

        # Load from config file if provided
        if config_file:
            self._load_from_file(config_file)

        # Override with environment variables
        self._load_from_env()

    def _load_from_file(self, config_file: Union[str, Path]) -> None:
        """
        Load configuration from a JSON file.

        Args:
            config_file: Path to configuration file
        """
        config_path = Path(config_file)
        if config_path.exists() and config_path.is_file():
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}")

    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.

        Environment variables take precedence over config file values.
        """
        # Map of config keys to environment variable names
        env_map = {
            "metadata_target": f"{self.env_prefix}METADATA_TARGET",
            "encode_first_chunk_only": f"{self.env_prefix}ENCODE_FIRST_CHUNK_ONLY",
            "hmac_secret_key": f"{self.env_prefix}HMAC_SECRET_KEY",
            "timestamp_format": f"{self.env_prefix}TIMESTAMP_FORMAT",
            "logging_level": f"{self.env_prefix}LOGGING_LEVEL",
            "report_usage_metrics": f"{self.env_prefix}REPORT_USAGE_METRICS",
        }

        # Update config with environment variables if they exist
        for config_key, env_var in env_map.items():
            if env_var in os.environ:
                # Handle boolean values
                if config_key in ["encode_first_chunk_only", "report_usage_metrics"]:
                    self.config[config_key] = os.environ[env_var].lower() in [
                        "true",
                        "1",
                        "yes",
                        "y",
                    ]
                else:
                    self.config[config_key] = os.environ[env_var]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def get_metadata_target(self) -> MetadataTarget:
        """
        Get the metadata target as an enum value.

        Returns:
            MetadataTarget enum value
        """
        target_str = self.config.get("metadata_target", "whitespace")
        # Ensure target_str is a string before calling .upper()
        if isinstance(target_str, str):
            try:
                return MetadataTarget[target_str.upper()]
            except KeyError:
                return MetadataTarget.WHITESPACE  # Default if string is invalid enum key
        else:
            # Default if the config value wasn't a string
            return MetadataTarget.WHITESPACE

    def get_hmac_secret_key(self) -> str:
        """
        Get the HMAC secret key.

        Returns:
            HMAC secret key
        """
        return str(self.config.get("hmac_secret_key", ""))

    def get_encode_first_chunk_only(self) -> bool:
        """
        Get whether to encode metadata only in the first chunk.

        Returns:
            True if encoding only the first chunk, False otherwise
        """
        return bool(self.config.get("encode_first_chunk_only", True))

    def get_timestamp_format(self) -> str:
        """
        Get the timestamp format.

        Returns:
            Timestamp format string
        """
        return str(self.config.get("timestamp_format", "%Y-%m-%dT%H:%M%z"))

    def get_logging_level(self) -> str:
        """
        Get the logging level.

        Returns:
            Logging level string
        """
        return str(self.config.get("logging_level", "INFO"))

    def get_report_usage_metrics(self) -> bool:
        """
        Get whether to report usage metrics.

        Returns:
            True if reporting usage metrics, False otherwise
        """
        return bool(self.config.get("report_usage_metrics", False))

    def to_dict(self) -> Dict[str, Any]:
        """
        Get the configuration as a dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()
