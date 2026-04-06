from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    WATERMARK_SECRET: str = "encypher-video-wm-default"
    DEFAULT_WSR_DB: float = -30.0  # watermark-to-signal ratio in dB
    BLOCK_FRAMES: int = 300  # frames per processing block (10 sec at 30fps)
    PAYLOAD_BITS: int = 64
    ECC_ENABLED: bool = True
    MAX_VIDEO_SIZE_BYTES: int = 524_288_000  # 500 MB

    model_config = {"env_prefix": "VIDEO_WM_"}


settings = Settings()
