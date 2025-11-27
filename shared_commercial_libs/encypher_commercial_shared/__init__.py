# __init__.py for encypher_commercial_shared

__version__ = "0.1.0"

# Import and expose the high-level API
from .high_level import EncypherAI, VerificationResult

# Email module is available as encypher_commercial_shared.email
# Import directly: from encypher_commercial_shared.email import send_email, EmailConfig

__all__ = ["EncypherAI", "VerificationResult"]
