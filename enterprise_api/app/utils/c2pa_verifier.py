"""
C2PA Manifest Verification Utility

This utility provides C2PA (Coalition for Content Provenance and Authenticity)
manifest verification capabilities. It can be used both server-side and in the SDK.

C2PA manifests provide cryptographic proof of content provenance and authenticity.
"""

import asyncio
import base64
import copy
import hashlib
import ipaddress
import json
import logging
import socket
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from encypher.core.payloads import deserialize_c2pa_payload_from_cbor
from encypher.core.signing import extract_certificates_from_cose, verify_c2pa_cose

from app.config import settings
from app.services.session_service import session_service
from app.utils.c2pa_trust_list import validate_certificate_chain

logger = logging.getLogger(__name__)


@dataclass
class C2PAAssertion:
    """Represents a C2PA assertion."""

    label: str
    data: Dict[str, Any]
    verified: bool = False


@dataclass
class C2PASignature:
    """Represents a C2PA signature."""

    issuer: str
    time: datetime
    algorithm: str
    verified: bool = False


@dataclass
class C2PAVerificationResult:
    """Result of C2PA manifest verification."""

    valid: bool
    manifest_url: Optional[str] = None
    manifest_hash: Optional[str] = None
    assertions: List[C2PAAssertion] = field(default_factory=list)
    signatures: List[C2PASignature] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "valid": self.valid,
            "manifest_url": self.manifest_url,
            "manifest_hash": self.manifest_hash,
            "assertions": [{"label": a.label, "data": a.data, "verified": a.verified} for a in self.assertions],
            "signatures": [
                {
                    "issuer": s.issuer,
                    "time": s.time.isoformat() if isinstance(s.time, datetime) else s.time,
                    "algorithm": s.algorithm,
                    "verified": s.verified,
                }
                for s in self.signatures
            ],
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class _CachedVerificationResult:
    result: C2PAVerificationResult
    expires_at: float


@dataclass
class _HostCircuitState:
    failure_count: int = 0
    opened_until: float = 0.0


