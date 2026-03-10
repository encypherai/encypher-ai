from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

MIGRATION_PATH = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "add_audit_logs.py"


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_audit_logs", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, has_audit_logs_table: bool, index_names: set[str]) -> None:
        self._has_audit_logs_table = has_audit_logs_table
        self._index_names = index_names

    def has_table(self, table_name: str) -> bool:
        if table_name != "audit_logs":
            return False
        return self._has_audit_logs_table

    def get_indexes(self, table_name: str) -> list[dict[str, str]]:
        if table_name != "audit_logs":
            return []
        return [{"name": idx} for idx in sorted(self._index_names)]


def test_upgrade_skips_existing_table_and_indexes(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(
            has_audit_logs_table=True,
            index_names={
                "ix_audit_logs_org_created",
                "ix_audit_logs_org_action",
                "ix_audit_logs_actor",
                "ix_audit_logs_resource",
            },
        ),
    )

    create_table_calls: list[str] = []
    create_index_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.op,
        "create_table",
        lambda table_name, *args, **kwargs: create_table_calls.append(table_name),
    )
    monkeypatch.setattr(
        migration_module.op,
        "create_index",
        lambda index_name, table_name, columns, **kwargs: create_index_calls.append(index_name),
    )

    migration_module.upgrade()

    assert create_table_calls == []
    assert create_index_calls == []


def test_upgrade_creates_missing_indexes_when_table_exists(
    monkeypatch: pytest.MonkeyPatch,
    migration_module: ModuleType,
) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(has_audit_logs_table=True, index_names=set()),
    )

    create_table_calls: list[str] = []
    create_index_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.op,
        "create_table",
        lambda table_name, *args, **kwargs: create_table_calls.append(table_name),
    )
    monkeypatch.setattr(
        migration_module.op,
        "create_index",
        lambda index_name, table_name, columns, **kwargs: create_index_calls.append(index_name),
    )

    migration_module.upgrade()

    assert create_table_calls == []
    assert set(create_index_calls) == {
        "ix_audit_logs_org_created",
        "ix_audit_logs_org_action",
        "ix_audit_logs_actor",
        "ix_audit_logs_resource",
    }
