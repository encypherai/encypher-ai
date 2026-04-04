from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8011
    LOG_LEVEL: str = "INFO"
    # HMAC secret for payload generation (shared with enterprise API).
    WATERMARK_SECRET: str = ""
    MAX_AUDIO_SIZE_BYTES: int = 524_288_000  # 500 MB
    # Default SNR threshold in dB (negative). -20 for speech, -30 for music.
    DEFAULT_SNR_DB: float = -20.0
    # Payload length in bits.
    PAYLOAD_BITS: int = 64
    # Chip rate: number of STFT bins per payload bit.
    CHIP_RATE: int = 8

    class Config:
        env_file = ".env"


settings = Settings()
