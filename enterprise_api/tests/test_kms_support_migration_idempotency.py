from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

MIGRATION_PATH = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "add_kms_support.py"


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_kms_support", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, columns_by_table: dict[str, set[str]]) -> None:
        self._columns_by_table = columns_by_table

    def get_columns(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": name} for name in sorted(self._columns_by_table.get(table_name, set()))]


def test_upgrade_skips_existing_columns(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector({"organizations": {"kms_key_id", "kms_region"}}),
    )

    added_columns: list[str] = []

    def _add_column(table_name: str, column) -> None:  # type: ignore[no-untyped-def]
        added_columns.append(column.name)

    monkeypatch.setattr(migration_module.op, "add_column", _add_column)

    migration_module.upgrade()

    assert added_columns == []


def test_upgrade_adds_missing_columns(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector({"organizations": set()}),
    )

    added_columns: list[str] = []

    def _add_column(table_name: str, column) -> None:  # type: ignore[no-untyped-def]
        added_columns.append(column.name)

    monkeypatch.setattr(migration_module.op, "add_column", _add_column)

    migration_module.upgrade()

    assert set(added_columns) == {"kms_key_id", "kms_region"}
