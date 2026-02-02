"""
Configuration management for Key Service

Environment Variables:
- Shared: DATABASE_URL, REDIS_URL, JWT_SECRET_KEY, ALLOWED_ORIGINS, AUTH_SERVICE_URL
- Service-specific: KEY_PREFIX, KEY_LENGTH
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "key-service"
    SERVICE_PORT: int = 8003
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # ===========================================
    # SHARED: Database (from shared vars)
    # ===========================================
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ===========================================
    # SHARED: Redis (from shared vars)
    # ===========================================
    REDIS_URL: str = "redis://localhost:6379"

    # ===========================================
    # SHARED: CORS (from shared vars)
    # ===========================================
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # ===========================================
    # SHARED: Internal Service URLs (from shared vars)
    # ===========================================
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ENTERPRISE_API_URL: str = "http://enterprise-api:8000"

    # ===========================================
    # SHARED: Internal Service Authentication (from shared vars)
    # ===========================================
    INTERNAL_SERVICE_TOKEN: str = ""

    # ===========================================
    # SERVICE-SPECIFIC: Key Generation
    # ===========================================
    KEY_PREFIX: str = "ency_"
    KEY_LENGTH: int = 32

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
