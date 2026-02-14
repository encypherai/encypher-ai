from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "20251201_110000_add_status_lists.py"
)


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_status_lists", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, tables: set[str], indexes: dict[str, set[str]], columns: dict[str, set[str]]) -> None:
        self._tables = tables
        self._indexes = indexes
        self._columns = columns

    def has_table(self, table_name: str) -> bool:
        return table_name in self._tables

    def get_indexes(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": idx} for idx in sorted(self._indexes.get(table_name, set()))]

    def get_columns(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": col} for col in sorted(self._columns.get(table_name, set()))]


def test_upgrade_skips_existing_status_list_artifacts(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(
            tables={"status_list_entries", "status_list_metadata"},
            indexes={
                "status_list_entries": {
                    "idx_status_entry_document",
                    "idx_status_entry_org_revoked",
                    "idx_status_entry_list",
                },
                "status_list_metadata": {
                    "idx_status_meta_org_list",
                    "idx_status_meta_stale",
                },
            },
            columns={
                "content_references": {
                    "status_list_index",
                    "status_bit_index",
                    "status_list_url",
                }
            },
        ),
    )

    create_table_calls: list[str] = []
    create_index_calls: list[str] = []
    add_column_calls: list[str] = []

    monkeypatch.setattr(migration_module.op, "create_table", lambda name, *args, **kwargs: create_table_calls.append(name))
    monkeypatch.setattr(migration_module.op, "create_index", lambda name, table, cols, **kwargs: create_index_calls.append(name))
    monkeypatch.setattr(migration_module.op, "add_column", lambda table, column, **kwargs: add_column_calls.append(column.name))

    migration_module.upgrade()

    assert create_table_calls == []
    assert create_index_calls == []
    assert add_column_calls == []
