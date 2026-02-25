"""
Configuration management for Auth Service

Environment Variables:
- Shared (from Railway shared vars): DATABASE_URL, REDIS_URL, JWT_SECRET_KEY,
  ALLOWED_ORIGINS, MARKETING_SITE_URL, DASHBOARD_URL
- Service-specific: SMTP_*, GOOGLE_*, GITHUB_*, etc.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8001
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # ===========================================
    # DATABASE CONFIGURATION
    # ===========================================
    # Each service gets its own DATABASE_URL pointing to its own database
    # In dev: postgresql://...@postgres:5432/encypher_auth
    # In prod: Separate PostgreSQL instance per service
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ===========================================
    # SHARED: Redis (from shared vars)
    # ===========================================
    REDIS_URL: str = "redis://localhost:6379"

    # ===========================================
    # SHARED: JWT Configuration (from shared vars)
    # ===========================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    # Extended session for better UX: 8 hour access, 30 day refresh
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ===========================================
    # SHARED: CORS (from shared vars)
    # ===========================================
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # ===========================================
    # SHARED: Frontend URLs (from shared vars)
    # Used for email links, redirects, etc.
    # ===========================================
    MARKETING_SITE_URL: str = "http://localhost:3000"
    DASHBOARD_URL: str = "http://localhost:3001"
    API_URL: str = "http://localhost:8000"

    # ===========================================
    # SERVICE-SPECIFIC: OAuth Providers
    # ===========================================
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # ===========================================
    # SERVICE-SPECIFIC: Email Configuration
    # ===========================================
    SMTP_HOST: str = "smtp.zoho.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_TLS: bool = True
    EMAIL_FROM: str = "noreply@encypherai.com"
    EMAIL_FROM_NAME: str = "Encypher"
    ADMIN_EMAIL: str = "erik.svilich@encypherai.com"
    SUPPORT_EMAIL: str = "support@encypherai.com"  # BCC for signup notifications
    SEND_STARTUP_EMAIL: bool = True

    # ===========================================
    # SERVICE-SPECIFIC: Token Expiration
    # ===========================================
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # ===========================================
    # SERVICE-SPECIFIC: Auth Limits
    # ===========================================
    AUTH_MAX_PASSWORD_LENGTH: int = 256
    AUTH_MAX_REQUEST_BODY_BYTES: int = 65536

    # ===========================================
    # SERVICE-SPECIFIC: Bot/Abuse Protection (Turnstile)
    # ===========================================
    TURNSTILE_ENABLED: bool = False
    TURNSTILE_SECRET_KEY: str = ""
    TURNSTILE_VERIFY_URL: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    TURNSTILE_REQUIRE_SIGNUP: bool = True
    TURNSTILE_REQUIRE_LOGIN: bool = True

    # ===========================================
    # SERVICE-SPECIFIC: MFA / Passkeys
    # ===========================================
    MFA_ISSUER: str = "Encypher"
    MFA_BACKUP_CODES_COUNT: int = 8
    MFA_CHALLENGE_EXPIRE_MINUTES: int = 10
    PASSKEY_ENABLED: bool = True
    PASSKEY_RP_ID: str = "localhost"
    PASSKEY_RP_NAME: str = "Encypher"
    PASSKEY_EXPECTED_ORIGIN: str = "http://localhost:3001"

    # ===========================================
    # INTERNAL SERVICE URLS (for service-to-service)
    # ===========================================
    COALITION_SERVICE_URL: str = "http://localhost:8009"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8008"
    BILLING_SERVICE_URL: str = "http://localhost:8007"
    WEB_SERVICE_URL: str = "http://localhost:8002"
    INTERNAL_SERVICE_TOKEN: str = ""

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

    @property
    def FRONTEND_URL(self) -> str:
        """Alias for MARKETING_SITE_URL for backward compatibility"""
        return self.MARKETING_SITE_URL


# Global settings instance
settings = Settings()
