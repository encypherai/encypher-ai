"""
Configuration for API Gateway
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # CORS
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,https://encypherai.com,https://www.encypherai.com"
    )

    # Downstream services
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8006"
    ENTERPRISE_API_URL: str = "http://localhost:9000"

    # Proxy timeouts (seconds)
    PROXY_CONNECT_TIMEOUT: int = 5
    PROXY_READ_TIMEOUT: int = 30
    PROXY_WRITE_TIMEOUT: int = 30

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
