"""Ensure Alembic revision graph has no missing down_revision references."""

from __future__ import annotations

import ast
from pathlib import Path


VERSIONS_DIR = Path(__file__).resolve().parents[1] / "alembic" / "versions"


def _extract_revision_metadata(path: Path) -> tuple[str | None, str | tuple[str, ...] | None]:
    tree = ast.parse(path.read_text())
    revision: str | None = None
    down_revision: str | tuple[str, ...] | None = None

    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue

        if target.id == "revision" and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            revision = node.value.value

        if target.id == "down_revision":
            if isinstance(node.value, ast.Constant):
                down_revision = node.value.value if isinstance(node.value.value, str) else None
            elif isinstance(node.value, (ast.Tuple, ast.List)):
                refs: list[str] = []
                for elt in node.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        refs.append(elt.value)
                down_revision = tuple(refs)

    return revision, down_revision


def test_all_down_revisions_point_to_existing_revisions() -> None:
    revision_to_file: dict[str, str] = {}
    down_references: list[tuple[str, str | tuple[str, ...] | None]] = []

    for migration_file in sorted(VERSIONS_DIR.glob("*.py")):
        revision, down_revision = _extract_revision_metadata(migration_file)
        if not revision:
            continue
        revision_to_file[revision] = migration_file.name
        down_references.append((migration_file.name, down_revision))

    missing_refs: list[str] = []
    for migration_name, down_revision in down_references:
        if down_revision is None:
            continue
        refs = down_revision if isinstance(down_revision, tuple) else (down_revision,)
        for ref in refs:
            if ref and ref not in revision_to_file:
                missing_refs.append(f"{migration_name} -> {ref}")

    assert not missing_refs, "Missing Alembic down_revision targets: " + ", ".join(sorted(missing_refs))
