"""Configuration for Alert Service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "alert-service"
    SERVICE_PORT: int = 8011
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://localhost/alert_service"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5

    # Redis (for consuming metrics stream)
    REDIS_URL: str = "redis://localhost:6379"

    # Discord webhook for notifications
    DISCORD_WEBHOOK_URL: str = ""

    # Discord bot (slash commands)
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""
    DISCORD_STATUS_CHANNEL_ID: str = ""

    # Claude Code investigation trigger
    CC_WEBHOOK_URL: str = ""
    CC_WEBHOOK_SECRET: str = ""
    CC_AUTO_INVESTIGATE: bool = True
    ALERT_SERVICE_URL: str = ""

    # Email escalation (optional)
    NOTIFICATION_SERVICE_URL: str = ""
    ALERT_EMAIL_RECIPIENT: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Alert tuning
    SPIKE_WINDOW_SECONDS: int = 300
    SPIKE_MULTIPLIER: float = 3.0
    SPIKE_MIN_EVENTS: int = 5
    AUTO_RESOLVE_AFTER_MINUTES: int = 30
    PATTERN_CHECK_INTERVAL_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
