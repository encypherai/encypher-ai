"""
Configuration management for Verification Service

Environment Variables:
- Shared: CONTENT_DATABASE_URL, REDIS_URL, ALLOWED_ORIGINS, AUTH_SERVICE_URL, KEY_SERVICE_URL
- Service-specific: ENCODING_SERVICE_URL
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "verification-service"
    SERVICE_PORT: int = 8005
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # ===========================================
    # SHARED: Database (from shared vars)
    # Note: Verification service uses CONTENT database
    # ===========================================
    DATABASE_URL: str  # Points to content DB
    CONTENT_DATABASE_URL: str = ""  # Alias, falls back to DATABASE_URL
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ===========================================
    # SHARED: Redis (from shared vars)
    # ===========================================
    REDIS_URL: str = "redis://localhost:6379"

    # ===========================================
    # SHARED: CORS (from shared vars)
    # Note: Verification is public, allows all origins
    # ===========================================
    ALLOWED_ORIGINS: str = "*"

    # ===========================================
    # SHARED: Internal Service URLs (from shared vars)
    # ===========================================
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    KEY_SERVICE_URL: str = "http://localhost:8003"
    ENCODING_SERVICE_URL: str = "http://localhost:8004"
    ENTERPRISE_API_URL: str = "http://localhost:9000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def db_url(self) -> str:
        """Get the appropriate database URL"""
        return self.CONTENT_DATABASE_URL or self.DATABASE_URL


settings = Settings()
