from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "add_team_members.py"
)


@pytest.fixture
def migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("add_team_members", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Inspector:
    def __init__(self, tables: set[str], indexes: dict[str, set[str]], unique_constraints: dict[str, set[str]]) -> None:
        self._tables = tables
        self._indexes = indexes
        self._unique_constraints = unique_constraints

    def has_table(self, table_name: str) -> bool:
        return table_name in self._tables

    def get_indexes(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": idx} for idx in sorted(self._indexes.get(table_name, set()))]

    def get_unique_constraints(self, table_name: str) -> list[dict[str, str]]:
        return [{"name": name} for name in sorted(self._unique_constraints.get(table_name, set()))]


def test_upgrade_skips_existing_team_artifacts(monkeypatch: pytest.MonkeyPatch, migration_module: ModuleType) -> None:
    monkeypatch.setattr(migration_module.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        migration_module.sa,
        "inspect",
        lambda _bind: _Inspector(
            tables={"team_members", "team_invites"},
            indexes={
                "team_members": {"ix_team_members_org", "ix_team_members_user", "ix_team_members_email"},
                "team_invites": {"ix_team_invites_org", "ix_team_invites_email", "ix_team_invites_token"},
            },
            unique_constraints={"team_members": {"uq_team_members_org_user"}},
        ),
    )

    create_table_calls: list[str] = []
    create_index_calls: list[str] = []
    create_unique_calls: list[str] = []

    monkeypatch.setattr(migration_module.op, "create_table", lambda name, *args, **kwargs: create_table_calls.append(name))
    monkeypatch.setattr(migration_module.op, "create_index", lambda name, table, cols, **kwargs: create_index_calls.append(name))
    monkeypatch.setattr(migration_module.op, "create_unique_constraint", lambda name, table, cols, **kwargs: create_unique_calls.append(name))

    migration_module.upgrade()

    assert create_table_calls == []
    assert create_index_calls == []
    assert create_unique_calls == []
