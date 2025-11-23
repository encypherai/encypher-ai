"""
Directory scanning service to detect signed/unsigned files and optionally mark
unmarked files by calling the Enterprise API.
"""
from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator, Dict, List

import httpx
from encypher.interop.c2pa.text_wrapper import find_and_decode

from app.core.config import settings
from app.schemas.scanning import (
    DirectoryScanRequest,
    DirectoryScanResponse,
    ScannedFileResult,
)
from app.services.directory_signing import (
    _iter_candidate_files,
    _is_excluded,
    _matches_extension,
    _build_context,
    _sign_file_via_api,
)


async def scan_directory(request: DirectoryScanRequest) -> DirectoryScanResponse:
    base_dir = Path(request.directory_path).expanduser()
    if not base_dir.exists() or not base_dir.is_dir():
        raise ValueError(f"Directory not found: {base_dir}")

    if request.mark_unmarked and not settings.ENTERPRISE_API_KEY:
        raise RuntimeError("ENTERPRISE_API_KEY must be configured to mark unmarked files.")

    total = 0
    scanned = 0
    marked = 0
    errors = 0
    skipped = 0
    results: List[ScannedFileResult] = []

    headers = {"Authorization": f"Bearer {settings.ENTERPRISE_API_KEY}"} if settings.ENTERPRISE_API_KEY else {}
    endpoint = f"{settings.ENTERPRISE_API_BASE_URL.rstrip('/')}/sign"

    async with httpx.AsyncClient(timeout=settings.ENTERPRISE_API_TIMEOUT) as client:
        async for res in _process_scan(
            client=client,
            endpoint=endpoint,
            headers=headers,
            base_dir=base_dir,
            request=request,
        ):
            total += 1
            results.append(res)
            if res.status == "scanned":
                scanned += 1
            elif res.status == "marked":
                marked += 1
            elif res.status == "error":
                errors += 1
            else:
                skipped += 1

    return DirectoryScanResponse(
        total_files=total,
        scanned=scanned,
        marked=marked,
        errors=errors,
        skipped=skipped,
        results=results,
    )


async def _process_scan(
    client: httpx.AsyncClient,
    endpoint: str,
    headers: Dict[str, str],
    base_dir: Path,
    request: DirectoryScanRequest,
) -> AsyncIterator[ScannedFileResult]:
    for file_path in _iter_candidate_files(base_dir, request.recursive):
        if _is_excluded(file_path, request.exclude_patterns):
            yield ScannedFileResult(
                file_path=str(file_path),
                status="skipped",
                has_metadata=False,
                message="Excluded by pattern match.",
            )
            continue

        if not _matches_extension(file_path, request.include_extensions):
            yield ScannedFileResult(
                file_path=str(file_path),
                status="skipped",
                has_metadata=False,
                message="Extension filtered.",
            )
            continue

        try:
            text = file_path.read_text(encoding=request.encoding)
        except Exception as exc:  # noqa: BLE001
            yield ScannedFileResult(
                file_path=str(file_path),
                status="error",
                has_metadata=False,
                message=f"Failed to read file: {exc}",
            )
            continue

        try:
            manifest_bytes, _clean, _span = find_and_decode(text)
            has_meta = manifest_bytes is not None
        except Exception as exc:
            yield ScannedFileResult(
                file_path=str(file_path),
                status="error",
                has_metadata=False,
                message=f"Failed to inspect file: {exc}",
            )
            continue

        if has_meta and not request.mark_unmarked:
            yield ScannedFileResult(
                file_path=str(file_path),
                status="scanned",
                has_metadata=True,
                message="Already contains C2PA text wrapper.",
            )
            continue

        if has_meta and request.mark_unmarked:
            # Nothing to do for marked files when marking is enabled
            yield ScannedFileResult(
                file_path=str(file_path),
                status="scanned",
                has_metadata=True,
                message="Already contains C2PA text wrapper.",
            )
            continue

        if not request.mark_unmarked:
            yield ScannedFileResult(
                file_path=str(file_path),
                status="scanned",
                has_metadata=False,
                message="No metadata present.",
            )
            continue

        # Mark unmarked: sign via Enterprise API
        rendered = request.schema or {}
        ctx = _build_context(base_dir, file_path, text, request.encoding)
        # Reuse signing service for consistent behavior and writing strategy
        # Map DirectoryScanRequest fields to signing behavior
        from app.schemas.signing import DirectorySigningRequest

        sign_req = DirectorySigningRequest(
            directory_path=str(base_dir),
            recursive=False,
            include_extensions=None,
            exclude_patterns=None,
            output_mode=request.sign_output_mode,
            schema=rendered,
            encoding=request.encoding,
        )

        signed_res = await _sign_file_via_api(
            client=client,
            endpoint=endpoint,
            headers=headers,
            base_dir=base_dir,
            file_path=file_path,
            text_content=text,
            request=sign_req,
        )

        if signed_res.status == "success":
            yield ScannedFileResult(
                file_path=str(file_path),
                status="marked",
                has_metadata=True,
                signed_path=signed_res.signed_path,
                document_id=signed_res.document_id,
                verification_url=signed_res.verification_url,
                message="Marked successfully.",
            )
        elif signed_res.status == "error":
            yield ScannedFileResult(
                file_path=str(file_path),
                status="error",
                has_metadata=False,
                message=signed_res.message,
            )
        else:
            yield ScannedFileResult(
                file_path=str(file_path),
                status="skipped",
                has_metadata=False,
                message=signed_res.message,
            )
