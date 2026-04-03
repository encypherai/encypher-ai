"""
Configuration management for Notification Service

Environment Variables:
- Shared: DATABASE_URL, REDIS_URL, ALLOWED_ORIGINS, AUTH_SERVICE_URL, MARKETING_SITE_URL, DASHBOARD_URL
- Service-specific: SMTP_* (email configuration)
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8008
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # ===========================================
    # SHARED: Database (from shared vars)
    # ===========================================
    DATABASE_URL: str

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

    # ===========================================
    # SHARED: Frontend URLs (from shared vars)
    # ===========================================
    MARKETING_SITE_URL: str = "http://localhost:3000"
    DASHBOARD_URL: str = "http://localhost:3001"

    # ===========================================
    # SERVICE-SPECIFIC: Email Configuration
    # ===========================================
    SMTP_HOST: str = "smtp.zoho.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_TLS: bool = True
    EMAIL_FROM: str = "support@encypher.com"
    EMAIL_FROM_NAME: str = "Support - Encypher"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
