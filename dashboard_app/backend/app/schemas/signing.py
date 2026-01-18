"""
Pydantic schemas for directory signing workflow.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class DirectorySigningRequest(BaseModel):
    """Request payload for initiating directory signing via Enterprise API."""

    directory_path: str = Field(..., description="Absolute path to the directory containing files to sign.")
    recursive: bool = Field(default=True, description="Recurse into sub-directories when true.")
    include_extensions: Optional[List[str]] = Field(
        default=None,
        description="Optional whitelist of file extensions (e.g. ['.txt', '.md']). All files included when omitted.",
    )
    exclude_patterns: Optional[List[str]] = Field(
        default=None,
        description="Optional fnmatch-style patterns to skip (matched against absolute path).",
    )
    output_mode: Literal["sidecar", "overwrite", "dry_run"] = Field(
        default="sidecar",
        description="Writing strategy: sidecar writes <filename>.signed, overwrite replaces originals, dry_run skips file writes.",
    )
    schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template dict used to populate sign request metadata per file.",
    )
    encoding: str = Field(default="utf-8", description="Text encoding used when reading/writing files.")

    @field_validator("include_extensions")
    @classmethod
    def normalize_extensions(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return value
        normalized = []
        for item in value:
            if not item:
                continue
            normalized.append(item if item.startswith(".") else f".{item}")
        return normalized or None


class SignedFileResult(BaseModel):
    """Outcome for a single file processed during directory signing."""

    file_path: str = Field(..., description="Original file path.")
    status: Literal["success", "skipped", "error"] = Field(..., description="Processing outcome.")
    document_id: Optional[str] = Field(default=None, description="Document identifier returned by Enterprise API.")
    verification_url: Optional[str] = Field(default=None, description="Verification URL returned by Enterprise API.")
    signed_path: Optional[str] = Field(default=None, description="Path to the signed output file when written.")
    message: Optional[str] = Field(default=None, description="Additional context or error message.")


class DirectorySigningResponse(BaseModel):
    """Summary response for directory signing run."""

    total_files: int = Field(..., description="Total candidate files discovered.")
    processed_files: int = Field(..., description="Files attempted (excludes filtered/skipped).")
    successful: int = Field(..., description="Number of files signed successfully.")
    failed: int = Field(..., description="Number of files that failed to sign.")
    skipped: int = Field(..., description="Files skipped due to filters or read errors.")
    results: List[SignedFileResult] = Field(default_factory=list, description="Per-file processing results.")
