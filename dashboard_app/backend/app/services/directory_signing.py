"""
Directory signing orchestration leveraging the Enterprise API.
"""
from __future__ import annotations

import fnmatch
import hashlib
from collections.abc import AsyncIterator, Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.schemas.signing import (
    DirectorySigningRequest,
    DirectorySigningResponse,
    SignedFileResult,
)

MAX_SIGN_BYTES = 1_000_000  # Aligns with Enterprise API contract


def _iter_candidate_files(
    base_dir: Path,
    recursive: bool,
) -> Iterable[Path]:
    """Yield candidate files in directory (without applying filters)."""
    if recursive:
        yield from (p for p in base_dir.rglob("*") if p.is_file())
    else:
        yield from (p for p in base_dir.iterdir() if p.is_file())


def _is_excluded(path: Path, patterns: Optional[List[str]]) -> bool:
    if not patterns:
        return False
    path_str = str(path)
    return any(fnmatch.fnmatch(path_str, pattern) for pattern in patterns)


def _matches_extension(path: Path, extensions: Optional[List[str]]) -> bool:
    if not extensions:
        return True
    suffix = path.suffix.lower()
    return suffix in {ext.lower() for ext in extensions}


def _render_template(value: Any, context: Dict[str, Any]) -> Any:
    """Recursively render str.format templates inside arbitrary JSON-like structures."""
    if isinstance(value, str):
        try:
            return value.format(**context)
        except KeyError:
            return value
    if isinstance(value, list):
        return [_render_template(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _render_template(val, context) for key, val in value.items()}
    return value


def _sidecar_path(file_path: Path) -> Path:
    """Return default sidecar path (<name>.signed)."""
    return file_path.with_name(f"{file_path.name}.signed")


async def sign_directory(request: DirectorySigningRequest) -> DirectorySigningResponse:
    """
    Iterate over files in the provided directory, signing each via Enterprise API.

    Returns summary response with per-file outcomes.
    """
    base_dir = Path(request.directory_path).expanduser()
    if not base_dir.exists() or not base_dir.is_dir():
        raise ValueError(f"Directory not found: {base_dir}")

    if not settings.ENTERPRISE_API_KEY:
        raise RuntimeError("ENTERPRISE_API_KEY must be configured for directory signing.")

    total_candidates = 0
    processed = 0
    successes = 0
    failures = 0
    skipped = 0
    results: List[SignedFileResult] = []

    headers = {"Authorization": f"Bearer {settings.ENTERPRISE_API_KEY}"}
    endpoint = f"{settings.ENTERPRISE_API_BASE_URL.rstrip('/')}/sign"

    async with httpx.AsyncClient(timeout=settings.ENTERPRISE_API_TIMEOUT) as client:
        async for outcome in _process_files(
            client=client,
            endpoint=endpoint,
            headers=headers,
            base_dir=base_dir,
            request=request,
        ):
            total_candidates += 1
            results.append(outcome)
            if outcome.status == "success":
                successes += 1
                processed += 1
            elif outcome.status == "error":
                failures += 1
                processed += 1
            else:
                skipped += 1

    return DirectorySigningResponse(
        total_files=total_candidates,
        processed_files=processed,
        successful=successes,
        failed=failures,
        skipped=skipped,
        results=results,
    )


async def _process_files(
    client: httpx.AsyncClient,
    endpoint: str,
    headers: Dict[str, str],
    base_dir: Path,
    request: DirectorySigningRequest,
) -> AsyncIterator[SignedFileResult]:
    """Async generator yielding SignedFileResult for each file encountered."""
    for file_path in _iter_candidate_files(base_dir, request.recursive):
        if _is_excluded(file_path, request.exclude_patterns):
            yield SignedFileResult(
                file_path=str(file_path),
                status="skipped",
                message="Excluded by pattern match.",
            )
            continue

        if not _matches_extension(file_path, request.include_extensions):
            yield SignedFileResult(
                file_path=str(file_path),
                status="skipped",
                message="Extension filtered.",
            )
            continue

        try:
            text_content = file_path.read_text(encoding=request.encoding)
        except Exception as exc:  # noqa: BLE001
            yield SignedFileResult(
                file_path=str(file_path),
                status="skipped",
                message=f"Failed to read file: {exc}",
            )
            continue

        byte_length = len(text_content.encode(request.encoding))
        if byte_length > MAX_SIGN_BYTES:
            yield SignedFileResult(
                file_path=str(file_path),
                status="skipped",
                message=f"File exceeds {MAX_SIGN_BYTES} byte limit.",
            )
            continue

        result = await _sign_file_via_api(
            client=client,
            endpoint=endpoint,
            headers=headers,
            base_dir=base_dir,
            file_path=file_path,
            text_content=text_content,
            request=request,
        )
        yield result


async def _sign_file_via_api(
    client: httpx.AsyncClient,
    endpoint: str,
    headers: Dict[str, str],
    base_dir: Path,
    file_path: Path,
    text_content: str,
    request: DirectorySigningRequest,
) -> SignedFileResult:
    """Sign a single file via Enterprise API."""
    context = _build_context(base_dir, file_path, text_content, request.encoding)
    rendered_schema = _render_template(request.schema, context) if request.schema else {}

    payload: Dict[str, Any] = {"text": text_content}
    document_title = rendered_schema.get("document_title", file_path.name)
    payload["document_title"] = document_title

    document_type = rendered_schema.get("document_type")
    if document_type:
        payload["document_type"] = document_type

    document_url = rendered_schema.get("document_url")
    if document_url:
        payload["document_url"] = document_url

    # Optional C2PA fields forwarded to Enterprise API
    claim_generator = rendered_schema.get("claim_generator")
    if claim_generator:
        payload["claim_generator"] = claim_generator

    actions = rendered_schema.get("actions")
    if isinstance(actions, list):
        payload["actions"] = actions

    try:
        response = await client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return SignedFileResult(
            file_path=str(file_path),
            status="error",
            message=f"Enterprise API returned {exc.response.status_code}: {exc.response.text}",
        )
    except httpx.RequestError as exc:
        return SignedFileResult(
            file_path=str(file_path),
            status="error",
            message=f"Enterprise API request failed: {exc}",
        )

    data = response.json()
    success = data.get("success")
    if not success:
        error_message = data.get("error", {}).get("message") if isinstance(data.get("error"), dict) else data
        return SignedFileResult(
            file_path=str(file_path),
            status="error",
            message=f"Enterprise API responded with failure: {error_message}",
        )

    signed_text = data.get("signed_text")
    document_id = data.get("document_id")
    verification_url = data.get("verification_url")

    signed_path: Optional[str] = None
    if request.output_mode != "dry_run" and signed_text is not None:
        target_path = (
            file_path
            if request.output_mode == "overwrite"
            else _sidecar_path(file_path)
        )
        try:
            target_path.write_text(signed_text, encoding=request.encoding)
            signed_path = str(target_path)
        except Exception as exc:  # noqa: BLE001
            return SignedFileResult(
                file_path=str(file_path),
                status="error",
                document_id=document_id,
                verification_url=verification_url,
                message=f"Failed to write signed file: {exc}",
            )

    return SignedFileResult(
        file_path=str(file_path),
        status="success",
        document_id=document_id,
        verification_url=verification_url,
        signed_path=signed_path,
        message="Signed successfully.",
    )


def _build_context(
    base_dir: Path,
    file_path: Path,
    text_content: str,
    encoding: str,
) -> Dict[str, Any]:
    """Build template context for schema substitution."""
    stat = file_path.stat()
    now = datetime.now(timezone.utc).isoformat()
    relative_path = str(file_path.relative_to(base_dir))
    topic = file_path.parent.name
    sha256_hash = hashlib.sha256(text_content.encode(encoding)).hexdigest()

    return {
        "file_name": file_path.name,
        "file_stem": file_path.stem,
        "extension": file_path.suffix,
        "absolute_path": str(file_path.resolve()),
        "relative_path": relative_path,
        "parent_dir": str(file_path.parent),
        "topic": topic,
        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "file_size": stat.st_size,
        "sha256": sha256_hash,
        "generated_at": now,
        "base_directory": str(base_dir),
    }
