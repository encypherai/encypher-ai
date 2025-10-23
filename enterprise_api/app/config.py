"""
Configuration module for Encypher Enterprise API.
Uses Pydantic Settings for environment variable management.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"  # development | preview | production

    # Database
    database_url: str

    # Encryption (for private key storage)
    # These should be bytes, but we'll handle conversion from hex strings
    key_encryption_key: str
    encryption_nonce: str

    # SSL.com
    ssl_com_api_key: str
    ssl_com_account_key: Optional[str] = None
    ssl_com_api_url: str = "https://api.ssl.com/v1"
    ssl_com_product_id: Optional[str] = None

    # API
    api_base_url: str = "https://api.encypherai.com"

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Domains
    marketing_domain: str = "encypher.ai"
    infrastructure_domain: str = "encypherai.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def key_encryption_key_bytes(self) -> bytes:
        """Convert hex string to bytes for encryption key."""
        return bytes.fromhex(self.key_encryption_key)

    @property
    def encryption_nonce_bytes(self) -> bytes:
        """Convert hex string to bytes for encryption nonce."""
        return bytes.fromhex(self.encryption_nonce)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_preview(self) -> bool:
        """Check if running in preview mode."""
        return self.environment == "preview"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
