"""
Batch verification for signed content repositories.

Verifies all signed files in a directory and generates verification reports.
"""
from pathlib import Path
from typing import List, Optional, Union
from dataclasses import dataclass
import asyncio
import time

from .client import EncypherClient
from .async_client import AsyncEncypherClient
from .models import VerifyResponse


@dataclass
class VerificationResult:
    """Result of verifying a single file."""
    file_path: Path
    is_valid: bool
    tampered: bool
    organization_name: Optional[str] = None
    document_title: Optional[str] = None
    publication_date: Optional[str] = None
    error: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class BatchVerificationResult:
    """Result of batch verification operation."""
    total_files: int
    valid: int
    tampered: int
    failed: int
    results: List[VerificationResult]
    total_time: float
    
    def summary(self) -> str:
        """Get human-readable summary."""
        return (
            f"Batch Verification Complete\n"
            f"  Total: {self.total_files}\n"
            f"  Valid: {self.valid}\n"
            f"  Tampered: {self.tampered}\n"
            f"  Failed: {self.failed}\n"
            f"  Time: {self.total_time:.2f}s"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "summary": {
                "total_files": self.total_files,
                "valid": self.valid,
                "tampered": self.tampered,
                "failed": self.failed,
                "total_time": self.total_time
            },
            "results": [
                {
                    "file_path": str(r.file_path),
                    "is_valid": r.is_valid,
                    "tampered": r.tampered,
                    "organization_name": r.organization_name,
                    "document_title": r.document_title,
                    "publication_date": r.publication_date,
                    "error": r.error,
                    "processing_time": r.processing_time
                }
                for r in self.results
            ]
        }


class RepositoryVerifier:
    """
    Verify all signed files in a repository.
    
    Example:
        >>> from encypher_enterprise import EncypherClient, RepositoryVerifier
        >>> 
        >>> client = EncypherClient(api_key="...")
        >>> verifier = RepositoryVerifier(client)
        >>> result = verifier.verify_directory(Path("./articles"))
        >>> print(result.summary())
    """
    
    def __init__(
        self,
        client: Union[EncypherClient, AsyncEncypherClient],
        max_concurrent: int = 5
    ):
        """
        Initialize repository verifier.
        
        Args:
            client: Encypher client (sync or async)
            max_concurrent: Maximum concurrent verifications (async only)
        """
        self.client = client
        self.max_concurrent = max_concurrent
        self._is_async = isinstance(client, AsyncEncypherClient)
    
    def verify_directory(
        self,
        directory: Path,
        patterns: List[str] = ["*.signed.md", "*.signed.txt", "*.signed.html"],
        exclude_patterns: List[str] = ["node_modules/**", ".git/**"],
        recursive: bool = True,
        fail_on_tampered: bool = False
    ) -> BatchVerificationResult:
        """
        Verify all signed files in a directory.
        
        Args:
            directory: Directory to scan
            patterns: Glob patterns to match signed files
            exclude_patterns: Patterns to exclude
            recursive: Recursively scan subdirectories
            fail_on_tampered: Raise exception if tampered files found
        
        Returns:
            BatchVerificationResult with verification details
        
        Raises:
            ValueError: If fail_on_tampered=True and tampered files found
        """
        if self._is_async:
            return asyncio.run(self._verify_directory_async(
                directory, patterns, exclude_patterns, recursive, fail_on_tampered
            ))
        else:
            return self._verify_directory_sync(
                directory, patterns, exclude_patterns, recursive, fail_on_tampered
            )
    
    def _verify_directory_sync(
        self,
        directory: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        recursive: bool,
        fail_on_tampered: bool
    ) -> BatchVerificationResult:
        """Synchronous directory verification."""
        start_time = time.time()
        
        # Find signed files
        files = self._find_files(directory, patterns, exclude_patterns, recursive)
        results = []
        
        for file_path in files:
            result = self._verify_file_sync(file_path)
            results.append(result)
        
        total_time = time.time() - start_time
        
        batch_result = BatchVerificationResult(
            total_files=len(results),
            valid=sum(1 for r in results if r.is_valid and not r.tampered),
            tampered=sum(1 for r in results if r.tampered),
            failed=sum(1 for r in results if not r.is_valid and not r.tampered),
            results=results,
            total_time=total_time
        )
        
        if fail_on_tampered and batch_result.tampered > 0:
            raise ValueError(
                f"Verification failed: {batch_result.tampered} tampered file(s) detected"
            )
        
        return batch_result
    
    async def _verify_directory_async(
        self,
        directory: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        recursive: bool,
        fail_on_tampered: bool
    ) -> BatchVerificationResult:
        """Asynchronous directory verification."""
        start_time = time.time()
        
        # Find signed files
        files = self._find_files(directory, patterns, exclude_patterns, recursive)
        
        # Verify files with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def verify_with_semaphore(file_path: Path) -> VerificationResult:
            async with semaphore:
                return await self._verify_file_async(file_path)
        
        results = await asyncio.gather(
            *[verify_with_semaphore(f) for f in files],
            return_exceptions=True
        )
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(VerificationResult(
                    file_path=files[i],
                    is_valid=False,
                    tampered=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        total_time = time.time() - start_time
        
        batch_result = BatchVerificationResult(
            total_files=len(processed_results),
            valid=sum(1 for r in processed_results if r.is_valid and not r.tampered),
            tampered=sum(1 for r in processed_results if r.tampered),
            failed=sum(1 for r in processed_results if not r.is_valid and not r.tampered),
            results=processed_results,
            total_time=total_time
        )
        
        if fail_on_tampered and batch_result.tampered > 0:
            raise ValueError(
                f"Verification failed: {batch_result.tampered} tampered file(s) detected"
            )
        
        return batch_result
    
    def _find_files(
        self,
        directory: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        recursive: bool
    ) -> List[Path]:
        """Find files matching patterns."""
        files = []
        
        for pattern in patterns:
            if recursive:
                matched = directory.rglob(pattern)
            else:
                matched = directory.glob(pattern)
            
            for file_path in matched:
                # Check exclusions
                excluded = False
                for exclude in exclude_patterns:
                    if file_path.match(exclude):
                        excluded = True
                        break
                
                if not excluded and file_path.is_file():
                    files.append(file_path)
        
        return sorted(set(files))
    
    def _verify_file_sync(self, file_path: Path) -> VerificationResult:
        """Verify a single file (synchronous)."""
        start_time = time.time()
        
        try:
            # Read signed content
            signed_content = file_path.read_text(encoding='utf-8')
            
            # Verify
            verification = self.client.verify(signed_content)
            
            processing_time = time.time() - start_time
            
            return VerificationResult(
                file_path=file_path,
                is_valid=verification.is_valid,
                tampered=verification.tampered,
                organization_name=verification.organization_name,
                document_title=verification.document_title,
                publication_date=verification.publication_date,
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return VerificationResult(
                file_path=file_path,
                is_valid=False,
                tampered=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def _verify_file_async(self, file_path: Path) -> VerificationResult:
        """Verify a single file (asynchronous)."""
        start_time = time.time()
        
        try:
            # Read signed content
            signed_content = file_path.read_text(encoding='utf-8')
            
            # Verify
            verification = await self.client.verify(signed_content)
            
            processing_time = time.time() - start_time
            
            return VerificationResult(
                file_path=file_path,
                is_valid=verification.is_valid,
                tampered=verification.tampered,
                organization_name=verification.organization_name,
                document_title=verification.document_title,
                publication_date=verification.publication_date,
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return VerificationResult(
                file_path=file_path,
                is_valid=False,
                tampered=False,
                error=str(e),
                processing_time=processing_time
            )
