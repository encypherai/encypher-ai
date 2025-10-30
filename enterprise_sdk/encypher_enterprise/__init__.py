"""
Encypher Enterprise SDK - Python client for C2PA content signing.
"""
__version__ = "1.0.0"

from .client import EncypherClient
from .async_client import AsyncEncypherClient
from .streaming import StreamingSigner, AsyncStreamingSigner, sign_stream, async_sign_stream
from .batch import RepositorySigner, FileMetadata, SigningResult, BatchSigningResult
from .state import StateManager, FileState
from .metadata_providers import GitMetadataProvider, FrontmatterMetadataProvider, CombinedMetadataProvider
from .reports import ReportGenerator, generate_verification_badge
from .verification import RepositoryVerifier, VerificationResult, BatchVerificationResult
from .diff import DiffGenerator, VersionTracker, VersionInfo, DiffStats, generate_diff_report
from .language import LanguageDetector, TranslationManager, LanguageInfo, TranslationLink
from .bulk_update import BulkMetadataUpdater, MetadataValidator, MetadataUpdate, UpdateResult, BulkUpdateResult
from .expiration import ExpirationTracker, SignatureRenewer, ExpirationMonitor, ExpirationInfo, RenewalResult, RenewalPolicy
from .analytics import MetricsCollector, DashboardExporter, OperationMetric, UsageStats, PerformanceMetrics
from .binary import BinaryFileSigner, TextExtractor, BinaryFileInfo
from .models import (
    SignResponse,
    VerifyResponse,
    LookupResponse,
    StatsResponse,
)
from .exceptions import (
    EncypherError,
    AuthenticationError,
    QuotaExceededError,
    SigningError,
    VerificationError,
    APIError,
    ConfigurationError,
    StreamingError,
)

__all__ = [
    # Clients
    "EncypherClient",
    "AsyncEncypherClient",
    # Streaming
    "StreamingSigner",
    "AsyncStreamingSigner",
    "sign_stream",
    "async_sign_stream",
    # Batch operations
    "RepositorySigner",
    "FileMetadata",
    "SigningResult",
    "BatchSigningResult",
    # State management
    "StateManager",
    "FileState",
    # Metadata providers
    "GitMetadataProvider",
    "FrontmatterMetadataProvider",
    "CombinedMetadataProvider",
    # Reports
    "ReportGenerator",
    "generate_verification_badge",
    # Verification
    "RepositoryVerifier",
    "VerificationResult",
    "BatchVerificationResult",
    # Diff & Versioning
    "DiffGenerator",
    "VersionTracker",
    "VersionInfo",
    "DiffStats",
    "generate_diff_report",
    # Language Support
    "LanguageDetector",
    "TranslationManager",
    "LanguageInfo",
    "TranslationLink",
    # Bulk Updates
    "BulkMetadataUpdater",
    "MetadataValidator",
    "MetadataUpdate",
    "UpdateResult",
    "BulkUpdateResult",
    # Expiration & Renewal
    "ExpirationTracker",
    "SignatureRenewer",
    "ExpirationMonitor",
    "ExpirationInfo",
    "RenewalResult",
    "RenewalPolicy",
    # Analytics & Metrics
    "MetricsCollector",
    "DashboardExporter",
    "OperationMetric",
    "UsageStats",
    "PerformanceMetrics",
    # Binary File Support
    "BinaryFileSigner",
    "TextExtractor",
    "BinaryFileInfo",
    # Models
    "SignResponse",
    "VerifyResponse",
    "LookupResponse",
    "StatsResponse",
    # Exceptions
    "EncypherError",
    "AuthenticationError",
    "QuotaExceededError",
    "SigningError",
    "VerificationError",
    "APIError",
    "ConfigurationError",
    "StreamingError",
]
