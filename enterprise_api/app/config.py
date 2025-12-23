"""
Configuration module for Encypher Enterprise API.
Uses Pydantic Settings for environment variable management.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"  # development | preview | production

    # Databases (Two-Database Architecture)
    # Core DB: Customer/billing data (organizations, api_keys, etc.)
    core_database_url: Optional[str] = None
    # Content DB: Verification data (documents, merkle trees, etc.)
    content_database_url: Optional[str] = None
    # Legacy single database URL (for backward compatibility)
    database_url: Optional[str] = None
    
    # Redis (for session management)
    redis_url: str = "redis://localhost:6379/0"

    # Encryption (for private key storage)
    # These should be bytes, but we'll handle conversion from hex strings
    key_encryption_key: str
    encryption_nonce: str

    # SSL.com (optional for staging/development)
    ssl_com_api_key: Optional[str] = None
    ssl_com_account_key: Optional[str] = None
    ssl_com_api_url: str = "https://api.ssl.com/v1"
    ssl_com_product_id: Optional[str] = None

    # API
    api_base_url: str = "https://api.encypherai.com"

    # API docs exposure
    enable_public_api_docs: bool = False

    # Service URLs
    coalition_service_url: str = "http://localhost:8009"
    auth_service_url: str = "http://localhost:8001"
    key_service_url: str = "http://localhost:8003"

    # Rate limiting
    rate_limit_per_minute: int = 60
    batch_worker_limit: int = 8
    batch_max_items: int = 100

    # Domains
    marketing_domain: str = "encypher.ai"
    infrastructure_domain: str = "encypherai.com"
    
    # CORS - comma-separated list of allowed origins
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    # Demo / sandbox API key support
    demo_api_key: Optional[str] = None
    demo_organization_id: str = "org_demo"
    demo_organization_name: str = "Encypher Demo Organization"
    demo_private_key_hex: Optional[str] = None
    # SECRET_KEY is an alias for demo_private_key_hex (used in Railway production)
    secret_key: Optional[str] = None
    # Legacy PEM format keys (for old content verification)
    demo_private_key_pem: Optional[str] = None
    demo_public_key_pem: Optional[str] = None

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def key_encryption_key_bytes(self) -> bytes:
        """Convert hex string to bytes for encryption key."""
        return bytes.fromhex(self.key_encryption_key)

    @property
    def encryption_nonce_bytes(self) -> bytes:
        """Convert hex string to bytes for encryption nonce."""
        return bytes.fromhex(self.encryption_nonce)

    @property
    def core_database_url_resolved(self) -> str:
        """Get core database URL, falling back to legacy database_url."""
        return self.core_database_url or self.database_url or ""
    
    @property
    def content_database_url_resolved(self) -> str:
        """Get content database URL, falling back to legacy database_url."""
        return self.content_database_url or self.database_url or ""

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

    @property
    def demo_private_key_bytes(self) -> Optional[bytes]:
        """Return demo private key bytes if configured."""
        if not self.demo_private_key_hex:
            return None
        # Strip whitespace and validate hex string
        hex_str = self.demo_private_key_hex.strip()
        if not hex_str:
            return None
        return bytes.fromhex(hex_str)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
