"""TrustMark neural watermarking service.

TrustMark is Adobe Research's neural watermarking library.
GitHub: https://github.com/adobe/trustmark (Apache 2.0)

Install in production:
  pip install trustmark torch torchvision
  OR use the optional-requirements.txt in this directory.

If trustmark is not installed, all methods raise ServiceUnavailableError.
"""
import logging
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


class ServiceUnavailableError(Exception):
    pass


def _mime_to_pil_format(mime_type: str) -> str:
    mapping = {
        "image/jpeg": "JPEG",
        "image/jpg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
    }
    return mapping.get(mime_type.lower(), "JPEG")


class TrustMarkService:
    def __init__(self) -> None:
        self._model: Optional[object] = None
        self._available: bool = False

    def load_model(self) -> None:
        """Load TrustMark model. Sets _available=False if trustmark not installed."""
        try:
            from trustmark import TrustMark  # type: ignore[import]
            from PIL import Image  # noqa: F401

            self._model = TrustMark(use_ECC=True)
            self._available = True
            logger.info("TrustMark model loaded successfully")
        except ImportError as e:
            logger.warning("TrustMark not installed: %s", e)
            self._available = False
        except Exception as e:
            logger.error("TrustMark model load failed: %s", e)
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def encode(self, image_bytes: bytes, mime_type: str, message_bits: str) -> tuple[bytes, float]:
        """Embed watermark into image.

        Args:
            image_bytes: Raw image bytes.
            mime_type: MIME type string.
            message_bits: 26-char hex string (100-bit message).

        Returns:
            Tuple of (watermarked_bytes, confidence).

        Raises:
            ServiceUnavailableError: If TrustMark model is not loaded.
        """
        if not self._available or self._model is None:
            raise ServiceUnavailableError(
                "TrustMark model not available. Install trustmark and torch."
            )
        from PIL import Image

        # Convert hex message to binary string (TrustMark expects a binary string).
        msg_int = int(message_bits, 16)
        binary_str = format(msg_int, "0100b")[:100]  # 100 bits

        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        # TrustMark.encode() returns a PIL Image.
        watermarked_img = self._model.encode(img, binary_str)  # type: ignore[union-attr]

        fmt = _mime_to_pil_format(mime_type)
        buf = BytesIO()
        save_kwargs: dict = {"format": fmt}
        if fmt == "JPEG":
            save_kwargs["quality"] = 95
        watermarked_img.save(buf, **save_kwargs)
        return buf.getvalue(), 1.0

    def decode(self, image_bytes: bytes) -> tuple[bool, Optional[str], float]:
        """Detect watermark in image.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            Tuple of (detected, message_bits_hex, confidence).
            message_bits_hex is None when detected is False.

        Raises:
            ServiceUnavailableError: If TrustMark model is not loaded.
        """
        if not self._available or self._model is None:
            raise ServiceUnavailableError(
                "TrustMark model not available. Install trustmark and torch."
            )
        from PIL import Image

        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        # TrustMark.decode() returns (secret, detected, confidence).
        secret, detected, confidence = self._model.decode(img)  # type: ignore[union-attr]

        if not detected:
            return False, None, float(confidence)

        # Convert binary string back to 26-char hex.
        msg_int = int(secret[:100], 2)
        msg_hex = format(msg_int, "026x")
        return True, msg_hex, float(confidence)
