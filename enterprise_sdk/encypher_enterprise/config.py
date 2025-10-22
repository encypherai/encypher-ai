"""
Configuration for Encypher Enterprise SDK.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class EncypherConfig(BaseSettings):
    """SDK configuration from environment variables."""

    encypher_api_key: Optional[str] = None
    encypher_base_url: str = "https://api.encypherai.com"
    encypher_timeout: float = 30.0
    encypher_max_retries: int = 3

    class Config:
        env_prefix = "ENCYPHER_"
        case_sensitive = False


def get_config() -> EncypherConfig:
    """Get SDK configuration."""
    return EncypherConfig()
