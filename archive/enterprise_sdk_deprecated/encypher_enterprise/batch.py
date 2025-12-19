"""
Batch operations for signing multiple files and repositories.

Provides utilities for publishers to recursively sign entire repositories
with C2PA-compliant metadata and optional sentence-level tracking.
"""
import asyncio
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import json

from .client import EncypherClient
from .async_client import AsyncEncypherClient
from .state import StateManager


@dataclass
class FileMetadata:
    """
    C2PA-compliant metadata for a file.
    
    Aligns with C2PA manifest structure for content credentials.
    """
    # Core metadata
    title: Optional[str] = None
    author: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    
    # C2PA standard fields
    content_type: Optional[str] = None  # MIME type
    instance_id: Optional[str] = None  # Unique identifier
    document_id: Optional[str] = None  # Document identifier
    
    # Publisher metadata
    publisher: Optional[str] = None
    publisher_url: Optional[str] = None
    license: Optional[str] = None
    copyright: Optional[str] = None
    
    # Content classification
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    language: Optional[str] = "en"
    
    # AI-related metadata
    ai_generated: bool = False
    ai_model: Optional[str] = None
    ai_training_data: Optional[str] = None
    
    # Custom metadata
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def to_c2pa_manifest(self) -> Dict[str, Any]:
        """
        Convert to C2PA manifest structure.
        
        Returns:
            Dict compatible with C2PA 2.2 specification
        """
        manifest = {
            "claim_generator": "Encypher Enterprise SDK",
            "claim_generator_version": "1.0.0",
            "title": self.title,
            "format": self.content_type,
            "instance_id": self.instance_id,
        }
        
        # Add assertions
        assertions = []
        
        # Creative work assertion
        if self.author or self.created:
            creative_work = {
                "label": "c2pa.creative-work",
                "data": {}
            }
            if self.author:
                creative_work["data"]["author"] = [{"name": self.author}]
            if self.created:
                creative_work["data"]["dateCreated"] = self.created.isoformat()
            assertions.append(creative_work)
        
        # Actions assertion (creation)
        actions = {
            "label": "c2pa.actions",
            "data": {
                "actions": [
                    {
                        "action": "c2pa.created",
                        "when": (self.created or datetime.utcnow()).isoformat(),
                        "softwareAgent": "Encypher Enterprise SDK"
                    }
                ]
            }
        }
        assertions.append(actions)
        
        # AI generation assertion
        if self.ai_generated:
            ai_assertion = {
                "label": "c2pa.ai-generative-training",
                "data": {
                    "use": "allowed" if not self.ai_training_data else "notAllowed",
                    "entries": []
                }
            }
            if self.ai_model:
                ai_assertion["data"]["entries"].append({
                    "name": self.ai_model,
                    "version": "unknown"
                })
            assertions.append(ai_assertion)
        
        manifest["assertions"] = assertions
        
        # Add custom metadata
        if self.custom:
            manifest["custom"] = self.custom
        
        return manifest


@dataclass
class SigningResult:
    """Result of signing a single file."""
    file_path: Path
    success: bool
    document_id: Optional[str] = None
    signed_content: Optional[str] = None
    verification_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[FileMetadata] = None
    processing_time: float = 0.0


@dataclass
class BatchSigningResult:
    """Result of batch signing operation."""
    total_files: int
    successful: int
    failed: int
    results: List[SigningResult]
    total_time: float
    skipped: int = 0
    
    def summary(self) -> str:
        """Get human-readable summary."""
        summary_text = (
            f"Batch Signing Complete\n"
            f"  Total: {self.total_files}\n"
            f"  Success: {self.successful}\n"
            f"  Failed: {self.failed}\n"
        )
        if self.skipped > 0:
            summary_text += f"  Skipped (unchanged): {self.skipped}\n"
        summary_text += f"  Time: {self.total_time:.2f}s"
        return summary_text
    
    def to_json(self, output_path: Path) -> None:
        """Save results to JSON file."""
        data = {
            "summary": {
                "total_files": self.total_files,
                "successful": self.successful,
                "failed": self.failed,
                "total_time": self.total_time
            },
            "results": [
                {
                    "file_path": str(r.file_path),
                    "success": r.success,
                    "document_id": r.document_id,
                    "verification_url": r.verification_url,
                    "error": r.error,
                    "processing_time": r.processing_time
                }
                for r in self.results
            ]
        }
        output_path.write_text(json.dumps(data, indent=2))


