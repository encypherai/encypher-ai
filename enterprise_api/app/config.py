"""
Configuration module for Encypher Enterprise API.
Uses Pydantic Settings for environment variable management.
"""

import ipaddress
import re
from functools import lru_cache
from typing import ClassVar, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"  # development | preview | production

    # Databases (Two-Database Architecture)
    # Core DB: Customer/billing data (organizations, api_keys, etc.)
    core_database_url: Optional[str] = None
    # Content DB: Verification data (documents, merkle trees, etc.)
    content_database_url: Optional[str] = None
    # Legacy single database URL (for backward compatibility)
    database_url: Optional[str] = None

    # Redis (for session management)
    redis_url: str = "redis://localhost:6379/0"

    # Encryption (for private key storage)
    # These should be bytes, but we'll handle conversion from hex strings
    key_encryption_key: str
    encryption_nonce: str

    auto_provision_signing_keys: bool = True

    # SSL.com (optional for staging/development)
    ssl_com_api_key: Optional[str] = None
    ssl_com_account_key: Optional[str] = None
    ssl_com_api_url: str = "https://api.ssl.com/v1"
    ssl_com_product_id: Optional[str] = None

    # Signing mode + managed signer material
    default_signing_mode: str = "organization"
    managed_signer_id: str = "encypher_managed"
    managed_signer_private_key_pem: Optional[str] = None
    managed_signer_certificate_pem: Optional[str] = None
    managed_signer_certificate_chain_pem: Optional[str] = None

    provisioning_token: Optional[str] = None

    # API
    api_base_url: str = "https://api.encypherai.com"

    # API docs exposure
    enable_public_api_docs: bool = False
    enable_public_metrics_endpoint: bool = False
    expose_health_details: bool = False
    expose_readiness_details: bool = False
    public_verify_minimal_response: bool = False
    public_rate_limit_use_redis: bool = True
    remote_manifest_verify_concurrency_limit: int = 8
    remote_manifest_verify_per_host_concurrency_limit: int = 2
    remote_manifest_verify_acquire_timeout_seconds: float = 0.25
    remote_manifest_verify_distributed_limit_use_redis: bool = True
    remote_manifest_verify_distributed_lease_seconds: int = 30
    remote_manifest_verify_cache_ttl_seconds: int = 300
    remote_manifest_verify_negative_cache_ttl_seconds: int = 60
    remote_manifest_verify_host_failure_threshold: int = 3
    remote_manifest_verify_circuit_open_seconds: int = 60

    # Service URLs
    coalition_service_url: str = "http://localhost:8009"
    auth_service_url: str = "http://localhost:8001"
    key_service_url: str = "http://localhost:8003"
    notification_service_url: str = "http://localhost:8005"

    # Dashboard URL for invite/claim links
    dashboard_url: str = "https://dashboard.encypherai.com"

    internal_service_token: Optional[str] = None
    compose_org_context_via_auth_service: bool = False

    # Database pool sizes (per replica)
    core_db_pool_size: int = 100
    core_db_max_overflow: int = 50
    content_db_pool_size: int = 200
    content_db_max_overflow: int = 100

    # Rate limiting
    rate_limit_per_minute: int = 60
    batch_worker_limit: int = 8
    batch_max_items: int = 100

    # Request logging controls (to avoid platform log-rate limits)
    request_logging_enabled: Optional[bool] = None
    log_health_checks: bool = False
    slow_request_threshold_ms: int = 2000

    # Domains
    marketing_domain: str = "encypher.ai"
    infrastructure_domain: str = "encypherai.com"

    # Status list base URL (consolidated under verify subdomain)
    status_list_base_url: str = "https://verify.encypherai.com/status/v1"

    # CORS - comma-separated list of allowed origins
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    # Trusted hosts - comma-separated list
    allowed_hosts: str = "api.encypherai.com,*.up.railway.app"

    # Trusted proxy IPs (comma-separated list)
    trusted_proxy_ips: str = ""

    # Image signing configuration
    image_max_size_bytes: int = 10_485_760  # 10 MB per image
    image_max_count_per_request: int = 20
    image_response_format: str = "base64"  # always base64 for now
    image_service_url: str = ""  # TrustMark microservice URL (empty = disabled)
    # When True: skip JUMBF embedding (no cert required). Returns original image bytes
    # unchanged. All metadata (hash, pHash, composite manifest, DB rows) is still written.
    # Use for local dev/CI where no CA-signed cert is available.
    # Never set this in production -- signed images will have no C2PA manifest.
    image_signing_passthrough: bool = False

    # C2PA signer trust list pinning/refresh
    c2pa_trust_list_url: Optional[str] = None
    c2pa_trust_list_sha256: Optional[str] = None
    c2pa_trust_list_refresh_hours: int = 24

    # C2PA TSA trust list pinning/refresh
    c2pa_tsa_trust_list_url: Optional[str] = None
    c2pa_tsa_trust_list_sha256: Optional[str] = None
    c2pa_tsa_trust_list_refresh_hours: int = 24

    # C2PA trust policy controls
    c2pa_required_signer_eku_oids: str = "1.3.6.1.4.1.62558.2.1"
    c2pa_revoked_certificate_serials: str = ""
    c2pa_revoked_certificate_fingerprints: str = ""

    # Embedding signature secret for public verification (HMAC)
    embedding_signature_secret: Optional[str] = None

    # Demo / sandbox API key support
    demo_api_key: Optional[str] = None
    demo_key_allowlist: Optional[str] = None
    demo_organization_id: str = "org_demo"
    demo_organization_name: str = "Encypher Demo Organization"
    demo_private_key_hex: Optional[str] = None
    # SECRET_KEY is an alias for demo_private_key_hex (used in Railway production)
    secret_key: Optional[str] = None
    # Legacy PEM format keys (for old content verification)
    demo_private_key_pem: Optional[str] = None
    demo_public_key_pem: Optional[str] = None

    # Stripe (for billing - used by other services, ignored by enterprise-api)
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_connect_webhook_secret: Optional[str] = None
    stripe_price_professional_monthly: Optional[str] = None
    stripe_price_professional_annual: Optional[str] = None
    stripe_price_business_monthly: Optional[str] = None
    stripe_price_business_annual: Optional[str] = None

    # NextAuth (for dashboard authentication - ignored by enterprise-api)
    nextauth_secret: Optional[str] = None
    nextauth_url: Optional[str] = None

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def key_encryption_key_bytes(self) -> bytes:
        """Convert hex string to bytes for encryption key."""
        return bytes.fromhex(self.key_encryption_key)

    @property
    def encryption_nonce_bytes(self) -> bytes:
        """Convert hex string to bytes for encryption nonce."""
        return bytes.fromhex(self.encryption_nonce)

    @property
    def core_database_url_resolved(self) -> str:
        """Get core database URL, falling back to legacy database_url."""
        return self.core_database_url or self.database_url or ""

    @property
    def content_database_url_resolved(self) -> str:
        """Get content database URL, falling back to legacy database_url."""
        return self.content_database_url or self.database_url or ""

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_preview(self) -> bool:
        """Check if running in preview mode."""
        return self.environment == "preview"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def request_logging_enabled_effective(self) -> bool:
        """Return effective request logging policy.

        Defaults to enabled in development and disabled elsewhere to reduce
        noisy per-request logs in preview/production deployments.
        """
        if self.request_logging_enabled is not None:
            return self.request_logging_enabled
        return self.is_development

    @property
    def demo_key_allowlist_set(self) -> set[str]:
        """Return allowlisted demo keys for production gating."""
        if not self.demo_key_allowlist:
            return set()
        return {item.strip() for item in self.demo_key_allowlist.split(",") if item.strip()}

    def is_demo_key_allowlisted(self, api_key: str) -> bool:
        """Check whether a demo key is allowlisted for production."""
        return api_key in self.demo_key_allowlist_set

    @property
    def demo_private_key_bytes(self) -> Optional[bytes]:
        """Return demo private key bytes if configured."""
        key_hex = self.demo_private_key_hex or self.secret_key
        if not key_hex:
            return None

        hex_str = key_hex.strip()
        if not hex_str:
            return None

        if not re.fullmatch(r"[0-9a-fA-F]+", hex_str):
            return None
        if len(hex_str) % 2 != 0:
            return None

        try:
            value = bytes.fromhex(hex_str)
        except ValueError:
            return None
        if len(value) != 32:
            return None

        return value

    @property
    def embedding_signature_secret_bytes(self) -> Optional[bytes]:
        """Return embedding signature secret bytes if configured."""
        if not self.embedding_signature_secret:
            return None

        secret = self.embedding_signature_secret.strip()
        if not secret:
            return None

        if re.fullmatch(r"[0-9a-fA-F]+", secret) and len(secret) % 2 == 0:
            return bytes.fromhex(secret)

        return secret.encode("utf-8")

    @property
    def trusted_proxy_ips_set(self) -> set[str]:
        """Return trusted proxy IP allowlist."""
        if not self.trusted_proxy_ips:
            return set()

        values = set()
        for entry in self.trusted_proxy_ips.split(","):
            candidate = entry.strip()
            if not candidate:
                continue
            try:
                ipaddress.ip_address(candidate)
            except ValueError:
                continue
            values.add(candidate)
        return values

    @staticmethod
    def _csv_tokens(value: str) -> list[str]:
        return [token.strip() for token in value.split(",") if token.strip()]

    @staticmethod
    def _normalize_hex_token(token: str) -> str:
        normalized = token.lower()
        if normalized.startswith("0x"):
            normalized = normalized[2:]
        return normalized

    @property
    def c2pa_required_signer_eku_oids_list(self) -> list[str]:
        """Return required signer EKU OIDs for C2PA certificate validation."""
        tokens = self._csv_tokens(self.c2pa_required_signer_eku_oids)
        return tokens or ["1.3.6.1.4.1.62558.2.1"]

    @property
    def c2pa_revoked_certificate_serials_set(self) -> set[str]:
        """Return denylisted certificate serial numbers for internal revocation policy."""
        return {self._normalize_hex_token(token) for token in self._csv_tokens(self.c2pa_revoked_certificate_serials)}

    @property
    def c2pa_revoked_certificate_fingerprints_set(self) -> set[str]:
        """Return denylisted certificate fingerprints for internal revocation policy."""
        return {self._normalize_hex_token(token) for token in self._csv_tokens(self.c2pa_revoked_certificate_fingerprints)}

    @property
    def default_signing_mode_normalized(self) -> str:
        """Return normalized default signing mode."""
        mode = (self.default_signing_mode or "organization").strip().lower().replace("-", "_")
        return mode or "organization"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
