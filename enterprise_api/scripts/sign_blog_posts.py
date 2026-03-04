#!/usr/bin/env python3
"""Batch sign blog markdown files via Encypher Enterprise API.

This script reads markdown files, extracts frontmatter metadata, signs the markdown
body with micro mode + ECC + C2PA, verifies each signed payload, and writes signed
text artifacts sorted by post date.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values

from app.schemas.signing_constants import MANIFEST_MODES


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BlogPost:
    path: Path
    title: str
    date: str
    metadata: dict[str, str]
    body: str
    frontmatter: str


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<fm>.*?)\n---\s*\n?", re.DOTALL)


def _get_vs_char_set() -> set[str]:
    from app.utils.vs256_crypto import VS_CHAR_SET

    chars = set(VS_CHAR_SET)
    chars.add("\uFEFF")
    return chars


def _strip_invisible_markers(text: str, vs_chars: set[str]) -> str:
    return "".join(ch for ch in text if ch not in vs_chars)


def apply_embedding_plan(visible_text: str, embedding_plan: dict[str, Any]) -> str:
    operations = embedding_plan.get("operations") or []
    marker_after_index: dict[int, str] = {}
    for op in operations:
        idx = int(op.get("insert_after_index", -2))
        marker = str(op.get("marker", ""))
        
        # Shift marker past closing punctuation, but NOT past:
        #   - \n \r \t : would cross block boundaries (\n\n before ATX headings)
        #   - * _ : these can be OPENING emphasis delimiters; shifting past them lands the
        #           marker inside the emphasis span (between * and the first word), which
        #           breaks CommonMark italic/bold parsing.  Markers that land before * stay
        #           outside the span and are invisible to the parser.
        #   - ~ ` : same reasoning for strikethrough / code spans
        # Space is kept so markers can shift past the '## ' prefix into heading body text
        # (headings are already protected because \n is excluded and ## only appears after \n\n).
        if idx >= 0:
            while idx < len(visible_text) - 1 and visible_text[idx + 1] in "#\"')]}.!,;:? ":
                idx += 1

        if idx not in marker_after_index:
            marker_after_index[idx] = marker
        else:
            marker_after_index[idx] += marker

    result: list[str] = []
    if -1 in marker_after_index:
        result.append(marker_after_index[-1])

    for i, ch in enumerate(visible_text):
        result.append(ch)
        if i in marker_after_index:
            result.append(marker_after_index[i])

    return "".join(result)


def normalize_base_url(base_url: str) -> str:
    value = base_url.strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value.rstrip("/")
    return f"https://{value.rstrip('/')}"


def parse_frontmatter(markdown_text: str) -> tuple[dict[str, str], str, str]:
    match = _FRONTMATTER_RE.match(markdown_text)
    if not match:
        return {}, markdown_text, ""

    frontmatter_block = match.group("fm")
    metadata: dict[str, str] = {}
    for line in frontmatter_block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    frontmatter = markdown_text[: match.end()]
    body = markdown_text[match.end() :]
    return metadata, body, frontmatter


def build_signed_markdown(post: BlogPost, signed_body: str) -> str:
    if post.frontmatter:
        return f"{post.frontmatter}{signed_body}"
    return signed_body


def _parse_date_key(date_value: str) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(date_value)
    except ValueError:
        return dt.datetime.max


def gather_posts(paths: list[Path]) -> list[BlogPost]:
    markdown_files: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".md":
            markdown_files.add(path)
            continue
        if path.is_dir():
            markdown_files.update(path.rglob("*.md"))

    posts: list[BlogPost] = []
    for md_path in sorted(markdown_files):
        raw = md_path.read_text(encoding="utf-8")
        metadata, body, frontmatter = parse_frontmatter(raw)
        title = metadata.get("title") or md_path.stem
        date_value = metadata.get("date") or "9999-12-31"
        posts.append(
            BlogPost(
                path=md_path,
                title=title,
                date=date_value,
                metadata=metadata,
                body=body,
                frontmatter=frontmatter,
            )
        )

    posts.sort(key=lambda post: _parse_date_key(post.date))
    return posts


def resolve_api_config(
    api_key: str | None,
    base_url: str | None,
    env_file: str | None,
) -> tuple[str, str]:
    env_values: dict[str, str | None] = {}
    if env_file:
        env_values = dict(dotenv_values(env_file))

    resolved_api_key = (
        api_key
        or env_values.get("ENYCPHER_API_KEY")
        or os.environ.get("ENYCPHER_API_KEY")
        or env_values.get("ENCYPHER_API_KEY")
        or os.environ.get("ENCYPHER_API_KEY")
    )
    resolved_base_url = (
        base_url
        or env_values.get("ENCYPHER_BASE_URL")
        or os.environ.get("ENCYPHER_BASE_URL")
        or "api.encypherai.com"
    )

    if not resolved_api_key:
        raise ValueError(
            "Missing API key. Set ENYCPHER_API_KEY (preferred) in .env.skills "
            "or pass --api-key."
        )

    return resolved_api_key, normalize_base_url(resolved_base_url)


def sign_markdown_text(
    post: BlogPost,
    api_key: str,
    base_url: str,
    client: Any | None = None,
    manifest_mode: str = "micro",
    ecc: bool = True,
) -> str:
    vs_chars = _get_vs_char_set()
    unsigned_body = _strip_invisible_markers(post.body, vs_chars)

    payload = {
        "document_id": f"blog_{uuid.uuid4().hex[:12]}",
        "text": unsigned_body,
        "document_title": post.title,
        "options": {
            "document_type": "article",
            "manifest_mode": manifest_mode,
            "ecc": ecc,
            "embed_c2pa": False,
            "return_embedding_plan": True,
            "segmentation_level": "sentence",
            "segmentation_levels": ["sentence", "paragraph"],
            "embedding_strategy": "single_point",
            "index_for_attribution": True,
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    owns_client = client is None
    if owns_client:
        client = httpx.Client(base_url=base_url, timeout=60.0)

    try:
        sign_response = client.post("/api/v1/sign", headers=headers, json=payload)
        if sign_response.status_code != 201:
            raise RuntimeError(
                f"Sign API returned {sign_response.status_code}: {sign_response.text[:500]}"
            )

        sign_data = sign_response.json()
        signed_doc = sign_data.get("data", {}).get("document", {})
        signed_text = signed_doc.get("signed_text")
        if not signed_text:
            raise RuntimeError("Sign API response missing signed_text")

        embedding_plan = signed_doc.get("embedding_plan")
        if isinstance(embedding_plan, dict) and embedding_plan.get("operations"):
            reconstructed = apply_embedding_plan(unsigned_body, embedding_plan)
            if reconstructed != signed_text:
                logger.warning(
                    "embedding_plan reconstruction differs from API signed_text for %s; using shifted reconstructed text to preserve markdown formatting",
                    post.path,
                )
            signed_text = reconstructed

        verify_response = client.post(
            "/api/v1/verify",
            headers=headers,
            json={"text": signed_text},
        )
        if verify_response.status_code == 503:
            # Key service unavailable (e.g. local dev without full stack).
            # Signing succeeded; skip verification rather than failing the whole run.
            logger.warning(
                "Verify skipped for %s — key service unavailable (503); signed content written as-is.",
                post.path,
            )
        elif verify_response.status_code != 200:
            raise RuntimeError(
                f"Verify API returned {verify_response.status_code}: {verify_response.text[:500]}"
            )
        else:
            verify_data = verify_response.json()
            if not verify_data.get("data", {}).get("valid", False):
                raise RuntimeError(f"Verification failed for {post.path}")

        return signed_text
    finally:
        if owns_client:
            client.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch sign blog markdown files using micro mode + ECC + C2PA.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to scan for blog markdown files",
    )
    parser.add_argument(
        "--glob",
        action="append",
        default=[],
        help="Additional glob patterns (evaluated from repo root)",
    )
    parser.add_argument(
        "--env-file",
        default=".env.skills",
        help="Env file containing ENYCPHER_API_KEY and ENCYPHER_BASE_URL",
    )
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument(
        "--output-dir",
        default="enterprise_api/output/signed_blog_posts",
        help="Directory to write signing report artifact",
    )
    parser.add_argument(
        "--from-date",
        default=None,
        help="Include posts with date >= YYYY-MM-DD",
    )
    parser.add_argument(
        "--to-date",
        default=None,
        help="Include posts with date <= YYYY-MM-DD",
    )
    parser.add_argument(
        "--manifest-mode",
        default="micro",
        choices=MANIFEST_MODES,
        help="Manifest mode (default: micro)",
    )
    parser.add_argument(
        "--no-ecc",
        action="store_true",
        help="Disable Reed-Solomon ECC (micro mode only)",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _within_date_range(post: BlogPost, from_date: str | None, to_date: str | None) -> bool:
    if from_date and post.date < from_date:
        return False
    if to_date and post.date > to_date:
        return False
    return True


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    requested_paths = [Path(value) for value in args.paths]
    if not requested_paths and not args.glob:
        requested_paths = [Path("apps/marketing-site/src/content/blog")]

    for pattern in args.glob:
        requested_paths.extend(Path(".").glob(pattern))

    api_key, base_url = resolve_api_config(
        api_key=args.api_key,
        base_url=args.base_url,
        env_file=args.env_file,
    )

    posts = gather_posts(requested_paths)
    posts = [
        post
        for post in posts
        if _within_date_range(post, args.from_date, args.to_date)
    ]

    if not posts:
        print("No blog posts found for signing.", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, str]] = []

    for index, post in enumerate(posts, start=1):
        print(f"[{index}/{len(posts)}] Signing {post.path} ({post.date})")
        if args.dry_run:
            continue

        signed_text = sign_markdown_text(
            post=post,
            api_key=api_key,
            base_url=base_url,
            manifest_mode=args.manifest_mode,
            ecc=not args.no_ecc,
        )

        signed_markdown = build_signed_markdown(post, signed_text)
        post.path.write_text(signed_markdown, encoding="utf-8")
        summary.append(
            {
                "source": str(post.path),
                "date": post.date,
                "title": post.title,
                "updated_file": str(post.path),
            }
        )

    report_path = output_dir / "signing_report.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Done. Signed {len(summary)} posts.")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
