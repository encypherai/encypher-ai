from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


SUBSCRIPTION_MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "20251125_150600_add_organization_subscriptions.py"
)

USAGE_MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "20251125_150700_add_usage_records.py"
)


@pytest.fixture
def subscription_migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_organization_subscriptions", SUBSCRIPTION_MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def usage_migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_usage_records", USAGE_MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, tables: set[str], indexes: dict[str, set[str]], unique_constraints: dict[str, set[str]]) -> None:
        self._tables = tables
        self._indexes = indexes
        self._unique_constraints = unique_constraints
        self._columns: dict[str, set[str]] = {}

    def has_table(self, table_name: str) -> bool:
        return table_name in self._tables

    def get_indexes(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": idx} for idx in sorted(self._indexes.get(table_name, set()))]

    def get_unique_constraints(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": name} for name in sorted(self._unique_constraints.get(table_name, set()))]

    def get_columns(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": col} for col in sorted(self._columns.get(table_name, set()))]


def test_subscription_upgrade_skips_existing_artifacts(monkeypatch: pytest.MonkeyPatch, subscription_migration_module: ModuleType) -> None:
    monkeypatch.setattr(subscription_migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        subscription_migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(
            tables={"organization_subscriptions"},
            indexes={
                "organization_subscriptions": {
                    "ix_org_subscriptions_org_id",
                    "ix_org_subscriptions_stripe_customer",
                    "ix_org_subscriptions_stripe_sub",
                    "ix_org_subscriptions_status",
                }
            },
            unique_constraints={},
        ),
    )

    create_table_calls: list[str] = []
    create_index_calls: list[str] = []

    monkeypatch.setattr(subscription_migration_module.op, "create_table", lambda name, *args, **kwargs: create_table_calls.append(name))
    monkeypatch.setattr(subscription_migration_module.op, "create_index", lambda name, table, cols, **kwargs: create_index_calls.append(name))

    subscription_migration_module.upgrade()

    assert create_table_calls == []
    assert create_index_calls == []


def test_usage_upgrade_skips_existing_artifacts(monkeypatch: pytest.MonkeyPatch, usage_migration_module: ModuleType) -> None:
    monkeypatch.setattr(usage_migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        usage_migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(
            tables={"usage_records"},
            indexes={
                "usage_records": {
                    "ix_usage_records_org_id",
                    "ix_usage_records_metric",
                    "ix_usage_records_period",
                    "ix_usage_records_org_metric",
                    "ix_usage_records_billed",
                }
            },
            unique_constraints={"usage_records": {"uq_usage_records_org_metric_period"}},
        ),
    )

    create_table_calls: list[str] = []
    create_index_calls: list[str] = []
    create_unique_calls: list[str] = []

    monkeypatch.setattr(usage_migration_module.op, "create_table", lambda name, *args, **kwargs: create_table_calls.append(name))
    monkeypatch.setattr(usage_migration_module.op, "create_index", lambda name, table, cols, **kwargs: create_index_calls.append(name))
    monkeypatch.setattr(usage_migration_module.op, "create_unique_constraint", lambda name, table, cols, **kwargs: create_unique_calls.append(name))

    usage_migration_module.upgrade()

    assert create_table_calls == []
    assert create_index_calls == []
    assert create_unique_calls == []


def test_usage_upgrade_skips_constraint_and_indexes_for_legacy_schema(
    monkeypatch: pytest.MonkeyPatch,
    usage_migration_module: ModuleType,
) -> None:
    monkeypatch.setattr(usage_migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        usage_migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(
            tables={"usage_records"},
            indexes={"usage_records": set()},
            unique_constraints={"usage_records": set()},
        ),
    )

    # Mirror production legacy usage schema where metric/billed/period columns do not exist.
    monkeypatch.setattr(
        usage_migration_module,
        "_has_columns",
        lambda _table, cols: cols.issubset({"id", "organization_id", "created_at"}),
    )

    create_unique_calls: list[str] = []
    create_index_calls: list[str] = []

    monkeypatch.setattr(usage_migration_module.op, "create_unique_constraint", lambda name, table, cols, **kwargs: create_unique_calls.append(name))
    monkeypatch.setattr(usage_migration_module.op, "create_index", lambda name, table, cols, **kwargs: create_index_calls.append(name))

    usage_migration_module.upgrade()

    assert create_unique_calls == []
    assert create_index_calls == ["ix_usage_records_org_id"]
