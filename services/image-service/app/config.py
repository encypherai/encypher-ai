from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8010
    LOG_LEVEL: str = "INFO"
    # Empty string means download from HuggingFace on first use.
    TRUSTMARK_MODEL_PATH: str = ""
    # HMAC secret for message generation.
    TRUSTMARK_SECRET: str = ""
    MAX_IMAGE_SIZE_BYTES: int = 10_485_760  # 10 MB

    class Config:
        env_file = ".env"


settings = Settings()
