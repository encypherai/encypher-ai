from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

BLOG_DIR = Path("/home/developer/code/encypherai-commercial/apps/marketing-site/src/content/blog")
OUTPUT_PATH = Path(
    "/home/developer/code/encypherai-commercial/integrations/wordpress-provenance-plugin/plugin/encypher-provenance/data/marketing-blog-posts.json"
)
CURATED_DEMO_FILES = [
    "What_Is_C2PA_A_Complete_Guide_to_Content_Provenance_Standards.md",
    "C2PA 2.3 Published - Encypher Authors Text Provenance Standard.md",
    "Why_Text_Was_the_Missing_Piece_in_Content_Authenticity.md",
    "Cryptographic_Watermarking_vs_AI_Detection_Why_Proof_Beats_Probability.md",
    "EU_AI_Act_Content_Disclosure_What_Publishers_Must_Know.md",
    "How_AI_Training_Data_Scraping_Works_And_Why_Publishers_Cant_Track_It.md",
    "How_Robots_txt_Fails_Publishers_The_Case_for_In_Content_Rights_Signals.md",
    "The_Downstream_Distribution_Problem_Why_Your_Content_Disappears_After_Publication.md",
    "2025_in_Review_The_Year_Content_Provenance_Became_Essential.md",
    "What If AI Content Came With Built-In Proof of Origin.md",
]


def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        return {}, raw
    parts = raw.split("---\n", 2)
    if len(parts) < 3:
        return {}, raw
    frontmatter_raw = parts[1]
    body = parts[2]
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in frontmatter_raw.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:\s*", line):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                data[key] = [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
            else:
                data[key] = value.strip("\"'")
            current_key = key
        elif current_key and isinstance(data.get(current_key), list):
            data[current_key].append(line.strip().strip("- ").strip("\"'"))
    return data, body


def markdown_to_html(markdown: str) -> str:
    text = markdown.replace("\r\n", "\n")
    text = re.sub(r"^---[\s\S]*?---\n", "", text, count=1)
    text = re.sub(r"\n```[\s\S]*?```\n", "\n", text)
    lines = text.split("\n")
    html_parts: list[str] = []
    in_list = False
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            html_parts.append(f"<p>{inline_markdown(' '.join(paragraph).strip())}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            flush_list()
            continue
        if line.startswith("# "):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<h1>{inline_markdown(line[2:].strip())}</h1>")
            continue
        if line.startswith("## "):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<h2>{inline_markdown(line[3:].strip())}</h2>")
            continue
        if line.startswith("### "):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<h3>{inline_markdown(line[4:].strip())}</h3>")
            continue
        if line.startswith("- "):
            flush_paragraph()
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{inline_markdown(line[2:].strip())}</li>")
            continue
        paragraph.append(line)

    flush_paragraph()
    flush_list()
    return "\n".join(html_parts).strip()


def inline_markdown(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    return text


def resolve_source_paths(*, limit: int | None, curated: bool, filenames: list[str]) -> list[Path]:
    if filenames:
        paths = [BLOG_DIR / name for name in filenames]
    elif curated:
        paths = [BLOG_DIR / name for name in CURATED_DEMO_FILES]
    else:
        paths = sorted(BLOG_DIR.glob("*.md"))

    existing_paths = [path for path in paths if path.exists()]
    if limit is not None:
        return existing_paths[:limit]
    return existing_paths


def build_posts(*, limit: int | None = 8, curated: bool = False, filenames: list[str] | None = None) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    selected_files = resolve_source_paths(limit=limit, curated=curated, filenames=filenames or [])
    for path in selected_files:
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw)
        title = str(frontmatter.get("title") or path.stem.replace("_", " ")).strip()
        excerpt = str(frontmatter.get("excerpt") or "")
        author = str(frontmatter.get("author") or "Encypher Editorial Team")
        tags = frontmatter.get("tags") if isinstance(frontmatter.get("tags"), list) else []
        date = str(frontmatter.get("date") or "2026-01-01")
        # Strip all Encypher watermark characters so imported content is unsigned plaintext.
        # Tags Block (U+E0000-U+E0FFF): inline C2PA manifest storage.
        # Must use \U000EXXXX (8-digit) notation -- \uEXXXX is only 4 hex digits in Python.
        body = re.sub(r"[\U000E0000-\U000E0FFF]", "", body)
        # Variation Selectors (U+FE00-U+FE0F, U+E0100-U+E01EF): watermark carriers.
        body = re.sub(r"[\uFE00-\uFE0F\U000E0100-\U000E01EF]", "", body)
        # Zero-width characters (ZWNJ, ZWJ, CGJ, MVS, ZWNBSP): watermark bit encoding.
        body = re.sub(r"[\u200C\u200D\u034F\u180E\uFEFF]", "", body)
        content_html = markdown_to_html(body)
        if excerpt:
            content_html = f"<p><strong>{inline_markdown(excerpt)}</strong></p>\n" + content_html
        posts.append(
            {
                "title": title,
                "slug": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-"),
                "date": date,
                "author": author,
                "tags": tags,
                "content": content_html,
            }
        )
    return posts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--curated", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--file", action="append", dest="filenames", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    posts = build_posts(limit=args.limit, curated=args.curated, filenames=args.filenames)
    args.output.write_text(json.dumps(posts, indent=2), encoding="utf-8")
    print(f"wrote {len(posts)} posts to {args.output}")


if __name__ == "__main__":
    main()
