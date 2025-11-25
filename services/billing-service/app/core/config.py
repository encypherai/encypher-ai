"""Configuration management for Billing Service"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    SERVICE_NAME: str = "billing-service"
    SERVICE_PORT: int = 8007
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    REDIS_URL: str = "redis://localhost:6379/5"
    REDIS_DB: int = 5
    
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8006"
    
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Stripe Configuration
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CONNECT_WEBHOOK_SECRET: str = ""
    
    # Stripe Price IDs (set after creating products in Stripe)
    STRIPE_PRICE_PROFESSIONAL_MONTHLY: str = ""
    STRIPE_PRICE_PROFESSIONAL_ANNUAL: str = ""
    STRIPE_PRICE_BUSINESS_MONTHLY: str = ""
    STRIPE_PRICE_BUSINESS_ANNUAL: str = ""
    
    API_GATEWAY_URL: str = "http://localhost:8000"
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    PROMETHEUS_PORT: int = 9007
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
