"""
Configuration management for Billing Service

Environment Variables:
- Shared: DATABASE_URL, REDIS_URL, ALLOWED_ORIGINS, AUTH_SERVICE_URL
- Service-specific: STRIPE_* (all Stripe configuration)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # ===========================================
    # SERVICE CONFIGURATION (service-specific)
    # ===========================================
    SERVICE_NAME: str = "billing-service"
    SERVICE_PORT: int = 8007
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
    ANALYTICS_SERVICE_URL: str = "http://localhost:8006"
    COALITION_SERVICE_URL: str = "http://localhost:8009"
    DASHBOARD_URL: str = "http://localhost:3001"
    INTERNAL_SERVICE_TOKEN: str = ""

    # ===========================================
    # SERVICE-SPECIFIC: Stripe Configuration
    # ===========================================
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CONNECT_WEBHOOK_SECRET: str = ""
    STRIPE_BILLING_PORTAL_CONFIG_ID: str = ""

    # Stripe Price IDs (set after creating products in Stripe)
    STRIPE_PRICE_PROFESSIONAL_MONTHLY: str = ""
    STRIPE_PRICE_PROFESSIONAL_ANNUAL: str = ""
    STRIPE_PRICE_BUSINESS_MONTHLY: str = ""
    STRIPE_PRICE_BUSINESS_ANNUAL: str = ""
    STRIPE_PRICE_BULK_ARCHIVE_BACKFILL: str = ""

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
    def stripe_enabled(self) -> bool:
        """Check if Stripe billing is fully configured."""
        return bool(self.STRIPE_API_KEY)

    def validate_stripe_config(self) -> list[str]:
        """Validate Stripe configuration at startup. Returns list of warnings."""
        warnings = []

        if not self.STRIPE_API_KEY:
            warnings.append("STRIPE_API_KEY not set - billing disabled")
            return warnings

        # Check price IDs - warn but don't fail
        price_checks = [
            ("STRIPE_PRICE_PROFESSIONAL_MONTHLY", self.STRIPE_PRICE_PROFESSIONAL_MONTHLY),
            ("STRIPE_PRICE_PROFESSIONAL_ANNUAL", self.STRIPE_PRICE_PROFESSIONAL_ANNUAL),
            ("STRIPE_PRICE_BUSINESS_MONTHLY", self.STRIPE_PRICE_BUSINESS_MONTHLY),
            ("STRIPE_PRICE_BUSINESS_ANNUAL", self.STRIPE_PRICE_BUSINESS_ANNUAL),
            ("STRIPE_PRICE_BULK_ARCHIVE_BACKFILL", self.STRIPE_PRICE_BULK_ARCHIVE_BACKFILL),
        ]

        missing = [name for name, value in price_checks if not value]
        if missing:
            warnings.append(f"Missing Stripe price IDs (features disabled): {', '.join(missing)}")

        return warnings


settings = Settings()

# Log warnings for missing Stripe config but don't crash
_stripe_warnings = settings.validate_stripe_config()
if _stripe_warnings:
    import logging

    _logger = logging.getLogger(__name__)
    for w in _stripe_warnings:
        _logger.warning(w)