class C2PAVerifier:
    """
    C2PA Manifest Verifier.

    This class provides methods to verify C2PA manifests from URLs or raw data.
    It can be used both server-side and in client SDKs.
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize the C2PA verifier.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

        self._max_manifest_bytes = 1024 * 1024
        self._verification_semaphore = asyncio.Semaphore(max(1, settings.remote_manifest_verify_concurrency_limit))
        self._host_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._verification_cache: Dict[str, _CachedVerificationResult] = {}
        self._host_circuits: Dict[str, _HostCircuitState] = {}
        self._distributed_limit_prefix = "encypher:remote-manifest-verify:"

    async def _acquire_remote_verification_slot(self) -> bool:
        try:
            await asyncio.wait_for(
                self._verification_semaphore.acquire(),
                timeout=settings.remote_manifest_verify_acquire_timeout_seconds,
            )
            return True
        except asyncio.TimeoutError:
            return False

    def _distributed_limit_key(self, scope: str) -> str:
        return f"{self._distributed_limit_prefix}{scope}"

    async def _acquire_distributed_verification_slot(self, scope: str, limit: int) -> tuple[bool, Optional[str]]:
        redis_client = session_service.redis_client
        if not settings.remote_manifest_verify_distributed_limit_use_redis or redis_client is None:
            return True, None

        lease_seconds = max(1, settings.remote_manifest_verify_distributed_lease_seconds)
        now_ms = int(time.time() * 1000)
        lease_ms = lease_seconds * 1000
        token = uuid.uuid4().hex
        allowed = await redis_client.eval(
            """
            local key = KEYS[1]
            local now_ms = tonumber(ARGV[1])
            local lease_ms = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])
            local token = ARGV[4]
            redis.call('ZREMRANGEBYSCORE', key, '-inf', now_ms)
            local count = redis.call('ZCARD', key)
            if count >= limit then
                return 0
            end
            redis.call('ZADD', key, now_ms + lease_ms, token)
            redis.call('EXPIRE', key, math.max(1, math.ceil(lease_ms / 1000)))
            return 1
            """,
            1,
            self._distributed_limit_key(scope),
            now_ms,
            lease_ms,
            max(1, limit),
            token,
        )
        if bool(int(allowed)):
            return True, token
        return False, None

    async def _release_distributed_verification_slot(self, scope: str, token: Optional[str]) -> None:
        if not token:
            return

        redis_client = session_service.redis_client
        if not settings.remote_manifest_verify_distributed_limit_use_redis or redis_client is None:
            return

        try:
            await redis_client.eval(
                """
                local key = KEYS[1]
                local token = ARGV[1]
                redis.call('ZREM', key, token)
                return 1
                """,
                1,
                self._distributed_limit_key(scope),
                token,
            )
        except Exception as exc:
            logger.warning("Failed to release distributed verification slot for %s: %s", scope, exc)

    async def _acquire_host_verification_slot(self, host: str) -> bool:
        semaphore = self._host_semaphores.get(host)
        if semaphore is None:
            semaphore = asyncio.Semaphore(max(1, settings.remote_manifest_verify_per_host_concurrency_limit))
            self._host_semaphores[host] = semaphore

        try:
            await asyncio.wait_for(
                semaphore.acquire(),
                timeout=settings.remote_manifest_verify_acquire_timeout_seconds,
            )
            return True
        except asyncio.TimeoutError:
            return False

    def _get_cached_result(self, manifest_url: str) -> Optional[C2PAVerificationResult]:
        cached = self._verification_cache.get(manifest_url)
        if cached is None:
            return None

        if cached.expires_at <= time.monotonic():
            self._verification_cache.pop(manifest_url, None)
            return None

        return copy.deepcopy(cached.result)

    def _cache_result(self, manifest_url: str, result: C2PAVerificationResult) -> None:
        ttl = settings.remote_manifest_verify_cache_ttl_seconds if result.valid else settings.remote_manifest_verify_negative_cache_ttl_seconds
        if ttl <= 0:
            return

        self._verification_cache[manifest_url] = _CachedVerificationResult(
            result=copy.deepcopy(result),
            expires_at=time.monotonic() + ttl,
        )

    def _host_circuit_open(self, host: str) -> bool:
        state = self._host_circuits.get(host)
        if state is None:
            return False

        if state.opened_until <= time.monotonic():
            state.opened_until = 0.0
            return False

        return True

    def _record_host_success(self, host: str) -> None:
        state = self._host_circuits.get(host)
        if state is None:
            return

        state.failure_count = 0
        state.opened_until = 0.0

    def _record_host_failure(self, host: str) -> None:
        threshold = max(1, settings.remote_manifest_verify_host_failure_threshold)
        state = self._host_circuits.setdefault(host, _HostCircuitState())
        if state.opened_until > time.monotonic():
            return

        state.failure_count += 1
        if state.failure_count >= threshold:
            state.failure_count = 0
            state.opened_until = time.monotonic() + max(1, settings.remote_manifest_verify_circuit_open_seconds)

    async def verify_manifest_url(self, manifest_url: str) -> C2PAVerificationResult:
        """
        Verify a C2PA manifest from a URL (async).

        Args:
            manifest_url: URL to the C2PA manifest

        Returns:
            C2PAVerificationResult with verification details
        """
        host = ""
        remote_slot_acquired = False
        host_slot_acquired = False
        distributed_remote_token: Optional[str] = None
        distributed_host_token: Optional[str] = None
        try:
            parsed = urlparse(manifest_url)
            if parsed.scheme != "https" or not parsed.netloc:
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Untrusted manifest URL"],
                )

            host = (parsed.hostname or "").lower()
            if not host or host == "localhost":
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Untrusted manifest URL"],
                )

            if parsed.port not in (None, 443):
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Untrusted manifest URL"],
                )

            try:
                ip = ipaddress.ip_address(host)
                if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
                    return C2PAVerificationResult(
                        valid=False,
                        manifest_url=manifest_url,
                        errors=["Untrusted manifest URL"],
                    )
            except ValueError:
                addrs = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
                for _family, _socktype, _proto, _canon, sockaddr in addrs:
                    ip_str = sockaddr[0]
                    ip = ipaddress.ip_address(ip_str)
                    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
                        return C2PAVerificationResult(
                            valid=False,
                            manifest_url=manifest_url,
                            errors=["Untrusted manifest URL"],
                        )

            cached = self._get_cached_result(manifest_url)
            if cached is not None:
                return cached

            if self._host_circuit_open(host):
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Manifest host temporarily unavailable"],
                )

            acquired = await self._acquire_remote_verification_slot()
            if not acquired:
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Manifest verification busy; retry later"],
                )
            remote_slot_acquired = True

            distributed_allowed, distributed_remote_token = await self._acquire_distributed_verification_slot(
                scope="global",
                limit=settings.remote_manifest_verify_concurrency_limit,
            )
            if not distributed_allowed:
                self._verification_semaphore.release()
                remote_slot_acquired = False
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Manifest verification busy; retry later"],
                )

            host_acquired = await self._acquire_host_verification_slot(host)
            if not host_acquired:
                await self._release_distributed_verification_slot("global", distributed_remote_token)
                distributed_remote_token = None
                self._verification_semaphore.release()
                remote_slot_acquired = False
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Manifest verification busy; retry later"],
                )
            host_slot_acquired = True

            distributed_host_allowed, distributed_host_token = await self._acquire_distributed_verification_slot(
                scope=f"host:{host}",
                limit=settings.remote_manifest_verify_per_host_concurrency_limit,
            )
            if not distributed_host_allowed:
                self._host_semaphores[host].release()
                host_slot_acquired = False
                await self._release_distributed_verification_slot("global", distributed_remote_token)
                distributed_remote_token = None
                self._verification_semaphore.release()
                remote_slot_acquired = False
                return C2PAVerificationResult(
                    valid=False,
                    manifest_url=manifest_url,
                    errors=["Manifest verification busy; retry later"],
                )

            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=False,
            ) as client:
                try:
                    async with client.stream(
                        "GET",
                        manifest_url,
                        headers={"Accept": "application/json"},
                    ) as response:
                        response.raise_for_status()

                        total = 0
                        chunks: list[bytes] = []
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            if not chunk:
                                continue
                            total += len(chunk)
                            if total > self._max_manifest_bytes:
                                result = C2PAVerificationResult(
                                    valid=False,
                                    manifest_url=manifest_url,
                                    errors=["Manifest payload too large"],
                                )
                                self._record_host_failure(host)
                                self._cache_result(manifest_url, result)
                                return result
                            chunks.append(chunk)
                finally:
                    await self._release_distributed_verification_slot(f"host:{host}", distributed_host_token)
                    distributed_host_token = None
                    if host_slot_acquired:
                        self._host_semaphores[host].release()
                        host_slot_acquired = False
                    await self._release_distributed_verification_slot("global", distributed_remote_token)
                    distributed_remote_token = None
                    if remote_slot_acquired:
                        self._verification_semaphore.release()
                        remote_slot_acquired = False

            raw = b"".join(chunks)
            manifest_data = json.loads(raw.decode("utf-8"))
            manifest_hash = hashlib.sha256(raw).hexdigest()

            result = self._verify_manifest_data(manifest_data=manifest_data, manifest_url=manifest_url, manifest_hash=manifest_hash)
            self._record_host_success(host)
            self._cache_result(manifest_url, result)
            return result

        except httpx.RequestError as e:
            logger.error(f"Error fetching C2PA manifest from {manifest_url}: {e}")
            result = C2PAVerificationResult(
                valid=False,
                manifest_url=manifest_url,
                errors=[f"Failed to fetch manifest: {str(e)}"],
            )
            if host:
                self._record_host_failure(host)
                self._cache_result(manifest_url, result)
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching C2PA manifest from {manifest_url}: {e}")
            result = C2PAVerificationResult(valid=False, manifest_url=manifest_url, errors=[f"HTTP error: {str(e)}"])
            if host:
                self._record_host_failure(host)
                self._cache_result(manifest_url, result)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in C2PA manifest: {e}")
            result = C2PAVerificationResult(valid=False, manifest_url=manifest_url, errors=["Invalid JSON in manifest"])
            if host:
                self._record_host_failure(host)
                self._cache_result(manifest_url, result)
            return result
        except Exception as e:
            logger.error(f"Unexpected error verifying C2PA manifest: {e}", exc_info=True)
            result = C2PAVerificationResult(valid=False, manifest_url=manifest_url, errors=[f"Verification error: {str(e)}"])
            if host:
                self._record_host_failure(host)
                self._cache_result(manifest_url, result)
            return result

    def verify_manifest_data(self, manifest_data: Dict[str, Any], manifest_url: Optional[str] = None) -> C2PAVerificationResult:
        """
        Verify C2PA manifest from raw data.

        Args:
            manifest_data: C2PA manifest as dictionary
            manifest_url: Optional URL where manifest was fetched from

        Returns:
            C2PAVerificationResult with verification details
        """
        manifest_json = json.dumps(manifest_data, sort_keys=True)
        manifest_hash = hashlib.sha256(manifest_json.encode()).hexdigest()

        return self._verify_manifest_data(manifest_data=manifest_data, manifest_url=manifest_url, manifest_hash=manifest_hash)

    def _verify_manifest_data(
        self,
        manifest_data: Dict[str, Any],
        manifest_url: Optional[str] = None,
        manifest_hash: Optional[str] = None,
    ) -> C2PAVerificationResult:
        """
        Internal method to verify manifest data.

        Args:
            manifest_data: C2PA manifest as dictionary
            manifest_url: Optional URL
            manifest_hash: Optional hash of manifest

        Returns:
            C2PAVerificationResult
        """
        result = C2PAVerificationResult(
            valid=True,  # Assume valid until proven otherwise
            manifest_url=manifest_url,
            manifest_hash=manifest_hash,
        )

        try:
            # Verify manifest structure
            if not self._verify_structure(manifest_data, result):
                result.valid = False
                return result

            # Extract and verify assertions
            self._extract_assertions(manifest_data, result)

            # Extract and verify signatures
            self._extract_signatures(manifest_data, result)

            # Overall validation
            if result.errors:
                result.valid = False

            # Check if all signatures are verified
            if result.signatures:
                all_verified = all(s.verified for s in result.signatures)
                if not all_verified:
                    result.warnings.append("Not all signatures could be verified")

            logger.info(f"C2PA verification complete: valid={result.valid}, assertions={len(result.assertions)}, signatures={len(result.signatures)}")

            return result

        except Exception as e:
            logger.error(f"Error during C2PA verification: {e}", exc_info=True)
            result.valid = False
            result.errors.append(f"Verification error: {str(e)}")
            return result

    def _verify_structure(self, manifest_data: Dict[str, Any], result: C2PAVerificationResult) -> bool:
        """
        Verify basic C2PA manifest structure.

        Args:
            manifest_data: Manifest data
            result: Result object to populate

        Returns:
            True if structure is valid
        """
        # Check for required fields
        required_fields = ["claim_generator", "assertions"]

        for required_field in required_fields:
            if required_field not in manifest_data:
                result.errors.append(f"Missing required field: {required_field}")
                return False

        # Validate claim_generator
        if not isinstance(manifest_data.get("claim_generator"), str):
            result.errors.append("Invalid claim_generator format")
            return False

        # Validate assertions is a list
        if not isinstance(manifest_data.get("assertions"), list):
            result.errors.append("Assertions must be a list")
            return False

        return True

    def _extract_assertions(self, manifest_data: Dict[str, Any], result: C2PAVerificationResult):
        """
        Extract assertions from manifest.

        Args:
            manifest_data: Manifest data
            result: Result object to populate
        """
        assertions = manifest_data.get("assertions", [])

        for assertion in assertions:
            if not isinstance(assertion, dict):
                result.warnings.append("Invalid assertion format")
                continue

            label = assertion.get("label", "unknown")
            data = assertion.get("data", {})

            # Basic assertion validation
            verified = self._verify_assertion(assertion)

            result.assertions.append(C2PAAssertion(label=label, data=data, verified=verified))

    def _verify_assertion(self, assertion: Dict[str, Any]) -> bool:
        """
        Verify a single assertion.

        Args:
            assertion: Assertion data

        Returns:
            True if assertion is valid
        """
        # Basic validation - check for required fields
        if "label" not in assertion:
            return False

        # TODO: Add cryptographic verification of assertion signatures
        # For now, we do basic structural validation

        return True

    def _extract_signatures(self, manifest_data: Dict[str, Any], result: C2PAVerificationResult):
        """
        Extract and verify signatures from manifest.

        Args:
            manifest_data: Manifest data
            result: Result object to populate
        """
        signature_info = manifest_data.get("signature_info", {}) or {}
        cose_sign1 = signature_info.get("cose_sign1") or manifest_data.get("cose_sign1")
        if cose_sign1:
            signature_info = {**signature_info, "cose_sign1": cose_sign1}

        if not signature_info:
            result.warnings.append("No signature information found")
            return

        # Extract issuer
        issuer = signature_info.get("issuer", "unknown")

        # Extract time
        time_str = signature_info.get("time")
        try:
            time = datetime.fromisoformat(time_str) if time_str else datetime.utcnow()
        except (ValueError, TypeError):
            time = datetime.utcnow()
            result.warnings.append("Invalid signature timestamp")

        # Extract algorithm
        algorithm = signature_info.get("alg", "EdDSA")

        # Verify signature
        verified = self._verify_signature(signature_info, manifest_data, result)

        result.signatures.append(C2PASignature(issuer=issuer, time=time, algorithm=algorithm, verified=verified))

    def _verify_signature(
        self,
        signature_info: Dict[str, Any],
        manifest_data: Dict[str, Any],
        result: C2PAVerificationResult,
    ) -> bool:
        """
        Verify a signature.

        Args:
            signature_info: Signature information

        Returns:
            True if signature is valid
        """
        cose_b64 = signature_info.get("cose_sign1")
        if not cose_b64:
            result.warnings.append("Signature missing COSE data; cryptographic verification skipped")
            return False

        try:
            cose_bytes = base64.b64decode(cose_b64)
        except (ValueError, TypeError) as exc:
            result.errors.append(f"Invalid COSE signature encoding: {exc}")
            return False

        public_key = None
        chain_pem = None
        try:
            certificates = extract_certificates_from_cose(cose_bytes)
        except ValueError:
            certificates = []

        if certificates:
            leaf_cert = certificates[0]
            public_key = leaf_cert.public_key()
            leaf_pem = leaf_cert.public_bytes(serialization.Encoding.PEM).decode()
            if len(certificates) > 1:
                chain_pem = "\n".join(cert.public_bytes(serialization.Encoding.PEM).decode() for cert in certificates[1:])

            is_valid, error_msg, _ = validate_certificate_chain(leaf_pem, chain_pem)
            if not is_valid:
                result.warnings.append(f"Certificate chain untrusted: {error_msg}")
        else:
            public_key_pem = signature_info.get("public_key_pem")
            if public_key_pem:
                try:
                    public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
                except Exception as exc:
                    result.errors.append(f"Invalid public key: {exc}")
                    return False
            else:
                result.errors.append("No public key available for signature verification")
                return False

        try:
            payload_bytes = verify_c2pa_cose(public_key, cose_bytes)
        except InvalidSignature:
            result.errors.append("COSE signature verification failed")
            return False
        except Exception as exc:
            result.errors.append(f"COSE signature verification error: {exc}")
            return False

        try:
            payload = deserialize_c2pa_payload_from_cbor(payload_bytes)
        except Exception as exc:
            result.errors.append(f"Failed to decode COSE payload: {exc}")
            return False

        if isinstance(payload, dict):
            if "claim_generator" in manifest_data and payload.get("claim_generator") != manifest_data.get("claim_generator"):
                result.errors.append("Manifest claim_generator mismatch with COSE payload")
                return False
            if "assertions" in manifest_data and payload.get("assertions") != manifest_data.get("assertions"):
                result.errors.append("Manifest assertions mismatch with COSE payload")
                return False

        return True


# Global verifier instance
c2pa_verifier = C2PAVerifier()


async def verify_c2pa_manifest(manifest_url: str) -> C2PAVerificationResult:
    """
    Convenience function to verify a C2PA manifest (async).

    Args:
        manifest_url: URL to the C2PA manifest

    Returns:
        C2PAVerificationResult
    """
    return await c2pa_verifier.verify_manifest_url(manifest_url)
