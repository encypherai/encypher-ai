"""
C2PA Manifest Verification Utility

This utility provides C2PA (Coalition for Content Provenance and Authenticity)
manifest verification capabilities. It can be used both server-side and in the SDK.

C2PA manifests provide cryptographic proof of content provenance and authenticity.
"""
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
import hashlib
import json

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
    assertions: List[C2PAAssertion] = None
    signatures: List[C2PASignature] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.assertions is None:
            self.assertions = []
        if self.signatures is None:
            self.signatures = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "valid": self.valid,
            "manifest_url": self.manifest_url,
            "manifest_hash": self.manifest_hash,
            "assertions": [
                {
                    "label": a.label,
                    "data": a.data,
                    "verified": a.verified
                }
                for a in self.assertions
            ],
            "signatures": [
                {
                    "issuer": s.issuer,
                    "time": s.time.isoformat() if isinstance(s.time, datetime) else s.time,
                    "algorithm": s.algorithm,
                    "verified": s.verified
                }
                for s in self.signatures
            ],
            "errors": self.errors,
            "warnings": self.warnings
        }


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
    
    def verify_manifest_url(self, manifest_url: str) -> C2PAVerificationResult:
        """
        Verify a C2PA manifest from a URL.
        
        Args:
            manifest_url: URL to the C2PA manifest
        
        Returns:
            C2PAVerificationResult with verification details
        """
        try:
            # Fetch manifest
            response = requests.get(manifest_url, timeout=self.timeout)
            response.raise_for_status()
            
            manifest_data = response.json()
            manifest_hash = hashlib.sha256(response.content).hexdigest()
            
            return self._verify_manifest_data(
                manifest_data=manifest_data,
                manifest_url=manifest_url,
                manifest_hash=manifest_hash
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching C2PA manifest from {manifest_url}: {e}")
            return C2PAVerificationResult(
                valid=False,
                manifest_url=manifest_url,
                errors=[f"Failed to fetch manifest: {str(e)}"]
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in C2PA manifest: {e}")
            return C2PAVerificationResult(
                valid=False,
                manifest_url=manifest_url,
                errors=["Invalid JSON in manifest"]
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying C2PA manifest: {e}", exc_info=True)
            return C2PAVerificationResult(
                valid=False,
                manifest_url=manifest_url,
                errors=[f"Verification error: {str(e)}"]
            )
    
    def verify_manifest_data(
        self,
        manifest_data: Dict[str, Any],
        manifest_url: Optional[str] = None
    ) -> C2PAVerificationResult:
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
        
        return self._verify_manifest_data(
            manifest_data=manifest_data,
            manifest_url=manifest_url,
            manifest_hash=manifest_hash
        )
    
    def _verify_manifest_data(
        self,
        manifest_data: Dict[str, Any],
        manifest_url: Optional[str] = None,
        manifest_hash: Optional[str] = None
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
            manifest_hash=manifest_hash
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
            
            logger.info(
                f"C2PA verification complete: valid={result.valid}, "
                f"assertions={len(result.assertions)}, signatures={len(result.signatures)}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error during C2PA verification: {e}", exc_info=True)
            result.valid = False
            result.errors.append(f"Verification error: {str(e)}")
            return result
    
    def _verify_structure(
        self,
        manifest_data: Dict[str, Any],
        result: C2PAVerificationResult
    ) -> bool:
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
        
        for field in required_fields:
            if field not in manifest_data:
                result.errors.append(f"Missing required field: {field}")
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
    
    def _extract_assertions(
        self,
        manifest_data: Dict[str, Any],
        result: C2PAVerificationResult
    ):
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
            
            result.assertions.append(
                C2PAAssertion(
                    label=label,
                    data=data,
                    verified=verified
                )
            )
    
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
    
    def _extract_signatures(
        self,
        manifest_data: Dict[str, Any],
        result: C2PAVerificationResult
    ):
        """
        Extract and verify signatures from manifest.
        
        Args:
            manifest_data: Manifest data
            result: Result object to populate
        """
        signature_info = manifest_data.get("signature_info", {})
        
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
        algorithm = signature_info.get("alg", "unknown")
        
        # Verify signature
        verified = self._verify_signature(signature_info)
        
        result.signatures.append(
            C2PASignature(
                issuer=issuer,
                time=time,
                algorithm=algorithm,
                verified=verified
            )
        )
    
    def _verify_signature(self, signature_info: Dict[str, Any]) -> bool:
        """
        Verify a signature.
        
        Args:
            signature_info: Signature information
        
        Returns:
            True if signature is valid
        """
        # TODO: Implement actual cryptographic signature verification
        # This would require:
        # 1. Extracting the public key
        # 2. Verifying the signature against the manifest data
        # 3. Checking certificate chain
        # 4. Validating timestamp
        
        # For now, we do basic validation
        required_fields = ["issuer", "alg"]
        return all(field in signature_info for field in required_fields)


# Global verifier instance
c2pa_verifier = C2PAVerifier()


def verify_c2pa_manifest(manifest_url: str) -> C2PAVerificationResult:
    """
    Convenience function to verify a C2PA manifest.
    
    Args:
        manifest_url: URL to the C2PA manifest
    
    Returns:
        C2PAVerificationResult
    """
    return c2pa_verifier.verify_manifest_url(manifest_url)
