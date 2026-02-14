from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "add_tier_coalition_fields.py"
)


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_tier_coalition_fields", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, columns: set[str]) -> None:
        self._columns = columns

    def get_columns(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": col} for col in sorted(self._columns)]


def test_upgrade_skips_existing_columns(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    existing_columns = {
        "sentence_tracking_enabled",
        "streaming_enabled",
        "byok_enabled",
        "team_management_enabled",
        "audit_logs_enabled",
        "sso_enabled",
        "custom_assertions_enabled",
        "coalition_member",
        "coalition_rev_share_publisher",
        "coalition_rev_share_encypher",
        "coalition_opted_out",
        "coalition_opted_out_at",
        "sentences_tracked_this_month",
        "batch_operations_this_month",
    }

    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(existing_columns),
    )

    add_column_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.op,
        "add_column",
        lambda table_name, column, *args, **kwargs: add_column_calls.append(column.name),
    )

    execute_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.op,
        "execute",
        lambda sql: execute_calls.append(str(sql)),
    )

    migration_module.upgrade()

    assert add_column_calls == []
    assert len(execute_calls) == 4


def test_upgrade_adds_missing_columns(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(set()),
    )

    add_column_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.op,
        "add_column",
        lambda table_name, column, *args, **kwargs: add_column_calls.append(column.name),
    )

    execute_calls: list[str] = []
    monkeypatch.setattr(
        migration_module.op,
        "execute",
        lambda sql: execute_calls.append(str(sql)),
    )

    migration_module.upgrade()

    assert set(add_column_calls) == {
        "sentence_tracking_enabled",
        "streaming_enabled",
        "byok_enabled",
        "team_management_enabled",
        "audit_logs_enabled",
        "sso_enabled",
        "custom_assertions_enabled",
        "coalition_member",
        "coalition_rev_share_publisher",
        "coalition_rev_share_encypher",
        "coalition_opted_out",
        "coalition_opted_out_at",
        "sentences_tracked_this_month",
        "batch_operations_this_month",
    }
    assert len(execute_calls) == 4
