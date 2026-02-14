from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "add_licensing_agreement_management.py"
)


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_licensing_agreement_management", MIGRATION_PATH)
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


def test_upgrade_skips_existing_tables_and_indexes(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    table_names = {
        "ai_companies",
        "licensing_agreements",
        "content_access_logs",
        "revenue_distributions",
        "member_revenue",
    }
    index_map = {
        "ai_companies": {"ix_ai_companies_company_name", "ix_ai_companies_status"},
        "licensing_agreements": {
            "ix_licensing_agreements_ai_company_id",
            "ix_licensing_agreements_status",
            "ix_licensing_agreements_dates",
        },
        "content_access_logs": {
            "ix_content_access_logs_agreement_id",
            "ix_content_access_logs_content_id",
            "ix_content_access_logs_member_id",
            "ix_content_access_logs_accessed_at",
        },
        "revenue_distributions": {
            "ix_revenue_distributions_agreement_id",
            "ix_revenue_distributions_period",
            "ix_revenue_distributions_status",
        },
        "member_revenue": {
            "ix_member_revenue_distribution_id",
            "ix_member_revenue_member_id",
            "ix_member_revenue_status",
        },
    }

    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector({name: True for name in table_names}, index_map),
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


def test_upgrade_adds_missing_indexes_for_existing_tables(
    monkeypatch: pytest.MonkeyPatch,
    migration_module: ModuleType,
) -> None:
    table_names = {
        "ai_companies",
        "licensing_agreements",
        "content_access_logs",
        "revenue_distributions",
        "member_revenue",
    }

    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector({name: True for name in table_names}, {}),
    )

    created_indexes: list[str] = []
    monkeypatch.setattr(migration_module.op, "create_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        migration_module.op,
        "create_index",
        lambda index_name, table_name, columns, **kwargs: created_indexes.append(index_name),
    )

    migration_module.upgrade()

    assert set(created_indexes) == {
        "ix_ai_companies_company_name",
        "ix_ai_companies_status",
        "ix_licensing_agreements_ai_company_id",
        "ix_licensing_agreements_status",
        "ix_licensing_agreements_dates",
        "ix_content_access_logs_agreement_id",
        "ix_content_access_logs_content_id",
        "ix_content_access_logs_member_id",
        "ix_content_access_logs_accessed_at",
        "ix_revenue_distributions_agreement_id",
        "ix_revenue_distributions_period",
        "ix_revenue_distributions_status",
        "ix_member_revenue_distribution_id",
        "ix_member_revenue_member_id",
        "ix_member_revenue_status",
    }
