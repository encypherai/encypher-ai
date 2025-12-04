"""
High-level API for Encypher commercial tools.

This module provides a simplified, consistent interface for working with the
Encypher package across all commercial tools. It builds on top of the
core Encypher functionality while adding commercial-specific features.
"""

from datetime import datetime
from typing import Dict, Optional, Any, Union

from pydantic import BaseModel
from rich.console import Console

# Import from the core Encypher package
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
from encypher.core.keys import load_public_key_from_data, load_private_key_from_data

# Add compatibility function to the global namespace
def load_public_key_from_pem(pem_data):
    """Compatibility wrapper for load_public_key_from_data.
    
    This function exists to maintain backward compatibility with code that
    might be expecting load_public_key_from_pem to exist.
    
    Args:
        pem_data: PEM-encoded public key data
        
    Returns:
        Ed25519PublicKey: The loaded public key
    """
    return load_public_key_from_data(pem_data)


console = Console()


class VerificationResult(BaseModel):
    """
    Result of a metadata verification operation.
    
    This class provides a structured representation of the verification result,
    including the verification status, signer information, and extracted metadata.
    """
    verified: bool
    signer_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    model_id: Optional[str] = None
    format: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    raw_payload: Optional[Dict[str, Any]] = None
    verification_details: Optional[str] = None  # Additional details about verification failure
    
    @property
    def has_metadata(self) -> bool:
        """Returns True if any metadata was found, regardless of verification status."""
        return self.raw_payload is not None and bool(self.raw_payload)
    
    def __str__(self) -> str:
        """String representation of the verification result."""
        if not self.has_metadata:
            return "No metadata found"
        
        status = "✅ Verified" if self.verified else "❌ Verification failed"
        result = f"{status} | Signer: {self.signer_id or 'Unknown'}"
        
        if self.timestamp:
            result += f" | Timestamp: {self.timestamp.isoformat()}"
        if self.model_id:
            result += f" | Model: {self.model_id}"
        
        return result