class RepositorySigner:
    """
    Sign entire repositories recursively with C2PA-compliant metadata.
    
    Example:
        >>> from encypher_enterprise import EncypherClient, RepositorySigner
        >>> 
        >>> client = EncypherClient(api_key="encypher_...")
        >>> signer = RepositorySigner(client)
        >>> 
        >>> # Sign all markdown files in a directory
        >>> result = signer.sign_directory(
        ...     Path("./articles"),
        ...     patterns=["*.md", "*.txt"],
        ...     metadata_fn=lambda p: FileMetadata(
        ...         author="Jane Doe",
        ...         publisher="Acme News"
        ...     )
        ... )
        >>> print(result.summary())
    """
    
    def __init__(
        self,
        client: Union[EncypherClient, AsyncEncypherClient],
        use_sentence_tracking: bool = True,
        max_concurrent: int = 5
    ):
        """
        Initialize repository signer.
        
        Args:
            client: Encypher client instance
            use_sentence_tracking: Enable sentence-level tracking (Enterprise tier)
            max_concurrent: Maximum concurrent signing operations
        """
        self.client = client
        self.use_sentence_tracking = use_sentence_tracking
        self.max_concurrent = max_concurrent
        self._is_async = isinstance(client, AsyncEncypherClient)
    
    def sign_directory(
        self,
        directory: Path,
        patterns: List[str] = ["*.md", "*.txt", "*.html"],
        exclude_patterns: List[str] = ["node_modules/**", ".git/**", "**/__pycache__/**"],
        metadata_fn: Optional[Callable[[Path], FileMetadata]] = None,
        recursive: bool = True,
        output_dir: Optional[Path] = None,
        save_manifest: bool = True,
        incremental: bool = False,
        state_file: Optional[Path] = None,
        force_resign: bool = False,
        track_versions: bool = False
    ) -> BatchSigningResult:
        """
        Sign all files in a directory matching patterns.
        
        Args:
            directory: Directory to scan
            patterns: Glob patterns to match (e.g., ["*.md", "*.txt"])
            exclude_patterns: Patterns to exclude
            metadata_fn: Function to generate metadata for each file
            recursive: Recursively scan subdirectories
            output_dir: Directory to save signed files (default: same as source)
            save_manifest: Save C2PA manifest alongside signed files
            incremental: Only sign changed files (uses state file)
            state_file: Path to state file (default: .encypher-state.json in directory)
            force_resign: Force re-signing even if unchanged (when incremental=True)
        
        Returns:
            BatchSigningResult with details of all operations
        """
        if self._is_async:
            return asyncio.run(self._sign_directory_async(
                directory, patterns, exclude_patterns, metadata_fn,
                recursive, output_dir, save_manifest, incremental, state_file, force_resign, track_versions
            ))
        else:
            return self._sign_directory_sync(
                directory, patterns, exclude_patterns, metadata_fn,
                recursive, output_dir, save_manifest, incremental, state_file, force_resign, track_versions
            )
    
    def _sign_directory_sync(
        self,
        directory: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        metadata_fn: Optional[Callable[[Path], FileMetadata]],
        recursive: bool,
        output_dir: Optional[Path],
        save_manifest: bool,
        incremental: bool,
        state_file: Optional[Path],
        force_resign: bool,
        track_versions: bool
    ) -> BatchSigningResult:
        """Synchronous directory signing."""
        import time
        start_time = time.time()
        
        # Initialize state manager if incremental
        state_manager = None
        if incremental:
            if state_file is None:
                state_file = directory / ".encypher-state.json"
            state_manager = StateManager(state_file)
        
        # Find files
        all_files = self._find_files(directory, patterns, exclude_patterns, recursive)
        
        # Filter to changed files if incremental
        if incremental and not force_resign:
            files_to_sign = state_manager.get_changed_files(all_files)
            skipped_count = len(all_files) - len(files_to_sign)
        else:
            files_to_sign = all_files
            skipped_count = 0
        
        results = []
        
        for file_path in files_to_sign:
            result = self._sign_file_sync(
                file_path, metadata_fn, output_dir, save_manifest
            )
            results.append(result)
            
            # Update state if successful
            if incremental and result.success and state_manager:
                state_manager.update_file_state(file_path, result.document_id, track_versions=track_versions)
        
        # Save state if incremental
        if incremental and state_manager:
            state_manager.save_state()
        
        total_time = time.time() - start_time
        
        batch_result = BatchSigningResult(
            total_files=len(results),
            successful=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            results=results,
            total_time=total_time
        )
        
        # Add skipped count to summary
        if skipped_count > 0:
            batch_result.skipped = skipped_count
        
        return batch_result
    
    async def _sign_directory_async(
        self,
        directory: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        metadata_fn: Optional[Callable[[Path], FileMetadata]],
        recursive: bool,
        output_dir: Optional[Path],
        save_manifest: bool,
        incremental: bool,
        state_file: Optional[Path],
        force_resign: bool,
        track_versions: bool
    ) -> BatchSigningResult:
        """Asynchronous directory signing with concurrency control."""
        import time
        start_time = time.time()
        
        # Initialize state manager if incremental
        state_manager = None
        if incremental:
            if state_file is None:
                state_file = directory / ".encypher-state.json"
            state_manager = StateManager(state_file)
        
        # Find files
        all_files = self._find_files(directory, patterns, exclude_patterns, recursive)
        
        # Filter to changed files if incremental
        if incremental and not force_resign:
            files_to_sign = state_manager.get_changed_files(all_files)
            skipped_count = len(all_files) - len(files_to_sign)
        else:
            files_to_sign = all_files
            skipped_count = 0
        
        # Sign files with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def sign_with_semaphore(file_path: Path) -> SigningResult:
            async with semaphore:
                return await self._sign_file_async(
                    file_path, metadata_fn, output_dir, save_manifest
                )
        
        results = await asyncio.gather(
            *[sign_with_semaphore(f) for f in files_to_sign],
            return_exceptions=True
        )
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(SigningResult(
                    file_path=files_to_sign[i],
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
                # Update state if successful
                if incremental and result.success and state_manager:
                    state_manager.update_file_state(files_to_sign[i], result.document_id, track_versions=track_versions)
        
        # Save state if incremental
        if incremental and state_manager:
            state_manager.save_state()
        
        total_time = time.time() - start_time
        
        batch_result = BatchSigningResult(
            total_files=len(processed_results),
            successful=sum(1 for r in processed_results if r.success),
            failed=sum(1 for r in processed_results if not r.success),
            results=processed_results,
            total_time=total_time
        )
        
        # Add skipped count to summary
        if skipped_count > 0:
            batch_result.skipped = skipped_count
        
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
        
        # Always exclude signed files
        default_excludes = ["*.signed.*", "**/*.signed.*"]
        all_excludes = list(exclude_patterns) + default_excludes
        
        for pattern in patterns:
            if recursive:
                matched = directory.rglob(pattern)
            else:
                matched = directory.glob(pattern)
            
            for file_path in matched:
                # Check exclusions
                excluded = False
                for exclude in all_excludes:
                    if file_path.match(exclude):
                        excluded = True
                        break
                
                if not excluded and file_path.is_file():
                    files.append(file_path)
        
        return sorted(set(files))
    
    def _sign_file_sync(
        self,
        file_path: Path,
        metadata_fn: Optional[Callable[[Path], FileMetadata]],
        output_dir: Optional[Path],
        save_manifest: bool
    ) -> SigningResult:
        """Sign a single file synchronously."""
        import time
        start_time = time.time()
        
        try:
            # Read file
            content = file_path.read_text(encoding='utf-8')
            
            # Generate metadata
            metadata = metadata_fn(file_path) if metadata_fn else FileMetadata()
            
            # Set defaults
            if not metadata.title:
                metadata.title = file_path.stem
            if not metadata.content_type:
                metadata.content_type = mimetypes.guess_type(file_path)[0] or "text/plain"
            if not metadata.instance_id:
                metadata.instance_id = self._generate_instance_id(file_path, content)
            
            # Convert to C2PA manifest
            c2pa_metadata = metadata.to_c2pa_manifest()
            
            # Sign content
            response = self.client.sign(
                text=content,
                title=metadata.title,
                metadata=c2pa_metadata
            )
            
            # Determine output path
            if output_dir:
                output_path = output_dir / file_path.name
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_path = file_path.parent / f"{file_path.stem}.signed{file_path.suffix}"
            
            # Save signed content
            output_path.write_text(response.signed_text, encoding='utf-8')
            
            # Save manifest if requested
            if save_manifest:
                manifest_path = output_path.parent / f"{output_path.stem}.c2pa.json"
                manifest_path.write_text(json.dumps(c2pa_metadata, indent=2))
            
            processing_time = time.time() - start_time
            
            return SigningResult(
                file_path=file_path,
                success=True,
                document_id=response.document_id,
                signed_content=response.signed_text,
                verification_url=response.verification_url,
                metadata=metadata,
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return SigningResult(
                file_path=file_path,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def _sign_file_async(
        self,
        file_path: Path,
        metadata_fn: Optional[Callable[[Path], FileMetadata]],
        output_dir: Optional[Path],
        save_manifest: bool
    ) -> SigningResult:
        """Sign a single file asynchronously."""
        import time
        start_time = time.time()
        
        try:
            # Read file
            content = file_path.read_text(encoding='utf-8')
            
            # Generate metadata
            metadata = metadata_fn(file_path) if metadata_fn else FileMetadata()
            
            # Set defaults
            if not metadata.title:
                metadata.title = file_path.stem
            if not metadata.content_type:
                metadata.content_type = mimetypes.guess_type(file_path)[0] or "text/plain"
            if not metadata.instance_id:
                metadata.instance_id = self._generate_instance_id(file_path, content)
            
            # Convert to C2PA manifest
            c2pa_metadata = metadata.to_c2pa_manifest()
            
            # Sign content
            response = await self.client.sign(
                text=content,
                title=metadata.title,
                metadata=c2pa_metadata
            )
            
            # Determine output path
            if output_dir:
                output_path = output_dir / file_path.name
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_path = file_path.parent / f"{file_path.stem}.signed{file_path.suffix}"
            
            # Save signed content
            output_path.write_text(response.signed_text, encoding='utf-8')
            
            # Save manifest if requested
            if save_manifest:
                manifest_path = output_path.parent / f"{output_path.stem}.c2pa.json"
                manifest_path.write_text(json.dumps(c2pa_metadata, indent=2))
            
            processing_time = time.time() - start_time
            
            return SigningResult(
                file_path=file_path,
                success=True,
                document_id=response.document_id,
                signed_content=response.signed_text,
                verification_url=response.verification_url,
                metadata=metadata,
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return SigningResult(
                file_path=file_path,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    def _generate_instance_id(self, file_path: Path, content: str) -> str:
        """Generate unique instance ID for file."""
        # Use file path + content hash for deterministic ID
        combined = f"{file_path}:{hashlib.sha256(content.encode()).hexdigest()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
