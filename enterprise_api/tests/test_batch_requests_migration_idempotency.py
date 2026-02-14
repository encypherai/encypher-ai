from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "add_batch_requests.py"
)


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_batch_requests", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, table_map: dict[str, bool], index_map: dict[str, set[str]]) -> None:
        self._table_map = table_map
        self._index_map = index_map

    def has_table(self, table_name: str) -> bool:
        return self._table_map.get(table_name, False)

    def get_indexes(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": name} for name in sorted(self._index_map.get(table_name, set()))]


def test_enum_definitions_disable_implicit_create(migration_module: ModuleType) -> None:
    assert getattr(migration_module.batch_request_type, "create_type", None) is False
    assert getattr(migration_module.batch_status_enum, "create_type", None) is False
    assert getattr(migration_module.batch_item_status_enum, "create_type", None) is False


def test_upgrade_skips_existing_tables_and_indexes(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    index_map = {
        "batch_requests": {"ix_batch_requests_org_status", "ix_batch_requests_expires_at"},
        "batch_items": {"ix_batch_items_batch_request_id", "ix_batch_items_document_status"},
    }

    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector({"batch_requests": True, "batch_items": True}, index_map),
    )

    enum_create_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.batch_request_type,
        "create",
        lambda bind, checkfirst=True: enum_create_calls.append("batch_request_type"),
    )
    monkeypatch.setattr(
        migration_module.batch_status_enum,
        "create",
        lambda bind, checkfirst=True: enum_create_calls.append("batch_request_status"),
    )
    monkeypatch.setattr(
        migration_module.batch_item_status_enum,
        "create",
        lambda bind, checkfirst=True: enum_create_calls.append("batch_item_status"),
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

    assert enum_create_calls == ["batch_request_type", "batch_request_status", "batch_item_status"]
    assert create_table_calls == []
    assert create_index_calls == []


def test_upgrade_creates_missing_tables_and_indexes(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector({"batch_requests": False, "batch_items": False}, {}),
    )

    monkeypatch.setattr(migration_module.batch_request_type, "create", lambda bind, checkfirst=True: None)
    monkeypatch.setattr(migration_module.batch_status_enum, "create", lambda bind, checkfirst=True: None)
    monkeypatch.setattr(migration_module.batch_item_status_enum, "create", lambda bind, checkfirst=True: None)

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

    assert create_table_calls == ["batch_requests", "batch_items"]
    assert set(create_index_calls) == {
        "ix_batch_requests_org_status",
        "ix_batch_requests_expires_at",
        "ix_batch_items_batch_request_id",
        "ix_batch_items_document_status",
    }