class Encypher:
    """
    High-level API for Encypher operations.
    
    This class provides a simplified interface for working with the Encypher
    package, including metadata embedding, verification, and extraction.
    """
    
    # Add compatibility function as a class method
    @staticmethod
    def load_public_key_from_pem(pem_data):
        """Compatibility wrapper for load_public_key_from_data.
        
        This function exists to maintain backward compatibility with code that
        might be expecting load_public_key_from_pem to exist.
        
        Args:
            pem_data: PEM-encoded public key data
            
        Returns:
            Ed25519PublicKey: The loaded public key
        """
        return load_public_key_from_data(pem_data)
    
    def __init__(
        self,
        private_key_path: Optional[str] = None,
        public_key_path: Optional[str] = None,
        signer_id: Optional[str] = None,
        trusted_signers: Optional[Dict[str, str]] = None,
        verbose: bool = False
    ):
        """
        Initialize the Encypher high-level API.
        
        Args:
            private_key_path: Path to the private key file for signing (PEM format)
            public_key_path: Path to the public key file for verification (PEM format)
            signer_id: Identifier for the signer (required for embedding)
            trusted_signers: Dictionary mapping signer IDs to public key paths
            verbose: Whether to print verbose output
        """
        self.verbose = verbose
        self._private_key = None
        self._public_key = None
        self._signer_id = signer_id
        self._trusted_signers = {}
        
        # Make private attributes accessible as properties
        self.trusted_signers = self._trusted_signers
        
        # Load trusted signers if provided
        if trusted_signers:
            for signer_id, key_path in trusted_signers.items():
                # Skip files that don't look like public keys
                if "private" in signer_id.lower():
                    if self.verbose:
                        console.print(f"Skipping private key file: {signer_id}")
                    continue
                    
                try:
                    # Load the public key from the PEM file
                    with open(key_path, "rb") as f:
                        key_data = f.read()
                        
                    # Try to load the public key
                    self._trusted_signers[signer_id] = load_public_key_from_data(key_data)
                    
                    if self.verbose:
                        console.print(f"Loaded trusted signer {signer_id}")
                except NameError:
                    # Handle specific case of function not found - this is likely due to a module import issue
                    # but we can still proceed with verification
                    if self.verbose:
                        console.print(f"[yellow]Warning: Function not found when loading {signer_id}, but verification may still work[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error loading trusted signer {signer_id}: {e}[/red]")
        
        # Load private key if provided
        if private_key_path:
            try:
                with open(private_key_path, "rb") as f:
                    key_data = f.read()
                self._private_key = load_private_key_from_data(key_data)
                if self.verbose:
                    console.print(f"[green]Loaded private key from {private_key_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error loading private key: {e}[/red]")
        
        # Load public key if provided
        if public_key_path:
            try:
                with open(public_key_path, "rb") as f:
                    key_data = f.read()
                self._public_key = load_public_key_from_data(key_data)
                if self.verbose:
                    console.print(f"[green]Loaded public key from {public_key_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error loading public key: {e}[/red]")
        
        # Note: Trusted signers are already loaded above
    
    def _get_public_key_for_signer(self, signer_id: str):
        """Get the public key for a given signer ID."""
        return self._trusted_signers.get(signer_id)
    
    def embed_metadata(
        self,
        text: str,
        custom_metadata: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None,
        metadata_format: str = "basic",
        target: Union[str, MetadataTarget] = MetadataTarget.WHITESPACE,
    ) -> str:
        """
        Embed metadata into text.
        
        Args:
            text: The text to embed metadata into
            custom_metadata: Optional custom metadata to include
            model_id: Optional model identifier
            metadata_format: Format of the metadata ("basic" or "manifest")
            target: Where to embed the metadata (whitespace, punctuation, etc.)
            
        Returns:
            Text with embedded metadata
        
        Raises:
            ValueError: If private key or signer ID is not set
        """
        if not self._private_key:
            raise ValueError("Private key is required for embedding metadata")
        if not self._signer_id:
            raise ValueError("Signer ID is required for embedding metadata")
        
        try:
            result = UnicodeMetadata.embed_metadata(
                text=text,
                private_key=self._private_key,
                signer_id=self._signer_id,
                metadata_format=metadata_format,
                model_id=model_id,
                custom_metadata=custom_metadata,
                target=target,
            )
            if self.verbose:
                console.print("[green]Successfully embedded metadata[/green]")
            return result
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Error embedding metadata: {e}[/red]")
            raise
    
    def verify_from_text(self, text: str) -> VerificationResult:
        """
        Verify metadata from text.
        
        Args:
            text: Text with potentially embedded metadata
            
        Returns:
            VerificationResult object with verification status and metadata
        """
        # Define a key provider function that uses our trusted signers dictionary
        def key_provider(signer_id: str):
            return self._trusted_signers.get(signer_id)
        
        try:
            # Extract metadata regardless of verification status
            raw_payload = UnicodeMetadata.extract_metadata(text)
            
            # If no metadata found, return early
            if not raw_payload:
                return VerificationResult(verified=False, raw_payload=None)
            
            # Verify the metadata if we have trusted signers
            if self._trusted_signers:
                verified, signer_id, payload = UnicodeMetadata.verify_metadata(
                    text=text,
                    public_key_provider=key_provider,
                    return_payload_on_failure=True
                )
            else:
                # If no trusted signers, we can only extract but not verify
                verified = False
                signer_id = raw_payload.get("signer_id")
                payload = raw_payload
            
            # Extract relevant fields from the payload
            timestamp_str = payload.get("timestamp") if payload else None
            timestamp = None
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    pass
            
            # Create and return the verification result
            return VerificationResult(
                verified=verified,
                signer_id=signer_id,
                timestamp=timestamp,
                model_id=payload.get("model_id") if payload else None,
                format=payload.get("format") if payload else None,
                custom_metadata=payload.get("custom_metadata") if payload else None,
                raw_payload=payload
            )
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Error verifying metadata: {e}[/red]")
            return VerificationResult(verified=False, raw_payload=None)
    
    def verify_from_file(self, file_path: str) -> VerificationResult:
        """
        Verify metadata from a file.
        
        Args:
            file_path: Path to the file to verify
            
        Returns:
            VerificationResult object with verification status and metadata
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return self.verify_from_text(text)
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Error reading file {file_path}: {e}[/red]")
            return VerificationResult(verified=False, raw_payload=None)
