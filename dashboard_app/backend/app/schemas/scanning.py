"""
Pydantic schemas for directory scanning workflow.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class DirectoryScanRequest(BaseModel):
    """Request payload for scanning a directory for signed/unsigned files.

    If mark_unmarked=True, unmarked files will be signed using the provided schema
    (same templating as DirectorySigningRequest) and sign_output_mode controls write strategy.
    """

    directory_path: str = Field(..., description="Absolute path to the directory to scan.")
    recursive: bool = Field(default=True, description="Recurse into sub-directories when true.")
    include_extensions: Optional[List[str]] = Field(
        default=None, description="Optional whitelist of extensions (e.g. ['.txt', '.md'])."
    )
    exclude_patterns: Optional[List[str]] = Field(
        default=None, description="Optional fnmatch-style patterns to skip (matched against absolute path)."
    )
    encoding: str = Field(default="utf-8", description="Text encoding used when reading files.")
    mark_unmarked: bool = Field(
        default=False, description="When true, unmarked files will be signed via Enterprise API."
    )
    sign_output_mode: Literal["sidecar", "overwrite"] = Field(
        default="sidecar", description="Writing strategy when marking unmarked files."
    )
    schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template dict used to populate sign request metadata per file (same as directory signing).",
    )

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


class ScannedFileResult(BaseModel):
    """Outcome for a single file during scanning."""

    file_path: str = Field(...)
    has_metadata: bool = Field(..., description="Heuristic flag indicating presence of C2PA text wrapper.")
    status: Literal["scanned", "marked", "error", "skipped"] = Field(...)
    message: Optional[str] = Field(default=None)
    signed_path: Optional[str] = Field(default=None)
    document_id: Optional[str] = Field(default=None)
    verification_url: Optional[str] = Field(default=None)


class DirectoryScanResponse(BaseModel):
    total_files: int
    scanned: int
    marked: int
    errors: int
    skipped: int
    results: List[ScannedFileResult] = Field(default_factory=list)
