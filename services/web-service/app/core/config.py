from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EncypherAI Web Service"
    API_V1_STR: str = "/api/v1"

    # Security - MUST be set via environment variable in production
    SECRET_KEY: str = ""  # noqa: S105 - Default empty, must be set via env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Default Next.js dev server
        "https://encypherai.com",
        "https://www.encypherai.com",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database - credentials should be set via environment variables
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""  # noqa: S105 - Must be set via env
    POSTGRES_DB: str = "encypher_web"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        port = values.data.get("POSTGRES_PORT", 5432)
        host = f"{values.data.get('POSTGRES_SERVER')}:{port}"
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=host,
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""  # noqa: S105
    EMAILS_ENABLED: bool = False
    EMAIL_FROM_EMAIL: str = "noreply@encypherai.com"
    EMAIL_FROM_NAME: str = "Encypher"
    SALES_EMAIL: str = "sales@encypherai.com"
    DEMO_EMAIL: str = "demo@encypherai.com"

    # Web Analytics
    ANALYTICS_ENABLED: bool = True
    ANALYTICS_DB_URI: Optional[PostgresDsn] = None

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
