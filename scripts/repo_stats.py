# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "rich",
# ]
# ///
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple, Optional, Set, Iterable

from rich.console import Console
from rich.table import Table


def is_binary(path: Path, sample_size: int = 2048) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(sample_size)
        if b"\x00" in chunk:
            return True
        try:
            chunk.decode("utf-8")
            return False
        except Exception:
            return True
    except Exception:
        return True


essential_excludes = {
    ".git",
    ".svn",
    ".hg",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".cache",
    ".swc",
}


def walk_files(root: Path, exclude_dirs: Set[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        parts = set(part for part in p.parts)
        if parts & exclude_dirs:
            continue
        yield p


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.1f} {u}"
        size /= 1024.0
    return f"{size:.1f} TB"


def collect_stats(root: Path, include_ext: Optional[Set[str]], exclude_dirs: Set[str]) -> Tuple[Dict[str, Dict[str, int]], Dict[str, int]]:
    by_ext: Dict[str, Dict[str, int]] = {}
    totals = {"files": 0, "bytes": 0, "lines": 0, "non_empty": 0, "blank": 0}

    for file_path in walk_files(root, exclude_dirs):
        ext = file_path.suffix.lower() or "(no_ext)"
        if include_ext and ext not in include_ext:
            continue
        st = by_ext.setdefault(ext, {"files": 0, "bytes": 0, "lines": 0, "non_empty": 0, "blank": 0})
        try:
            size = file_path.stat().st_size
        except Exception:
            size = 0
        st["files"] += 1
        st["bytes"] += size
        totals["files"] += 1
        totals["bytes"] += size

        if not is_binary(file_path):
            try:
                lines = 0
                non_empty = 0
                with file_path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
                    for line in f:
                        lines += 1
                        if line.strip():
                            non_empty += 1
                blank = lines - non_empty
                st["lines"] += lines
                st["non_empty"] += non_empty
                st["blank"] += blank
                totals["lines"] += lines
                totals["non_empty"] += non_empty
                totals["blank"] += blank
            except Exception:
                pass

    return by_ext, totals


def render_table(by_ext: Dict[str, Dict[str, int]], totals: Dict[str, int], sort_by: str) -> None:
    console = Console()
    table = Table(show_lines=False, header_style="bold", title="Repository File Statistics")
    table.add_column("Extension", justify="left")
    table.add_column("Files", justify="right")
    table.add_column("Lines", justify="right")
    table.add_column("Non-empty", justify="right")
    table.add_column("Blank", justify="right")
    table.add_column("Size", justify="right")

    def sort_key(item: Tuple[str, Dict[str, int]]):
        ext, data = item
        return data.get(sort_by, 0)

    for ext, data in sorted(by_ext.items(), key=sort_key, reverse=True):
        table.add_row(
            ext,
            f"{data['files']:,}",
            f"{data['lines']:,}",
            f"{data['non_empty']:,}",
            f"{data['blank']:,}",
            human_size(data["bytes"]),
        )

    table.add_section()
    table.add_row(
        "Total",
        f"{totals['files']:,}",
        f"{totals['lines']:,}",
        f"{totals['non_empty']:,}",
        f"{totals['blank']:,}",
        human_size(totals["bytes"]),
        style="bold",
    )

    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(prog="repo-stats")
    parser.add_argument("--root", type=str, default=".")
    parser.add_argument(
        "--include-ext",
        type=str,
        default="",
        help="Comma-separated list of extensions to include (e.g. .py,.ts,.tsx)",
    )
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        default="",
        help="Comma-separated list of directory names to exclude",
    )
    parser.add_argument(
        "--sort-by",
        type=str,
        choices=["files", "lines", "bytes", "non_empty", "blank"],
        default="lines",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    include_ext = {e.strip().lower() for e in args.include_ext.split(",") if e.strip()} or None
    exclude_dirs = set(essential_excludes)
    if args.exclude_dirs:
        exclude_dirs |= {e.strip() for e in args.exclude_dirs.split(",") if e.strip()}

    by_ext, totals = collect_stats(root, include_ext, exclude_dirs)
    render_table(by_ext, totals, args.sort_by)


if __name__ == "__main__":
    main()
