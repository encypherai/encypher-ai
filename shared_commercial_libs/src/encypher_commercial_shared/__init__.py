"""
EncypherAI Commercial Shared Library

Shared functionality for EncypherAI commercial tools and services.

Modules:
    core: High-level EncypherAI wrapper (EncypherAI, VerificationResult, utils)
    email: Email sending and templates (EmailConfig, send_email, etc.)
    db: Database utilities (ensure_database_ready, check_database_connection)

Usage:
    # Core functionality (for CLI tools)
    from encypher_commercial_shared import EncypherAI, VerificationResult
    from encypher_commercial_shared.core import scan_directory, generate_report
    
    # Email functionality (for services)
    from encypher_commercial_shared.email import EmailConfig, send_email
    
    # Database startup (for microservices)
    from encypher_commercial_shared.db import ensure_database_ready
"""

__version__ = "0.2.1"

# Re-export core API for backward compatibility
from .core import EncypherAI, VerificationResult

__all__ = [
    "__version__",
    "EncypherAI",
    "VerificationResult",
]
